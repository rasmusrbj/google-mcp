# Google Workspace MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing **full Google Workspace integration** with **complete shared drive support**.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why This Server?

Most Google Drive MCP servers have limited or no shared drive (Team Drive) support. This server provides:

✅ **Full Shared Drive Support** - Create, read, and manage files in shared drives
✅ **Complete Google Workspace** - Gmail, Drive, Docs, Sheets, Slides, Forms, Chat, Calendar, Tasks
✅ **223 Production-Ready Tools** - Comprehensive coverage of all services
✅ **Simple Setup** - Automated installation and authentication
✅ **Production Ready** - Proper error handling and token refresh

## Features

### 📧 Gmail (41 tools) - NOW WITH FILTERS & AUTO-REPLY!
- **Search** emails with advanced Gmail queries
- **Read** full message content with headers and body
- **Send** emails with CC support
- **Send with attachments** - Attach files to emails
- **Reply** to email threads
- **Forward** emails to other recipients
- **Mark as read/unread**
- **Star/unstar** emails - Mark favorites
- **Mark as important/not important**
- **Archive** emails
- **Move to inbox** - Unarchive emails
- **Delete** emails (move to trash)
- **Untrash** - Restore from trash
- **Permanently delete** - Delete forever
- **Get attachments** - Download email attachments
- **Add/remove labels** - Apply custom labels
- **List labels** - View all system and custom labels
- **Create custom labels**
- **Delete custom labels**
- **List threads** - Browse email conversations
- **Get thread** - Read entire conversation
- **Batch modify** - Apply changes to multiple messages
- **Batch delete** - Delete multiple messages at once
- **List drafts** - View all draft emails
- **Create draft** - Save email as draft
- **Get draft** - **NEW!** Read draft details
- **Update draft** - **NEW!** Modify existing drafts
- **Send draft** - Send a saved draft
- **Delete draft** - Remove draft
- **List filters** - **NEW!** View all email filters/rules
- **Create filter** - **NEW!** Create automatic email rules (auto-label, archive, forward, etc.)
- **Delete filter** - **NEW!** Remove filters
- **Get vacation settings** - **NEW!** Check auto-reply status
- **Set vacation responder** - **NEW!** Enable/disable out-of-office auto-reply
- **Get profile** - **NEW!** Get email address and account info
- Full thread support

💡 **New automation features**: Create filters to automatically organize incoming emails, and enable vacation responder for out-of-office auto-replies!

### 📁 Google Drive (52 tools) - **Full Shared Drives Support!**
- **List all shared drives** you have access to
- **List files** in any folder (My Drive or Shared Drives)
- **Create folders** in My Drive or Shared Drives
- **Upload files** to any location including Shared Drives
- **Download files** to local filesystem (exports Google Docs as DOCX, Sheets as XLSX, etc.)
- **Delete** files and folders
- **Copy** files
- **Move** files between folders
- **Rename** files and folders
- **Share** files with specific users (reader, writer, commenter roles)
- **List permissions** - See who has access to files
- **Remove permissions** - Unshare/revoke access
- **Update permission roles** - Change reader to writer, etc.
- **Transfer ownership** - Transfer file ownership to another user
- **Set permission expiration** - Time-limited access
- **Make files public** - Share with anyone who has the link
- **Update file description** and metadata
- **Star/unstar files** - Mark favorites
- **Get file metadata** with detailed information
- **Search files** with advanced query syntax
- **Add to folder** - Add file to folder without removing from others
- **Remove from folder** - Remove from folder, keep in others
- **List parent folders** - See all folders containing a file
- **Create comments** on files
- **List comments** on files
- **Reply to comments**
- **Delete comments**
- **Resolve/unresolve comments**
- **List trashed files** - Browse trash
- **Restore files** from trash
- **Empty trash** - Permanently delete all trashed files
- **Export files** to multiple formats (PDF, DOCX, XLSX, CSV, HTML, etc.)
- **Create shortcuts** to files/folders
- **List file revisions** - View version history
- **Get specific revision** details
- **Update revision** - Keep forever or allow cleanup
- **Delete revision** from history
- **Download specific revision**
- **Create shared drives** - Create new Team Drives
- **Update shared drives** - Change name or restrictions
- **Delete shared drives**
- **Hide/unhide shared drives**
- **Set custom properties** - Key-value metadata
- **Get custom properties**
- **Set app properties** - App-specific metadata
- **Set content restrictions** - Read-only mode
- **List recent changes** - Track Drive activity
- **Get Drive info** - Storage quota, user info, limits
- **Batch get metadata** - Multiple files at once
- **Batch delete** - Delete multiple files at once
- Works seamlessly with both My Drive and Team Drives

