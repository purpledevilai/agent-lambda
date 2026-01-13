# Outlook Integration

## Overview

The Outlook integration allows agents to read, send, and manage emails on behalf of users through Microsoft's Graph API. This is accomplished through OAuth 2.0 authentication with Microsoft Entra (Azure Active Directory).

## Setup

### 1. Azure App Registration

Before using the Outlook integration, you need to register an application in Microsoft Entra:

1. **Create an App Registration**
   - Go to [Microsoft Entra Admin Center](https://entra.microsoft.com/)
   - Navigate to "Identity" > "Applications" > "App registrations"
   - Click "New registration"

2. **Configure App Registration**
   - **Name**: Choose a name (e.g., "Ajentify Outlook Integration")
   - **Supported account types**: Choose based on your needs:
     - "Accounts in any organizational directory and personal Microsoft accounts" for broadest access
     - "Accounts in this organizational directory only" for single-tenant
   - **Redirect URI**: Select "Web" and enter your callback URL (e.g., `https://yourapp.com/outlook/callback`)

3. **Obtain Client Credentials**
   - After registration, note the **Application (client) ID** from the overview page
   - Go to "Certificates & secrets" > "New client secret"
   - Create a secret and copy the **Value** immediately (it won't be shown again)

4. **Configure API Permissions**
   - Go to "API Permissions" > "Add a permission"
   - Select "Microsoft Graph" > "Delegated permissions"
   - Add these permissions:
     - `Mail.ReadWrite`
     - `Mail.Send`
     - `User.Read`
     - `offline_access` (for refresh tokens)
   - Click "Grant admin consent" for your organization

### 2. Environment Variables

Add these environment variables to your Lambda:

```bash
OUTLOOK_CLIENT_ID=your-client-id
OUTLOOK_CLIENT_SECRET=your-client-secret
OUTLOOK_REDIRECT_URI=https://yourapp.com/outlook/callback
```

## OAuth Flow

### Step 1: Get Authorization URL

```bash
GET /outlook/auth-url
Authorization: Bearer <user_token>
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with
- `state` (optional): State parameter to pass through OAuth flow

**Response:**
```json
{
  "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id=..."
}
```

Redirect the user to this URL. After authorization, Microsoft redirects back to your `OUTLOOK_REDIRECT_URI` with a `code` parameter.

### Step 2: Exchange Code for Tokens

```bash
POST /outlook/auth
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "code": "authorization_code_from_microsoft"
}
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with

**Response:**
```json
{
  "integration_id": "uuid-of-integration",
  "org_id": "org-uuid",
  "type": "outlook",
  "integration_config": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": 1234567890,
    "email": "user@outlook.com"
  },
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

Save the `integration_id` - this is what you'll pass to agents to use Outlook tools.

## Agent Tools

Once you have an Outlook integration, agents can use these tools. All tools require the `integration_id` parameter.

### Tool Reference Summary

| Tool ID | Description |
|---------|-------------|
| `list_outlook_emails` | List and search emails with OData filters |
| `get_outlook_email` | Get full content of a specific email |
| `send_outlook_email` | Send a new email directly |
| `set_outlook_email_read_status` | Mark email as read or unread |
| `create_outlook_draft` | Create a new draft email |
| `list_outlook_drafts` | List all draft emails |
| `get_outlook_draft` | Get full content of a draft |
| `update_outlook_draft` | Update an existing draft |
| `send_outlook_draft` | Send a draft email |
| `delete_outlook_draft` | Delete a draft without sending |
| `list_outlook_folders` | List all folders (system and custom) |
| `create_outlook_folder` | Create a new custom folder |
| `delete_outlook_folder` | Delete a custom folder |
| `move_outlook_email` | Move email to a different folder |
| `modify_outlook_email_categories` | Add or remove categories from an email |
| `archive_outlook_email` | Archive an email |
| `trash_outlook_email` | Move email to Deleted Items |
| `untrash_outlook_email` | Restore email from Deleted Items |
| `delete_outlook_email` | Permanently delete an email |

---

## Core Email Tools

### list_outlook_emails

List and search emails from the Outlook account with powerful filtering options.

**Tool ID:** `list_outlook_emails`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `folder` | string | No | Folder to filter by (inbox, drafts, sentitems, deleteditems, archive, junkemail) |
| `filter_query` | string | No | OData $filter query (see filter syntax below) |
| `search_query` | string | No | Full-text search query |
| `max_results` | int | No | Maximum emails to return (default 10, max 100) |

**Filter Query Examples (OData):**
- Unread: `isRead eq false`
- With attachments: `hasAttachments eq true`
- High importance: `importance eq 'high'`
- After date: `receivedDateTime ge 2024-01-01T00:00:00Z`
- Combine with `and`: `isRead eq false and hasAttachments eq true`

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "folder": "inbox",
  "filter_query": "isRead eq false",
  "max_results": 5
}
```

**Returns:**
```json
{
  "emails": [
    {
      "id": "message-id",
      "conversation_id": "conversation-id",
      "from": "sender@example.com",
      "from_name": "Sender Name",
      "to": "recipient@outlook.com",
      "subject": "Meeting Tomorrow",
      "received_date": "2024-01-01T10:00:00Z",
      "snippet": "Hi, just wanted to confirm...",
      "is_read": false,
      "is_draft": false,
      "has_attachments": false,
      "importance": "normal",
      "categories": [],
      "flag": "notFlagged"
    }
  ],
  "count": 1
}
```

---

### get_outlook_email

Get the full content of a specific email including the complete body text.

**Tool ID:** `get_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID from list_outlook_emails |

**Returns:**
```json
{
  "id": "message-id",
  "conversation_id": "conversation-id",
  "from": "sender@example.com",
  "from_name": "Sender Name",
  "to": ["recipient@outlook.com"],
  "cc": [],
  "subject": "Meeting Tomorrow",
  "received_date": "2024-01-01T10:00:00Z",
  "sent_date": "2024-01-01T09:59:30Z",
  "body": "Hi,\n\nJust wanted to confirm our meeting tomorrow at 2pm.\n\nBest,\nJohn",
  "body_type": "Text",
  "snippet": "Hi, just wanted to confirm...",
  "is_read": false,
  "is_draft": false,
  "has_attachments": false,
  "importance": "normal",
  "categories": [],
  "flag": "notFlagged",
  "parent_folder_id": "inbox-folder-id"
}
```

---

### send_outlook_email

Send an email directly from the connected Outlook account.

**Tool ID:** `send_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `to` | string | Yes | Recipient email address |
| `subject` | string | Yes | Email subject line |
| `body` | string | Yes | Email body content |
| `html` | bool | No | Set true if body is HTML (default false) |

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "to": "recipient@example.com",
  "subject": "Re: Meeting Tomorrow",
  "body": "Sounds great! See you at 2pm."
}
```

**Returns:**
```json
{
  "status": "sent",
  "to": "recipient@example.com",
  "subject": "Re: Meeting Tomorrow"
}
```

---

### set_outlook_email_read_status

Mark an email as read or unread using a single boolean parameter.

**Tool ID:** `set_outlook_email_read_status`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to modify |
| `mark_as_read` | bool | Yes | `true` to mark as read, `false` to mark as unread |

**Example (mark as read):**
```json
{
  "integration_id": "outlook-integration-uuid",
  "message_id": "message-id",
  "mark_as_read": true
}
```

**Returns:**
```json
{
  "status": "success",
  "message_id": "message-id",
  "action": "marked_as_read",
  "is_read": true
}
```

---

## Draft Tools

Draft tools allow creating, managing, and sending email drafts. Useful for composing emails that need review before sending.

### create_outlook_draft

Create a new draft email. All content fields are optional - you can create an empty draft and update it later.

**Tool ID:** `create_outlook_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `to` | string | No | Recipient email address |
| `subject` | string | No | Email subject line |
| `body` | string | No | Email body content |
| `html` | bool | No | Set true if body is HTML (default false) |

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "to": "recipient@example.com",
  "subject": "Project Proposal",
  "body": "Here is my proposal for the project..."
}
```

**Returns:**
```json
{
  "status": "created",
  "draft_id": "draft-id",
  "to": "recipient@example.com",
  "subject": "Project Proposal"
}
```

---

### list_outlook_drafts

List all draft emails in the account.

**Tool ID:** `list_outlook_drafts`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `max_results` | int | No | Maximum drafts to return (default 10, max 100) |

**Returns:**
```json
{
  "drafts": [
    {
      "draft_id": "draft-id",
      "to": "recipient@example.com",
      "subject": "Project Proposal",
      "snippet": "Here is my proposal...",
      "created_date": "2024-01-01T10:00:00Z",
      "last_modified": "2024-01-01T10:30:00Z"
    }
  ],
  "count": 1
}
```

---

### get_outlook_draft

Get the full content of a specific draft.

**Tool ID:** `get_outlook_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `draft_id` | string | Yes | The draft ID from list_outlook_drafts |

