#!/usr/bin/env python3
"""
Authentication script for Google Workspace MCP Server
"""
import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Paths
CLIENT_SECRET_PATH = Path.home() / "google-workspace-mcp" / "client_secret.json"
TOKEN_DIR = Path.home() / ".google_workspace_mcp" / "credentials"
TOKEN_PATH = TOKEN_DIR / "rasmus@happenings.dk.json"

# Scopes needed for all services
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/forms.body',
    'https://www.googleapis.com/auth/tasks',
]


def authenticate():
    """Run the OAuth flow to get credentials."""
    print("🔐 Google Workspace MCP Authentication")
    print("=" * 60)

    # Check if client secret exists
    if not CLIENT_SECRET_PATH.exists():
        print(f"\n❌ ERROR: Client secret not found at {CLIENT_SECRET_PATH}")
        print("Please make sure you have downloaded the OAuth credentials from Google Cloud Console.")
        return False

    print(f"\n✅ Found client secret at {CLIENT_SECRET_PATH}")

    # Check if credentials already exist
    if TOKEN_PATH.exists():
        print(f"\n⚠️  Credentials already exist at {TOKEN_PATH}")
        response = input("Do you want to re-authenticate? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing credentials.")
            return True

    print("\n🌐 Starting OAuth flow...")
    print("A browser window will open for you to sign in with your @happenings.dk account.")
    print()

    # Run OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(
        str(CLIENT_SECRET_PATH),
        SCOPES
    )

    creds = flow.run_local_server(port=0)

    # Save credentials
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

    print(f"\n✅ Authentication successful!")
    print(f"📁 Credentials saved to: {TOKEN_PATH}")
    print()
    print("You can now use the Google Workspace MCP server!")

    return True


if __name__ == "__main__":
    success = authenticate()
    exit(0 if success else 1)
