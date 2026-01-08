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
    'https://www.googleapis.com/auth/chat.spaces',
    'https://www.googleapis.com/auth/chat.messages',
    'https://www.googleapis.com/auth/chat.memberships',
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


@mcp.tool()
def gmail_untrash(message_id: str) -> str:
    """Restore an email from trash."""
    service = get_service('gmail', 'v1')
    service.users().messages().untrash(userId='me', id=message_id).execute()
    return f"✅ Restored message {message_id} from trash"


@mcp.tool()
def gmail_permanently_delete(message_id: str) -> str:
    """Permanently delete an email. WARNING: This cannot be undone!"""
    service = get_service('gmail', 'v1')
    service.users().messages().delete(userId='me', id=message_id).execute()
    return f"✅ Permanently deleted message {message_id}"


@mcp.tool()
def gmail_move_to_inbox(message_id: str) -> str:
    """Move an email to inbox (unarchive)."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['INBOX']}).execute()
    return f"✅ Moved message {message_id} to inbox"


@mcp.tool()
def gmail_star(message_id: str) -> str:
    """Star an email."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['STARRED']}).execute()
    return f"✅ Starred message {message_id}"


@mcp.tool()
def gmail_unstar(message_id: str) -> str:
    """Unstar an email."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['STARRED']}).execute()
    return f"✅ Unstarred message {message_id}"


@mcp.tool()
def gmail_mark_important(message_id: str) -> str:
    """Mark an email as important."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': ['IMPORTANT']}).execute()
    return f"✅ Marked message {message_id} as important"


@mcp.tool()
def gmail_mark_not_important(message_id: str) -> str:
    """Mark an email as not important."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': ['IMPORTANT']}).execute()
    return f"✅ Marked message {message_id} as not important"


@mcp.tool()
def gmail_add_label(message_id: str, label_id: str) -> str:
    """Add a label to an email. Use gmail_list_labels to get label IDs."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'addLabelIds': [label_id]}).execute()
    return f"✅ Added label {label_id} to message {message_id}"


@mcp.tool()
def gmail_remove_label(message_id: str, label_id: str) -> str:
    """Remove a label from an email."""
    service = get_service('gmail', 'v1')
    service.users().messages().modify(userId='me', id=message_id, body={'removeLabelIds': [label_id]}).execute()
    return f"✅ Removed label {label_id} from message {message_id}"


@mcp.tool()
def gmail_list_labels() -> str:
    """List all Gmail labels (both system and custom)."""
    service = get_service('gmail', 'v1')
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        return "No labels found."

    system_labels = []
    custom_labels = []

    for label in labels:
        label_type = label.get('type', 'user')
        if label_type == 'system':
            system_labels.append(label)
        else:
            custom_labels.append(label)

    output = ""

    if system_labels:
        output += "📌 System Labels:\n\n"
        for label in system_labels:
            output += f"  {label['name']}\n"
            output += f"    ID: {label['id']}\n\n"

    if custom_labels:
        output += "🏷️  Custom Labels:\n\n"
        for label in custom_labels:
            output += f"  {label['name']}\n"
            output += f"    ID: {label['id']}\n\n"

    return output


@mcp.tool()
def gmail_create_label(name: str) -> str:
    """Create a new custom label."""
    service = get_service('gmail', 'v1')

    label_object = {
        'name': name,
        'messageListVisibility': 'show',
        'labelListVisibility': 'labelShow'
    }

    created_label = service.users().labels().create(userId='me', body=label_object).execute()
    return f"✅ Label created!\nName: {created_label['name']}\nID: {created_label['id']}"


@mcp.tool()
def gmail_delete_label(label_id: str) -> str:
    """Delete a custom label."""
    service = get_service('gmail', 'v1')
    service.users().labels().delete(userId='me', id=label_id).execute()
    return f"✅ Deleted label {label_id}"


@mcp.tool()
def gmail_send_with_attachment(to: str, subject: str, body: str, attachment_path: str, cc: Optional[str] = None) -> str:
    """Send an email with a file attachment."""
    service = get_service('gmail', 'v1')

    # Check if attachment exists
    att_path = Path(attachment_path)
    if not att_path.exists():
        return f"❌ Attachment not found: {attachment_path}"

    # Create message with attachment
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc

    # Add body
    message.attach(MIMEText(body, 'plain'))

    # Add attachment
    with open(attachment_path, 'rb') as f:
        attachment = MIMEText(f.read(), _subtype='octet-stream', _charset='utf-8')
        attachment.add_header('Content-Disposition', 'attachment', filename=att_path.name)
        message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent_message = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"✅ Email sent with attachment!\nMessage ID: {sent_message['id']}\nTo: {to}\nAttachment: {att_path.name}"


@mcp.tool()
def gmail_get_attachment(message_id: str, attachment_id: str, destination_path: str) -> str:
    """Download an email attachment. Use gmail_read to see attachment IDs."""
    service = get_service('gmail', 'v1')

    attachment = service.users().messages().attachments().get(
        userId='me',
        messageId=message_id,
        id=attachment_id
    ).execute()

    file_data = base64.urlsafe_b64decode(attachment['data'])

    dest_path = Path(destination_path)
    with open(dest_path, 'wb') as f:
        f.write(file_data)

    return f"✅ Attachment downloaded!\nSaved to: {dest_path}\nSize: {attachment.get('size', 'unknown')} bytes"


