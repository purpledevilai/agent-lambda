# Gmail Integration

## Overview

The Gmail integration allows agents to read, send, and manage emails on behalf of users. This is accomplished through OAuth 2.0 authentication with Google's Gmail API.

## Setup

### 1. Google Cloud Project Setup

Before using the Gmail integration, you need to set up a Google Cloud project:

1. **Create a Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (e.g., "Ajentify Gmail Integration")

2. **Enable Gmail API**
   - Navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose user type (Internal or External)
   - Fill in required details:
     - App name
     - Support email
     - Authorized domains
   - Add scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.send`
     - `https://www.googleapis.com/auth/gmail.modify`

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Web application"
   - Add your redirect URI (e.g., `https://yourapp.com/gmail/callback`)
   - Save the **Client ID** and **Client Secret**

### 2. Environment Variables

Add these environment variables to your Lambda:

```bash
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_REDIRECT_URI=https://yourapp.com/gmail/callback
```

## OAuth Flow

### Step 1: Get Authorization URL

```bash
GET /gmail/auth-url
Authorization: Bearer <user_token>
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with
- `state` (optional): State parameter to pass through OAuth flow

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
}
```

Redirect the user to this URL. After authorization, Google redirects back to your `GMAIL_REDIRECT_URI` with a `code` parameter.

### Step 2: Exchange Code for Tokens

```bash
POST /gmail/auth
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "code": "authorization_code_from_google"
}
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with

**Response:**
```json
{
  "integration_id": "uuid-of-integration",
  "org_id": "org-uuid",
  "type": "gmail",
  "integration_config": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": 1234567890,
    "email": "user@gmail.com"
  },
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

Save the `integration_id` - this is what you'll pass to agents to use Gmail tools.

## Agent Tools

Once you have a Gmail integration, agents can use these tools. All tools require the `integration_id` parameter.

### Tool Reference Summary

| Tool ID | Description |
|---------|-------------|
| `list_emails` | List and search emails with powerful query filters |
| `get_email` | Get full content of a specific email |
| `send_email` | Send a new email directly |
| `set_email_read_status` | Mark email as read or unread |
| `create_draft` | Create a new draft email |
| `list_drafts` | List all draft emails |
| `get_draft` | Get full content of a draft |
| `update_draft` | Update an existing draft |
| `send_draft` | Send a draft email |
| `delete_draft` | Delete a draft without sending |
| `list_labels` | List all labels (system and custom) |
| `create_label` | Create a new custom label |
| `delete_label` | Delete a custom label |
| `modify_email_labels` | Add or remove labels from an email |
| `archive_email` | Archive an email (remove from inbox) |
| `trash_email` | Move email to trash |
| `untrash_email` | Restore email from trash |
| `delete_email` | Permanently delete an email |

---

## Core Email Tools

### list_emails

List and search emails from the Gmail account with powerful filtering options.

**Tool ID:** `list_emails`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `query` | string | No | Gmail search query (see search syntax below) |
| `max_results` | int | No | Maximum emails to return (default 10, max 100) |

**Search Query Examples:**
- Keywords: `meeting` (searches everywhere - subject, body, sender)
- Exact phrase: `"project deadline"`
- Location: `in:inbox`, `in:trash`, `in:sent`, `in:spam`
- Labels: `label:YourLabelName`
- Status: `is:unread`, `is:starred`
- People: `from:email@example.com`, `to:email@example.com`
- Attachments: `has:attachment`, `filename:pdf`
- Dates: `after:2024/01/01`, `before:2024/12/31`
- Exclude: `-unsubscribe` (exclude emails with this word)
- Combine with spaces for AND logic

**Example:**
```json
{
  "integration_id": "gmail-integration-uuid",
  "query": "is:unread from:boss@company.com",
  "max_results": 5
}
```

**Returns:**
```json
{
  "emails": [
    {
      "id": "message-id",
      "thread_id": "thread-id",
      "from": "sender@example.com",
      "to": "recipient@gmail.com",
      "subject": "Meeting Tomorrow",
      "date": "Mon, 1 Jan 2024 10:00:00 -0500",
      "snippet": "Hi, just wanted to confirm...",
      "is_unread": true,
      "labels": ["INBOX", "UNREAD"]
    }
  ],
  "count": 1,
  "result_size_estimate": 5
}
```