### 📝 Google Docs (38 tools)
- **Create** documents in My Drive or Shared Drives
- **Read** full document content
- **Append** text to existing documents
- **Insert** text at specific positions
- **Replace** text (find and replace)
- **Format text** - Bold, italic, underline, strikethrough, font size, font family, text color, background color, small caps, superscript/subscript
- **Insert tables** into documents
- **Insert table row/column** - Add rows or columns to existing tables
- **Delete table row/column** - Remove rows or columns
- **Delete table** - Remove entire table
- **Merge/unmerge table cells**
- **Format table cells** - Background colors and borders
- **Update table cells** with text
- **Insert images** from URLs
- **Add hyperlinks** to text
- **Create bulleted lists**
- **Create numbered lists**
- **Set heading styles** (H1-H6, Title, Subtitle, Normal)
- **Set paragraph alignment** - Left, center, right, justified
- **Set indentation** - First line, start, end indentation
- **Set line spacing** - Single, double, custom spacing
- **Set spacing before/after** paragraphs
- **Set text direction** - LTR or RTL
- **Add page breaks**
- **Insert table of contents** - Auto-generated from headings
- **Insert section breaks** - Continuous or next page
- **Insert horizontal rules**
- **Create/update headers** - Document headers
- **Create/update footers** - Document footers
- **Insert footnotes** with text
- **Get document structure** - Headings, tables, images overview
- **Delete content** from ranges
- **Add bookmarks** for internal linking
- **Create named ranges** - Reference text selections
- **Delete named ranges**
- Full shared drive support

### 📊 Google Sheets (38 tools)
- **Create** spreadsheets in any location
- **Read** data from any range
- **Write** data to specific cells/ranges
- **Append** rows to existing sheets
- **Clear** data from ranges
- **Get metadata** (sheet names, IDs, properties)
- **Create sheet tabs** in existing spreadsheets
- **Format cells** (bold, colors, etc.)
- **Delete sheet tabs**
- **Rename sheet tabs**
- **Duplicate sheet tabs**
- **Move sheet tabs** - Reorder sheet position
- **Hide/show sheet tabs**
- **Copy sheet to another spreadsheet**
- **Insert rows/columns** - Add blank rows or columns
- **Delete rows/columns** - Remove specific rows or columns
- **Resize rows/columns** - Set custom heights and widths
- **Auto-resize columns** - Fit columns to content
- **Hide/show rows/columns**
- **Merge cells** - Combine cells in various ways
- **Unmerge cells**
- **Add borders** - Cell borders with styles and colors
- **Set number formats** - Currency, percent, date, time, etc.
- **Data validation** - Dropdown lists and validation rules
- **Copy/paste ranges** - Copy values, formats, or formulas
- **Find and replace** - Search and replace text
- **Sort ranges** - Sort data by columns
- **Freeze rows/columns** - Freeze panes for scrolling
- **Named ranges** - Create and manage named ranges
- **Conditional formatting** - Rules with colors and conditions
- **Add notes** - Cell comments and notes
- **Protect ranges** - Lock cells from editing
- **Create charts** - Column, bar, line, pie, area, scatter
- **Create filters** - Add filter views
- Formula support via USER_ENTERED mode