**Returns:**
```json
{
  "draft_id": "draft-id",
  "to": "recipient@example.com",
  "subject": "Project Proposal",
  "body": "Here is my proposal for the project...",
  "body_type": "Text",
  "snippet": "Here is my proposal...",
  "created_date": "2024-01-01T10:00:00Z",
  "last_modified": "2024-01-01T10:30:00Z",
  "categories": []
}
```

---

### update_outlook_draft

Update an existing draft. Only the fields you provide will be updated.

**Tool ID:** `update_outlook_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `draft_id` | string | Yes | The draft ID to update |
| `to` | string | No | Recipient email address |
| `subject` | string | No | Email subject line |
| `body` | string | No | Email body content |
| `html` | bool | No | Set true if body is HTML (default false) |

**Returns:**
```json
{
  "status": "updated",
  "draft_id": "draft-id",
  "to": "recipient@example.com",
  "subject": "Updated Subject"
}
```

---

### send_outlook_draft

Send an existing draft. The draft must have a recipient (`to` address) to be sent. This removes the draft from the drafts folder.

**Tool ID:** `send_outlook_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `draft_id` | string | Yes | The draft ID to send |

**Returns:**
```json
{
  "status": "sent",
  "draft_id": "draft-id"
}
```

---

### delete_outlook_draft

