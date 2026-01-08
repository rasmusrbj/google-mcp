#!/usr/bin/env python3
"""
Authentication script for Google Workspace MCP Server
"""
import json
import webbrowser
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import threading

# Paths
CLIENT_SECRET_PATH = Path.home() / "google-workspace-mcp" / "client_secret.json"
TOKEN_DIR = Path.home() / ".google_workspace_mcp" / "credentials"

# Token path will be determined dynamically based on user's email

# Scopes needed for all services
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
    'https://www.googleapis.com/auth/userinfo.email',  # Needed to get user's email for token filename
]


class CallbackHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler to serve the beautiful callback page."""

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

    def do_GET(self):
        """Handle the OAuth callback."""
        # Parse the query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        # Check if this is the OAuth callback
        if 'code' in params:
            # Serve our beautiful HTML page
            callback_html_path = Path(__file__).parent / "oauth_callback.html"

            if callback_html_path.exists():
                with open(callback_html_path, 'r') as f:
                    html_content = f.read()
            else:
                # Fallback HTML if file not found
                html_content = """
                <!DOCTYPE html>
                <html><head><title>Success</title></head>
                <body style="background:#27272a;color:#fafafa;font-family:sans-serif;text-align:center;padding:50px;">
                <h1>✓ Authentication Successful</h1>
                <p>You can close this window.</p>
                </body></html>
                """

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html_content.encode())

            # Store the authorization code for the flow
            self.server.auth_code = params['code'][0]
        else:
            # Redirect to error page
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error_html = """
            <!DOCTYPE html>
            <html><head><title>Error</title></head>
            <body style="background:#27272a;color:#fafafa;font-family:sans-serif;text-align:center;padding:50px;">
            <h1>⚠ Authentication Failed</h1>
            <p>No authorization code received.</p>
            </body></html>
            """
            self.wfile.write(error_html.encode())


def authenticate():
    """Run the OAuth flow to get credentials with beautiful callback."""
    print("🔐 Google Workspace MCP Authentication")
    print("=" * 60)

    # Check if client secret exists
    if not CLIENT_SECRET_PATH.exists():
        print(f"\n❌ ERROR: Client secret not found at {CLIENT_SECRET_PATH}")
        print("Please make sure you have downloaded the OAuth credentials from Google Cloud Console.")
        return False

    print(f"\n✅ Found client secret at {CLIENT_SECRET_PATH}")

    print("\n🌐 Starting OAuth flow...")
    print("A browser window will open for you to sign in with your Google account.")
    print()

    # Create flow
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_PATH),
        scopes=SCOPES,
        redirect_uri='http://localhost:8080'
    )

    # Start local server
    server = HTTPServer(('localhost', 8080), CallbackHandler)
    server.auth_code = None

    # Get authorization URL
    auth_url, _ = flow.authorization_url(prompt='consent')

    print(f"🔗 Opening browser to: {auth_url[:60]}...")
    webbrowser.open(auth_url)

    print("⏳ Waiting for authorization...")

    # Handle one request (the callback)
    server.handle_request()

    if not server.auth_code:
        print("\n❌ No authorization code received!")
        return False

    # Exchange code for credentials
    flow.fetch_token(code=server.auth_code)
    creds = flow.credentials

    # Get user email from credentials (requires userinfo.email scope)
    from googleapiclient.discovery import build
    userinfo_service = build('oauth2', 'v2', credentials=creds)
    user_info = userinfo_service.userinfo().get().execute()
    user_email = user_info.get('email', 'default')

    print(f"\n✅ Authenticated as: {user_email}")

    # Save credentials with user's email as filename
    TOKEN_DIR.mkdir(parents=True, exist_ok=True)
    token_path = TOKEN_DIR / f"{user_email}.json"

    # Check if credentials already exist for this user
    if token_path.exists():
        response = input(f"\n⚠️  Credentials already exist for {user_email}. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Keeping existing credentials.")
            return True

    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    print(f"\n✅ Authentication successful!")
    print(f"📁 Credentials saved to: {token_path}")
    print()
    print("You can now use the Google Workspace MCP server!")

    return True


if __name__ == "__main__":
    success = authenticate()
    exit(0 if success else 1)