@mcp.tool()
def gmail_forward(message_id: str, to: str, comment: Optional[str] = None) -> str:
    """Forward an email to another recipient."""
    service = get_service('gmail', 'v1')

    # Get original message
    original = service.users().messages().get(userId='me', id=message_id, format='full').execute()
    headers = original['payload']['headers']

    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
    if not subject.startswith('Fwd:'):
        subject = f"Fwd: {subject}"

    # Build forwarded message
    forward_body = ""
    if comment:
        forward_body = f"{comment}\n\n---------- Forwarded message ---------\n"

    # Extract original body
    if 'parts' in original['payload']:
        for part in original['payload']['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                forward_body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                break
    elif 'body' in original['payload'] and 'data' in original['payload']['body']:
        forward_body += base64.urlsafe_b64decode(original['payload']['body']['data']).decode('utf-8')

    message = MIMEText(forward_body)
    message['to'] = to
    message['subject'] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    sent = service.users().messages().send(userId='me', body={'raw': raw}).execute()
    return f"✅ Message forwarded!\nMessage ID: {sent['id']}\nTo: {to}"


@mcp.tool()
def gmail_list_threads(query: Optional[str] = None, max_results: int = 10) -> str:
    """List email threads (conversations). Optional query to filter."""
    service = get_service('gmail', 'v1')

    params = {'userId': 'me', 'maxResults': max_results}
    if query:
        params['q'] = query

    results = service.users().threads().list(**params).execute()
    threads = results.get('threads', [])

    if not threads:
        return "No threads found."

    output = f"Found {len(threads)} thread(s):\n\n"
    for thread in threads:
        # Get thread details
        thread_data = service.users().threads().get(userId='me', id=thread['id'], format='metadata').execute()
        messages = thread_data.get('messages', [])

        if messages:
            first_msg = messages[0]
            headers = first_msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')

            output += f"💬 {subject}\n"
            output += f"   Thread ID: {thread['id']}\n"
            output += f"   Messages: {len(messages)}\n\n"

    return output


@mcp.tool()
def gmail_get_thread(thread_id: str) -> str:
    """Read an entire email thread (conversation) with all messages."""
    service = get_service('gmail', 'v1')

    thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
    messages = thread.get('messages', [])

    if not messages:
        return f"No messages in thread {thread_id}"

    output = f"Thread ID: {thread_id}\nMessages: {len(messages)}\n\n"
    output += "="*60 + "\n\n"

    for idx, msg in enumerate(messages, 1):
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_addr = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

        output += f"Message {idx}/{len(messages)}:\n"
        output += f"Subject: {subject}\n"
        output += f"From: {from_addr}\n"
        output += f"Date: {date}\n\n"

        # Extract body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

        output += f"{body}\n\n"
        output += "-"*60 + "\n\n"

    return output


@mcp.tool()
def gmail_batch_modify(message_ids: str, add_labels: Optional[str] = None, remove_labels: Optional[str] = None) -> str:
    """Modify multiple messages at once. message_ids: comma-separated IDs. Labels: comma-separated label IDs."""
    service = get_service('gmail', 'v1')

    ids = [mid.strip() for mid in message_ids.split(',')]

    body = {'ids': ids}

    if add_labels:
        body['addLabelIds'] = [lid.strip() for lid in add_labels.split(',')]

    if remove_labels:
        body['removeLabelIds'] = [lid.strip() for lid in remove_labels.split(',')]

    service.users().messages().batchModify(userId='me', body=body).execute()

    return f"✅ Modified {len(ids)} message(s)"


@mcp.tool()
def gmail_batch_delete(message_ids: str) -> str:
    """Permanently delete multiple messages at once. message_ids: comma-separated IDs. WARNING: Cannot be undone!"""
    service = get_service('gmail', 'v1')

    ids = [mid.strip() for mid in message_ids.split(',')]

    body = {'ids': ids}

    service.users().messages().batchDelete(userId='me', body=body).execute()

    return f"✅ Permanently deleted {len(ids)} message(s)"


@mcp.tool()
def gmail_list_drafts(max_results: int = 10) -> str:
    """List all draft emails."""
    service = get_service('gmail', 'v1')

    results = service.users().drafts().list(userId='me', maxResults=max_results).execute()
    drafts = results.get('drafts', [])

    if not drafts:
        return "No drafts found."

    output = f"Found {len(drafts)} draft(s):\n\n"
    for draft in drafts:
        draft_data = service.users().drafts().get(userId='me', id=draft['id'], format='metadata').execute()
        message = draft_data.get('message', {})
        headers = message.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        to = next((h['value'] for h in headers if h['name'] == 'To'), 'No recipient')

        output += f"📝 {subject}\n"
        output += f"   To: {to}\n"
        output += f"   Draft ID: {draft['id']}\n\n"

    return output


@mcp.tool()
def gmail_create_draft(to: str, subject: str, body: str, cc: Optional[str] = None) -> str:
    """Create a draft email."""
    service = get_service('gmail', 'v1')

    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    if cc:
        message['cc'] = cc

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId='me',
        body={'message': {'raw': raw}}
    ).execute()

    return f"✅ Draft created!\nDraft ID: {draft['id']}\nTo: {to}\nSubject: {subject}"


@mcp.tool()
def gmail_send_draft(draft_id: str) -> str:
    """Send a draft email."""
    service = get_service('gmail', 'v1')

    sent = service.users().drafts().send(userId='me', body={'id': draft_id}).execute()

    return f"✅ Draft sent!\nMessage ID: {sent['id']}"


@mcp.tool()
def gmail_delete_draft(draft_id: str) -> str:
    """Delete a draft email."""
    service = get_service('gmail', 'v1')

    service.users().drafts().delete(userId='me', id=draft_id).execute()

    return f"✅ Draft {draft_id} deleted"


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


@mcp.tool()
def drive_rename_file(file_id: str, new_name: str, drive_id: Optional[str] = None) -> str:
    """Rename a file or folder."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    file = service.files().update(
        fileId=file_id,
        body={'name': new_name},
        fields='id, name',
        **params
    ).execute()

    return f"✅ Renamed file!\nNew name: {file['name']}\nID: {file['id']}"


@mcp.tool()
def drive_list_permissions(file_id: str, drive_id: Optional[str] = None) -> str:
    """List all permissions (who has access) for a file."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    permissions = service.permissions().list(
        fileId=file_id,
        fields='permissions(id, type, role, emailAddress, domain, displayName)',
        **params
    ).execute()

    perms = permissions.get('permissions', [])

    if not perms:
        return "No permissions found (file is private)."

    output = f"Permissions for file {file_id}:\n\n"
    for perm in perms:
        perm_type = perm.get('type', 'unknown')
        role = perm.get('role', 'unknown')

        if perm_type == 'user':
            output += f"👤 {perm.get('displayName', perm.get('emailAddress', 'Unknown'))}\n"
            output += f"   Email: {perm.get('emailAddress', 'N/A')}\n"
        elif perm_type == 'group':
            output += f"👥 {perm.get('displayName', perm.get('emailAddress', 'Unknown'))}\n"
            output += f"   Email: {perm.get('emailAddress', 'N/A')}\n"
        elif perm_type == 'domain':
            output += f"🏢 Domain: {perm.get('domain', 'Unknown')}\n"
        elif perm_type == 'anyone':
            output += f"🌐 Anyone with the link\n"

        output += f"   Role: {role}\n"
        output += f"   Permission ID: {perm['id']}\n\n"

    return output


