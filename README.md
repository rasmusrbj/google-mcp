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

### 📧 Gmail (8 tools)
- **Search** emails with advanced Gmail queries
- **Read** full message content with headers and body
- **Send** emails with CC support
- **Reply** to email threads
- **Mark as read/unread**
- **Archive** emails
- **Delete** emails (move to trash)
- Full thread support

### 📁 Google Drive (12 tools) - **Full Shared Drives Support!**
- **List all shared drives** you have access to
- **List files** in any folder (My Drive or Shared Drives)
- **Create folders** in My Drive or Shared Drives
- **Upload files** to any location including Shared Drives
- **Download files** to local filesystem (exports Google Docs as DOCX, Sheets as XLSX, etc.)
- **Delete** files and folders
- **Copy** files
- **Move** files between folders
- **Share** files with specific users (reader, writer, commenter roles)
- **Get file metadata** with detailed information
- **Search files** with advanced query syntax
- Works seamlessly with both My Drive and Team Drives

### 📝 Google Docs (16 tools)
- **Create** documents in My Drive or Shared Drives
- **Read** full document content
- **Append** text to existing documents
- **Insert** text at specific positions
- **Replace** text (find and replace)
- **Format** text (bold, italic, underline, font size)
- **Insert tables** into documents
- **Insert images** from URLs
- **Add hyperlinks** to text
- **Create bulleted lists**
- **Create numbered lists**
- **Set heading styles** (H1-H6, Title, Subtitle, Normal)
- **Add page breaks**
- **Delete content** from ranges
- **Update table cells** with text
- **Add bookmarks** for internal linking
- Full shared drive support

### 📊 Google Sheets (8 tools)
- **Create** spreadsheets in any location
- **Read** data from any range
- **Write** data to specific cells/ranges
- **Append** rows to existing sheets
- **Clear** data from ranges
- **Get metadata** (sheet names, IDs, properties)
- **Create sheet tabs** in existing spreadsheets
- **Format cells** (bold, colors, etc.)
- Formula support via USER_ENTERED mode

### 🎨 Google Slides (12 tools)
- **Create** presentations in My Drive or Shared Drives
- **Get details** about presentations (slide count, structure)
- **Read** all text content from presentations
- **Add slides** to presentations
- **Add text** boxes to slides
- **Delete** slides from presentations
- **Insert images** from URLs
- **Replace text** across all slides (template automation!)
- **Format text** in slides (bold, italic, font size, color)
- **Add shapes** (rectangles, ellipses, arrows, etc.)
- **Duplicate slides**
- **Add speaker notes** to slides
- Full shared drive support

### 📋 Google Forms (5 tools)
- **Create** new forms
- **Get** form details and questions
- **Add text questions** (short or paragraph)
- **Add multiple choice** questions
- **List responses** with full answer data

### 📅 Google Calendar (4 tools)
- **List** upcoming events
- **Create** events with attendees and location
- **Update** existing events
- **Delete** events
- Full timezone support

### ✅ Google Tasks (4 tools)
- **List** tasks from any task list
- **Create** new tasks with notes
- **Complete** tasks (mark as done)
- **Delete** tasks

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

## Available Tools (69 Tools Total)

### Gmail Tools (8 tools)
- `gmail_search(query, max_results)` - Search emails with Gmail query syntax
- `gmail_read(message_id)` - Read full email content
- `gmail_send(to, subject, body, cc)` - Send new emails
- `gmail_reply(message_id, body)` - Reply to email threads
- `gmail_mark_read(message_id)` - Mark email as read
- `gmail_mark_unread(message_id)` - Mark email as unread
- `gmail_archive(message_id)` - Archive email (remove from inbox)
- `gmail_delete(message_id)` - Move email to trash

### Drive Tools (12 tools)
- `drive_list_shared_drives(page_size)` - List all shared drives you have access to
- `drive_list_files(folder_id, drive_id, query, page_size)` - List files in folders
- `drive_create_folder(name, parent_id, drive_id)` - Create folders anywhere
- `drive_upload_file(file_path, name, parent_id, drive_id)` - Upload files
- `drive_download_file(file_id, destination_path, drive_id)` - Download files to local filesystem
- `drive_delete_file(file_id, drive_id)` - Delete files/folders
- `drive_copy_file(file_id, new_name, parent_id, drive_id)` - Copy files
- `drive_move_file(file_id, new_parent_id, drive_id)` - Move files between folders
- `drive_share_file(file_id, email, role, drive_id)` - Share with users
- `drive_get_file_metadata(file_id, drive_id)` - Get detailed file information
- `drive_search_files(query, drive_id, page_size)` - Advanced file search