### 🎨 Google Slides (14 tools) - NOW WITH PROFESSIONAL LAYOUTS!
- **List layouts** - View all available slide templates (title slide, bullet points, two columns, etc.)
- **Add slides with layouts** - Use predefined layouts instead of blank slides for professional design
- **Insert text in placeholders** - Fill layout placeholders automatically (no manual positioning!)
- **Create** presentations in My Drive or Shared Drives
- **Get details** about presentations (slide count, structure)
- **Read** all text content from presentations
- **Add text** boxes with manual positioning
- **Delete** slides from presentations
- **Insert images** from URLs
- **Replace text** across all slides (template automation!)
- **Format text** in slides (bold, italic, font size, color)
- **Add shapes** (rectangles, ellipses, arrows, etc.)
- **Duplicate slides**
- **Add speaker notes** to slides
- Full shared drive support

💡 **For beautiful slides**: Use `slides_list_layouts()` to see available layouts, then create slides with `slides_add_slide(layout_name="Title Slide")` and fill them using `slides_insert_text_in_placeholder()`. This gives you professional design automatically!

### 📋 Google Forms (13 tools)
- **Create** new forms
- **Get** form details and questions
- **Add text questions** (short answer)
- **Add paragraph text** questions (long-form)
- **Add multiple choice** questions
- **Add checkbox** questions (multiple selections)
- **Add dropdown** questions
- **Add scale questions** (1-5 ratings, linear scale)
- **Add date questions** with optional year
- **Add time questions** (time of day or duration)
- **Update form settings** (title, description, quiz mode)
- **Delete questions** by index
- **Get specific response** with detailed answers
- **List all responses** with answer data

### 💬 Google Chat (14 tools)
- **List spaces** - View all Chat rooms and DMs
- **Get space** details
- **Create spaces** - New Chat rooms
- **Update spaces** - Change name or description
- **Delete spaces**
- **Send messages** to spaces with threading support
- **List messages** in a space
- **Get message** details
- **Update messages** - Edit sent messages
- **Delete messages**
- **List members** in a space
- **Add members** to spaces
- **Remove members** from spaces
- **Create reactions** - Add emoji reactions to messages
- **List reactions** on messages
- **Delete reactions**

### 📅 Google Calendar (6 tools)
- **List calendars** - View all available calendars
- **List events** - Advanced filtering (time range, search query, multi-calendar)
- **Get event** - View detailed event information
- **Create events** - Full customization (reminders, colors, visibility, transparency, all-day events, timezones)
- **Update events** - Modify any aspect of existing events
- **Delete events** - Remove events from calendar

