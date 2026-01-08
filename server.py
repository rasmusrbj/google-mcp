#!/usr/bin/env python3
"""
Comprehensive Google Workspace MCP Server
with Full Shared Drive Support
Supports: Gmail, Drive, Docs, Sheets, Slides, Calendar, Tasks
"""
import os
import json
import base64
from pathlib import Path
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Initialize MCP server
mcp = FastMCP("google-workspace-full")

# Token storage - automatically detect the user's credentials
TOKEN_DIR = Path.home() / ".google_workspace_mcp" / "credentials"

def get_token_path():
    """Automatically find the user's credential file."""
    if not TOKEN_DIR.exists():
        raise Exception(f"Credentials directory not found: {TOKEN_DIR}\nPlease run authenticate.py first.")

    # Look for any .json credential file
    json_files = list(TOKEN_DIR.glob("*.json"))

    if not json_files:
        raise Exception(f"No credential files found in {TOKEN_DIR}\nPlease run authenticate.py first.")

    # Use the most recently modified credential file
    token_path = max(json_files, key=lambda p: p.stat().st_mtime)
    return token_path

# All scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/tasks',
    'https://www.googleapis.com/auth/calendar',
]


def get_credentials():
    """Get authenticated credentials with automatic user detection."""
    token_path = get_token_path()
    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(token_path, 'w') as token:
                token.write(creds.to_json())
        else:
            raise Exception("Credentials expired. Please run authenticate.py again.")

    return creds


def get_service(service_name: str, version: str):
    """Get Google API service."""
    creds = get_credentials()
    return build(service_name, version, credentials=creds)


# ============================================================================
# GMAIL TOOLS
# ============================================================================

@mcp.tool()
def gmail_search(query: str, max_results: int = 10) -> str:
    """Search for emails in Gmail with advanced queries."""
    service = get_service('gmail', 'v1')
    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        return f"No messages found for query: {query}"

    output = f"Found {len(messages)} message(s):\n\n"
    for msg in messages:
        message = service.users().messages().get(userId='me', id=msg['id'], format='metadata').execute()
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')
        output += f"📧 {subject}\n   From: {from_addr}\n   Date: {date}\n   ID: {msg['id']}\n\n"
    return output


