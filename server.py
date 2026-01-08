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


@mcp.tool()
def drive_download_file(file_id: str, destination_path: str, drive_id: Optional[str] = None) -> str:
    """Download a file from Google Drive to local filesystem."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    # Get file metadata to check if it's a Google Workspace file
    file_metadata = service.files().get(fileId=file_id, fields='name, mimeType', **params).execute()
    file_name = file_metadata['name']
    mime_type = file_metadata['mimeType']

    # Handle Google Workspace files (need to export)
    export_mimes = {
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    }

    dest_path = Path(destination_path)

    if mime_type in export_mimes:
        # Export Google Workspace file
        request = service.files().export_media(fileId=file_id, mimeType=export_mimes[mime_type])
    else:
        # Download regular file
        request = service.files().get_media(fileId=file_id, **params)

    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return f"✅ Downloaded file!\nName: {file_name}\nSaved to: {dest_path}"


@mcp.tool()
def drive_move_file(file_id: str, new_parent_id: str, drive_id: Optional[str] = None) -> str:
    """Move a file to a different folder."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    # Get current parents
    file = service.files().get(fileId=file_id, fields='parents', **params).execute()
    previous_parents = ",".join(file.get('parents', []))

    # Move file
    file = service.files().update(
        fileId=file_id,
        addParents=new_parent_id,
        removeParents=previous_parents,
        fields='id, name, parents',
        **params
    ).execute()

    return f"✅ Moved file!\nFile ID: {file['id']}\nNew parent: {new_parent_id}"