---

### get_email

Get the full content of a specific email including the complete body text.

**Tool ID:** `get_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID from list_emails |

**Returns:**
```json
{
  "id": "message-id",
  "thread_id": "thread-id",
  "from": "sender@example.com",
  "to": "recipient@gmail.com",
  "subject": "Meeting Tomorrow",
  "date": "Mon, 1 Jan 2024 10:00:00 -0500",
  "body": "Hi,\n\nJust wanted to confirm our meeting tomorrow at 2pm.\n\nBest,\nJohn",
  "snippet": "Hi, just wanted to confirm...",
  "is_unread": true,
  "labels": ["INBOX", "UNREAD"]
}
```

---

### send_email

Send an email directly from the connected Gmail account.

**Tool ID:** `send_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `to` | string | Yes | Recipient email address |
| `subject` | string | Yes | Email subject line |
| `body` | string | Yes | Email body content |
| `html` | bool | No | Set true if body is HTML (default false) |

**Example:**
```json
{
  "integration_id": "gmail-integration-uuid",
  "to": "recipient@example.com",
  "subject": "Re: Meeting Tomorrow",
  "body": "Sounds great! See you at 2pm."
}
```

**Returns:**
```json
{
  "status": "sent",
  "message_id": "new-message-id",
  "thread_id": "thread-id",
  "to": "recipient@example.com",
  "subject": "Re: Meeting Tomorrow"
}
```

---

### set_email_read_status

Mark an email as read or unread using a single boolean parameter.

**Tool ID:** `set_email_read_status`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to modify |
| `mark_as_read` | bool | Yes | `true` to mark as read, `false` to mark as unread |

**Example (mark as read):**
```json
{
  "integration_id": "gmail-integration-uuid",
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
  "labels": ["INBOX"]
}
```

---

## Draft Tools

Draft tools allow creating, managing, and sending email drafts. Useful for composing emails that need review before sending.

### create_draft

Create a new draft email. All content fields are optional - you can create an empty draft and update it later.

**Tool ID:** `create_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `to` | string | No | Recipient email address |
| `subject` | string | No | Email subject line |
| `body` | string | No | Email body content |
| `html` | bool | No | Set true if body is HTML (default false) |

**Example:**
```json
{
  "integration_id": "gmail-integration-uuid",
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
  "message_id": "message-id",
  "to": "recipient@example.com",
  "subject": "Project Proposal"
}
```

---

### list_drafts

List all draft emails in the account.

**Tool ID:** `list_drafts`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `max_results` | int | No | Maximum drafts to return (default 10, max 100) |

**Returns:**
```json
{
  "drafts": [
    {
      "draft_id": "draft-id",
      "message_id": "message-id",
      "to": "recipient@example.com",
      "subject": "Project Proposal",
      "snippet": "Here is my proposal..."
    }
  ],
  "count": 1,
  "result_size_estimate": 1
}
```

---

### get_draft

Get the full content of a specific draft.

**Tool ID:** `get_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `draft_id` | string | Yes | The draft ID from list_drafts |

**Returns:**
```json
{
  "draft_id": "draft-id",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "to": "recipient@example.com",
  "subject": "Project Proposal",
  "body": "Here is my proposal for the project...",
  "snippet": "Here is my proposal...",
  "labels": ["DRAFT"]
}
```

---

### update_draft

Update an existing draft. This replaces the entire draft content, so provide all fields you want to keep.

**Tool ID:** `update_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
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
  "message_id": "message-id",
  "to": "recipient@example.com",
  "subject": "Updated Subject"
}
```

---

### send_draft

Send an existing draft. The draft must have a recipient (`to` address) to be sent. This removes the draft from the drafts folder.