@mcp.tool()
def gmail_read(message_id: str) -> str:
    """Read a specific Gmail message with full content."""
    service = get_service('gmail', 'v1')
    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    headers = message['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    to_addr = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

    body = ""
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

    return f"Subject: {subject}\nFrom: {from_addr}\nTo: {to_addr}\nDate: {date}\n\n{'-'*60}\n\n{body}"


@mcp.tool()
def gmail_send(to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
    """Send an email via Gmail."""
    service = get_service('gmail', 'v1')
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent_message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"✅ Email sent!\nMessage ID: {sent_message['id']}\nTo: {to}\nSubject: {subject}"


@mcp.tool()
def gmail_reply(message_id: str, body: str) -> str:
    """Reply to an email thread."""
    service = get_service('gmail', 'v1')

    # Get original message to extract thread ID and headers
    original = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    thread_id = original['threadId']
    headers = original['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    to = next((h['value'] for h in headers if h['name'] == 'From'), None)

    if not subject.startswith('Re:'):
        subject = f"Re: {subject}"

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    message['In-Reply-To'] = message_id
    message['References'] = message_id

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId='me', body={'raw': raw, 'threadId': thread_id}).execute()
    return f"✅ Reply sent!\nMessage ID: {sent['id']}\nThread ID: {thread_id}"


@mcp.tool()
def gmail_mark_read(message_id: str) -> str:
    """Mark an email as read."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['UNREAD']}).execute()
    return f"✅ Marked message {message_id} as read"


@mcp.tool()
def gmail_mark_unread(message_id: str) -> str:
    """Mark an email as unread."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['UNREAD']}).execute()
    return f"✅ Marked message {message_id} as unread"


@mcp.tool()
def gmail_archive(message_id: str) -> str:
    """Archive an email (remove from inbox)."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['INBOX']}).execute()
    return f"✅ Archived message {message_id}"


@mcp.tool()
def gmail_delete(message_id: str) -> str:
    """Move an email to trash."""
    service = get_service('gmail', 'v1')
    service.users().messages().trash(userId='me', id=message_id).execute()
    return f"✅ Moved message {message_id} to trash"


# ============================================================================
# DRIVE TOOLS (with Shared Drive support)
# ============================================================================

@mcp.tool()
def drive_list_shared_drives(page_size: int = 100) -> str:
    """List all shared drives (Team Drives) the user has access to."""
    service = get_service('drive', 'v3')
    results = service.drives().list(pageSize=page_size, fields="drives(id, name)").execute()
    drives = results.get('drives', [])

    if not drives:
        return "No shared drives found."

    output = f"Found {len(drives)} shared drive(s):\n\n"
    for drive in drives:
        output += f"📁 {drive['name']}\n   ID: {drive['id']}\n\n"
    return output


@mcp.tool()
def drive_list_files(folder_id: Optional[str] = None, drive_id: Optional[str] = None,
                     query: Optional[str] = None, page_size: int = 20) -> str:
    """List files and folders in Google Drive or Shared Drives."""
    service = get_service('drive', 'v3')

    q_parts = []
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if query:
        q_parts.append(query)

    params = {
        'pageSize': page_size,
        'fields': 'files(id, name, mimeType, modifiedTime, size, webViewLink)',
        'orderBy': 'modifiedTime desc'
    }

    if q_parts:
        params['q'] = " and ".join(q_parts)

    if drive_id:
        params['driveId'] = drive_id
        params['corpora'] = 'drive'
        params['includeItemsFromAllDrives'] = True
        params['supportsAllDrives'] = True
    else:
        params['corpora'] = 'user'

    results = service.files().list(**params).execute()
    files = results.get('files', [])

    if not files:
        return "No files found."

    output = f"Found {len(files)} file(s):\n\n"
    for file in files:
        icon = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
        output += f"{icon} {file['name']}\n   ID: {file['id']}\n   Type: {file['mimeType']}\n   Link: {file.get('webViewLink', 'N/A')}\n\n"
    return output


@mcp.tool()
def drive_create_folder(name: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Create a new folder in Google Drive or a Shared Drive."""
    service = get_service('drive', 'v3')

    file_metadata = {'name': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {'supportsAllDrives': True} if drive_id else {}
    folder = service.files().create(body=file_metadata, fields='id, name, webViewLink', **params).execute()

    return f"✅ Folder created!\nName: {folder['name']}\nID: {folder['id']}\nLink: {folder.get('webViewLink', 'N/A')}"


@mcp.tool()
def drive_upload_file(file_path: str, name: Optional[str] = None, parent_id: Optional[str] = None,
                      drive_id: Optional[str] = None) -> str:
    """Upload a file to Google Drive or Shared Drive."""
    service = get_service('drive', 'v3')

    path = Path(file_path)
    if not path.exists():
        return f"❌ File not found: {file_path}"

    file_metadata = {'name': name or path.name}
    if parent_id:
        file_metadata['parents'] = [parent_id]

    media = MediaFileUpload(file_path, resumable=True)
    params = {'supportsAllDrives': True} if drive_id else {}

    file = service.files().create(body=file_metadata, media_body=media, fields='id, name, webViewLink', **params).execute()
    return f"✅ File uploaded!\nName: {file['name']}\nID: {file['id']}\nLink: {file.get('webViewLink', 'N/A')}"


@mcp.tool()
def drive_delete_file(file_id: str, drive_id: Optional[str] = None) -> str:
    """Delete a file or folder from Drive."""
    service = get_service('drive', 'v3')
    params = {'supportsAllDrives': True} if drive_id else {}
    service.files().delete(fileId=file_id, **params).execute()
    return f"✅ Deleted file {file_id}"


@mcp.tool()
def drive_copy_file(file_id: str, new_name: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Copy a file in Drive."""
    service = get_service('drive', 'v3')

    body = {'name': new_name}
    if parent_id:
        body['parents'] = [parent_id]

    params = {'supportsAllDrives': True} if drive_id else {}
    copied = service.files().copy(fileId=file_id, body=body, **params).execute()
    return f"✅ File copied!\nNew ID: {copied['id']}\nName: {copied['name']}"


@mcp.tool()
def drive_share_file(file_id: str, email: str, role: str = "reader", drive_id: Optional[str] = None) -> str:
    """Share a file with a user. Roles: reader, writer, commenter."""
    service = get_service('drive', 'v3')

    permission = {
        'type': 'user',
        'role': role,
        'emailAddress': email
    }

    params = {'supportsAllDrives': True, 'sendNotificationEmail': True} if drive_id else {'sendNotificationEmail': True}
    service.permissions().create(fileId=file_id, body=permission, **params).execute()
    return f"✅ Shared file {file_id} with {email} as {role}"


# ============================================================================
# CALENDAR TOOLS
# ============================================================================

@mcp.tool()
def calendar_list_events(max_results: int = 10, time_min: Optional[str] = None) -> str:
    """List upcoming calendar events. time_min format: 2024-01-01T00:00:00Z"""
    service = get_service('calendar', 'v3')

    if not time_min:
        time_min = datetime.utcnow().isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',
        timeMin=time_min,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "No upcoming events found."

    output = f"Found {len(events)} upcoming event(s):\n\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        output += f"📅 {event['summary']}\n"
        output += f"   Start: {start}\n"
        output += f"   ID: {event['id']}\n\n"
    return output


@mcp.tool()
def calendar_create_event(summary: str, start_time: str, end_time: str,
                          description: Optional[str] = None, location: Optional[str] = None,
                          attendees: Optional[str] = None) -> str:
    """Create a calendar event. Times in RFC3339: 2024-01-01T10:00:00-07:00. Attendees: comma-separated emails."""
    service = get_service('calendar', 'v3')

    event = {
        'summary': summary,
        'start': {'dateTime': start_time, 'timeZone': 'UTC'},
        'end': {'dateTime': end_time, 'timeZone': 'UTC'},
    }

    if description:
        event['description'] = description
    if location:
        event['location'] = location
    if attendees:
        event['attendees'] = [{'email': email.strip()} for email in attendees.split(',')]

    created = service.events().insert(calendarId='primary', body=event).execute()
    return f"✅ Event created!\nID: {created['id']}\nLink: {created.get('htmlLink', 'N/A')}"


@mcp.tool()
def calendar_delete_event(event_id: str) -> str:
    """Delete a calendar event."""
    service = get_service('calendar', 'v3')
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return f"✅ Deleted event {event_id}"


# ============================================================================
# DOCS TOOLS
# ============================================================================

@mcp.tool()
def docs_create(title: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Create a new Google Doc."""
    drive_service = get_service('drive', 'v3')
    file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.document'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    params = {'supportsAllDrives': True} if drive_id else {}
    doc = drive_service.files().create(body=file_metadata, fields='id, name, webViewLink', **params).execute()
    return f"✅ Google Doc created!\nTitle: {doc['name']}\nID: {doc['id']}\nLink: {doc.get('webViewLink', 'N/A')}"


@mcp.tool()
def docs_read(document_id: str) -> str:
    """Read content from a Google Doc."""
    service = get_service('docs', 'v1')
    doc = service.documents().get(documentId=document_id).execute()
    title = doc.get('title', 'Untitled')
    content = []
    for element in doc.get('body', {}).get('content', []):
        if 'paragraph' in element:
            for elem in element['paragraph'].get('elements', []):
                if 'textRun' in elem:
                    content.append(elem['textRun'].get('content', ''))
    text = ''.join(content)
    return f"Title: {title}\n\n{'-'*60}\n\n{text}"


@mcp.tool()
def docs_append_text(document_id: str, text: str) -> str:
    """Append text to the end of a Google Doc."""
    service = get_service('docs', 'v1')
    requests = [{'insertText': {'location': {'index': 1}, 'text': text}}]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Text appended to document {document_id}"


# ============================================================================
# SHEETS TOOLS
# ============================================================================

@mcp.tool()
def sheets_create(title: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Create a new Google Sheet."""
    drive_service = get_service('drive', 'v3')
    file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.spreadsheet'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    params = {'supportsAllDrives': True} if drive_id else {}
    sheet = drive_service.files().create(body=file_metadata, fields='id, name, webViewLink', **params).execute()
    return f"✅ Google Sheet created!\nTitle: {sheet['name']}\nID: {sheet['id']}\nLink: {sheet.get('webViewLink', 'N/A')}"


@mcp.tool()
def sheets_read(spreadsheet_id: str, range_name: str = "A1:Z1000") -> str:
    """Read data from a Google Sheet."""
    service = get_service('sheets', 'v4')
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    values = result.get('values', [])
    if not values:
        return "No data found in sheet."
    output = f"Data from {range_name}:\n\n"
    for row in values:
        output += " | ".join(str(cell) for cell in row) + "\n"
    return output


@mcp.tool()
def sheets_write(spreadsheet_id: str, range_name: str, values: str) -> str:
    """Write data to a Google Sheet. values: JSON array like '[["Name", "Email"], ["John", "john@example.com"]]'"""
    service = get_service('sheets', 'v4')
    try:
        data = json.loads(values)
    except:
        return "❌ Error: values must be valid JSON array"

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()
    return f"✅ Updated {result.get('updatedCells', 0)} cells in range {range_name}"


@mcp.tool()
def sheets_append(spreadsheet_id: str, range_name: str, values: str) -> str:
    """Append rows to a Google Sheet. values: JSON array like '[["Name", "Email"], ["John", "john@example.com"]]'"""
    service = get_service('sheets', 'v4')
    try:
        data = json.loads(values)
    except:
        return "❌ Error: values must be valid JSON array"

    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body={'values': data}
    ).execute()
    return f"✅ Appended {result.get('updates', {}).get('updatedRows', 0)} row(s)"


# ============================================================================
# SLIDES TOOLS
# ============================================================================

@mcp.tool()
def slides_create(title: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Create a new Google Slides presentation."""
    drive_service = get_service('drive', 'v3')
    file_metadata = {'name': title, 'mimeType': 'application/vnd.google-apps.presentation'}
    if parent_id:
        file_metadata['parents'] = [parent_id]
    params = {'supportsAllDrives': True} if drive_id else {}
    slides = drive_service.files().create(body=file_metadata, fields='id, name, webViewLink', **params).execute()
    return f"✅ Google Slides created!\nTitle: {slides['name']}\nID: {slides['id']}\nLink: {slides.get('webViewLink', 'N/A')}"


# ============================================================================
# FORMS TOOLS
# ============================================================================

@mcp.tool()
def forms_create(title: str, description: Optional[str] = None) -> str:
    """Create a new Google Form."""
    service = get_service('forms', 'v1')

    form = {
        'info': {
            'title': title,
        }
    }

    if description:
        form['info']['documentTitle'] = description

    created_form = service.forms().create(body=form).execute()

    return f"✅ Google Form created!\nTitle: {created_form['info']['title']}\nForm ID: {created_form['formId']}\nEdit Link: https://docs.google.com/forms/d/{created_form['formId']}/edit"


@mcp.tool()
def forms_get(form_id: str) -> str:
    """Get details about a Google Form including all questions."""
    service = get_service('forms', 'v1')

    form = service.forms().get(formId=form_id).execute()

    output = f"Form: {form['info']['title']}\n"
    output += f"ID: {form['formId']}\n"
    output += f"Edit Link: https://docs.google.com/forms/d/{form['formId']}/edit\n"
    output += f"Response Link: https://docs.google.com/forms/d/{form['formId']}/viewform\n\n"

    if 'items' in form:
        output += f"Questions ({len(form['items'])}):\n\n"
        for idx, item in enumerate(form['items'], 1):
            if 'questionItem' in item:
                question = item['questionItem']['question']
                output += f"{idx}. {question.get('questionId', 'N/A')}\n"
                if 'textQuestion' in question:
                    output += f"   Type: Text\n"
                elif 'choiceQuestion' in question:
                    output += f"   Type: Multiple Choice\n"
                elif 'scaleQuestion' in question:
                    output += f"   Type: Scale\n"
                output += "\n"

    return output


@mcp.tool()
def forms_add_text_question(form_id: str, question_text: str, required: bool = False) -> str:
    """Add a text question to a form."""
    service = get_service('forms', 'v1')

    request = {
        'requests': [{
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'textQuestion': {
                                'paragraph': False
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added text question: {question_text}"


@mcp.tool()
def forms_add_multiple_choice(form_id: str, question_text: str, options: str, required: bool = False) -> str:
    """Add a multiple choice question. options: comma-separated like 'Option 1,Option 2,Option 3'"""
    service = get_service('forms', 'v1')

    option_list = [opt.strip() for opt in options.split(',')]

    request = {
        'requests': [{
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'choiceQuestion': {
                                'type': 'RADIO',
                                'options': [{'value': opt} for opt in option_list]
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added multiple choice question: {question_text}"


@mcp.tool()
def forms_list_responses(form_id: str) -> str:
    """List all responses to a form."""
    service = get_service('forms', 'v1')

    try:
        responses = service.forms().responses().list(formId=form_id).execute()
        response_list = responses.get('responses', [])

        if not response_list:
            return "No responses yet."

        output = f"Found {len(response_list)} response(s):\n\n"
        for idx, resp in enumerate(response_list, 1):
            output += f"Response #{idx}\n"
            output += f"Response ID: {resp['responseId']}\n"
            output += f"Timestamp: {resp.get('lastSubmittedTime', 'N/A')}\n"

            if 'answers' in resp:
                output += "Answers:\n"
                for question_id, answer in resp['answers'].items():
                    if 'textAnswers' in answer:
                        for text_ans in answer['textAnswers'].get('answers', []):
                            output += f"  - {text_ans.get('value', 'N/A')}\n"
            output += "\n"

        return output

    except Exception as e:
        return f"❌ Error listing responses: {str(e)}"


# ============================================================================
# TASKS TOOLS
# ============================================================================

@mcp.tool()
def tasks_list(task_list_id: str = "@default", max_results: int = 20) -> str:
    """List tasks from a task list."""
    service = get_service('tasks', 'v1')
    results = service.tasks().list(tasklist=task_list_id, maxResults=max_results).execute()
    tasks = results.get('items', [])
    if not tasks:
        return "No tasks found."
    output = f"Found {len(tasks)} task(s):\n\n"
    for task in tasks:
        status = "✅" if task.get('status') == 'completed' else "⬜"
        output += f"{status} {task['title']}\n"
        if task.get('notes'):
            output += f"   Notes: {task['notes']}\n"
        if task.get('due'):
            output += f"   Due: {task['due']}\n"
        output += f"   ID: {task['id']}\n\n"
    return output


@mcp.tool()
def tasks_create(title: str, notes: Optional[str] = None, task_list_id: str = "@default") -> str:
    """Create a new task."""
    service = get_service('tasks', 'v1')
    task = {'title': title}
    if notes:
        task['notes'] = notes
    result = service.tasks().insert(tasklist=task_list_id, body=task).execute()
    return f"✅ Task created!\nTitle: {result['title']}\nID: {result['id']}"


@mcp.tool()
def tasks_complete(task_id: str, task_list_id: str = "@default") -> str:
    """Mark a task as completed."""
    service = get_service('tasks', 'v1')
    task = service.tasks().get(tasklist=task_list_id, task=task_id).execute()
    task['status'] = 'completed'
    service.tasks().update(tasklist=task_list_id, task=task_id, body=task).execute()
    return f"✅ Task {task_id} marked as completed"


@mcp.tool()
def tasks_delete(task_id: str, task_list_id: str = "@default") -> str:
    """Delete a task."""
    service = get_service('tasks', 'v1')
    service.tasks().delete(tasklist=task_list_id, task=task_id).execute()
    return f"✅ Task {task_id} deleted"


if __name__ == "__main__":
    mcp.run()
