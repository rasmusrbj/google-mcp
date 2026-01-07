# Complete Setup Guide - Google Workspace MCP Server

This guide will walk you through every step of setting up the Google Workspace MCP server, from creating a Google Cloud project to configuring Claude Desktop.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Part 1: Google Cloud Console Setup](#part-1-google-cloud-console-setup)
- [Part 2: Enable Required APIs](#part-2-enable-required-apis)
- [Part 3: Configure OAuth Consent Screen](#part-3-configure-oauth-consent-screen)
- [Part 4: Create OAuth Credentials](#part-4-create-oauth-credentials)
- [Part 5: Install the MCP Server](#part-5-install-the-mcp-server)
- [Part 6: Authenticate](#part-6-authenticate)
- [Part 7: Configure Claude Desktop/Code](#part-7-configure-claude-desktopcode)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **A Google Account** (personal Gmail or Google Workspace account)
- ✅ **Python 3.8 or higher** installed ([Download Python](https://www.python.org/downloads/))
- ✅ **Claude Desktop** or **Claude Code CLI** installed ([Get Claude](https://claude.ai/download))
- ✅ **Git** (optional, for cloning) ([Download Git](https://git-scm.com/downloads))
- ✅ **Terminal/Command Line** access

**Check your Python version:**
```bash
python3 --version
```
You should see Python 3.8 or higher.

---

## Part 1: Google Cloud Console Setup

### Step 1.1: Access Google Cloud Console

1. Open your web browser
2. Navigate to [Google Cloud Console](https://console.cloud.google.com/)
3. Sign in with your Google account
4. Accept the Terms of Service if prompted

### Step 1.2: Create a New Project

1. Click the **project dropdown** at the top of the page (next to "Google Cloud")
   - If you have no projects, you'll see "Select a project"
   - If you have existing projects, you'll see the current project name

2. Click **"NEW PROJECT"** in the top right of the project selector dialog

3. Fill in the project details:
   - **Project name**: `Google Workspace MCP` (or your preferred name)
   - **Organization**: Select your organization (if applicable) or leave as "No organization"
   - **Location**: Leave as default or select your organization

4. Click **"CREATE"**

5. Wait for the project to be created (usually takes a few seconds)

6. Click **"SELECT PROJECT"** when the notification appears, or manually select your new project from the project dropdown

**Direct Link:** [Create New Project](https://console.cloud.google.com/projectcreate)

### Step 1.3: Note Your Project ID

Your Project ID will be automatically generated (e.g., `google-workspace-mcp-123456`). You can find it:
- In the project selector dropdown
- In the project settings
- On the dashboard

You'll need this if you encounter API errors later.

---

## Part 2: Enable Required APIs

You must enable each API individually. Click on each link below **while your project is selected**:

### Core APIs (Required)

#### 2.1: Gmail API
**Purpose:** Send, read, and search emails

1. **[Click here to enable Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)**
2. Ensure your project is selected at the top
3. Click **"ENABLE"**
4. Wait for the API to be enabled (5-10 seconds)
5. You should see "API enabled" with a green checkmark

#### 2.2: Google Drive API
**Purpose:** Access files in My Drive and Shared Drives

1. **[Click here to enable Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

#### 2.3: Google Calendar API
**Purpose:** Manage calendar events

1. **[Click here to enable Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

#### 2.4: Google Docs API
**Purpose:** Create and edit Google Documents

1. **[Click here to enable Google Docs API](https://console.cloud.google.com/apis/library/docs.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

#### 2.5: Google Sheets API
**Purpose:** Create and edit Google Spreadsheets

1. **[Click here to enable Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

#### 2.6: Google Slides API
**Purpose:** Create and edit Google Presentations

1. **[Click here to enable Google Slides API](https://console.cloud.google.com/apis/library/slides.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

### Optional APIs (Recommended)

#### 2.7: Google Forms API
**Purpose:** Create and manage Google Forms

1. **[Click here to enable Google Forms API](https://console.cloud.google.com/apis/library/forms.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

#### 2.8: Google Tasks API
**Purpose:** Manage Google Tasks

1. **[Click here to enable Google Tasks API](https://console.cloud.google.com/apis/library/tasks.googleapis.com)**
2. Click **"ENABLE"**
3. Wait for confirmation

### Step 2.9: Verify All APIs Are Enabled

1. Go to [APIs & Services Dashboard](https://console.cloud.google.com/apis/dashboard)
2. You should see all enabled APIs listed
3. Verify you see at least:
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Docs API
   - Google Sheets API
   - Google Slides API

**✅ Checkpoint:** You should have 6-8 APIs enabled at this point.

---

## Part 3: Configure OAuth Consent Screen

The OAuth consent screen is what users see when they authorize your application.

### Step 3.1: Navigate to OAuth Consent Screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Or navigate manually:
   - Click the hamburger menu (☰) in the top left
   - Click **"APIs & Services"**
   - Click **"OAuth consent screen"** in the left sidebar

### Step 3.2: Choose User Type

You'll see two options:

#### Option A: Internal (For Google Workspace Users)
**Choose this if:**
- You have a Google Workspace account (e.g., @yourcompany.com)
- You want to restrict access to users in your organization only
- **Advantage:** No verification needed, simpler setup

1. Select **"Internal"**
2. Click **"CREATE"**

#### Option B: External (For Personal Gmail Users)
**Choose this if:**
- You have a personal Gmail account (@gmail.com)
- You want to allow any Google user to authenticate
- **Note:** Limited to 100 users while in testing mode

1. Select **"External"**
2. Click **"CREATE"**

### Step 3.3: Configure OAuth Consent Screen - App Information

Fill in the required fields:

#### Required Fields:
- **App name:** `Google Workspace MCP Server` (or your preferred name)
- **User support email:** Select your email from the dropdown
- **Developer contact information:** Enter your email address

#### Optional Fields (you can skip these):
- App logo
- App domain
- Authorized domains
- Application home page
- Application privacy policy link
- Application terms of service link

Click **"SAVE AND CONTINUE"**

### Step 3.4: Configure Scopes

1. Click **"ADD OR REMOVE SCOPES"**

2. In the filter box, search for and select each of these scopes:

#### Gmail Scopes:
- `https://www.googleapis.com/auth/gmail.modify` - Read, compose, send, and permanently delete messages
- `https://www.googleapis.com/auth/gmail.send` - Send messages only

To find them:
- Type "gmail" in the filter box
- Scroll through the list
- Check the boxes for the scopes above

#### Drive Scopes:
- `https://www.googleapis.com/auth/drive` - See, edit, create, and delete all Drive files

To find it:
- Type "drive" in the filter box
- Select the main drive scope (not drive.file or drive.readonly)

#### Docs, Sheets, Slides Scopes:
- `https://www.googleapis.com/auth/documents` - See, edit, create, and delete Google Docs
- `https://www.googleapis.com/auth/spreadsheets` - See, edit, create, and delete Google Sheets
- `https://www.googleapis.com/auth/presentations` - See, edit, create, and delete Google Slides

#### Tasks Scope:
- `https://www.googleapis.com/auth/tasks` - Create, edit, organize, and delete all your tasks

#### Forms Scope:
- `https://www.googleapis.com/auth/forms.body` - See, edit, create, and delete all your Google Forms

#### Calendar Scope:
- `https://www.googleapis.com/auth/calendar` - See, edit, share, and permanently delete all calendars

3. **Alternative Method - Manual Entry:**

   If you prefer, you can manually add scopes:
   - Scroll to the bottom of the scopes list
   - Click **"MANUALLY ADD SCOPES"**
   - Paste each scope URL one per line:
   ```
   https://www.googleapis.com/auth/gmail.modify
   https://www.googleapis.com/auth/gmail.send
   https://www.googleapis.com/auth/drive
   https://www.googleapis.com/auth/documents
   https://www.googleapis.com/auth/spreadsheets
   https://www.googleapis.com/auth/presentations
   https://www.googleapis.com/auth/forms.body
   https://www.googleapis.com/auth/tasks
   https://www.googleapis.com/auth/calendar
   ```
   - Click **"ADD TO TABLE"**

4. Click **"UPDATE"** at the bottom

5. Verify you see all scopes listed in the "Your sensitive scopes" section

6. Click **"SAVE AND CONTINUE"**

### Step 3.5: Add Test Users (External User Type Only)

**If you selected "Internal" user type, skip this step.**

If you selected "External" user type:

1. Click **"ADD USERS"**
2. Enter the email address(es) that will use this MCP server
   - Add your own email
   - Add any other users who need access (up to 100 in testing mode)
3. Click **"ADD"**
4. Click **"SAVE AND CONTINUE"**

### Step 3.6: Review Summary

1. Review all the information
2. Click **"BACK TO DASHBOARD"** or **"SAVE"**

**✅ Checkpoint:** Your OAuth consent screen is now configured!

---

## Part 4: Create OAuth Credentials

### Step 4.1: Navigate to Credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Or navigate manually:
   - Click **"Credentials"** in the left sidebar (under APIs & Services)

### Step 4.2: Create OAuth Client ID

1. Click **"+ CREATE CREDENTIALS"** at the top of the page
2. Select **"OAuth client ID"** from the dropdown

### Step 4.3: Configure OAuth Client

1. **Application type:** Select **"Desktop app"** from the dropdown
   - Desktop app is required for the local authentication flow
   - Do NOT select "Web application" or "Mobile app"

2. **Name:** Enter a name for this OAuth client
   - Example: `Google Workspace MCP Desktop Client`
   - This name is just for your reference

3. Click **"CREATE"**

### Step 4.4: Download Credentials

A dialog will appear showing your client ID and client secret:

1. **Important:** Click the **"DOWNLOAD JSON"** button (download icon)
   - Do NOT just copy the client ID and secret
   - You need the complete JSON file

2. The file will download with a name like:
   - `client_secret_123456789-abcdefg.apps.googleusercontent.com.json`

3. **Save this file securely** - it contains sensitive credentials

### Step 4.5: Move Credentials to Correct Location

1. Create the directory for credentials:
   ```bash
   mkdir -p ~/google-workspace-mcp
   ```

2. Move and rename the downloaded file:
   ```bash
   mv ~/Downloads/client_secret_*.json ~/google-workspace-mcp/client_secret.json
   ```

3. Verify the file is in place:
   ```bash
   ls -la ~/google-workspace-mcp/client_secret.json
   ```

You should see the file listed.

**✅ Checkpoint:** Your OAuth credentials are created and saved!

---

## Part 5: Install the MCP Server

### Step 5.1: Download the Server Code

Choose one of these methods:

#### Method A: Using Git (Recommended)

```bash
cd ~
git clone https://github.com/rasmusrbj/google-mcp.git google-drive-shared-mcp
cd google-drive-shared-mcp
```

#### Method B: Download ZIP

1. Visit [https://github.com/rasmusrbj/google-mcp](https://github.com/rasmusrbj/google-mcp)
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Extract the ZIP file
5. Rename the folder to `google-drive-shared-mcp`
6. Move it to your home directory:
   ```bash
   mv ~/Downloads/google-mcp-main ~/google-drive-shared-mcp
   ```

### Step 5.2: Run the Setup Script

The easiest way to install is using the automated setup script:

```bash
cd ~/google-drive-shared-mcp
chmod +x setup.sh
./setup.sh
```

The script will:
- ✅ Check Python version
- ✅ Create a virtual environment
- ✅ Install all dependencies
- ✅ Verify OAuth credentials exist
- ✅ Guide you through authentication

**OR** follow the manual installation steps below:

### Step 5.3: Manual Installation (Alternative)

If you prefer to install manually:

#### Create Virtual Environment

```bash
cd ~/google-drive-shared-mcp
python3 -m venv venv
```

#### Activate Virtual Environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```powershell
venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- FastMCP (MCP framework)
- Google API Python Client
- Google Auth libraries
- All other required packages

**✅ Checkpoint:** All dependencies are installed!

---

## Part 6: Authenticate

### Step 6.1: Run Authentication Script

```bash
cd ~/google-drive-shared-mcp
source venv/bin/activate  # If not already activated
python3 authenticate.py
```

### Step 6.2: Complete OAuth Flow

1. The script will print:
   ```
   🔐 Google Workspace MCP Authentication
   ========================================

   ✅ Found client secret at /Users/you/google-workspace-mcp/client_secret.json

   🌐 Starting OAuth flow...
   A browser window will open for you to sign in with your Google account.
   ```

2. **Your default browser will automatically open** to Google's authorization page

3. **If browser doesn't open automatically:**
   - Look for a URL in the terminal output
   - Copy and paste it into your browser manually

### Step 6.3: Authorize the Application

In the browser:

1. **Select your Google account**
   - Choose the account you want to use with the MCP server

2. **Review permissions**
   - You'll see a list of permissions the app is requesting
   - These match the scopes you configured earlier

3. **For External apps, you may see a warning:**
   - "Google hasn't verified this app"
   - Click **"Advanced"**
   - Click **"Go to Google Workspace MCP Server (unsafe)"**
   - This is normal for apps in testing mode

4. **Grant permissions:**
   - Review each permission
   - Scroll down
   - Click **"Allow"** or **"Continue"**

5. **Success page:**
   - After granting permissions, Google will redirect to a local callback URL
   - You'll see one of these success messages:
     - **"The authentication flow has completed. You may close this window."**
     - **"Authentication successful"**
     - A simple page saying "You can close this tab now"
   - The exact message depends on the OAuth library version
   - **This is the callback screen** - it confirms the local server received the authorization code
   - You can safely close the browser window/tab
   - The callback URL will be something like: `http://localhost:XXXXX/?code=...&scope=...`

### Step 6.4: Verify Authentication

Back in the terminal, you should see:

```
✅ Authentication successful!
📁 Credentials saved to: /Users/you/.google_workspace_mcp/credentials/your-email.json

You can now use the Google Workspace MCP server!
```

### Step 6.5: Test the Connection (Optional)

Verify everything works:

```bash
python3 test_auth.py
```

You should see:
```
✅ SUCCESS! Found X shared drive(s):
   - Drive Name 1
   - Drive Name 2
   ...
```

**✅ Checkpoint:** You're authenticated and ready to use the MCP server!

---

## Part 7: Configure Claude Desktop/Code

### For Claude Desktop (macOS)

#### Step 7.1: Locate Configuration File

The configuration file is located at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Step 7.2: Edit Configuration

1. Open the configuration file in your text editor:
   ```bash
   open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. If the file doesn't exist, create it:
   ```bash
   mkdir -p ~/Library/Application\ Support/Claude
   echo '{"mcpServers":{}}' > ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

#### Step 7.3: Add MCP Server Configuration

Add this configuration to the `mcpServers` object:

```json
{
  "mcpServers": {
    "google-workspace-full": {
      "command": "/Users/YOUR_USERNAME/google-drive-shared-mcp/venv/bin/python3",
      "args": ["/Users/YOUR_USERNAME/google-drive-shared-mcp/server.py"],
      "env": {}
    }
  }
}
```

**IMPORTANT:** Replace `YOUR_USERNAME` with your actual macOS username.

To find your username, run:
```bash
echo $HOME
```

#### Step 7.4: Verify Configuration

Your complete config file should look like:

```json
{
  "mcpServers": {
    "google-workspace-full": {
      "command": "/Users/johndoe/google-drive-shared-mcp/venv/bin/python3",
      "args": ["/Users/johndoe/google-drive-shared-mcp/server.py"],
      "env": {}
    }
  }
}
```

If you have other MCP servers configured, just add `google-workspace-full` to the existing `mcpServers` object.

#### Step 7.5: Restart Claude Desktop

1. Quit Claude Desktop completely (Cmd+Q)
2. Reopen Claude Desktop
3. The MCP server will load automatically

#### Step 7.6: Verify It's Working

In Claude Desktop, try asking:

```
List all my shared drives
```

You should see a list of your Google Shared Drives!

### For Claude Code CLI

#### Step 7.1: Locate Configuration File

Claude Code configuration is in:
```
~/.claude.json
```

#### Step 7.2: Add MCP Server

Run this command (replace `YOUR_USERNAME`):

```bash
claude mcp add google-workspace-full \
  --transport stdio \
  --command /Users/YOUR_USERNAME/google-drive-shared-mcp/venv/bin/python3 \
  -- /Users/YOUR_USERNAME/google-drive-shared-mcp/server.py
```

#### Step 7.3: Verify

```bash
claude mcp list
```

You should see `google-workspace-full` in the list.

**✅ Final Checkpoint:** Your MCP server is configured and ready to use!

---

## Troubleshooting

### Issue: "API has not been used in project before"

**Error message:**
```
Gmail API has not been used in project 123456789 before or it is disabled
```

**Solution:**
1. Go to the API Library: [https://console.cloud.google.com/apis/library](https://console.cloud.google.com/apis/library)
2. Make sure your project is selected at the top
3. Search for the API mentioned in the error (e.g., "Gmail")
4. Click on it and click "ENABLE"
5. Wait a few minutes for the API to fully activate
6. Try again

### Issue: "Invalid client_secret.json"

**Solution:**
1. Verify the file exists:
   ```bash
   ls -la ~/google-workspace-mcp/client_secret.json
   ```
2. Check it's valid JSON:
   ```bash
   python3 -c "import json; json.load(open('~/google-workspace-mcp/client_secret.json'))"
   ```
3. If invalid, re-download from Google Cloud Console:
   - Go to [Credentials](https://console.cloud.google.com/apis/credentials)
   - Find your OAuth 2.0 Client ID
   - Click the download icon on the right
   - Replace the file

### Issue: "No such file or directory: python3"

**Solution:**
You need to install Python 3.8+:
- **macOS:** `brew install python3` or download from [python.org](https://www.python.org/downloads/)
- **Linux:** `sudo apt install python3` (Ubuntu/Debian) or `sudo yum install python3` (CentOS/RHEL)
- **Windows:** Download from [python.org](https://www.python.org/downloads/)

### Issue: "This app isn't verified"

**This is normal** for apps in testing mode.

**Solution:**
1. Click "Advanced" at the bottom left
2. Click "Go to [Your App Name] (unsafe)"
3. This is safe when it's your own app
4. To remove this warning permanently:
   - Submit your app for verification (complex process)
   - Or keep it in testing mode (works fine for personal use)

### Issue: "Access blocked: Authorization Error"

**Solution:**
1. Make sure you added your email as a test user (External apps only)
2. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
3. Click "Test users"
4. Click "ADD USERS"
5. Add your email address
6. Try authenticating again

### Issue: MCP Server Not Appearing in Claude

**Solution:**
1. Check the configuration file exists and is valid JSON
2. Verify the paths are correct (no typos in username)
3. Check the virtual environment exists:
   ```bash
   ls -la ~/google-drive-shared-mcp/venv/bin/python3
   ```
4. Restart Claude Desktop completely (Cmd+Q, not just close window)
5. Check Claude Desktop logs:
   ```bash
   tail -f ~/Library/Logs/Claude/mcp*.log
   ```

### Issue: "Credentials not found"

**Solution:**
1. Run the authentication script:
   ```bash
   cd ~/google-drive-shared-mcp
   source venv/bin/activate
   python3 authenticate.py
   ```
2. Complete the OAuth flow in the browser
3. Verify credentials were created:
   ```bash
   ls -la ~/.google_workspace_mcp/credentials/
   ```

### Issue: "Permission denied" errors

**Solution:**
1. Make scripts executable:
   ```bash
   chmod +x ~/google-drive-shared-mcp/setup.sh
   chmod +x ~/google-drive-shared-mcp/authenticate.py
   ```
2. Check file ownership:
   ```bash
   ls -la ~/google-drive-shared-mcp/
   ```

---

## FAQ

### Q: Do I need a paid Google Workspace account?

**A:** No! This works with:
- Free personal Gmail accounts (@gmail.com)
- Google Workspace accounts (@yourcompany.com)
- Google Workspace for Education
- Any Google account type

### Q: How much does this cost?

**A:** The MCP server is completely free and open source. Google Cloud Console usage is free for the API calls typical of personal use. You only pay if you exceed generous free quotas (unlikely for individual use).

### Q: Can I use this with multiple Google accounts?

**A:** Yes, but you need to create separate credential files for each account. The easier approach is to re-authenticate when you want to switch accounts:
```bash
python3 authenticate.py
```

### Q: Is my data secure?

**A:** Yes:
- Your credentials never leave your computer
- The OAuth tokens are stored locally in `~/.google_workspace_mcp/credentials/`
- The MCP server runs locally on your machine
- All communication with Google uses encrypted HTTPS
- You can revoke access anytime: [Google Account Permissions](https://myaccount.google.com/permissions)

### Q: Can I use this in production/commercial applications?

**A:** Yes, but:
- Review the MIT License
- You may need to get your OAuth app verified by Google for external users
- Consider rate limits for high-volume usage
- See [Google API Terms of Service](https://developers.google.com/terms)

### Q: What happens if I revoke access?

If you revoke access from [Google Account Permissions](https://myaccount.google.com/permissions):
- The MCP server will stop working
- Just run `python3 authenticate.py` again to re-authorize

### Q: Can I see what scopes/permissions are being requested?

**A:** Yes! Check the `authenticate.py` file or look at the OAuth consent screen during authorization. All requested scopes are listed.

### Q: How do I update the MCP server?

```bash
cd ~/google-drive-shared-mcp
git pull origin main  # If installed via git
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### Q: Can I run this on Windows or Linux?

**A:** Yes! The setup is very similar:

**Windows:**
- Use PowerShell or Command Prompt
- Paths will be different (e.g., `C:\Users\YourName\google-drive-shared-mcp`)
- Virtual environment activation: `venv\Scripts\activate`

**Linux:**
- Same as macOS
- Configuration file location may differ depending on Claude installation

### Q: What Google APIs are supported?

Currently supported:
- ✅ Gmail (send, read, search)
- ✅ Google Drive (including Shared Drives!)
- ✅ Google Docs
- ✅ Google Sheets
- ✅ Google Slides
- ✅ Google Tasks
- ✅ Google Calendar (via existing workspace-mcp)
- ✅ Google Forms (via existing workspace-mcp)

### Q: How do I uninstall?

1. Remove from Claude config:
   ```bash
   # Edit and remove the google-workspace-full entry
   open -a TextEdit ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Remove the server files:
   ```bash
   rm -rf ~/google-drive-shared-mcp
   ```

3. Remove credentials:
   ```bash
   rm -rf ~/.google_workspace_mcp
   ```

4. Revoke OAuth access:
   - Go to [Google Account Permissions](https://myaccount.google.com/permissions)
   - Find "Google Workspace MCP Server"
   - Click "Remove Access"

5. Delete Google Cloud project (optional):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project
   - Go to Settings
   - Click "Shut down"

---

## Additional Resources

- **Google Cloud Console:** [https://console.cloud.google.com/](https://console.cloud.google.com/)
- **Google API Documentation:** [https://developers.google.com/workspace](https://developers.google.com/workspace)
- **MCP Protocol Docs:** [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **FastMCP Framework:** [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Project GitHub:** [https://github.com/rasmusrbj/google-mcp](https://github.com/rasmusrbj/google-mcp)

---

## Getting Help

If you encounter issues:

1. **Check this guide** - Most issues are covered in the Troubleshooting section
2. **Review error messages** - They often contain direct links to solutions
3. **Open an issue** - [GitHub Issues](https://github.com/rasmusrbj/google-mcp/issues)
4. **Check MCP docs** - [Model Context Protocol](https://modelcontextprotocol.io/)

---

**Congratulations!** 🎉

You've successfully set up the Google Workspace MCP Server with full shared drive support!

**What's next?**
- Try creating a folder in a shared drive
- Search your Gmail
- Create a Google Doc
- List your calendar events
- Explore all the available tools!

---

*Last updated: January 2026*
*Guide version: 1.0*
*For: google-mcp v1.0.0*