### Docs Tools (16 tools)
- `docs_create(title, parent_id, drive_id)` - Create documents
- `docs_read(document_id)` - Read document content
- `docs_append_text(document_id, text)` - Append text
- `docs_insert_text(document_id, text, index)` - Insert text at position
- `docs_replace_text(document_id, find_text, replace_text, match_case)` - Find and replace
- `docs_format_text(document_id, start_index, end_index, bold, italic, underline, font_size)` - Format text
- `docs_insert_table(document_id, rows, columns, index)` - Insert table
- `docs_insert_image(document_id, image_url, index, width, height)` - Insert image from URL
- `docs_add_hyperlink(document_id, start_index, end_index, url)` - Add hyperlink to text
- `docs_create_bulleted_list(document_id, start_index, end_index)` - Create bulleted list
- `docs_create_numbered_list(document_id, start_index, end_index)` - Create numbered list
- `docs_set_heading_style(document_id, start_index, end_index, heading_level)` - Set heading style (H1-H6, TITLE, SUBTITLE, NORMAL_TEXT)
- `docs_add_page_break(document_id, index)` - Insert page break
- `docs_delete_content(document_id, start_index, end_index)` - Delete content from range
- `docs_update_table_cell(document_id, table_start_index, row, column, text)` - Write to table cell
- `docs_add_bookmark(document_id, index, bookmark_name)` - Add named bookmark

### Sheets Tools (8 tools)
- `sheets_create(title, parent_id, drive_id)` - Create spreadsheets
- `sheets_read(spreadsheet_id, range_name)` - Read cell data
- `sheets_write(spreadsheet_id, range_name, values)` - Write/update cells
- `sheets_append(spreadsheet_id, range_name, values)` - Append rows
- `sheets_clear(spreadsheet_id, range_name)` - Clear range data
- `sheets_get_metadata(spreadsheet_id)` - Get spreadsheet metadata
- `sheets_create_sheet_tab(spreadsheet_id, sheet_name)` - Add new sheet tab
- `sheets_format_cells(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, bold, background_color, text_color)` - Format cells

### Slides Tools (12 tools)
- `slides_create(title, parent_id, drive_id)` - Create presentations
- `slides_get_details(presentation_id)` - Get presentation details
- `slides_read(presentation_id)` - Read all text content
- `slides_add_slide(presentation_id, index)` - Add new slide
- `slides_add_text(presentation_id, slide_id, text, x, y, width, height)` - Add text box to slide
- `slides_delete_slide(presentation_id, slide_id)` - Delete slide
- `slides_insert_image(presentation_id, slide_id, image_url, x, y, width, height)` - Insert image from URL
- `slides_replace_text(presentation_id, find_text, replace_text, match_case)` - Find and replace text across all slides
- `slides_format_text(presentation_id, slide_id, shape_id, start_index, end_index, bold, italic, font_size, foreground_color)` - Format text in shape
- `slides_add_shape(presentation_id, slide_id, shape_type, x, y, width, height)` - Add shape (RECTANGLE, ELLIPSE, TRIANGLE, ARROW, etc.)
- `slides_duplicate_slide(presentation_id, slide_id, index)` - Duplicate a slide
- `slides_add_speaker_notes(presentation_id, slide_id, notes)` - Add/update speaker notes

### Forms Tools (5 tools)
- `forms_create(title, description)` - Create new forms
- `forms_get(form_id)` - Get form structure and questions
- `forms_add_text_question(form_id, question_text, required)` - Add text questions
- `forms_add_multiple_choice(form_id, question_text, options, required)` - Add choice questions
- `forms_list_responses(form_id)` - Get all form responses

### Calendar Tools (4 tools)
- `calendar_list_events(max_results, time_min)` - List upcoming events
- `calendar_create_event(summary, start_time, end_time, description, location, attendees)` - Create events
- `calendar_update_event(event_id, summary, start_time, end_time, description, location, attendees)` - Update events
- `calendar_delete_event(event_id)` - Delete events

### Tasks Tools (4 tools)
- `tasks_list(task_list_id, max_results)` - List tasks
- `tasks_create(title, notes, task_list_id)` - Create new tasks
- `tasks_complete(task_id, task_list_id)` - Mark tasks as done
- `tasks_delete(task_id, task_list_id)` - Delete tasks

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
