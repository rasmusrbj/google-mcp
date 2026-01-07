#!/usr/bin/env python3
"""
Comprehensive Google Workspace MCP Server
with Full Shared Drive Support
Supports: Gmail, Drive, Docs, Sheets, Slides, Forms, Tasks
"""
import os
import json
import base64
from pathlib import Path
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastmcp import FastMCP
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import io

# Initialize MCP server
mcp = FastMCP("google-workspace-full")

# Token storage path (reuse existing workspace-mcp tokens)
TOKEN_PATH = Path.home() / ".google_workspace_mcp" / "credentials" / "rasmus@happenings.dk.json"

# All scopes needed
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/forms',
    'https://www.googleapis.com/auth/tasks',
]


def get_credentials():
    """Get authenticated credentials."""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())
        else:
            raise Exception("No valid credentials found. Please authenticate first using the workspace-mcp server.")

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
    """
    Search for emails in Gmail.

    Args:
        query: Search query (e.g., "from:user@example.com", "is:unread")
        max_results: Maximum number of results (default: 10)

    Returns:
        List of matching emails with basic info
    """
    service = get_service('gmail', 'v1')

    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()

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

        output += f"📧 {subject}\n"
        output += f"   From: {from_addr}\n"
        output += f"   Date: {date}\n"
        output += f"   ID: {msg['id']}\n\n"

    return output


@mcp.tool()
def gmail_read(message_id: str) -> str:
    """
    Read a specific Gmail message.

    Args:
        message_id: The message ID

    Returns:
        Full message content
    """
    service = get_service('gmail', 'v1')

    message = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    headers = message['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
    to_addr = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

    # Get body
    body = ""
    if 'parts' in message['payload']:
        for part in message['payload']['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in message['payload'] and 'data' in message['payload']['body']:
        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

    output = f"Subject: {subject}\n"
    output += f"From: {from_addr}\n"
    output += f"To: {to_addr}\n"
    output += f"Date: {date}\n"
    output += f"\n{'-'*60}\n\n"
    output += body

    return output


@mcp.tool()
def gmail_send(to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
    """
    Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        cc: CC recipients (optional)

    Returns:
        Confirmation message
    """
    service = get_service('gmail', 'v1')

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw}

    sent_message = service.users().messages().send(userId='me', body=message_body).execute()

    return f"✅ Email sent successfully!\nMessage ID: {sent_message['id']}\nTo: {to}\nSubject: {subject}"


# ============================================================================
# DRIVE TOOLS (with Shared Drive support)
# ============================================================================

@mcp.tool()
def drive_list_shared_drives(page_size: int = 100) -> str:
    """
    List all shared drives (Team Drives) the user has access to.

    Args:
        page_size: Maximum number of shared drives to return (default: 100)

    Returns:
        List of shared drives with their IDs and names
    """
    service = get_service('drive', 'v3')

    results = service.drives().list(
        pageSize=page_size,
        fields="drives(id, name)"
    ).execute()

    drives = results.get('drives', [])

    if not drives:
        return "No shared drives found."

    output = f"Found {len(drives)} shared drive(s):\n\n"
    for drive in drives:
        output += f"📁 {drive['name']}\n"
        output += f"   ID: {drive['id']}\n\n"

    return output


@mcp.tool()
def drive_list_files(
    folder_id: Optional[str] = None,
    drive_id: Optional[str] = None,
    query: Optional[str] = None,
    page_size: int = 20
) -> str:
    """
    List files and folders in Google Drive or Shared Drives.

    Args:
        folder_id: ID of the folder to list (optional, defaults to root)
        drive_id: ID of the shared drive to search in (optional)
        query: Additional search query (optional)
        page_size: Maximum number of files to return (default: 20)

    Returns:
        List of files with their metadata
    """
    service = get_service('drive', 'v3')

    q_parts = []
    if folder_id:
        q_parts.append(f"'{folder_id}' in parents")
    if query:
        q_parts.append(query)

    final_query = " and ".join(q_parts) if q_parts else None

    params = {
        'pageSize': page_size,
        'fields': 'files(id, name, mimeType, modifiedTime, size, webViewLink)',
        'orderBy': 'modifiedTime desc'
    }

    if final_query:
        params['q'] = final_query

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
        file_type = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
        output += f"{file_type} {file['name']}\n"
        output += f"   ID: {file['id']}\n"
        output += f"   Type: {file['mimeType']}\n"
        output += f"   Link: {file.get('webViewLink', 'N/A')}\n\n"

    return output


@mcp.tool()
def drive_create_folder(
    name: str,
    parent_id: Optional[str] = None,
    drive_id: Optional[str] = None
) -> str:
    """
    Create a new folder in Google Drive or a Shared Drive.

    Args:
        name: Name of the folder to create
        parent_id: ID of the parent folder (optional, defaults to root)
        drive_id: ID of the shared drive to create folder in (optional)

    Returns:
        Information about the created folder
    """
    service = get_service('drive', 'v3')

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {}
    if drive_id:
        params['supportsAllDrives'] = True

    folder = service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink',
        **params
    ).execute()

    return f"✅ Folder created!\n\nName: {folder['name']}\nID: {folder['id']}\nLink: {folder.get('webViewLink', 'N/A')}"


# ============================================================================
# DOCS TOOLS
# ============================================================================

@mcp.tool()
def docs_create(
    title: str,
    parent_id: Optional[str] = None,
    drive_id: Optional[str] = None
) -> str:
    """
    Create a new Google Doc.

    Args:
        title: Title of the document
        parent_id: ID of the parent folder (optional)
        drive_id: ID of the shared drive (optional)

    Returns:
        Information about the created document
    """
    drive_service = get_service('drive', 'v3')

    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.document'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {}
    if drive_id:
        params['supportsAllDrives'] = True

    doc = drive_service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink',
        **params
    ).execute()

    return f"✅ Google Doc created!\n\nTitle: {doc['name']}\nID: {doc['id']}\nLink: {doc.get('webViewLink', 'N/A')}"