@mcp.tool()
def drive_remove_permission(file_id: str, permission_id: str, drive_id: Optional[str] = None) -> str:
    """Remove a permission (unshare) from a file. Use drive_list_permissions to get permission IDs."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    service.permissions().delete(
        fileId=file_id,
        permissionId=permission_id,
        **params
    ).execute()

    return f"✅ Removed permission {permission_id} from file {file_id}"


@mcp.tool()
def drive_make_public(file_id: str, role: str = "reader", drive_id: Optional[str] = None) -> str:
    """Make a file publicly accessible to anyone with the link. Roles: reader, writer, commenter."""
    service = get_service('drive', 'v3')

    permission = {
        'type': 'anyone',
        'role': role
    }

    params = {'supportsAllDrives': True} if drive_id else {}

    service.permissions().create(
        fileId=file_id,
        body=permission,
        **params
    ).execute()

    return f"✅ File {file_id} is now public (anyone with link can {role})"


@mcp.tool()
def drive_update_description(file_id: str, description: str, drive_id: Optional[str] = None) -> str:
    """Update a file's description."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    file = service.files().update(
        fileId=file_id,
        body={'description': description},
        fields='id, name, description',
        **params
    ).execute()

    return f"✅ Updated description for {file['name']}\nDescription: {file.get('description', 'None')}"


@mcp.tool()
def drive_star_file(file_id: str, starred: bool = True, drive_id: Optional[str] = None) -> str:
    """Star or unstar a file (add to favorites)."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    service.files().update(
        fileId=file_id,
        body={'starred': starred},
        **params
    ).execute()

    status = "starred" if starred else "unstarred"
    return f"✅ File {file_id} {status}"


@mcp.tool()
def drive_list_trashed_files(page_size: int = 20) -> str:
    """List files in the trash."""
    service = get_service('drive', 'v3')

    results = service.files().list(
        q="trashed=true",
        pageSize=page_size,
        fields='files(id, name, mimeType, trashedTime, webViewLink)',
        orderBy='trashedTime desc'
    ).execute()

    files = results.get('files', [])

    if not files:
        return "Trash is empty."

    output = f"Found {len(files)} file(s) in trash:\n\n"
    for file in files:
        icon = "📁" if file['mimeType'] == 'application/vnd.google-apps.folder' else "📄"
        output += f"{icon} {file['name']}\n"
        output += f"   ID: {file['id']}\n"
        output += f"   Trashed: {file.get('trashedTime', 'N/A')}\n"
        output += f"   Link: {file.get('webViewLink', 'N/A')}\n\n"

    return output


@mcp.tool()
def drive_restore_file(file_id: str, drive_id: Optional[str] = None) -> str:
    """Restore a file from trash."""
    service = get_service('drive', 'v3')

    params = {'supportsAllDrives': True} if drive_id else {}

    file = service.files().update(
        fileId=file_id,
        body={'trashed': False},
        fields='id, name',
        **params
    ).execute()

    return f"✅ Restored file from trash!\nName: {file['name']}\nID: {file['id']}"


@mcp.tool()
def drive_empty_trash() -> str:
    """Permanently delete all files in trash. WARNING: This cannot be undone!"""
    service = get_service('drive', 'v3')

    service.files().emptyTrash().execute()

    return f"✅ Trash emptied! All trashed files permanently deleted."


@mcp.tool()
def drive_export_file(file_id: str, destination_path: str, export_format: str = "pdf") -> str:
    """Export a Google Workspace file to a specific format.
    Formats: pdf, docx, xlsx, pptx, txt, csv, html, zip, epub, rtf, odt, ods, odp.
    Auto-detects file type (Docs, Sheets, Slides) and uses appropriate export format."""
    service = get_service('drive', 'v3')

    # Get file metadata to determine type
    file_metadata = service.files().get(fileId=file_id, fields='name, mimeType').execute()
    mime_type = file_metadata['mimeType']
    file_name = file_metadata['name']

    # Map export formats to MIME types for each Google Workspace file type
    export_mappings = {
        'application/vnd.google-apps.document': {
            'pdf': 'application/pdf',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'html': 'text/html',
            'zip': 'application/zip',
            'epub': 'application/epub+zip',
            'rtf': 'application/rtf',
            'odt': 'application/vnd.oasis.opendocument.text'
        },
        'application/vnd.google-apps.spreadsheet': {
            'pdf': 'application/pdf',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'csv': 'text/csv',
            'zip': 'application/zip',
            'ods': 'application/vnd.oasis.opendocument.spreadsheet'
        },
        'application/vnd.google-apps.presentation': {
            'pdf': 'application/pdf',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'txt': 'text/plain',
            'odp': 'application/vnd.oasis.opendocument.presentation'
        }
    }

    if mime_type not in export_mappings:
        return f"❌ Cannot export {mime_type}. Only Google Docs, Sheets, and Slides can be exported."

    if export_format not in export_mappings[mime_type]:
        available = ', '.join(export_mappings[mime_type].keys())
        return f"❌ Format '{export_format}' not available for this file type. Available: {available}"

    export_mime = export_mappings[mime_type][export_format]

    # Export the file
    request = service.files().export_media(fileId=file_id, mimeType=export_mime)

    dest_path = Path(destination_path)
    fh = io.FileIO(dest_path, 'wb')
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    return f"✅ Exported file to {export_format}!\nName: {file_name}\nSaved to: {dest_path}"


@mcp.tool()
def drive_create_shortcut(name: str, target_file_id: str, parent_id: Optional[str] = None, drive_id: Optional[str] = None) -> str:
    """Create a shortcut to a file or folder."""
    service = get_service('drive', 'v3')

    file_metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.shortcut',
        'shortcutDetails': {
            'targetId': target_file_id
        }
    }

    if parent_id:
        file_metadata['parents'] = [parent_id]

    params = {'supportsAllDrives': True} if drive_id else {}

    shortcut = service.files().create(
        body=file_metadata,
        fields='id, name, shortcutDetails',
        **params
    ).execute()

    return f"✅ Shortcut created!\nName: {shortcut['name']}\nShortcut ID: {shortcut['id']}\nTarget ID: {shortcut['shortcutDetails']['targetId']}"


@mcp.tool()
def drive_list_revisions(file_id: str) -> str:
    """List all revisions (version history) of a file."""
    service = get_service('drive', 'v3')

    try:
        revisions = service.revisions().list(
            fileId=file_id,
            fields='revisions(id, modifiedTime, lastModifyingUser, size)'
        ).execute()

        revs = revisions.get('revisions', [])

        if not revs:
            return f"No revisions found for file {file_id}"

        output = f"Found {len(revs)} revision(s) for file {file_id}:\n\n"
        for idx, rev in enumerate(revs, 1):
            output += f"Version {idx}:\n"
            output += f"  Revision ID: {rev['id']}\n"
            output += f"  Modified: {rev.get('modifiedTime', 'N/A')}\n"

            if 'lastModifyingUser' in rev:
                user = rev['lastModifyingUser']
                output += f"  Modified by: {user.get('displayName', user.get('emailAddress', 'Unknown'))}\n"

            if 'size' in rev:
                output += f"  Size: {rev['size']} bytes\n"

            output += "\n"

        return output

    except Exception as e:
        return f"❌ Error listing revisions: {str(e)}\nNote: Revisions are only available for Google Docs, Sheets, and Slides."


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


@mcp.tool()
def sheets_delete_sheet_tab(spreadsheet_id: str, sheet_id: int) -> str:
    """Delete a sheet tab from a spreadsheet."""
    service = get_service('sheets', 'v4')

    requests = [{
        'deleteSheet': {
            'sheetId': sheet_id
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Deleted sheet with ID {sheet_id}"


@mcp.tool()
def sheets_rename_sheet_tab(spreadsheet_id: str, sheet_id: int, new_name: str) -> str:
    """Rename a sheet tab."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'title': new_name
            },
            'fields': 'title'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Renamed sheet to '{new_name}'"