Delete a draft permanently without sending it.

**Tool ID:** `delete_outlook_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `draft_id` | string | Yes | The draft ID to delete |

**Returns:**
```json
{
  "status": "deleted",
  "draft_id": "draft-id"
}
```

---

## Folder Tools

Outlook uses a folder-based system where each email exists in exactly one folder. This is different from Gmail's label system where an email can have multiple labels.

### list_outlook_folders

List all folders in the Outlook account, including system folders and user-created folders.

**Tool ID:** `list_outlook_folders`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |

**Returns:**
```json
{
  "system_folders": [
    {"id": "inbox-id", "name": "Inbox", "type": "system", "unread_count": 5, "total_count": 100},
    {"id": "sent-id", "name": "Sent Items", "type": "system", "unread_count": 0, "total_count": 50},
    {"id": "deleted-id", "name": "Deleted Items", "type": "system", "unread_count": 0, "total_count": 10}
  ],
  "user_folders": [
    {"id": "folder-123", "name": "Work Projects", "type": "user", "unread_count": 2, "total_count": 25}
  ],
  "total_count": 4
}
```

---

### create_outlook_folder

Create a new custom folder.

**Tool ID:** `create_outlook_folder`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `name` | string | Yes | Display name for the folder |
| `parent_folder_id` | string | No | Parent folder ID for creating subfolders |

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "name": "Important Projects"
}
```

**Returns:**
```json
{
  "status": "created",
  "folder_id": "folder-789",
  "name": "Important Projects",
  "parent_folder_id": null
}
```

---

### delete_outlook_folder

Delete a custom folder. System folders (Inbox, Sent Items, etc.) cannot be deleted.

**Tool ID:** `delete_outlook_folder`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `folder_id` | string | Yes | The folder ID to delete (from list_outlook_folders) |

**Returns:**
```json
{
  "status": "deleted",
  "folder_id": "folder-789"
}
```

---

### move_outlook_email

Move an email to a different folder.

**Tool ID:** `move_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to move |
| `destination_folder` | string | Yes | Folder ID or well-known name (inbox, archive, deleteditems, junkemail) |

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "message_id": "message-id",
  "destination_folder": "archive"
}
```

**Returns:**
```json
{
  "status": "moved",
  "message_id": "message-id",
  "destination_folder": "archive",
  "new_parent_folder_id": "archive-folder-id"
}
```

---

### modify_outlook_email_categories

Add or remove categories (colored tags) from an email. Categories in Outlook work similarly to Gmail labels - an email can have multiple categories.

**Tool ID:** `modify_outlook_email_categories`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to modify |
| `categories` | array | Yes | List of category names to set (empty list removes all) |

**Common preset categories:**
- Red category
- Orange category
- Yellow category
- Green category
- Blue category
- Purple category

**Example:**
```json
{
  "integration_id": "outlook-integration-uuid",
  "message_id": "message-id",
  "categories": ["Red category", "Work"]
}
```

**Returns:**
```json
{
  "status": "success",
  "message_id": "message-id",
  "categories": ["Red category", "Work"]
}
```

---

## Email Lifecycle Tools

Tools for archiving, trashing, and deleting emails.

### archive_outlook_email

Archive an email by moving it to the Archive folder.

**Tool ID:** `archive_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to archive |

**Returns:**
```json
{
  "status": "archived",
  "message_id": "message-id",
  "parent_folder_id": "archive-folder-id"
}
```

---

### trash_outlook_email

Move an email to the Deleted Items folder.

**Tool ID:** `trash_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to trash |

**Returns:**
```json
{
  "status": "trashed",
  "message_id": "message-id",
  "parent_folder_id": "deleteditems-folder-id"
}
```

---

### untrash_outlook_email

Restore an email from the Deleted Items folder back to the Inbox.

**Tool ID:** `untrash_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to restore |

**Returns:**
```json
{
  "status": "restored",
  "message_id": "message-id",
  "parent_folder_id": "inbox-folder-id"
}
```

---

### delete_outlook_email

**⚠️ WARNING: Permanently delete an email. This action is irreversible.**

Consider using `trash_outlook_email` instead, which allows recovery from Deleted Items.

**Tool ID:** `delete_outlook_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Outlook integration ID |
| `message_id` | string | Yes | The message ID to permanently delete |