### ✅ Google Tasks (7 tools)
- **List task lists** - View all your to-do lists
- **List tasks** - Advanced filtering (completed, deleted, hidden, date ranges)
- **Get task** - View details of a specific task
- **Create** tasks with due dates, notes, subtasks, and positioning
- **Update** tasks - Modify title, notes, status, due date
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
- [Google Chat API](https://console.cloud.google.com/apis/library/chat.googleapis.com)
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

## Available Tools (223 Tools Total)

### Gmail Tools (41 tools)
- `gmail_search(query, max_results)` - Search emails with Gmail query syntax
- `gmail_read(message_id)` - Read full email content
- `gmail_send(to, subject, body, cc)` - Send new emails
- `gmail_send_with_attachment(to, subject, body, attachment_path, cc)` - Send with file attachment
- `gmail_reply(message_id, body)` - Reply to email threads
- `gmail_forward(message_id, to, comment)` - Forward email to another recipient
- `gmail_mark_read(message_id)` - Mark email as read
- `gmail_mark_unread(message_id)` - Mark email as unread
- `gmail_star(message_id)` - Star email
- `gmail_unstar(message_id)` - Unstar email
- `gmail_mark_important(message_id)` - Mark as important
- `gmail_mark_not_important(message_id)` - Mark as not important
- `gmail_archive(message_id)` - Archive email (remove from inbox)
- `gmail_move_to_inbox(message_id)` - Move to inbox (unarchive)
- `gmail_delete(message_id)` - Move email to trash
- `gmail_untrash(message_id)` - Restore from trash
- `gmail_permanently_delete(message_id)` - Delete forever
- `gmail_get_attachment(message_id, attachment_id, destination_path)` - Download attachment
- `gmail_add_label(message_id, label_id)` - Add label to email
- `gmail_remove_label(message_id, label_id)` - Remove label from email
- `gmail_list_labels()` - List all system and custom labels
- `gmail_create_label(name)` - Create custom label
- `gmail_delete_label(label_id)` - Delete custom label
- `gmail_list_threads(query, max_results)` - List email threads/conversations
- `gmail_get_thread(thread_id)` - Read entire thread with all messages
- `gmail_batch_modify(message_ids, add_labels, remove_labels)` - Modify multiple messages
- `gmail_batch_delete(message_ids)` - Permanently delete multiple messages
- `gmail_list_drafts(max_results)` - List all draft emails
- `gmail_create_draft(to, subject, body, cc)` - Create draft email
- `gmail_get_draft(draft_id)` - **NEW!** Read draft details
- `gmail_update_draft(draft_id, to, subject, body, cc)` - **NEW!** Modify existing draft
- `gmail_send_draft(draft_id)` - Send a saved draft
- `gmail_delete_draft(draft_id)` - Delete draft
- `gmail_list_filters()` - **NEW!** List all email filters/rules
- `gmail_create_filter(criteria_from, criteria_to, criteria_subject, criteria_query, criteria_has_attachment, action_add_labels, action_remove_labels, action_forward, action_mark_read, action_archive, action_star, action_trash, action_mark_important)` - **NEW!** Create automatic email filter
- `gmail_delete_filter(filter_id)` - **NEW!** Delete email filter
- `gmail_get_vacation_settings()` - **NEW!** Get vacation responder status
- `gmail_set_vacation_responder(enable, response_subject, response_body, start_date, end_date, restrict_to_contacts, restrict_to_domain)` - **NEW!** Enable/disable auto-reply
- `gmail_get_profile()` - **NEW!** Get email address and account info

### Drive Tools (52 tools)
- `drive_list_shared_drives(page_size)` - List all shared drives you have access to
- `drive_list_files(folder_id, drive_id, query, page_size)` - List files in folders
- `drive_create_folder(name, parent_id, drive_id)` - Create folders anywhere
- `drive_upload_file(file_path, name, parent_id, drive_id)` - Upload files
- `drive_download_file(file_id, destination_path, drive_id)` - Download files to local filesystem
- `drive_delete_file(file_id, drive_id)` - Delete files/folders
- `drive_copy_file(file_id, new_name, parent_id, drive_id)` - Copy files
- `drive_move_file(file_id, new_parent_id, drive_id)` - Move files between folders
- `drive_rename_file(file_id, new_name, drive_id)` - Rename files/folders
- `drive_share_file(file_id, email, role, drive_id)` - Share with users
- `drive_list_permissions(file_id, drive_id)` - List who has access to a file
- `drive_remove_permission(file_id, permission_id, drive_id)` - Remove/revoke access
- `drive_update_permission(file_id, permission_id, role, drive_id)` - Update permission role (reader to writer, etc.)
- `drive_transfer_ownership(file_id, new_owner_email, drive_id)` - Transfer ownership to another user
- `drive_set_permission_expiration(file_id, permission_id, expiration_time, drive_id)` - Set time-limited access
- `drive_make_public(file_id, role, drive_id)` - Make file accessible to anyone with link
- `drive_update_description(file_id, description, drive_id)` - Update file description
- `drive_star_file(file_id, starred, drive_id)` - Star/unstar files (favorites)
- `drive_get_file_metadata(file_id, drive_id)` - Get detailed file information
- `drive_search_files(query, drive_id, page_size)` - Advanced file search
- `drive_add_to_folder(file_id, folder_id, drive_id)` - Add file to folder without removing from others
- `drive_remove_from_folder(file_id, folder_id, drive_id)` - Remove file from folder, keep in others
- `drive_list_parents(file_id, drive_id)` - List all parent folders of a file
- `drive_create_comment(file_id, content, drive_id)` - Create comment on file
- `drive_list_comments(file_id, drive_id)` - List all comments on file
- `drive_reply_to_comment(file_id, comment_id, content, drive_id)` - Reply to comment
- `drive_delete_comment(file_id, comment_id, drive_id)` - Delete comment
- `drive_resolve_comment(file_id, comment_id, resolved, drive_id)` - Resolve or unresolve comment
- `drive_list_trashed_files(page_size)` - List files in trash
- `drive_restore_file(file_id, drive_id)` - Restore file from trash
- `drive_empty_trash()` - Permanently delete all trashed files
- `drive_export_file(file_id, destination_path, export_format)` - Export to PDF, DOCX, XLSX, CSV, etc.
- `drive_create_shortcut(name, target_file_id, parent_id, drive_id)` - Create shortcut to file
- `drive_list_revisions(file_id)` - List file revision history
- `drive_get_revision(file_id, revision_id)` - Get specific revision details
- `drive_update_revision(file_id, revision_id, keep_forever)` - Keep revision forever or allow cleanup
- `drive_delete_revision(file_id, revision_id)` - Delete revision from history
- `drive_download_revision(file_id, revision_id, destination_path)` - Download specific revision
- `drive_create_shared_drive(name)` - Create new shared drive (Team Drive)
- `drive_update_shared_drive(drive_id, name, restrict_downloads)` - Update shared drive settings
- `drive_delete_shared_drive(drive_id)` - Delete shared drive
- `drive_hide_shared_drive(drive_id, hidden)` - Hide or unhide shared drive
- `drive_set_custom_properties(file_id, properties, drive_id)` - Set custom key-value metadata
- `drive_get_custom_properties(file_id, drive_id)` - Get custom properties
- `drive_set_app_properties(file_id, properties, drive_id)` - Set app-specific properties
- `drive_set_content_restrictions(file_id, read_only, reason, drive_id)` - Set read-only mode
- `drive_list_changes(page_token, drive_id, page_size)` - List recent changes in Drive
- `drive_get_about()` - Get Drive info (storage quota, user info, limits)
- `drive_batch_get_metadata(file_ids, drive_id)` - Get metadata for multiple files
- `drive_batch_delete(file_ids, drive_id)` - Delete multiple files at once

### Docs Tools (38 tools)
- `docs_create(title, parent_id, drive_id)` - Create documents
- `docs_read(document_id)` - Read document content
- `docs_append_text(document_id, text)` - Append text
- `docs_insert_text(document_id, text, index)` - Insert text at position
- `docs_replace_text(document_id, find_text, replace_text, match_case)` - Find and replace
- `docs_format_text(document_id, start_index, end_index, bold, italic, underline, strikethrough, font_size, font_family, text_color, background_color, small_caps, baseline_offset)` - Format text with all options
- `docs_insert_table(document_id, rows, columns, index)` - Insert table
- `docs_insert_table_row(document_id, table_start_index, row_index, insert_below)` - Insert table row
- `docs_insert_table_column(document_id, table_start_index, column_index, insert_right)` - Insert table column
- `docs_delete_table_row(document_id, table_start_index, row_index)` - Delete table row
- `docs_delete_table_column(document_id, table_start_index, column_index)` - Delete table column
- `docs_delete_table(document_id, table_start_index)` - Delete entire table
- `docs_merge_table_cells(document_id, table_start_index, start_row, end_row, start_col, end_col)` - Merge table cells
- `docs_unmerge_table_cells(document_id, table_start_index, row, col)` - Unmerge table cells
- `docs_format_table_cells(document_id, table_start_index, start_row, end_row, start_col, end_col, background_color, border_width, border_color)` - Format table cells
- `docs_update_table_cell(document_id, table_start_index, row, column, text)` - Write to table cell
- `docs_insert_image(document_id, image_url, index, width, height)` - Insert image from URL
- `docs_add_hyperlink(document_id, start_index, end_index, url)` - Add hyperlink to text
- `docs_create_bulleted_list(document_id, start_index, end_index)` - Create bulleted list
- `docs_create_numbered_list(document_id, start_index, end_index)` - Create numbered list
- `docs_set_heading_style(document_id, start_index, end_index, heading_level)` - Set heading style (H1-H6, TITLE, SUBTITLE, NORMAL_TEXT)
- `docs_set_paragraph_alignment(document_id, start_index, end_index, alignment)` - Set alignment (START, CENTER, END, JUSTIFIED)
- `docs_set_indentation(document_id, start_index, end_index, start_indent, end_indent, first_line_indent)` - Set paragraph indentation
- `docs_set_line_spacing(document_id, start_index, end_index, line_spacing)` - Set line spacing percentage
- `docs_set_spacing_before_after(document_id, start_index, end_index, space_above, space_below)` - Set paragraph spacing
- `docs_set_text_direction(document_id, start_index, end_index, direction)` - Set text direction (LTR/RTL)
- `docs_add_page_break(document_id, index)` - Insert page break
- `docs_insert_table_of_contents(document_id, index)` - Insert table of contents
- `docs_insert_section_break(document_id, index, section_type)` - Insert section break
- `docs_insert_horizontal_rule(document_id, index)` - Insert horizontal rule
- `docs_create_header(document_id, text, section_index)` - Create/update header
- `docs_create_footer(document_id, text, section_index)` - Create/update footer
- `docs_insert_footnote(document_id, index, footnote_text)` - Insert footnote
- `docs_get_structure(document_id)` - Get document structure overview
- `docs_delete_content(document_id, start_index, end_index)` - Delete content from range
- `docs_add_bookmark(document_id, index, bookmark_name)` - Add named bookmark
- `docs_create_named_range(document_id, range_name, start_index, end_index)` - Create named range
- `docs_delete_named_range(document_id, range_id)` - Delete named range

### Sheets Tools (38 tools)
- `sheets_create(title, parent_id, drive_id)` - Create spreadsheets
- `sheets_read(spreadsheet_id, range_name)` - Read cell data
- `sheets_write(spreadsheet_id, range_name, values)` - Write/update cells
- `sheets_append(spreadsheet_id, range_name, values)` - Append rows
- `sheets_clear(spreadsheet_id, range_name)` - Clear range data
- `sheets_get_metadata(spreadsheet_id)` - Get spreadsheet metadata
- `sheets_create_sheet_tab(spreadsheet_id, sheet_name)` - Add new sheet tab
- `sheets_format_cells(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, bold, background_color, text_color)` - Format cells
- `sheets_delete_sheet_tab(spreadsheet_id, sheet_id)` - Delete sheet tab
- `sheets_rename_sheet_tab(spreadsheet_id, sheet_id, new_name)` - Rename sheet tab
- `sheets_duplicate_sheet_tab(spreadsheet_id, sheet_id, new_sheet_name)` - Duplicate sheet tab
- `sheets_move_sheet_tab(spreadsheet_id, sheet_id, new_index)` - Move sheet to new position
- `sheets_hide_sheet_tab(spreadsheet_id, sheet_id, hidden)` - Hide or show sheet tab
- `sheets_copy_to_spreadsheet(source_spreadsheet_id, sheet_id, destination_spreadsheet_id)` - Copy sheet to another spreadsheet
- `sheets_insert_rows(spreadsheet_id, sheet_id, start_index, num_rows)` - Insert blank rows
- `sheets_insert_columns(spreadsheet_id, sheet_id, start_index, num_columns)` - Insert blank columns
- `sheets_delete_rows(spreadsheet_id, sheet_id, start_index, end_index)` - Delete rows
- `sheets_delete_columns(spreadsheet_id, sheet_id, start_index, end_index)` - Delete columns
- `sheets_resize_rows(spreadsheet_id, sheet_id, start_index, end_index, pixel_size)` - Set row height
- `sheets_resize_columns(spreadsheet_id, sheet_id, start_index, end_index, pixel_size)` - Set column width
- `sheets_auto_resize_columns(spreadsheet_id, sheet_id, start_index, end_index)` - Auto-resize columns to fit content
- `sheets_hide_rows(spreadsheet_id, sheet_id, start_index, end_index, hidden)` - Hide or show rows
- `sheets_hide_columns(spreadsheet_id, sheet_id, start_index, end_index, hidden)` - Hide or show columns
- `sheets_merge_cells(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, merge_type)` - Merge cells
- `sheets_unmerge_cells(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col)` - Unmerge cells
- `sheets_add_borders(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, border_style, border_color)` - Add cell borders
- `sheets_set_number_format(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, format_type)` - Set number format (CURRENCY, PERCENT, DATE, etc.)
- `sheets_add_data_validation(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, values, strict)` - Add dropdown validation
- `sheets_copy_paste(spreadsheet_id, source_sheet_id, source_start_row, source_end_row, source_start_col, source_end_col, dest_sheet_id, dest_start_row, dest_start_col, paste_type)` - Copy and paste cells
- `sheets_find_replace(spreadsheet_id, sheet_id, find, replacement, match_case, match_entire_cell)` - Find and replace text
- `sheets_sort_range(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, sort_col_index, ascending)` - Sort range by column
- `sheets_freeze_rows_columns(spreadsheet_id, sheet_id, frozen_row_count, frozen_column_count)` - Freeze rows/columns
- `sheets_create_named_range(spreadsheet_id, range_name, sheet_id, start_row, end_row, start_col, end_col)` - Create named range
- `sheets_add_conditional_format(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, condition_type, condition_value, background_color)` - Add conditional formatting
- `sheets_add_note(spreadsheet_id, sheet_id, row, col, note)` - Add note to cell
- `sheets_protect_range(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col, description, warning_only)` - Protect range from editing
- `sheets_create_chart(spreadsheet_id, sheet_id, chart_type, data_start_row, data_end_row, data_start_col, data_end_col, position_row, position_col)` - Create chart
- `sheets_create_filter(spreadsheet_id, sheet_id, start_row, end_row, start_col, end_col)` - Create filter view

### Slides Tools (14 tools)
- `slides_create(title, parent_id, drive_id)` - Create presentations
- `slides_get_details(presentation_id)` - Get presentation details
- `slides_list_layouts(presentation_id)` - **NEW!** List available slide layouts for professional design
- `slides_read(presentation_id)` - Read all text content
- `slides_add_slide(presentation_id, index, layout_id, layout_name)` - **ENHANCED!** Add slide with optional layout
- `slides_insert_text_in_placeholder(presentation_id, slide_id, text, placeholder_type, placeholder_index)` - **NEW!** Insert text in layout placeholders (recommended!)
- `slides_add_text(presentation_id, slide_id, text, x, y, width, height)` - Add text box with manual positioning
- `slides_delete_slide(presentation_id, slide_id)` - Delete slide
- `slides_insert_image(presentation_id, slide_id, image_url, x, y, width, height)` - Insert image from URL
- `slides_replace_text(presentation_id, find_text, replace_text, match_case)` - Find and replace text across all slides
- `slides_format_text(presentation_id, slide_id, shape_id, start_index, end_index, bold, italic, font_size, foreground_color)` - Format text in shape
- `slides_add_shape(presentation_id, slide_id, shape_type, x, y, width, height)` - Add shape (RECTANGLE, ELLIPSE, TRIANGLE, ARROW, etc.)
- `slides_duplicate_slide(presentation_id, slide_id, index)` - Duplicate a slide
- `slides_add_speaker_notes(presentation_id, slide_id, notes)` - Add/update speaker notes

### Forms Tools (13 tools)
- `forms_create(title, description)` - Create new forms
- `forms_get(form_id)` - Get form structure and questions
- `forms_add_text_question(form_id, question_text, required)` - Add short text questions
- `forms_add_paragraph_text(form_id, question_text, required)` - Add paragraph text questions
- `forms_add_multiple_choice(form_id, question_text, options, required)` - Add multiple choice questions
- `forms_add_checkbox(form_id, question_text, options, required)` - Add checkbox questions (multiple selections)
- `forms_add_dropdown(form_id, question_text, options, required)` - Add dropdown questions
- `forms_add_scale(form_id, question_text, low, high, low_label, high_label, required)` - Add linear scale questions (1-5, etc.)
- `forms_add_date(form_id, question_text, include_year, required)` - Add date questions
- `forms_add_time(form_id, question_text, duration, required)` - Add time questions (time of day or duration)
- `forms_update_settings(form_id, title, description, collect_email, allow_response_edits, quiz_mode)` - Update form settings
- `forms_delete_question(form_id, question_index)` - Delete question by index
- `forms_get_response(form_id, response_id)` - Get specific response with detailed answers
- `forms_list_responses(form_id)` - Get all form responses

### Chat Tools (14 tools)
- `chat_list_spaces(page_size)` - List all Chat spaces (rooms and DMs)
- `chat_get_space(space_id)` - Get space details
- `chat_create_space(display_name, space_type)` - Create new Chat room
- `chat_update_space(space_id, display_name, description)` - Update space name/description
- `chat_delete_space(space_id)` - Delete space
- `chat_send_message(space_id, text, thread_key)` - Send message to space with threading
- `chat_list_messages(space_id, page_size)` - List messages in space
- `chat_get_message(message_id)` - Get message details
- `chat_update_message(message_id, text)` - Edit a message
- `chat_delete_message(message_id)` - Delete message
- `chat_list_members(space_id, page_size)` - List members in space
- `chat_add_member(space_id, user_email)` - Add member to space
- `chat_remove_member(membership_id)` - Remove member from space
- `chat_create_reaction(message_id, emoji)` - Add emoji reaction to message
- `chat_list_reactions(message_id)` - List reactions on message
- `chat_delete_reaction(reaction_id)` - Delete reaction

### Calendar Tools (6 tools)
- `calendar_list_calendars()` - List all available calendars
- `calendar_list_events(calendar_id, max_results, time_min, time_max, query)` - List events with filtering
- `calendar_get_event(event_id, calendar_id)` - Get detailed event information
- `calendar_create_event(summary, start_time, end_time, calendar_id, description, location, attendees, timezone, color_id, visibility, transparency, reminders, use_default_reminders)` - Create events with full customization
- `calendar_update_event(event_id, calendar_id, summary, start_time, end_time, description, location, attendees, timezone, color_id, visibility, transparency, reminders, use_default_reminders)` - Update events
- `calendar_delete_event(event_id, calendar_id)` - Delete events

### Tasks Tools (7 tools)
- `tasks_list_task_lists(max_results)` - List all task lists
- `tasks_list(task_list_id, max_results, show_completed, show_deleted, show_hidden, completed_min, completed_max, due_min, due_max, updated_min)` - List tasks with advanced filtering
- `tasks_get(task_id, task_list_id)` - Get details of a specific task
- `tasks_create(title, notes, due, parent, previous, task_list_id)` - Create tasks with due dates, subtasks, and positioning
- `tasks_update(task_id, task_list_id, title, notes, status, due)` - Update existing tasks
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