@mcp.tool()
def sheets_duplicate_sheet_tab(spreadsheet_id: str, sheet_id: int, new_sheet_name: Optional[str] = None) -> str:
    """Duplicate a sheet tab within the same spreadsheet."""
    service = get_service('sheets', 'v4')

    requests = [{
        'duplicateSheet': {
            'sourceSheetId': sheet_id,
            'insertSheetIndex': None,
            'newSheetName': new_sheet_name
        }
    }]

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    new_id = response['replies'][0]['duplicateSheet']['properties']['sheetId']
    new_title = response['replies'][0]['duplicateSheet']['properties']['title']
    return f"✅ Duplicated sheet!\nNew sheet: {new_title}\nNew sheet ID: {new_id}"


@mcp.tool()
def sheets_move_sheet_tab(spreadsheet_id: str, sheet_id: int, new_index: int) -> str:
    """Move a sheet tab to a new position. Index starts at 0."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'index': new_index
            },
            'fields': 'index'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Moved sheet to position {new_index}"


@mcp.tool()
def sheets_hide_sheet_tab(spreadsheet_id: str, sheet_id: int, hidden: bool = True) -> str:
    """Hide or show a sheet tab."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'hidden': hidden
            },
            'fields': 'hidden'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    status = "hidden" if hidden else "visible"
    return f"✅ Sheet is now {status}"


@mcp.tool()
def sheets_copy_to_spreadsheet(source_spreadsheet_id: str, sheet_id: int,
                                destination_spreadsheet_id: str) -> str:
    """Copy a sheet to another spreadsheet."""
    service = get_service('sheets', 'v4')

    request_body = {
        'destinationSpreadsheetId': destination_spreadsheet_id
    }

    response = service.spreadsheets().sheets().copyTo(
        spreadsheetId=source_spreadsheet_id,
        sheetId=sheet_id,
        body=request_body
    ).execute()

    return f"✅ Sheet copied!\nNew sheet ID in destination: {response.get('sheetId')}\nTitle: {response.get('title')}"


