#!/usr/bin/env python3
import os
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

CLIENT_SECRET_PATH = Path.home() / "google-workspace-mcp" / "client_secret.json"
TOKEN_DIR = Path.home() / ".google_workspace_mcp" / "credentials"

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.labels',
    'https://www.googleapis.com/auth/gmail.settings.basic',
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
    'https://www.googleapis.com/auth/userinfo.email',
]

print("🔐 Google Workspace Authentication")
print("=" * 50)

# Create flow with run_local_server
flow = InstalledAppFlow.from_client_secrets_file(
    str(CLIENT_SECRET_PATH),
    scopes=SCOPES
)

# This will automatically open browser and handle callback
print("\nOpening browser for authentication...")
creds = flow.run_local_server(port=8080)

# Get user email
userinfo_service = build('oauth2', 'v2', credentials=creds)
user_info = userinfo_service.userinfo().get().execute()
user_email = user_info.get('email', 'default')

print(f"\n✅ Authenticated as: {user_email}")

# Save credentials
TOKEN_DIR.mkdir(parents=True, exist_ok=True)
token_path = TOKEN_DIR / f"{user_email}.json"

with open(token_path, 'w') as token:
    token.write(creds.to_json())

print(f"✅ Credentials saved to: {token_path}")
print("\n🎉 Authentication successful!")