@mcp.tool()
def docs_read(document_id: str) -> str:
    """
    Read content from a Google Doc.

    Args:
        document_id: The document ID

    Returns:
        Document content as text
    """
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
    """
    Append text to the end of a Google Doc.

    Args:
        document_id: The document ID
        text: Text to append

    Returns:
        Confirmation message
    """
    service = get_service('docs', 'v1')

    requests = [
        {
            'insertText': {
                'location': {'index': 1},
                'text': text
            }
        }
    ]

    service.documents().batchUpdate(
        documentId=document_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Text appended to document {document_id}"


# ============================================================================
# SHEETS TOOLS
# ============================================================================

@mcp.tool()
def sheets_create(
    title: str,
    parent_id: Optional[str] = None,
    drive_id: Optional[str] = None
) -> str:
    """
    Create a new Google Sheet.

    Args:
        title: Title of the spreadsheet
        parent_id: ID of the parent folder (optional)
        drive_id: ID of the shared drive (optional)

    Returns:
        Information about the created spreadsheet
    """
    drive_service = get_service('drive', 'v3')

    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.spreadsheet'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {}
    if drive_id:
        params['supportsAllDrives'] = True

    sheet = drive_service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink',
        **params
    ).execute()

    return f"✅ Google Sheet created!\n\nTitle: {sheet['name']}\nID: {sheet['id']}\nLink: {sheet.get('webViewLink', 'N/A')}"


@mcp.tool()
def sheets_read(spreadsheet_id: str, range_name: str = "A1:Z1000") -> str:
    """
    Read data from a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: Range to read (e.g., "Sheet1!A1:D10")

    Returns:
        Sheet data as formatted text
    """
    service = get_service('sheets', 'v4')

    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()

    values = result.get('values', [])

    if not values:
        return "No data found in sheet."

    output = f"Data from {range_name}:\n\n"
    for row in values:
        output += " | ".join(str(cell) for cell in row) + "\n"

    return output


@mcp.tool()
def sheets_write(spreadsheet_id: str, range_name: str, values: str) -> str:
    """
    Write data to a Google Sheet.

    Args:
        spreadsheet_id: The spreadsheet ID
        range_name: Range to write to (e.g., "Sheet1!A1")
        values: JSON array of values (e.g., '[["Name", "Email"], ["John", "john@example.com"]]')

    Returns:
        Confirmation message
    """
    service = get_service('sheets', 'v4')

    # Parse the values JSON
    import json
    try:
        data = json.loads(values)
    except:
        return "❌ Error: values must be valid JSON array"

    body = {
        'values': data
    }

    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()

    return f"✅ Updated {result.get('updatedCells', 0)} cells in range {range_name}"


# ============================================================================
# SLIDES TOOLS
# ============================================================================

@mcp.tool()
def slides_create(
    title: str,
    parent_id: Optional[str] = None,
    drive_id: Optional[str] = None
) -> str:
    """
    Create a new Google Slides presentation.

    Args:
        title: Title of the presentation
        parent_id: ID of the parent folder (optional)
        drive_id: ID of the shared drive (optional)

    Returns:
        Information about the created presentation
    """
    drive_service = get_service('drive', 'v3')

    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.presentation'
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {}
    if drive_id:
        params['supportsAllDrives'] = True

    slides = drive_service.files().create(
        body=file_metadata,
        fields='id, name, webViewLink',
        **params
    ).execute()

    return f"✅ Google Slides created!\n\nTitle: {slides['name']}\nID: {slides['id']}\nLink: {slides.get('webViewLink', 'N/A')}"


# ============================================================================
# TASKS TOOLS
# ============================================================================

@mcp.tool()
def tasks_list(task_list_id: str = "@default", max_results: int = 20) -> str:
    """
    List tasks from a task list.

    Args:
        task_list_id: The task list ID (default: "@default" for default list)
        max_results: Maximum number of tasks to return

    Returns:
        List of tasks
    """
    service = get_service('tasks', 'v1')

    results = service.tasks().list(
        tasklist=task_list_id,
        maxResults=max_results
    ).execute()

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
    """
    Create a new task.

    Args:
        title: Task title
        notes: Task notes/description (optional)
        task_list_id: The task list ID (default: "@default")

    Returns:
        Confirmation message
    """
    service = get_service('tasks', 'v1')

    task = {
        'title': title
    }
    if notes:
        task['notes'] = notes

    result = service.tasks().insert(
        tasklist=task_list_id,
        body=task
    ).execute()

    return f"✅ Task created!\n\nTitle: {result['title']}\nID: {result['id']}"


if __name__ == "__main__":
    mcp.run()