@mcp.tool()
def sheets_insert_rows(spreadsheet_id: str, sheet_id: int, start_index: int, num_rows: int) -> str:
    """Insert blank rows. start_index is 0-based (0 = before first row)."""
    service = get_service('sheets', 'v4')

    requests = [{
        'insertDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_index,
                'endIndex': start_index + num_rows
            },
            'inheritFromBefore': False
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Inserted {num_rows} row(s) at index {start_index}"


@mcp.tool()
def sheets_insert_columns(spreadsheet_id: str, sheet_id: int, start_index: int, num_columns: int) -> str:
    """Insert blank columns. start_index is 0-based (0 = before column A)."""
    service = get_service('sheets', 'v4')

    requests = [{
        'insertDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,
                'endIndex': start_index + num_columns
            },
            'inheritFromBefore': False
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Inserted {num_columns} column(s) at index {start_index}"


@mcp.tool()
def sheets_delete_rows(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int) -> str:
    """Delete rows. Indices are 0-based (0 = first row). Deletes rows from start_index to end_index-1."""
    service = get_service('sheets', 'v4')

    requests = [{
        'deleteDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_index,
                'endIndex': end_index
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_deleted = end_index - start_index
    return f"✅ Deleted {num_deleted} row(s) (indices {start_index}-{end_index-1})"


@mcp.tool()
def sheets_delete_columns(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int) -> str:
    """Delete columns. Indices are 0-based (0 = column A). Deletes columns from start_index to end_index-1."""
    service = get_service('sheets', 'v4')

    requests = [{
        'deleteDimension': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,
                'endIndex': end_index
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_deleted = end_index - start_index
    return f"✅ Deleted {num_deleted} column(s) (indices {start_index}-{end_index-1})"


@mcp.tool()
def sheets_resize_rows(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int,
                       pixel_size: int) -> str:
    """Set row height in pixels. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_index,
                'endIndex': end_index
            },
            'properties': {
                'pixelSize': pixel_size
            },
            'fields': 'pixelSize'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_rows = end_index - start_index
    return f"✅ Resized {num_rows} row(s) to {pixel_size}px"


@mcp.tool()
def sheets_resize_columns(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int,
                          pixel_size: int) -> str:
    """Set column width in pixels. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,
                'endIndex': end_index
            },
            'properties': {
                'pixelSize': pixel_size
            },
            'fields': 'pixelSize'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_cols = end_index - start_index
    return f"✅ Resized {num_cols} column(s) to {pixel_size}px"


@mcp.tool()
def sheets_auto_resize_columns(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int) -> str:
    """Auto-resize columns to fit content. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'autoResizeDimensions': {
            'dimensions': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,
                'endIndex': end_index
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_cols = end_index - start_index
    return f"✅ Auto-resized {num_cols} column(s)"


@mcp.tool()
def sheets_hide_rows(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int,
                     hidden: bool = True) -> str:
    """Hide or show rows. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'ROWS',
                'startIndex': start_index,
                'endIndex': end_index
            },
            'properties': {
                'hiddenByUser': hidden
            },
            'fields': 'hiddenByUser'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_rows = end_index - start_index
    status = "hidden" if hidden else "visible"
    return f"✅ {num_rows} row(s) are now {status}"


@mcp.tool()
def sheets_hide_columns(spreadsheet_id: str, sheet_id: int, start_index: int, end_index: int,
                        hidden: bool = True) -> str:
    """Hide or show columns. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateDimensionProperties': {
            'range': {
                'sheetId': sheet_id,
                'dimension': 'COLUMNS',
                'startIndex': start_index,
                'endIndex': end_index
            },
            'properties': {
                'hiddenByUser': hidden
            },
            'fields': 'hiddenByUser'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    num_cols = end_index - start_index
    status = "hidden" if hidden else "visible"
    return f"✅ {num_cols} column(s) are now {status}"


@mcp.tool()
def sheets_merge_cells(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                       start_col: int, end_col: int, merge_type: str = "MERGE_ALL") -> str:
    """Merge cells. merge_type: MERGE_ALL, MERGE_COLUMNS, or MERGE_ROWS. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'mergeCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            },
            'mergeType': merge_type
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Merged cells (rows {start_row}-{end_row-1}, cols {start_col}-{end_col-1})"


@mcp.tool()
def sheets_unmerge_cells(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                         start_col: int, end_col: int) -> str:
    """Unmerge cells in a range. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'unmergeCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Unmerged cells in range"


@mcp.tool()
def sheets_add_borders(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                       start_col: int, end_col: int, border_style: str = "SOLID",
                       border_color: str = "#000000") -> str:
    """Add borders to cells. border_style: SOLID, DOTTED, DASHED. Color in hex. Indices 0-based."""
    service = get_service('sheets', 'v4')

    # Convert hex to RGB
    r = int(border_color[1:3], 16) / 255
    g = int(border_color[3:5], 16) / 255
    b = int(border_color[5:7], 16) / 255

    border = {
        'style': border_style,
        'color': {'red': r, 'green': g, 'blue': b}
    }

    requests = [{
        'updateBorders': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            },
            'top': border,
            'bottom': border,
            'left': border,
            'right': border,
            'innerHorizontal': border,
            'innerVertical': border
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Added borders to range"


@mcp.tool()
def sheets_set_number_format(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                              start_col: int, end_col: int, format_type: str) -> str:
    """Set number format. Types: NUMBER, CURRENCY, PERCENT, DATE, TIME, DATE_TIME, SCIENTIFIC, TEXT. Indices 0-based."""
    service = get_service('sheets', 'v4')

    # Format patterns
    patterns = {
        'NUMBER': '0.00',
        'CURRENCY': '$#,##0.00',
        'PERCENT': '0.00%',
        'DATE': 'yyyy-mm-dd',
        'TIME': 'h:mm:ss am/pm',
        'DATE_TIME': 'yyyy-mm-dd h:mm:ss',
        'SCIENTIFIC': '0.00E+00',
        'TEXT': '@'
    }

    pattern = patterns.get(format_type, '0.00')

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
                'userEnteredFormat': {
                    'numberFormat': {
                        'type': format_type if format_type != 'CURRENCY' else 'NUMBER',
                        'pattern': pattern
                    }
                }
            },
            'fields': 'userEnteredFormat.numberFormat'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Applied {format_type} format to range"


@mcp.tool()
def sheets_add_data_validation(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                                start_col: int, end_col: int, values: str, strict: bool = True) -> str:
    """Add dropdown data validation. values: JSON array like '["Option1", "Option2"]'. Indices 0-based."""
    service = get_service('sheets', 'v4')

    try:
        value_list = json.loads(values)
    except:
        return "❌ Error: values must be valid JSON array"

    condition_values = [{'userEnteredValue': v} for v in value_list]

    requests = [{
        'setDataValidation': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            },
            'rule': {
                'condition': {
                    'type': 'ONE_OF_LIST',
                    'values': condition_values
                },
                'showCustomUi': True,
                'strict': strict
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Added dropdown validation with {len(value_list)} options"


@mcp.tool()
def sheets_copy_paste(spreadsheet_id: str, source_sheet_id: int, source_start_row: int,
                      source_end_row: int, source_start_col: int, source_end_col: int,
                      dest_sheet_id: int, dest_start_row: int, dest_start_col: int,
                      paste_type: str = "NORMAL") -> str:
    """Copy and paste cells. paste_type: NORMAL, VALUES, FORMAT, FORMULA. All indices 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'copyPaste': {
            'source': {
                'sheetId': source_sheet_id,
                'startRowIndex': source_start_row,
                'endRowIndex': source_end_row,
                'startColumnIndex': source_start_col,
                'endColumnIndex': source_end_col
            },
            'destination': {
                'sheetId': dest_sheet_id,
                'startRowIndex': dest_start_row,
                'endRowIndex': dest_start_row + (source_end_row - source_start_row),
                'startColumnIndex': dest_start_col,
                'endColumnIndex': dest_start_col + (source_end_col - source_start_col)
            },
            'pasteType': f'PASTE_{paste_type}'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Copied and pasted range ({paste_type})"


@mcp.tool()
def sheets_find_replace(spreadsheet_id: str, sheet_id: int, find: str, replacement: str,
                        match_case: bool = False, match_entire_cell: bool = False) -> str:
    """Find and replace text in a sheet."""
    service = get_service('sheets', 'v4')

    requests = [{
        'findReplace': {
            'find': find,
            'replacement': replacement,
            'matchCase': match_case,
            'matchEntireCell': match_entire_cell,
            'sheetId': sheet_id
        }
    }]

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    occurrences = response['replies'][0]['findReplace'].get('occurrencesChanged', 0)
    return f"✅ Replaced {occurrences} occurrence(s) of '{find}' with '{replacement}'"


@mcp.tool()
def sheets_sort_range(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                      start_col: int, end_col: int, sort_col_index: int, ascending: bool = True) -> str:
    """Sort a range by a column. sort_col_index is 0-based within the range."""
    service = get_service('sheets', 'v4')

    requests = [{
        'sortRange': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': start_row,
                'endRowIndex': end_row,
                'startColumnIndex': start_col,
                'endColumnIndex': end_col
            },
            'sortSpecs': [{
                'dimensionIndex': start_col + sort_col_index,
                'sortOrder': 'ASCENDING' if ascending else 'DESCENDING'
            }]
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    direction = "ascending" if ascending else "descending"
    return f"✅ Sorted range by column {start_col + sort_col_index} ({direction})"


@mcp.tool()
def sheets_freeze_rows_columns(spreadsheet_id: str, sheet_id: int, frozen_row_count: int = 0,
                                frozen_column_count: int = 0) -> str:
    """Freeze rows and/or columns. Set counts to 0 to unfreeze."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateSheetProperties': {
            'properties': {
                'sheetId': sheet_id,
                'gridProperties': {
                    'frozenRowCount': frozen_row_count,
                    'frozenColumnCount': frozen_column_count
                }
            },
            'fields': 'gridProperties.frozenRowCount,gridProperties.frozenColumnCount'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Froze {frozen_row_count} row(s) and {frozen_column_count} column(s)"


@mcp.tool()
def sheets_create_named_range(spreadsheet_id: str, range_name: str, sheet_id: int,
                               start_row: int, end_row: int, start_col: int, end_col: int) -> str:
    """Create a named range. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'addNamedRange': {
            'namedRange': {
                'name': range_name,
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                }
            }
        }
    }]

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Created named range '{range_name}'"


@mcp.tool()
def sheets_add_conditional_format(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                                   start_col: int, end_col: int, condition_type: str,
                                   condition_value: str, background_color: str = "#00FF00") -> str:
    """Add conditional formatting. condition_type: NUMBER_GREATER, NUMBER_LESS, TEXT_CONTAINS, etc. Indices 0-based."""
    service = get_service('sheets', 'v4')

    # Convert hex to RGB
    r = int(background_color[1:3], 16) / 255
    g = int(background_color[3:5], 16) / 255
    b = int(background_color[5:7], 16) / 255

    condition_values = [{'userEnteredValue': condition_value}]

    requests = [{
        'addConditionalFormatRule': {
            'rule': {
                'ranges': [{
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                }],
                'booleanRule': {
                    'condition': {
                        'type': condition_type,
                        'values': condition_values
                    },
                    'format': {
                        'backgroundColor': {'red': r, 'green': g, 'blue': b}
                    }
                }
            },
            'index': 0
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Added conditional formatting rule ({condition_type})"


@mcp.tool()
def sheets_add_note(spreadsheet_id: str, sheet_id: int, row: int, col: int, note: str) -> str:
    """Add a note to a cell. Row and column are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'updateCells': {
            'range': {
                'sheetId': sheet_id,
                'startRowIndex': row,
                'endRowIndex': row + 1,
                'startColumnIndex': col,
                'endColumnIndex': col + 1
            },
            'rows': [{
                'values': [{
                    'note': note
                }]
            }],
            'fields': 'note'
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Added note to cell (row {row}, col {col})"


@mcp.tool()
def sheets_protect_range(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                         start_col: int, end_col: int, description: str = "Protected Range",
                         warning_only: bool = False) -> str:
    """Protect a range from editing. warning_only=True shows warning instead of blocking. Indices 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'addProtectedRange': {
            'protectedRange': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                },
                'description': description,
                'warningOnly': warning_only
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    protection_type = "warning" if warning_only else "protected"
    return f"✅ Range is now {protection_type}: {description}"


@mcp.tool()
def sheets_create_chart(spreadsheet_id: str, sheet_id: int, chart_type: str,
                        data_start_row: int, data_end_row: int, data_start_col: int, data_end_col: int,
                        position_row: int = 0, position_col: int = 0) -> str:
    """Create a chart. chart_type: COLUMN, BAR, LINE, PIE, AREA, SCATTER. All indices 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'addChart': {
            'chart': {
                'spec': {
                    'title': 'Chart',
                    'basicChart': {
                        'chartType': chart_type,
                        'legendPosition': 'RIGHT_LEGEND',
                        'domains': [{
                            'domain': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': data_start_row,
                                        'endRowIndex': data_end_row,
                                        'startColumnIndex': data_start_col,
                                        'endColumnIndex': data_start_col + 1
                                    }]
                                }
                            }
                        }],
                        'series': [{
                            'series': {
                                'sourceRange': {
                                    'sources': [{
                                        'sheetId': sheet_id,
                                        'startRowIndex': data_start_row,
                                        'endRowIndex': data_end_row,
                                        'startColumnIndex': data_start_col + 1,
                                        'endColumnIndex': data_end_col
                                    }]
                                }
                            }
                        }]
                    }
                },
                'position': {
                    'overlayPosition': {
                        'anchorCell': {
                            'sheetId': sheet_id,
                            'rowIndex': position_row,
                            'columnIndex': position_col
                        }
                    }
                }
            }
        }
    }]

    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Created {chart_type} chart"


@mcp.tool()
def sheets_create_filter(spreadsheet_id: str, sheet_id: int, start_row: int, end_row: int,
                         start_col: int, end_col: int) -> str:
    """Create a filter view on a range. Indices are 0-based."""
    service = get_service('sheets', 'v4')

    requests = [{
        'setBasicFilter': {
            'filter': {
                'range': {
                    'sheetId': sheet_id,
                    'startRowIndex': start_row,
                    'endRowIndex': end_row,
                    'startColumnIndex': start_col,
                    'endColumnIndex': end_col
                }
            }
        }
    }]

    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body={'requests': requests}
    ).execute()

    return f"✅ Created filter on range"


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
def forms_add_paragraph_text(form_id: str, question_text: str, required: bool = False) -> str:
    """Add a paragraph text question (long-form text) to a form."""
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
                                'paragraph': True
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added paragraph text question: {question_text}"


@mcp.tool()
def forms_add_checkbox(form_id: str, question_text: str, options: str, required: bool = False) -> str:
    """Add a checkbox question (multiple selections allowed). options: comma-separated like 'Option 1,Option 2,Option 3'"""
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
                                'type': 'CHECKBOX',
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
    return f"✅ Added checkbox question: {question_text}"


@mcp.tool()
def forms_add_dropdown(form_id: str, question_text: str, options: str, required: bool = False) -> str:
    """Add a dropdown question. options: comma-separated like 'Option 1,Option 2,Option 3'"""
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
                                'type': 'DROP_DOWN',
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
    return f"✅ Added dropdown question: {question_text}"


@mcp.tool()
def forms_add_scale(form_id: str, question_text: str, low: int = 1, high: int = 5,
                    low_label: Optional[str] = None, high_label: Optional[str] = None, required: bool = False) -> str:
    """Add a linear scale question (e.g., 1-5 rating). Optionally provide labels for low and high values."""
    service = get_service('forms', 'v1')

    scale_question = {
        'low': low,
        'high': high
    }

    if low_label:
        scale_question['lowLabel'] = low_label
    if high_label:
        scale_question['highLabel'] = high_label

    request = {
        'requests': [{
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'scaleQuestion': scale_question
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added scale question: {question_text} ({low}-{high})"


@mcp.tool()
def forms_add_date(form_id: str, question_text: str, include_year: bool = True, required: bool = False) -> str:
    """Add a date question to a form."""
    service = get_service('forms', 'v1')

    request = {
        'requests': [{
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'dateQuestion': {
                                'includeYear': include_year
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added date question: {question_text}"


@mcp.tool()
def forms_add_time(form_id: str, question_text: str, duration: bool = False, required: bool = False) -> str:
    """Add a time question. If duration=True, asks for duration instead of time of day."""
    service = get_service('forms', 'v1')

    request = {
        'requests': [{
            'createItem': {
                'item': {
                    'title': question_text,
                    'questionItem': {
                        'question': {
                            'required': required,
                            'timeQuestion': {
                                'duration': duration
                            }
                        }
                    }
                },
                'location': {'index': 0}
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Added time question: {question_text}"


@mcp.tool()
def forms_update_settings(form_id: str, title: Optional[str] = None, description: Optional[str] = None,
                          collect_email: Optional[bool] = None, allow_response_edits: Optional[bool] = None,
                          quiz_mode: Optional[bool] = None) -> str:
    """Update form settings like title, description, and response options."""
    service = get_service('forms', 'v1')

    requests = []

    if title is not None:
        requests.append({
            'updateFormInfo': {
                'info': {
                    'title': title
                },
                'updateMask': 'title'
            }
        })

    if description is not None:
        requests.append({
            'updateFormInfo': {
                'info': {
                    'description': description
                },
                'updateMask': 'description'
            }
        })

    if collect_email is not None:
        requests.append({
            'updateSettings': {
                'settings': {
                    'quizSettings': {
                        'isQuiz': quiz_mode if quiz_mode is not None else False
                    }
                },
                'updateMask': 'quizSettings.isQuiz'
            }
        })

    if not requests:
        return "No settings to update."

    request_body = {'requests': requests}
    service.forms().batchUpdate(formId=form_id, body=request_body).execute()

    return f"✅ Form settings updated!"


@mcp.tool()
def forms_delete_question(form_id: str, question_index: int) -> str:
    """Delete a question from a form by its index (0-based)."""
    service = get_service('forms', 'v1')

    # Get form to find item at index
    form = service.forms().get(formId=form_id).execute()

    if 'items' not in form or question_index >= len(form['items']):
        return f"❌ Question at index {question_index} not found."

    item_id = form['items'][question_index].get('itemId')

    if not item_id:
        return f"❌ Could not get item ID for question at index {question_index}"

    request = {
        'requests': [{
            'deleteItem': {
                'location': {
                    'index': question_index
                }
            }
        }]
    }

    service.forms().batchUpdate(formId=form_id, body=request).execute()
    return f"✅ Deleted question at index {question_index}"


@mcp.tool()
def forms_get_response(form_id: str, response_id: str) -> str:
    """Get a specific form response with detailed answers."""
    service = get_service('forms', 'v1')

    try:
        response = service.forms().responses().get(formId=form_id, responseId=response_id).execute()

        output = f"Response ID: {response['responseId']}\n"
        output += f"Timestamp: {response.get('lastSubmittedTime', 'N/A')}\n\n"

        if 'answers' in response:
            output += "Answers:\n\n"
            for question_id, answer in response['answers'].items():
                output += f"Question ID: {question_id}\n"

                if 'textAnswers' in answer:
                    for text_ans in answer['textAnswers'].get('answers', []):
                        output += f"  Answer: {text_ans.get('value', 'N/A')}\n"

                if 'fileUploadAnswers' in answer:
                    output += f"  File upload response\n"

                output += "\n"

        return output

    except Exception as e:
        return f"❌ Error getting response: {str(e)}"


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
# GOOGLE CHAT TOOLS
# ============================================================================

@mcp.tool()
def chat_list_spaces(page_size: int = 100) -> str:
    """List all Google Chat spaces (rooms and DMs) the user has access to."""
    service = get_service('chat', 'v1')

    results = service.spaces().list(pageSize=page_size).execute()
    spaces = results.get('spaces', [])

    if not spaces:
        return "No Chat spaces found."

    output = f"Found {len(spaces)} space(s):\n\n"
    for space in spaces:
        space_type = space.get('type', 'UNKNOWN')
        display_name = space.get('displayName', 'Unnamed')

        icon = "💬" if space_type == 'DM' else "👥"
        output += f"{icon} {display_name}\n"
        output += f"   Type: {space_type}\n"
        output += f"   Space ID: {space['name']}\n\n"

    return output


@mcp.tool()
def chat_get_space(space_id: str) -> str:
    """Get details about a specific Google Chat space."""
    service = get_service('chat', 'v1')

    space = service.spaces().get(name=space_id).execute()

    output = f"Space: {space.get('displayName', 'Unnamed')}\n"
    output += f"ID: {space['name']}\n"
    output += f"Type: {space.get('type', 'UNKNOWN')}\n"
    output += f"Space threaded: {space.get('spaceThreadingState', 'UNKNOWN')}\n"

    if 'spaceDetails' in space:
        details = space['spaceDetails']
        if 'description' in details:
            output += f"Description: {details['description']}\n"
        if 'guidelines' in details:
            output += f"Guidelines: {details['guidelines']}\n"

    return output


@mcp.tool()
def chat_create_space(display_name: str, space_type: str = "SPACE") -> str:
    """Create a new Google Chat space. Types: SPACE (room) or DM (direct message)."""
    service = get_service('chat', 'v1')

    space_body = {
        'displayName': display_name,
        'spaceType': space_type
    }

    created_space = service.spaces().create(body=space_body).execute()

    return f"✅ Chat space created!\nName: {created_space.get('displayName', 'Unnamed')}\nSpace ID: {created_space['name']}"


@mcp.tool()
def chat_update_space(space_id: str, display_name: Optional[str] = None, description: Optional[str] = None) -> str:
    """Update a Google Chat space's name or description."""
    service = get_service('chat', 'v1')

    update_mask = []
    space_body = {}

    if display_name:
        space_body['displayName'] = display_name
        update_mask.append('displayName')

    if description:
        space_body['spaceDetails'] = {'description': description}
        update_mask.append('spaceDetails.description')

    if not update_mask:
        return "No fields to update."

    updated_space = service.spaces().patch(
        name=space_id,
        updateMask=','.join(update_mask),
        body=space_body
    ).execute()

    return f"✅ Space updated!\nName: {updated_space.get('displayName', 'Unnamed')}\nSpace ID: {updated_space['name']}"


@mcp.tool()
def chat_delete_space(space_id: str) -> str:
    """Delete a Google Chat space."""
    service = get_service('chat', 'v1')

    service.spaces().delete(name=space_id).execute()

    return f"✅ Space {space_id} deleted"


@mcp.tool()
def chat_send_message(space_id: str, text: str, thread_key: Optional[str] = None) -> str:
    """Send a message to a Google Chat space. Optional thread_key to reply in thread."""
    service = get_service('chat', 'v1')

    message_body = {'text': text}

    if thread_key:
        message_body['thread'] = {'threadKey': thread_key}

    message = service.spaces().messages().create(
        parent=space_id,
        body=message_body
    ).execute()

    return f"✅ Message sent!\nMessage ID: {message['name']}\nSpace: {space_id}"


@mcp.tool()
def chat_list_messages(space_id: str, page_size: int = 25) -> str:
    """List messages in a Google Chat space."""
    service = get_service('chat', 'v1')

    results = service.spaces().messages().list(
        parent=space_id,
        pageSize=page_size,
        orderBy='createTime desc'
    ).execute()

    messages = results.get('messages', [])

    if not messages:
        return f"No messages found in space {space_id}"

    output = f"Found {len(messages)} message(s):\n\n"
    for msg in messages:
        sender_name = msg.get('sender', {}).get('displayName', 'Unknown')
        text = msg.get('text', '(no text)')
        create_time = msg.get('createTime', 'Unknown')

        output += f"💬 {sender_name}: {text[:100]}\n"
        output += f"   Time: {create_time}\n"
        output += f"   Message ID: {msg['name']}\n\n"

    return output


@mcp.tool()
def chat_get_message(message_id: str) -> str:
    """Get details about a specific Google Chat message."""
    service = get_service('chat', 'v1')

    message = service.spaces().messages().get(name=message_id).execute()

    output = f"Message ID: {message['name']}\n"
    output += f"Sender: {message.get('sender', {}).get('displayName', 'Unknown')}\n"
    output += f"Time: {message.get('createTime', 'Unknown')}\n"
    output += f"Text: {message.get('text', '(no text)')}\n"

    if 'thread' in message:
        output += f"Thread: {message['thread'].get('name', 'N/A')}\n"

    return output


@mcp.tool()
def chat_update_message(message_id: str, text: str) -> str:
    """Update (edit) a Google Chat message."""
    service = get_service('chat', 'v1')

    updated_message = service.spaces().messages().patch(
        name=message_id,
        updateMask='text',
        body={'text': text}
    ).execute()

    return f"✅ Message updated!\nMessage ID: {updated_message['name']}"


@mcp.tool()
def chat_delete_message(message_id: str) -> str:
    """Delete a Google Chat message."""
    service = get_service('chat', 'v1')

    service.spaces().messages().delete(name=message_id).execute()

    return f"✅ Message {message_id} deleted"


@mcp.tool()
def chat_list_members(space_id: str, page_size: int = 100) -> str:
    """List all members in a Google Chat space."""
    service = get_service('chat', 'v1')

    results = service.spaces().members().list(
        parent=space_id,
        pageSize=page_size
    ).execute()

    members = results.get('memberships', [])

    if not members:
        return f"No members found in space {space_id}"

    output = f"Found {len(members)} member(s):\n\n"
    for member in members:
        member_data = member.get('member', {})
        name = member_data.get('displayName', 'Unknown')
        email = member_data.get('name', 'N/A')
        role = member.get('role', 'MEMBER')

        output += f"👤 {name}\n"
        output += f"   Email/ID: {email}\n"
        output += f"   Role: {role}\n"
        output += f"   Membership ID: {member['name']}\n\n"

    return output


@mcp.tool()
def chat_add_member(space_id: str, user_email: str) -> str:
    """Add a member to a Google Chat space."""
    service = get_service('chat', 'v1')

    membership_body = {
        'member': {
            'name': f'users/{user_email}',
            'type': 'HUMAN'
        }
    }

    membership = service.spaces().members().create(
        parent=space_id,
        body=membership_body
    ).execute()

    return f"✅ Added {user_email} to space!\nMembership ID: {membership['name']}"


@mcp.tool()
def chat_remove_member(membership_id: str) -> str:
    """Remove a member from a Google Chat space. Use chat_list_members to get membership IDs."""
    service = get_service('chat', 'v1')

    service.spaces().members().delete(name=membership_id).execute()

    return f"✅ Removed member {membership_id} from space"


@mcp.tool()
def chat_create_reaction(message_id: str, emoji: str) -> str:
    """Add a reaction (emoji) to a message. Emoji examples: '👍', '❤️', '😊'"""
    service = get_service('chat', 'v1')

    reaction_body = {
        'emoji': {
            'unicode': emoji
        }
    }

    reaction = service.spaces().messages().reactions().create(
        parent=message_id,
        body=reaction_body
    ).execute()

    return f"✅ Reaction added!\nEmoji: {emoji}\nReaction ID: {reaction['name']}"


@mcp.tool()
def chat_list_reactions(message_id: str) -> str:
    """List all reactions on a message."""
    service = get_service('chat', 'v1')

    results = service.spaces().messages().reactions().list(parent=message_id).execute()
    reactions = results.get('reactions', [])

    if not reactions:
        return f"No reactions on message {message_id}"

    output = f"Found {len(reactions)} reaction(s):\n\n"
    for reaction in reactions:
        emoji = reaction.get('emoji', {}).get('unicode', '?')
        user = reaction.get('user', {}).get('displayName', 'Unknown')

        output += f"{emoji} by {user}\n"
        output += f"   Reaction ID: {reaction['name']}\n\n"

    return output


@mcp.tool()
def chat_delete_reaction(reaction_id: str) -> str:
    """Delete a reaction from a message. Use chat_list_reactions to get reaction IDs."""
    service = get_service('chat', 'v1')

    service.spaces().messages().reactions().delete(name=reaction_id).execute()

    return f"✅ Reaction {reaction_id} deleted"


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