**Returns:**
```json
{
  "status": "permanently_deleted",
  "message_id": "message-id",
  "warning": "This action is irreversible. The email has been permanently deleted."
}
```

## Agent Configuration

To give an agent access to Outlook, include the Outlook tools and provide the integration ID in the prompt:

### Adding Tools to Agent

When creating or updating an agent, include the Outlook tools you want the agent to use:

```json
{
  "agent_name": "Email Assistant",
  "prompt": "You are an email assistant. You have access to Outlook via integration ID {outlook_integration_id}. Help the user manage their emails.",
  "tools": [
    "list_outlook_emails",
    "get_outlook_email",
    "send_outlook_email",
    "set_outlook_email_read_status",
    "create_outlook_draft",
    "list_outlook_drafts",
    "get_outlook_draft",
    "update_outlook_draft",
    "send_outlook_draft",
    "delete_outlook_draft",
    "list_outlook_folders",
    "create_outlook_folder",
    "delete_outlook_folder",
    "move_outlook_email",
    "modify_outlook_email_categories",
    "archive_outlook_email",
    "trash_outlook_email",
    "untrash_outlook_email",
    "delete_outlook_email"
  ]
}
```

**Recommended tool sets by use case:**

| Use Case | Recommended Tools |
|----------|-------------------|
| Read-only email access | `list_outlook_emails`, `get_outlook_email`, `list_outlook_folders` |
| Basic email management | Above + `set_outlook_email_read_status`, `archive_outlook_email`, `move_outlook_email`, `modify_outlook_email_categories` |
| Send emails | Above + `send_outlook_email` |
| Draft workflow | Above + `create_outlook_draft`, `list_outlook_drafts`, `get_outlook_draft`, `update_outlook_draft`, `send_outlook_draft`, `delete_outlook_draft` |
| Full email management | All tools (use `delete_outlook_email` with caution) |

### Using with Context

When creating a context, pass the integration ID via `prompt_args`:

```json
{
  "agent_id": "email-assistant-uuid",
  "prompt_args": {
    "outlook_integration_id": "actual-outlook-integration-uuid"
  }
}
```

The agent will then use this integration ID when calling Outlook tools.

## Outlook vs Gmail: Key Differences

### Folders vs Labels

| Gmail | Outlook |
|-------|---------|
| Uses labels (an email can have multiple labels) | Uses folders (an email exists in one folder) |
| `modify_email_labels` to add/remove labels | `move_outlook_email` to move between folders |
| Labels are tags | Categories are the closest equivalent to labels |

### Categories (Outlook's "Labels")

Outlook has a category system that allows tagging emails with colored tags. This is similar to Gmail labels:
- An email can have multiple categories
- Use `modify_outlook_email_categories` to manage them
- Preset colors: Red, Orange, Yellow, Green, Blue, Purple
- Custom categories can be created by users

### Search Syntax

| Gmail | Outlook |
|-------|---------|
| `is:unread` | `$filter=isRead eq false` |
| `from:email@example.com` | `$filter=from/emailAddress/address eq 'email@example.com'` |
| `has:attachment` | `$filter=hasAttachments eq true` |
| `after:2024/01/01` | `$filter=receivedDateTime ge 2024-01-01T00:00:00Z` |
| Free-text search | `$search="keywords"` |

## Token Refresh

Access tokens expire after approximately 1 hour. The system automatically refreshes tokens when needed:

1. Before each API call, the token expiry is checked
2. If expired (or expiring within 60 seconds), the refresh token is used to get a new access token
3. The new tokens are saved to the integration

This happens transparently - agents don't need to handle token refresh.

## Error Handling

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `Integration not found` | Invalid integration_id | Verify the integration ID exists |
| `Not an Outlook integration` | Wrong integration type | Use an Outlook integration ID |
| `Failed to refresh token` | Refresh token revoked | User needs to re-authorize |
| `Outlook API error: 401` | Token expired/invalid | Token refresh should happen automatically |
| `Outlook API error: 403` | Insufficient permissions | Check API permissions in Azure |
| `Outlook API error: 429` | Rate limited | Implement backoff/retry |

## Security Considerations

1. **Store integration IDs securely** - Don't expose them in client-side code
2. **Scope limitation** - The integration requests only necessary scopes (Mail.ReadWrite, Mail.Send, User.Read)
3. **Organization isolation** - Integrations are tied to organizations
4. **Token encryption** - Consider encrypting tokens at rest in DynamoDB

## Related Documentation

- [Gmail Integration](./gmail-integration.md) - Gmail tool reference
- [Additional Agent Tools](./additional-agent-tools.md) - Built-in tool reference
- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results

