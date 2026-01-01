# Gmail Integration - Frontend Implementation Guide

## Overview

This guide explains what the frontend needs to implement to support Gmail OAuth integration. The backend handles token management and the actual Gmail API calls - the frontend just needs to handle the OAuth flow UI and display integrations.

## Integration Management

### Existing CRUD API

The Integrations model already has a full CRUD API that the frontend can use to display and manage integrations:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/integrations` | List all integrations for the user's organizations |
| GET | `/integration/{integration_id}` | Get a specific integration |
| POST | `/integration` | Create an integration (not needed for Gmail - handled by OAuth) |
| POST | `/integration/{integration_id}` | Update an integration |
| DELETE | `/integration/{integration_id}` | Delete an integration |

### Displaying Integrations

To show existing Gmail integrations:

```typescript
// Fetch integrations
const response = await fetch('/integrations', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});
const integrations = await response.json();

// Filter for Gmail integrations
const gmailIntegrations = integrations.filter(i => i.type === 'gmail');

// Each Gmail integration has:
// - integration_id: string
// - org_id: string
// - type: "gmail"
// - integration_config: { email: string, ... }
// - created_at: number
// - updated_at: number
```

### Deleting Integrations

```typescript
await fetch(`/integration/${integrationId}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${accessToken}` }
});
```

## OAuth Flow Implementation

The frontend needs to implement two things:
1. A "Connect Gmail" button that initiates OAuth
2. A callback page that handles the redirect from Google

### Step 1: Connect Gmail Button

Create a button that fetches the authorization URL from the backend and redirects the user:

```typescript
async function connectGmail(orgId?: string) {
  // 1. Fetch the auth URL from backend
  const params = new URLSearchParams();
  if (orgId) {
    params.append('org_id', orgId);
  }
  
  const response = await fetch(`/gmail/auth-url?${params}`, {
    headers: { 'Authorization': `Bearer ${accessToken}` }
  });
  
  const { auth_url } = await response.json();
  
  // 2. Redirect user to Google OAuth
  window.location.href = auth_url;
}
```

**React Example:**

```tsx
function ConnectGmailButton({ orgId }: { orgId?: string }) {
  const [loading, setLoading] = useState(false);
  
  const handleConnect = async () => {
    setLoading(true);
    try {
      const params = orgId ? `?org_id=${orgId}` : '';
      const response = await api.get(`/gmail/auth-url${params}`);
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error('Failed to get auth URL:', error);
      setLoading(false);
    }
  };
  
  return (
    <button onClick={handleConnect} disabled={loading}>
      {loading ? 'Connecting...' : 'Connect Gmail'}
    </button>
  );
}
```

### Step 2: OAuth Callback Page

Create a page at `/gmail/authcode` (or whatever your redirect URI is configured to). This page:
1. Extracts the `code` parameter from the URL
2. Sends it to the backend for token exchange
3. Redirects to the integrations page on success

```typescript
// pages/gmail/authcode.tsx (Next.js example)

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function GmailAuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const code = searchParams.get('code');
    const state = searchParams.get('state'); // Contains org_id if provided
    const errorParam = searchParams.get('error');
    
    if (errorParam) {
      setStatus('error');
      setError(`Google OAuth error: ${errorParam}`);
      return;
    }
    
    if (!code) {
      setStatus('error');
      setError('No authorization code received');
      return;
    }
    
    // Exchange the code for tokens
    exchangeCode(code, state);
  }, [searchParams]);
  
  async function exchangeCode(code: string, orgId: string | null) {
    try {
      const params = orgId ? `?org_id=${orgId}` : '';
      
      const response = await fetch(`/gmail/auth${params}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Token exchange failed');
      }
      
      const integration = await response.json();
      
      setStatus('success');
      
      // Redirect to integrations page after short delay
      setTimeout(() => {
        router.push('/settings/integrations');
      }, 2000);
      
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err.message : 'Failed to connect Gmail');
    }
  }
  
  return (
    <div className="flex items-center justify-center min-h-screen">
      {status === 'loading' && (
        <div>
          <Spinner />
          <p>Connecting your Gmail account...</p>
        </div>
      )}
      
      {status === 'success' && (
        <div>
          <CheckIcon />
          <p>Gmail connected successfully!</p>
          <p>Redirecting...</p>
        </div>
      )}
      
      {status === 'error' && (
        <div>
          <ErrorIcon />
          <p>Failed to connect Gmail</p>
          <p>{error}</p>
          <button onClick={() => router.push('/settings/integrations')}>
            Go back
          </button>
        </div>
      )}
    </div>
  );
}
```

### Redirect URI Configuration

Make sure your Google Cloud Console OAuth credentials have the correct redirect URI:
- Development: `http://localhost:3000/gmail/authcode`
- Production: `https://yourdomain.com/gmail/authcode`

The backend's `GMAIL_REDIRECT_URI` environment variable must match exactly.

## Integrations UI Component

Here's an example component for displaying and managing Gmail integrations:

```tsx
function GmailIntegrations({ orgId }: { orgId: string }) {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchIntegrations();
  }, []);
  
  async function fetchIntegrations() {
    const response = await api.get('/integrations');
    const gmailIntegrations = response.data.filter(
      (i: Integration) => i.type === 'gmail' && i.org_id === orgId
    );
    setIntegrations(gmailIntegrations);
    setLoading(false);
  }
  
  async function disconnectGmail(integrationId: string) {
    if (!confirm('Are you sure you want to disconnect this Gmail account?')) {
      return;
    }
    
    await api.delete(`/integration/${integrationId}`);
    setIntegrations(integrations.filter(i => i.integration_id !== integrationId));
  }
  
  if (loading) return <Spinner />;
  
  return (
    <div>
      <h2>Gmail Integrations</h2>
      
      {integrations.length === 0 ? (
        <div>
          <p>No Gmail accounts connected</p>
          <ConnectGmailButton orgId={orgId} />
        </div>
      ) : (
        <div>
          {integrations.map(integration => (
            <div key={integration.integration_id} className="integration-card">
              <div>
                <GmailIcon />
                <span>{integration.integration_config.email}</span>
              </div>
              <div>
                <span>Connected {formatDate(integration.created_at)}</span>
                <button onClick={() => disconnectGmail(integration.integration_id)}>
                  Disconnect
                </button>
              </div>
            </div>
          ))}
          
          <ConnectGmailButton orgId={orgId} />
        </div>
      )}
    </div>
  );
}
```

## Agent Builder - Gmail Tools

The following tool IDs need to be added to the agent builder's available tools list:

### New Tool IDs

| Tool ID | Name | Description |
|---------|------|-------------|
| `list_emails` | List Emails | List emails from Gmail inbox with filtering |
| `get_email` | Get Email | Get full content of a specific email |
| `send_email` | Send Email | Send an email from connected Gmail |
| `mark_email_read` | Mark Email Read | Mark an email as read |
| `mark_email_unread` | Mark Email Unread | Mark an email as unread |

### Adding to Agent Builder

```typescript
// Tool definitions for the agent builder
const GMAIL_TOOLS = [
  {
    id: 'list_emails',
    name: 'List Emails',
    description: 'List emails from Gmail inbox with optional search filters',
    category: 'gmail',
    icon: 'mail',
  },
  {
    id: 'get_email',
    name: 'Get Email',
    description: 'Get the full content of a specific email',
    category: 'gmail',
    icon: 'mail-open',
  },
  {
    id: 'send_email',
    name: 'Send Email',
    description: 'Send an email from the connected Gmail account',
    category: 'gmail',
    icon: 'send',
  },
  {
    id: 'mark_email_read',
    name: 'Mark as Read',
    description: 'Mark an email as read',
    category: 'gmail',
    icon: 'check',
  },
  {
    id: 'mark_email_unread',
    name: 'Mark as Unread',
    description: 'Mark an email as unread',
    category: 'gmail',
    icon: 'mail',
  },
];

// Add to your existing built-in tools
const BUILT_IN_TOOLS = [
  // ... existing tools ...
  ...GMAIL_TOOLS,
];
```

### Tool Selection UI

When Gmail tools are selected for an agent, you may want to show a note that the agent needs a Gmail integration ID in its prompt:

```tsx
function ToolSelector({ selectedTools, onSelect }) {
  const hasGmailTools = selectedTools.some(t => 
    ['list_emails', 'get_email', 'send_email', 'mark_email_read', 'mark_email_unread'].includes(t)
  );
  
  return (
    <div>
      {/* Tool selection UI */}
      
      {hasGmailTools && (
        <div className="info-banner">
          <InfoIcon />
          <p>
            Gmail tools require a Gmail integration. Include <code>{'{gmail_integration_id}'}</code> in 
            the agent's prompt and pass the actual integration ID via <code>prompt_args</code> when 
            creating a context.
          </p>
        </div>
      )}
    </div>
  );
}
```

## Summary

### Frontend Implementation Checklist

- [ ] **Integrations Page**
  - [ ] Display Gmail integrations using `GET /integrations`
  - [ ] Show email address from `integration_config.email`
  - [ ] Add disconnect button using `DELETE /integration/{id}`

- [ ] **Connect Gmail Button**
  - [ ] Fetch auth URL from `GET /gmail/auth-url`
  - [ ] Redirect to the returned `auth_url`

- [ ] **Callback Page** (`/gmail/authcode`)
  - [ ] Extract `code` from URL params
  - [ ] Send to `POST /gmail/auth` with the code
  - [ ] Handle success (redirect to integrations)
  - [ ] Handle errors (display message)

- [ ] **Agent Builder**
  - [ ] Add `list_emails` to available tools
  - [ ] Add `get_email` to available tools
  - [ ] Add `send_email` to available tools
  - [ ] Add `mark_email_read` to available tools
  - [ ] Add `mark_email_unread` to available tools
  - [ ] Show info message when Gmail tools selected

### API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `GET /integrations` | List all integrations |
| `DELETE /integration/{id}` | Remove an integration |
| `GET /gmail/auth-url` | Get OAuth authorization URL |
| `POST /gmail/auth` | Exchange code for tokens (creates integration) |

