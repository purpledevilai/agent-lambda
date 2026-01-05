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

Once you have a Gmail integration, agents can use these tools:

### list_emails

List emails from the inbox with optional filtering.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `query` | string | No | Gmail search query (e.g., "is:unread", "from:boss@company.com") |
| `max_results` | int | No | Maximum emails to return (default 10, max 100) |

**Example:**
```json
{
  "integration_id": "gmail-integration-uuid",
  "query": "is:unread",
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

### get_email

Get the full content of a specific email.

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

### send_email

Send an email from the connected Gmail account.

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

### mark_email_read

Mark an email as read (removes the UNREAD label).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to mark as read |

**Returns:**
```json
{
  "status": "success",
  "message_id": "message-id",
  "action": "marked_as_read",
  "labels": ["INBOX"]
}
```

### mark_email_unread

Mark an email as unread (adds the UNREAD label).

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Gmail integration ID |
| `message_id` | string | Yes | The message ID to mark as unread |

**Returns:**
```json
{
  "status": "success",
  "message_id": "message-id",
  "action": "marked_as_unread",
  "labels": ["INBOX", "UNREAD"]
}
```

## Agent Configuration

To give an agent access to Gmail, include the Gmail tools and provide the integration ID in the prompt:

### Adding Tools to Agent

When creating or updating an agent, include the Gmail tools:

```json
{
  "agent_name": "Email Assistant",
  "prompt": "You are an email assistant. You have access to Gmail via integration ID {gmail_integration_id}. Help the user manage their emails.",
  "tools": [
    "list_emails",
    "get_email",
    "send_email",
    "mark_email_read",
    "mark_email_unread"
  ]
}
```

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

## Gmail Search Query Examples

The `query` parameter in `list_emails` supports Gmail's search syntax:

| Query | Description |
|-------|-------------|
| `is:unread` | Unread emails |
| `is:starred` | Starred emails |
| `from:john@example.com` | Emails from a specific sender |
| `to:me` | Emails sent to you |
| `subject:meeting` | Emails with "meeting" in subject |
| `has:attachment` | Emails with attachments |
| `after:2024/01/01` | Emails after a date |
| `before:2024/12/31` | Emails before a date |
| `newer_than:7d` | Emails from the last 7 days |
| `label:important` | Emails with specific label |
| `in:inbox` | Emails in inbox |
| `in:sent` | Sent emails |

Queries can be combined: `is:unread from:boss@company.com after:2024/01/01`

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

