# Google Workspace MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing **full Google Workspace integration** with **complete shared drive support**.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Server?

Most Google Drive MCP servers have limited or no shared drive (Team Drive) support. This server provides:

✅ **Full Shared Drive Support** - Create, read, and manage files in shared drives
✅ **Complete Google Workspace** - Gmail, Drive, Docs, Sheets, Slides, Tasks
✅ **Simple Setup** - Automated installation and authentication
✅ **Production Ready** - Proper error handling and token refresh

## Features

### 📧 Gmail
- Search emails with advanced queries
- Read full message content
- Send emails with CC support
- Manage labels and threads

### 📁 Google Drive (with Shared Drives!)
- **List all shared drives** you have access to
- **Create folders and files** in shared drives
- Browse shared drive contents
- Upload files to shared drives
- Full file metadata access

### 📝 Google Docs
- Create documents in My Drive or Shared Drives
- Read document content
- Append text to documents
- Full formatting support

### 📊 Google Sheets
- Create spreadsheets anywhere
- Read and write cell data
- Formula support
- Multi-sheet operations

### 🎨 Google Slides
- Create presentations in any drive
- Add and modify slides
- Template support

### ✅ Google Tasks
- List and create tasks
- Manage task lists
- Due dates and notes

## Installation

### Prerequisites

- Python 3.8 or higher
- A Google Cloud project with OAuth credentials

### Quick Start

1. **Clone or download** this repository
2. **Run the setup script:**

```bash
cd google-drive-shared-mcp
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Create a Python virtual environment
- Install all dependencies
- Guide you through OAuth authentication
- Provide configuration for Claude Code/Desktop

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Authenticate
python3 authenticate.py
```

## Google Cloud Setup

### 1. Create a Google Cloud Project

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Click "New Project"
3. Name it (e.g., "Google Workspace MCP")
4. Note the Project ID

### 2. Enable Required APIs

Enable these APIs in your project:
- [Gmail API](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
- [Google Drive API](https://console.cloud.google.com/apis/library/drive.googleapis.com)
- [Google Calendar API](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)
- [Google Docs API](https://console.cloud.google.com/apis/library/docs.googleapis.com)
- [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com)
- [Google Slides API](https://console.cloud.google.com/apis/library/slides.googleapis.com)
- [Google Forms API](https://console.cloud.google.com/apis/library/forms.googleapis.com)
- [Google Tasks API](https://console.cloud.google.com/apis/library/tasks.googleapis.com)

### 3. Configure OAuth Consent Screen

1. Go to **OAuth consent screen**
2. Select **Internal** (for Workspace) or **External** (for personal)
3. Fill in app name and contact info
4. Add required scopes (the authenticate.py script lists all needed scopes)
5. Add test users if using External

### 4. Create OAuth Credentials

1. Go to **Credentials** > **Create Credentials** > **OAuth client ID**
2. Select **Desktop app**
3. Name it "Google Workspace MCP"
4. Download the JSON file
5. Save to `~/google-workspace-mcp/client_secret.json`

## Configuration

### For Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

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

### For Claude Code CLI

The setup script will provide the exact configuration for your system.

## Usage Examples

### List Shared Drives

```
List all my shared drives
```

Response:
```
Found 10 shared drive(s):

📁 Admin
   ID: 0AL3RedoLx77VUk9PVA

📁 Product Development
   ID: 0AMd7nmoOBpFGUk9PVA
...
```

### Create Folder in Shared Drive

```
Create a folder called "Q1 Reports" in shared drive 0AL3RedoLx77VUk9PVA
```

### Search Gmail

```
Search my Gmail for emails from john@example.com sent this week
```

### Create Google Doc in Shared Drive

```
Create a Google Doc titled "Meeting Notes" in folder abc123 in shared drive xyz789
```

## Available Tools

### Drive Tools
- `drive_list_shared_drives(page_size)` - List all shared drives
- `drive_list_files(folder_id, drive_id, query, page_size)` - List files
- `drive_create_folder(name, parent_id, drive_id)` - Create folders
- `get_file_info(file_id, drive_id)` - Get file details

### Gmail Tools
- `gmail_search(query, max_results)` - Search emails
- `gmail_read(message_id)` - Read email content
- `gmail_send(to, subject, body, cc)` - Send emails

### Docs Tools
- `docs_create(title, parent_id, drive_id)` - Create documents
- `docs_read(document_id)` - Read document content
- `docs_append_text(document_id, text)` - Add text

### Sheets Tools
- `sheets_create(title, parent_id, drive_id)` - Create spreadsheets
- `sheets_read(spreadsheet_id, range_name)` - Read data
- `sheets_write(spreadsheet_id, range_name, values)` - Write data

### Slides Tools
- `slides_create(title, parent_id, drive_id)` - Create presentations

### Tasks Tools
- `tasks_list(task_list_id, max_results)` - List tasks
- `tasks_create(title, notes, task_list_id)` - Create tasks

## Troubleshooting

### "No valid credentials found"

Run the authentication script:
```bash
python3 authenticate.py
```

### API Not Enabled Error

Enable the required API in Google Cloud Console. The error message will include a direct link.

### Token Expired

Tokens are automatically refreshed. If you see authentication errors, re-run `authenticate.py`.

## Architecture

This server:
- Uses **FastMCP** framework for MCP protocol implementation
- Authenticates via **OAuth 2.0** with automatic token refresh
- Stores tokens in `~/.google_workspace_mcp/credentials/`
- Communicates via **stdio** transport (standard for MCP servers)

## API Documentation

Implementation follows official Google Workspace APIs (2026):
- [Drive API - Shared Drives](https://developers.google.com/workspace/drive/api/guides/enable-shareddrives)
- [Gmail API - Sending](https://developers.google.com/workspace/gmail/api/guides/sending)
- [Docs API - Batch Update](https://developers.google.com/workspace/docs/api/reference/rest/v1/documents/batchUpdate)

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Open an issue on GitHub
- Check the [MCP documentation](https://modelcontextprotocol.io/)
- Review [Google Workspace API docs](https://developers.google.com/workspace)

## Acknowledgments

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP framework
- [Google API Python Client](https://github.com/googleapis/google-api-python-client)
- [Model Context Protocol](https://modelcontextprotocol.io/)

---

## Author

**Rasmus Jensing**
CEO @ [Happenings](https://happenings.com)
GitHub: [@rasmusrbj](https://github.com/rasmusrbj)

Made with ❤️ for the MCP community