**Tool ID:** `send_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `draft_id` | string | Yes | The draft ID to send |

**Returns:**
```json
{
  "status": "sent",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "labels": ["SENT"]
}
```

---

### delete_draft

Delete a draft permanently without sending it.

**Tool ID:** `delete_draft`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `draft_id` | string | Yes | The draft ID to delete |

**Returns:**
```json
{
  "status": "deleted",
  "draft_id": "draft-id"
}
```

---

## Label Tools

Label tools allow managing Gmail labels for organizing emails.

### list_labels

List all labels in the Gmail account, including system labels (INBOX, SENT, etc.) and user-created labels.

**Tool ID:** `list_labels`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |

**Returns:**
```json
{
  "system_labels": [
    {"id": "INBOX", "name": "INBOX", "type": "system"},
    {"id": "SENT", "name": "SENT", "type": "system"},
    {"id": "TRASH", "name": "TRASH", "type": "system"},
    {"id": "UNREAD", "name": "UNREAD", "type": "system"},
    {"id": "STARRED", "name": "STARRED", "type": "system"}
  ],
  "user_labels": [
    {"id": "Label_123", "name": "Work", "type": "user"},
    {"id": "Label_456", "name": "Personal", "type": "user"}
  ],
  "total_count": 7
}
```

---

### create_label

Create a new custom label.

**Tool ID:** `create_label`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `name` | string | Yes | Display name for the label |
| `label_list_visibility` | string | No | `labelShow` (default), `labelShowIfUnread`, or `labelHide` |
| `message_list_visibility` | string | No | `show` (default) or `hide` |

**Example:**
```json
{
  "integration_id": "gmail-integration-uuid",
  "name": "Important Projects"
}
```

**Returns:**
```json
{
  "status": "created",
  "label_id": "Label_789",
  "name": "Important Projects",
  "type": "user",
  "label_list_visibility": "labelShow",
  "message_list_visibility": "show"
}
```

---

### delete_label

Delete a custom label. System labels (INBOX, SENT, TRASH, etc.) cannot be deleted.

**Tool ID:** `delete_label`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `label_id` | string | Yes | The label ID to delete (from list_labels) |

**Returns:**
```json
{
  "status": "deleted",
  "label_id": "Label_789"
}
```

---

### modify_email_labels

Add or remove labels from an email. Use this to organize emails, star/unstar, or apply custom labels.

**Tool ID:** `modify_email_labels`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to modify |
| `add_labels` | array | No | Label IDs to add (e.g., `["STARRED", "Label_123"]`) |
| `remove_labels` | array | No | Label IDs to remove |

**Example (star an email and add custom label):**
```json
{
  "integration_id": "gmail-integration-uuid",
  "message_id": "message-id",
  "add_labels": ["STARRED", "Label_123"],
  "remove_labels": []
}
```

**Returns:**
```json
{
  "status": "success",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "labels_added": ["STARRED", "Label_123"],
  "labels_removed": [],
  "current_labels": ["INBOX", "STARRED", "Label_123"]
}
```

---

## Email Lifecycle Tools

Tools for archiving, trashing, and deleting emails.

### archive_email

Archive an email by removing it from the inbox. The email is not deleted and can still be found in "All Mail" or by searching.

**Tool ID:** `archive_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to archive |

**Returns:**
```json
{
  "status": "archived",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "labels": ["UNREAD"]
}
```

---

### trash_email

Move an email to the trash. The email will be automatically permanently deleted after 30 days.

**Tool ID:** `trash_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to trash |

**Returns:**
```json
{
  "status": "trashed",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "labels": ["TRASH"]
}
```

---

### untrash_email

Restore an email from the trash back to its previous location.

**Tool ID:** `untrash_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to restore |

**Returns:**
```json
{
  "status": "restored",
  "message_id": "message-id",
  "thread_id": "thread-id",
  "labels": ["INBOX"]
}
```

---

### delete_email

**⚠️ WARNING: Permanently delete an email. This action is irreversible.**

Consider using `trash_email` instead, which allows recovery within 30 days.

**Tool ID:** `delete_email`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
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

To give an agent access to Gmail, include the Gmail tools and provide the integration ID in the prompt:

### Adding Tools to Agent

When creating or updating an agent, include the Gmail tools you want the agent to use:

```json
{
  "agent_name": "Email Assistant",
  "prompt": "You are an email assistant. You have access to Gmail via integration ID {gmail_integration_id}. Help the user manage their emails.",
  "tools": [
    "list_emails",
    "get_email",
    "send_email",
    "set_email_read_status",
    "create_draft",
    "list_drafts",
    "get_draft",
    "update_draft",
    "send_draft",
    "delete_draft",
    "list_labels",
    "create_label",
    "delete_label",
    "modify_email_labels",
    "archive_email",
    "trash_email",
    "untrash_email",
    "delete_email"
  ]
}
```

**Recommended tool sets by use case:**

| Use Case | Recommended Tools |
|----------|-------------------|
| Read-only email access | `list_emails`, `get_email`, `list_labels` |
| Basic email management | Above + `set_email_read_status`, `archive_email`, `modify_email_labels` |
| Send emails | Above + `send_email` |
| Draft workflow | Above + `create_draft`, `list_drafts`, `get_draft`, `update_draft`, `send_draft`, `delete_draft` |
| Full email management | All tools (use `delete_email` with caution) |

### Using with Context

When creating a context, pass the integration ID via `prompt_args`:

```json
{
  "agent_id": "email-assistant-uuid",
  "prompt_args": {
    "gmail_integration_id": "actual-gmail-integration-uuid"
  }
}
```

The agent will then use this integration ID when calling Gmail tools.

## Gmail Search Query Reference

The `query` parameter in `list_emails` supports Gmail's full search syntax:

### Content Search
| Query | Description |
|-------|-------------|
| `meeting` | Emails containing "meeting" anywhere (subject, body, sender) |
| `"project deadline"` | Exact phrase match |
| `budget report` | Must contain both words (AND) |
| `{budget OR report}` | Contains either word (OR) |
| `-unsubscribe` | Exclude emails with this word |

### Location/Label Filters
| Query | Description |
|-------|-------------|
| `in:inbox` | Emails in inbox |
| `in:sent` | Sent emails |
| `in:trash` | Trashed emails |
| `in:spam` | Spam folder |
| `-in:inbox -in:trash -in:spam` | Archived emails |
| `label:Work` | Emails with specific label |

### Status Filters
| Query | Description |
|-------|-------------|
| `is:unread` | Unread emails |
| `is:starred` | Starred emails |
| `is:read` | Read emails |

### People Filters
| Query | Description |
|-------|-------------|
| `from:john@example.com` | From specific sender |
| `to:me` | Sent to you |
| `cc:team@company.com` | CC'd to someone |

### Attachment Filters
| Query | Description |
|-------|-------------|
| `has:attachment` | Has any attachment |
| `filename:pdf` | Has PDF attachment |
| `filename:report.xlsx` | Specific filename |

### Date & Size Filters
| Query | Description |
|-------|-------------|
| `after:2024/01/01` | After a date |
| `before:2024/12/31` | Before a date |
| `newer_than:7d` | Last 7 days |
| `older_than:1y` | Older than 1 year |
| `larger:5M` | Larger than 5MB |
| `smaller:1M` | Smaller than 1MB |

### Combining Queries
Queries can be combined with spaces for AND logic:
```
is:unread from:boss@company.com after:2024/01/01 has:attachment
```

## Token Refresh

Access tokens expire after 1 hour. The system automatically refreshes tokens when needed:

1. Before each API call, the token expiry is checked
2. If expired (or expiring within 60 seconds), the refresh token is used to get a new access token
3. The new tokens are saved to the integration

This happens transparently - agents don't need to handle token refresh.

## Error Handling

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `Integration not found` | Invalid integration_id | Verify the integration ID exists |
| `Not a Gmail integration` | Wrong integration type | Use a Gmail integration ID |
| `Failed to refresh token` | Refresh token revoked | User needs to re-authorize |
| `Gmail API error: 403` | Insufficient permissions | Check OAuth scopes |
| `Gmail API error: 429` | Rate limited | Implement backoff/retry |

## Security Considerations

1. **Store integration IDs securely** - Don't expose them in client-side code
2. **Scope limitation** - The integration requests only necessary scopes (read, send, modify)
3. **Organization isolation** - Integrations are tied to organizations
4. **Token encryption** - Consider encrypting tokens at rest in DynamoDB

## Related Documentation

- [Additional Agent Tools](./additional-agent-tools.md) - Built-in tool reference
- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results