@mcp.tool()
def drive_get_file_metadata(file_id: str, drive_id: Optional[str] = None) -> str:
    """Get detailed metadata about a file."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    file = service.files().get(
        fileId=file_id,
        fields='id, name, mimeType, size, createdTime, modifiedTime, owners, sharingUser, webViewLink, webContentLink',
        **params
    ).execute()

    output = f"File: {file['name']}\n"
    output += f"ID: {file['id']}\n"
    output += f"Type: {file['mimeType']}\n"
    output += f"Size: {file.get('size', 'N/A')} bytes\n"
    output += f"Created: {file.get('createdTime', 'N/A')}\n"
    output += f"Modified: {file.get('modifiedTime', 'N/A')}\n"
    output += f"View Link: {file.get('webViewLink', 'N/A')}\n"

    if 'owners' in file:
        owners = ", ".join([owner.get('displayName', owner.get('emailAddress', 'Unknown')) for owner in file['owners']])
        output += f"Owners: {owners}\n"

    return output


@mcp.tool()
def drive_search_files(query: str, drive_id: Optional[str] = None, page_size: int = 20) -> str:
    """Advanced file search using Google Drive query syntax. Example: 'name contains \"report\" and mimeType contains \"pdf\"'"""
    service = get_service('drive', 'v3')

    params = {
        'q': query,
        'pageSize': page_size,
        'fields': 'files(id, name, mimeType, modifiedTime, size, webViewLink)',
        'orderBy': 'modifiedTime desc'
    }

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
        return f"No files found matching: {query}"

    output = f"Found {len(files)} file(s) matching '{query}':\n\n"
    for file in files:
        icon = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
        size = f"{file.get('size', 'N/A')} bytes" if 'size' in file else 'N/A'
        output += f"{icon} {file['name']}\n"
        output += f"   ID: {file['id']}\n"
        output += f"   Size: {size}\n"
        output += f"   Modified: {file.get('modifiedTime', 'N/A')}\n"
        output += f"   Link: {file.get('webViewLink', 'N/A')}\n\n"

    return output


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
def calendar_update_event(event_id: str, summary: Optional[str] = None, start_time: Optional[str] = None,
                          end_time: Optional[str] = None, description: Optional[str] = None,
                          location: Optional[str] = None, attendees: Optional[str] = None) -> str:
    """Update an existing calendar event. Provide only the fields you want to change."""
    service = get_service('calendar', 'v3')

    # Get existing event
    event = service.events().get(calendarId='primary', eventId=event_id).execute()

    # Update only provided fields
    if summary:
        event['summary'] = summary
    if start_time:
        event['start'] = {'dateTime': start_time, 'timeZone': 'UTC'}
    if end_time:
        event['end'] = {'dateTime': end_time, 'timeZone': 'UTC'}
    if description is not None:
        event['description'] = description
    if location is not None:
        event['location'] = location
    if attendees:
        event['attendees'] = [{'email': email.strip()} for email in attendees.split(',')]

    updated = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
    return f"✅ Event updated!\nID: {updated['id']}\nSummary: {updated['summary']}\nLink: {updated.get('htmlLink', 'N/A')}"


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


@mcp.tool()
def docs_insert_text(document_id: str, text: str, index: int) -> str:
    """Insert text at a specific position in a Google Doc. Index 1 is the start of the document."""
    service = get_service('docs', 'v1')
    requests = [{'insertText': {'location': {'index': index}, 'text': text}}]
    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Inserted text at position {index}"


@mcp.tool()
def docs_replace_text(document_id: str, find_text: str, replace_text: str, match_case: bool = False) -> str:
    """Find and replace text in a Google Doc."""
    service = get_service('docs', 'v1')

    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': find_text,
                'matchCase': match_case
            },
            'replaceText': replace_text
        }
    }]

    response = service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    occurrences = response.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)

    return f"✅ Replaced {occurrences} occurrence(s) of '{find_text}' with '{replace_text}'"


@mcp.tool()
def docs_format_text(document_id: str, start_index: int, end_index: int,
                     bold: Optional[bool] = None, italic: Optional[bool] = None,
                     underline: Optional[bool] = None, font_size: Optional[int] = None) -> str:
    """Apply formatting to text in a Google Doc. Specify start and end index of text to format."""
    service = get_service('docs', 'v1')

    text_style = {}
    if bold is not None:
        text_style['bold'] = bold
    if italic is not None:
        text_style['italic'] = italic
    if underline is not None:
        text_style['underline'] = underline
    if font_size is not None:
        text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}

    requests = [{
        'updateTextStyle': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            },
            'textStyle': text_style,
            'fields': ','.join(text_style.keys())
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    formatting = []
    if bold: formatting.append("bold")
    if italic: formatting.append("italic")
    if underline: formatting.append("underline")
    if font_size: formatting.append(f"font size {font_size}")

    return f"✅ Applied formatting ({', '.join(formatting)}) to text at indices {start_index}-{end_index}"


@mcp.tool()
def docs_insert_table(document_id: str, rows: int, columns: int, index: int) -> str:
    """Insert a table at a specific position in a Google Doc."""
    service = get_service('docs', 'v1')

    requests = [{
        'insertTable': {
            'rows': rows,
            'columns': columns,
            'location': {
                'index': index
            }
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Inserted {rows}x{columns} table at position {index}"


@mcp.tool()
def docs_insert_image(document_id: str, image_url: str, index: int, width: Optional[int] = None, height: Optional[int] = None) -> str:
    """Insert an image from a URL at a specific position. Width/height in points (72 points = 1 inch)."""
    service = get_service('docs', 'v1')

    image_properties = {'sourceUri': image_url}
    if width:
        image_properties['width'] = {'magnitude': width, 'unit': 'PT'}
    if height:
        image_properties['height'] = {'magnitude': height, 'unit': 'PT'}

    requests = [{
        'insertInlineImage': {
            'uri': image_url,
            'location': {
                'index': index
            },
            'objectSize': {
                'width': {'magnitude': width or 400, 'unit': 'PT'},
                'height': {'magnitude': height or 300, 'unit': 'PT'}
            }
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Image inserted at position {index}"


@mcp.tool()
def docs_add_hyperlink(document_id: str, start_index: int, end_index: int, url: str) -> str:
    """Add a hyperlink to text in a Google Doc."""
    service = get_service('docs', 'v1')

    requests = [{
        'updateTextStyle': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            },
            'textStyle': {
                'link': {
                    'url': url
                }
            },
            'fields': 'link'
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Hyperlink added to text at indices {start_index}-{end_index}\nURL: {url}"


@mcp.tool()
def docs_create_bulleted_list(document_id: str, start_index: int, end_index: int) -> str:
    """Convert text range into a bulleted list. Each paragraph becomes a list item."""
    service = get_service('docs', 'v1')

    requests = [{
        'createParagraphBullets': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            },
            'bulletPreset': 'BULLET_DISC_CIRCLE_SQUARE'
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Created bulleted list for text at indices {start_index}-{end_index}"


@mcp.tool()
def docs_create_numbered_list(document_id: str, start_index: int, end_index: int) -> str:
    """Convert text range into a numbered list. Each paragraph becomes a list item."""
    service = get_service('docs', 'v1')

    requests = [{
        'createParagraphBullets': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            },
            'bulletPreset': 'NUMBERED_DECIMAL_ALPHA_ROMAN'
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Created numbered list for text at indices {start_index}-{end_index}"


@mcp.tool()
def docs_set_heading_style(document_id: str, start_index: int, end_index: int,
                           heading_level: str = "HEADING_1") -> str:
    """Apply heading style to text. Levels: HEADING_1, HEADING_2, HEADING_3, HEADING_4, HEADING_5, HEADING_6, NORMAL_TEXT, TITLE, SUBTITLE."""
    service = get_service('docs', 'v1')

    requests = [{
        'updateParagraphStyle': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            },
            'paragraphStyle': {
                'namedStyleType': heading_level
            },
            'fields': 'namedStyleType'
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Applied {heading_level} style to text at indices {start_index}-{end_index}"


@mcp.tool()
def docs_add_page_break(document_id: str, index: int) -> str:
    """Insert a page break at a specific position."""
    service = get_service('docs', 'v1')

    requests = [{
        'insertPageBreak': {
            'location': {
                'index': index
            }
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Page break inserted at position {index}"


@mcp.tool()
def docs_delete_content(document_id: str, start_index: int, end_index: int) -> str:
    """Delete content from a specific range in a Google Doc."""
    service = get_service('docs', 'v1')

    requests = [{
        'deleteContentRange': {
            'range': {
                'startIndex': start_index,
                'endIndex': end_index
            }
        }
    }]

    service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
    return f"✅ Deleted content from indices {start_index}-{end_index}"


@mcp.tool()
def docs_update_table_cell(document_id: str, table_start_index: int, row: int, column: int, text: str) -> str:
    """Write text to a specific table cell. Row and column are 0-indexed."""
    service = get_service('docs', 'v1')

    # First, we need to find the cell's location
    # This is a simplified version - in practice you'd need to read the table structure
    # For now, we'll use a workaround by getting the document and finding the table

    doc = service.documents().get(documentId=document_id).execute()

    # Find the table at the given index
    table_location = None
    for element in doc.get('body', {}).get('content', []):
        if 'table' in element:
            if element['startIndex'] == table_start_index:
                table = element['table']
                if row < len(table['tableRows']) and column < len(table['tableRows'][row]['tableCells']):
                    cell = table['tableRows'][row]['tableCells'][column]
                    cell_content = cell['content']
                    if cell_content:
                        # Get the first content element's start index and insert there
                        cell_start = cell_content[0]['startIndex']
                        cell_end = cell_content[0]['endIndex']

                        # Delete existing content and insert new
                        requests = [
                            {
                                'deleteContentRange': {
                                    'range': {
                                        'startIndex': cell_start,
                                        'endIndex': cell_end - 1  # Don't delete the table cell end marker
                                    }
                                }
                            },
                            {
                                'insertText': {
                                    'location': {
                                        'index': cell_start
                                    },
                                    'text': text
                                }
                            }
                        ]

                        service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
                        return f"✅ Updated cell (row {row}, col {column}) with text: {text}"

    return f"❌ Could not find table at index {table_start_index} or cell at row {row}, column {column}"


@mcp.tool()
def docs_add_bookmark(document_id: str, index: int, bookmark_name: str) -> str:
    """Add a named bookmark at a specific position for internal linking."""
    service = get_service('docs', 'v1')

    requests = [{
        'createNamedRange': {
            'name': bookmark_name,
            'range': {
                'startIndex': index,
                'endIndex': index
            }
        }
    }]

    response = service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

    # Get the bookmark ID from response
    bookmark_id = response['replies'][0]['createNamedRange']['namedRangeId']

    return f"✅ Bookmark '{bookmark_name}' created at position {index}\nBookmark ID: {bookmark_id}"


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


@mcp.tool()
def sheets_clear(spreadsheet_id: str, range_name: str) -> str:
    """Clear all data in a specific range of a Google Sheet."""
    service = get_service('sheets', 'v4')
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    return f"✅ Cleared data in range {range_name}"


@mcp.tool()
def sheets_get_metadata(spreadsheet_id: str) -> str:
    """Get spreadsheet metadata including sheet names, IDs, and properties."""
    service = get_service('sheets', 'v4')
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

    output = f"Spreadsheet: {spreadsheet.get('properties', {}).get('title', 'Untitled')}\n"
    output += f"ID: {spreadsheet_id}\n"
    output += f"Sheets: {len(spreadsheet.get('sheets', []))}\n\n"

    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        output += f"📊 {props.get('title', 'Untitled')}\n"
        output += f"   Sheet ID: {props.get('sheetId')}\n"
        output += f"   Rows: {props.get('gridProperties', {}).get('rowCount', 'N/A')}\n"
        output += f"   Columns: {props.get('gridProperties', {}).get('columnCount', 'N/A')}\n\n"

    return output


@mcp.tool()
def sheets_create_sheet_tab(spreadsheet_id: str, sheet_name: str) -> str:
    """Add a new sheet tab to an existing spreadsheet."""
    service = get_service('sheets', 'v4')

    requests = [{
        'addSheet': {
            'properties': {
                'title': sheet_name
            }
        }
    }]

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    new_sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
    return f"✅ Created new sheet tab '{sheet_name}'\nSheet ID: {new_sheet_id}"


@mcp.tool()
def sheets_format_cells(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                        start_col: int, end_col: int, bold: Optional[bool] = None,
                        background_color: Optional[str] = None, text_color: Optional[str] = None) -> str:
    """Format cells in a Google Sheet. Colors in hex format like '#FF0000'. Rows and columns are 0-indexed."""
    service = get_service('sheets', 'v4')

    cell_format = {}

    if bold is not None:
        cell_format['textFormat'] = {'bold': bold}

    if background_color:
        # Convert hex to RGB
        r = int(background_color[1:3], 16) / 255
        g = int(background_color[3:5], 16) / 255
        b = int(background_color[5:7], 16) / 255
        cell_format['backgroundColor'] = {'red': r, 'green': g, 'blue': b}

    if text_color:
        r = int(text_color[1:3], 16) / 255
        g = int(text_color[3:5], 16) / 255
        b = int(text_color[5:7], 16) / 255
        if 'textFormat' not in cell_format:
            cell_format['textFormat'] = {}
        cell_format['textFormat']['foregroundColor'] = {'red': r, 'green': g, 'blue': b}

    requests = [{
        'repeatCell': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            },
            'cell': {
                'userEnteredFormat': cell_format
            },
            'fields': 'userEnteredFormat(' + ','.join(cell_format.keys()) + ')'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Formatted cells in range (rows {start_row}-{end_row}, cols {start_col}-{end_col})"


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


@mcp.tool()
def slides_get_details(presentation_id: str) -> str:
    """Get presentation details including slide count and structure."""
    service = get_service('slides', 'v1')
    presentation = service.presentations().get(presentationId=presentation_id).execute()

    output = f"Presentation: {presentation.get('title', 'Untitled')}\n"
    output += f"ID: {presentation_id}\n"
    output += f"Slides: {len(presentation.get('slides', []))}\n\n"

    for idx, slide in enumerate(presentation.get('slides', []), 1):
        output += f"Slide {idx}:\n"
        output += f"  ID: {slide['objectId']}\n"

        # Count text elements
        text_count = 0
        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                text_count += 1
        output += f"  Text elements: {text_count}\n\n"

    return output


@mcp.tool()
def slides_read(presentation_id: str) -> str:
    """Read all text content from a presentation."""
    service = get_service('slides', 'v1')
    presentation = service.presentations().get(presentationId=presentation_id).execute()

    output = f"Presentation: {presentation.get('title', 'Untitled')}\n"
    output += f"{'-'*60}\n\n"

    for idx, slide in enumerate(presentation.get('slides', []), 1):
        output += f"=== Slide {idx} ===\n"

        for element in slide.get('pageElements', []):
            if 'shape' in element and 'text' in element['shape']:
                text_elements = element['shape']['text'].get('textElements', [])
                for text_elem in text_elements:
                    if 'textRun' in text_elem:
                        output += text_elem['textRun'].get('content', '')

        output += "\n\n"

    return output


@mcp.tool()
def slides_add_slide(presentation_id: str, index: Optional[int] = None) -> str:
    """Add a new blank slide to presentation. Index starts at 0 (default: append to end)."""
    service = get_service('slides', 'v1')

    # Generate a unique ID for the new slide
    slide_id = f'slide_{datetime.now().timestamp()}'

    requests = [{
        'createSlide': {
            'objectId': slide_id,
            'insertionIndex': index if index is not None else None
        }
    }]

    response = service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    created_slide_id = response['replies'][0]['createSlide']['objectId']
    return f"✅ New slide added!\nSlide ID: {created_slide_id}\nPresentation: {presentation_id}"


@mcp.tool()
def slides_add_text(presentation_id: str, slide_id: str, text: str,
                    x: float = 100, y: float = 100, width: float = 400, height: float = 100) -> str:
    """Add a text box to a slide. Coordinates in points (1 inch = 72 points)."""
    service = get_service('slides', 'v1')

    # Generate unique ID for text box
    text_box_id = f'textbox_{datetime.now().timestamp()}'

    requests = [
        {
            'createShape': {
                'objectId': text_box_id,
                'shapeType': 'TEXT_BOX',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'width': {'magnitude': width, 'unit': 'PT'},
                        'height': {'magnitude': height, 'unit': 'PT'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
                        'unit': 'PT'
                    }
                }
            }
        },
        {
            'insertText': {
                'objectId': text_box_id,
                'text': text
            }
        }
    ]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Text added to slide!\nText: {text[:50]}...\nSlide: {slide_id}"


@mcp.tool()
def slides_delete_slide(presentation_id: str, slide_id: str) -> str:
    """Delete a slide from presentation."""
    service = get_service('slides', 'v1')

    requests = [{
        'deleteObject': {
            'objectId': slide_id
        }
    }]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Slide deleted!\nSlide ID: {slide_id}"


@mcp.tool()
def slides_insert_image(presentation_id: str, slide_id: str, image_url: str,
                        x: float = 100, y: float = 100, width: float = 400, height: float = 300) -> str:
    """Insert an image into a slide from a URL. Coordinates in points (1 inch = 72 points)."""
    service = get_service('slides', 'v1')

    image_id = f'image_{datetime.now().timestamp()}'

    requests = [{
        'createImage': {
            'objectId': image_id,
            'url': image_url,
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'width': {'magnitude': width, 'unit': 'PT'},
                    'height': {'magnitude': height, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    }]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Image inserted!\nImage ID: {image_id}\nSlide: {slide_id}"


@mcp.tool()
def slides_replace_text(presentation_id: str, find_text: str, replace_text: str, match_case: bool = False) -> str:
    """Find and replace text across all slides in presentation."""
    service = get_service('slides', 'v1')

    requests = [{
        'replaceAllText': {
            'containsText': {
                'text': find_text,
                'matchCase': match_case
            },
            'replaceText': replace_text
        }
    }]

    response = service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    occurrences = response.get('replies', [{}])[0].get('replaceAllText', {}).get('occurrencesChanged', 0)
    return f"✅ Replaced {occurrences} occurrence(s) of '{find_text}' with '{replace_text}'"


@mcp.tool()
def slides_format_text(presentation_id: str, slide_id: str, shape_id: str,
                       start_index: int, end_index: int, bold: Optional[bool] = None,
                       italic: Optional[bool] = None, font_size: Optional[int] = None,
                       foreground_color: Optional[str] = None) -> str:
    """Format text within a text box/shape on a slide. Color in hex format like '#FF0000'."""
    service = get_service('slides', 'v1')

    requests = []

    # Build text style
    text_style = {}
    fields = []

    if bold is not None:
        text_style['bold'] = bold
        fields.append('bold')

    if italic is not None:
        text_style['italic'] = italic
        fields.append('italic')

    if font_size is not None:
        text_style['fontSize'] = {'magnitude': font_size, 'unit': 'PT'}
        fields.append('fontSize')

    if foreground_color:
        r = int(foreground_color[1:3], 16) / 255
        g = int(foreground_color[3:5], 16) / 255
        b = int(foreground_color[5:7], 16) / 255
        text_style['foregroundColor'] = {
            'opaqueColor': {
                'rgbColor': {'red': r, 'green': g, 'blue': b}
            }
        }
        fields.append('foregroundColor')

    if text_style:
        requests.append({
            'updateTextStyle': {
                'objectId': shape_id,
                'textRange': {
                    'type': 'FIXED_RANGE',
                    'startIndex': start_index,
                    'endIndex': end_index
                },
                'style': text_style,
                'fields': ','.join(fields)
            }
        })

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Formatted text in shape {shape_id} (indices {start_index}-{end_index})"


@mcp.tool()
def slides_add_shape(presentation_id: str, slide_id: str, shape_type: str,
                     x: float = 100, y: float = 100, width: float = 200, height: float = 200) -> str:
    """Add a shape to a slide. Types: RECTANGLE, ELLIPSE, TRIANGLE, ARROW, etc."""
    service = get_service('slides', 'v1')

    shape_id = f'shape_{datetime.now().timestamp()}'

    requests = [{
        'createShape': {
            'objectId': shape_id,
            'shapeType': shape_type,
            'elementProperties': {
                'pageObjectId': slide_id,
                'size': {
                    'width': {'magnitude': width, 'unit': 'PT'},
                    'height': {'magnitude': height, 'unit': 'PT'}
                },
                'transform': {
                    'scaleX': 1,
                    'scaleY': 1,
                    'translateX': x,
                    'translateY': y,
                    'unit': 'PT'
                }
            }
        }
    }]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Shape added!\nShape ID: {shape_id}\nType: {shape_type}"


@mcp.tool()
def slides_duplicate_slide(presentation_id: str, slide_id: str, index: Optional[int] = None) -> str:
    """Duplicate a slide within the presentation."""
    service = get_service('slides', 'v1')

    requests = [{
        'duplicateObject': {
            'objectId': slide_id,
            'objectIds': {}
        }
    }]

    response = service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    new_slide_id = response['replies'][0]['duplicateObject']['objectId']
    return f"✅ Slide duplicated!\nOriginal: {slide_id}\nNew slide ID: {new_slide_id}"


@mcp.tool()
def slides_add_speaker_notes(presentation_id: str, slide_id: str, notes: str) -> str:
    """Add or update speaker notes for a slide."""
    service = get_service('slides', 'v1')

    # Get the presentation to find the notes page
    presentation = service.presentations().get(presentationId=presentation_id).execute()

    # Find the slide and its notes page
    notes_page_id = None
    for slide in presentation.get('slides', []):
        if slide['objectId'] == slide_id:
            notes_page_id = slide.get('slideProperties', {}).get('notesPage', {}).get('objectId')
            break

    if not notes_page_id:
        return f"❌ Could not find notes page for slide {slide_id}"

    # Get notes page to find the notes shape
    notes_page = service.presentations().pages().get(
        presentationId=presentation_id,
        pageObjectId=notes_page_id
    ).execute()

    # Find the notes shape (usually the second shape on the notes page)
    notes_shape_id = None
    for element in notes_page.get('pageElements', []):
        if 'shape' in element and element['shape'].get('shapeType') == 'TEXT_BOX':
            # Skip the first text box (slide thumbnail placeholder)
            if notes_shape_id is None:
                notes_shape_id = element['objectId']
                continue
            notes_shape_id = element['objectId']
            break

    if not notes_shape_id:
        return f"❌ Could not find notes shape on slide {slide_id}"

    # Insert text into notes
    requests = [
        {
            'deleteText': {
                'objectId': notes_shape_id,
                'textRange': {'type': 'ALL'}
            }
        },
        {
            'insertText': {
                'objectId': notes_shape_id,
                'text': notes,
                'insertionIndex': 0
            }
        }
    ]

    service.presentations().batchUpdate(
        presentationId=presentation_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Speaker notes added to slide {slide_id}"


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
