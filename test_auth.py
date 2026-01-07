#!/usr/bin/env python3
"""Test authentication and API access"""
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TOKEN_PATH = Path.home() / ".google_workspace_mcp" / "credentials" / "rasmus@happenings.dk.json"

print(f"Looking for credentials at: {TOKEN_PATH}")
print(f"Credentials exist: {TOKEN_PATH.exists()}")

if not TOKEN_PATH.exists():
    print("\n❌ ERROR: No credentials found!")
    print("Please authenticate first using the workspace-mcp server.")
    exit(1)

print("\n✅ Loading credentials...")
creds = Credentials.from_authorized_user_file(str(TOKEN_PATH))

print(f"Credentials valid: {creds.valid}")
print(f"Credentials expired: {creds.expired}")
print(f"Has refresh token: {creds.refresh_token is not None}")

if creds.expired and creds.refresh_token:
    print("\n🔄 Refreshing expired credentials...")
    creds.refresh(Request())
    print("✅ Credentials refreshed!")

print("\n🧪 Testing Drive API - Listing shared drives...")
try:
    drive_service = build('drive', 'v3', credentials=creds)
    results = drive_service.drives().list(pageSize=10, fields="drives(id, name)").execute()
    drives = results.get('drives', [])

    if drives:
        print(f"\n✅ SUCCESS! Found {len(drives)} shared drive(s):")
        for drive in drives:
            print(f"   - {drive['name']} (ID: {drive['id']})")
    else:
        print("\n✅ API works but no shared drives found (this is OK)")

except Exception as e:
    print(f"\n❌ ERROR testing Drive API: {e}")
    import traceback
    traceback.print_exc()

print("\n🧪 Testing Gmail API - Checking inbox...")
try:
    gmail_service = build('gmail', 'v1', credentials=creds)
    results = gmail_service.users().messages().list(userId='me', maxResults=1).execute()
    messages = results.get('messages', [])

    if messages:
        print(f"✅ Gmail API works! Found messages in inbox")
    else:
        print("✅ Gmail API works (no messages found)")

except Exception as e:
    print(f"❌ ERROR testing Gmail API: {e}")
    print("   This might mean the credentials don't have Gmail scope")

print("\n🎉 Test complete!")
