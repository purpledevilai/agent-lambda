# API Keys & Client Token Streaming

## Overview

Ajentify supports two types of API keys for authentication:

1. **Org API Keys** - Long-lived tokens for server-side API access
2. **Client API Keys** - Short-lived tokens for client-side WebSocket connections

This guide focuses on **Client API Keys**, which enable secure, direct WebSocket connections from browser clients to Ajentify's token streaming server for real-time AI responses.

## Why Client API Keys?

When building client-side applications (web apps, mobile apps, etc.) that need to stream AI responses in real-time, you face a security challenge:

- **Problem**: You can't safely embed long-lived API keys in client code
- **Solution**: Generate short-lived Client API Keys that:
  - Expire after 2 minutes
  - Only allow connection to specific contexts (not full API access)
  - Can be safely passed to the frontend

## Getting Started

### Step 1: Request an Org API Key

To generate Client API Keys, you first need an Org API Key. Contact the Ajentify team to request one:

📧 **Request your Org API Key** - Reach out to us and we'll provision one for your organization.

### Step 2: Store Your Org API Key Securely

Your Org API Key should be stored securely on your backend server:

```bash
# Environment variable (recommended)
AJENTIFY_ORG_API_KEY=your_org_api_key_here
```

⚠️ **Never expose your Org API Key to clients** - This key has full API access and should only be used server-side.

## Architecture Pattern

Here's the recommended architecture for secure client-side streaming:

### Two-Endpoint Strategy

Your backend should expose **two separate endpoints**:

1. **Create Context Endpoint** - Creates a new context with a non-public agent
2. **Generate Client Token Endpoint** - Generates a short-lived token for WebSocket connection

This separation allows clients to:
- Create a context once and reuse it across multiple sessions
- Generate fresh tokens for reconnection without recreating the context
- Handle WebSocket disconnections gracefully

### Flow Diagram

```
┌──────────────┐
│   Browser    │
│   Client     │
└──────┬───────┘
       │
       │ 1. Request: Create Context
       ↓
┌──────────────────┐
│   Your Backend   │
│  (Authenticated) │
└──────┬───────────┘
       │
       │ 2. Create Context with Org API Key
       ↓
┌──────────────────┐
│  Ajentify API    │
│  POST /context   │
└──────┬───────────┘
       │
       │ 3. Return Context ID
       ↓
┌──────────────────┐
│   Your Backend   │
└──────┬───────────┘
       │
       │ 4. Pass Context ID to Browser
       ↓
┌──────────────────┐
│   Browser        │
│   Client         │
└──────┬───────────┘
       │
       │ 5. Request: Generate Client Token (with Context ID)
       ↓
┌──────────────────┐
│   Your Backend   │
│  (Authenticated) │
└──────┬───────────┘
       │
       │ 6. Generate Client API Key with Org API Key
       ↓
┌──────────────────┐
│  Ajentify API    │
│ POST /generate-  │
│    api-key       │
└──────┬───────────┘
       │
       │ 7. Return Client Token
       ↓
┌──────────────────┐
│   Your Backend   │
└──────┬───────────┘
       │
       │ 8. Pass Token to Browser
       ↓
┌──────────────────┐
│   Browser        │
│   Client         │
└──────┬───────────┘
       │
       │ 9. Connect to WebSocket (Context ID + Token)
       ↓
┌──────────────────┐
│ Token Streaming  │
│    Server        │
└──────────────────┘


    ╔════════════════════════════════════════╗
    ║  If WebSocket disconnects, client      ║
    ║  can repeat steps 5-9 with existing    ║
    ║  context ID to reconnect!              ║
    ╚════════════════════════════════════════╝
```

### Why Two Endpoints?

**Scenario: WebSocket Disconnection**

If your client's WebSocket connection drops:
1. The context still exists on Ajentify
2. The client already has the `contextId`
3. The client generates a fresh token (step 5-8)
4. The client reconnects to the same context (step 9)

**Without separation**, you'd have to:
- Create a new context every time (losing conversation history)
- OR manage token refresh logic on the backend (more complex)

**With separation**, you get:
- Simple reconnection flow
- Preserved conversation history
- Clean separation of concerns

## Implementation Guide

### Backend: Endpoint 1 - Create Context

Create an authenticated endpoint that creates a new context with your non-public agent:

```javascript
// Example: Node.js/Express
app.post('/api/create-context', authenticateUser, async (req, res) => {
  const { agentId } = req.body;
  
  // Validate user has access to this agent (your auth logic)
  if (!userCanAccessAgent(req.user, agentId)) {
    return res.status(403).json({ error: 'Unauthorized' });
  }
  
  // Create context using your Org API Key
  const response = await fetch('https://api.ajentify.com/context', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.AJENTIFY_ORG_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agent_id: agentId
    })
  });
  
  const context = await response.json();
  
  // Return only the context ID
  res.json({
    contextId: context.context_id
  });
});
```

```python
# Example: Python/Flask
@app.route('/api/create-context', methods=['POST'])
@require_auth
def create_context():
    agent_id = request.json.get('agent_id')
    
    # Validate user has access to this agent (your auth logic)
    if not user_can_access_agent(current_user, agent_id):
        return {'error': 'Unauthorized'}, 403
    
    # Create context using your Org API Key
    response = requests.post(
        'https://api.ajentify.com/context',
        headers={
            'Authorization': f'Bearer {os.environ["AJENTIFY_ORG_API_KEY"]}',
            'Content-Type': 'application/json'
        },
        json={
            'agent_id': agent_id
        }
    )
    
    context = response.json()
    
    # Return only the context ID
    return {
        'contextId': context['context_id']
    }
```

### Backend: Endpoint 2 - Generate Client Token

Create a second authenticated endpoint that generates a fresh client token:

```javascript
// Example: Node.js/Express
app.post('/api/get-client-token', authenticateUser, async (req, res) => {
  const { contextId } = req.body;
  
  // Validate user has access to this context (your auth logic)
  if (!userCanAccessContext(req.user, contextId)) {
    return res.status(403).json({ error: 'Unauthorized' });
  }
  
  // Generate Client API Key using your Org API Key
  const response = await fetch('https://api.ajentify.com/generate-api-key', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.AJENTIFY_ORG_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      org_id: 'your-org-id',
      type: 'client'
    })
  });
  
  const { token } = await response.json();
  
  // Return only the client token
  res.json({
    clientToken: token
  });
});
```

```python
# Example: Python/Flask
@app.route('/api/get-client-token', methods=['POST'])
@require_auth
def get_client_token():
    context_id = request.json.get('context_id')
    
    # Validate user has access to this context (your auth logic)
    if not user_can_access_context(current_user, context_id):
        return {'error': 'Unauthorized'}, 403
    
    # Generate Client API Key using your Org API Key
    response = requests.post(
        'https://api.ajentify.com/generate-api-key',
        headers={
            'Authorization': f'Bearer {os.environ["AJENTIFY_ORG_API_KEY"]}',
            'Content-Type': 'application/json'
        },
        json={
            'org_id': 'your-org-id',
            'type': 'client'
        }
    )
    
    client_token = response.json()['token']
    
    # Return only the client token
    return {
        'clientToken': client_token
    }
```

**Important Notes:**
- **Both endpoints must authenticate users** - Verify the user has access to the agent/context
- **Context creation uses your Org API Key** - Never expose this to clients
- **Token generation is separate** - Allows reconnection without recreating context
- **Tokens expire in 2 minutes** - Frontend should request fresh tokens as needed

### Frontend: Initial Connection

For the first connection, call both endpoints in sequence:

```javascript
// 1. Create a new context
const contextResponse = await fetch('/api/create-context', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userSessionToken}`, // Your app's auth
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    agentId: 'your-agent-id'
  })
});

const { contextId } = await contextResponse.json();

// Store contextId for later reconnections
localStorage.setItem('contextId', contextId);

// 2. Get a client token for this context
const tokenResponse = await fetch('/api/get-client-token', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${userSessionToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    contextId: contextId
  })
});

const { clientToken } = await tokenResponse.json();

// 3. Connect to WebSocket
const ws = new WebSocket('wss://token-streaming-server.prod.token-streaming.ajentify.com/ws');

ws.onopen = () => {
  ws.send(JSON.stringify({
    method: 'connect_to_context',
    params: {
      context_id: contextId,
      access_token: clientToken
    },
    id: 'connect-1'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  // Connection response
  if (data.id === 'connect-1') {
    if (data.result.success) {
      console.log('Connected to:', data.result.agent.agent_name);
    } else {
      console.error('Connection failed:', data.result.error);
    }
  }
  
  // Streaming tokens
  if (data.method === 'on_token') {
    console.log('Token:', data.params.token);
  }
  
  // Tool calls
  if (data.method === 'on_tool_call') {
    console.log('Tool called:', data.params.tool_name);
  }
};
```

### Frontend: Reconnection

If the WebSocket disconnects, reconnect to the same context with a fresh token:

```javascript
async function reconnectToContext(contextId) {
  // 1. Get a fresh client token (no need to create new context!)
  const tokenResponse = await fetch('/api/get-client-token', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${userSessionToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      contextId: contextId
    })
  });

  const { clientToken } = await tokenResponse.json();

  // 2. Reconnect to WebSocket with the same context ID
  const ws = new WebSocket('wss://token-streaming-server.prod.token-streaming.ajentify.com/ws');

  ws.onopen = () => {
    ws.send(JSON.stringify({
      method: 'connect_to_context',
      params: {
        context_id: contextId,
        access_token: clientToken
      },
      id: 'reconnect-1'
    }));
  };

  // ... rest of WebSocket handlers

  return ws;
}

// Usage: Reconnect to existing context
const existingContextId = localStorage.getItem('contextId');
if (existingContextId) {
  await reconnectToContext(existingContextId);
}
```

## WebSocket Protocol

The Token Streaming Server uses a JSON-RPC-like protocol. Here are the key message formats:

### 1. Connect to Context

**Client Request:**
```json
{
  "method": "connect_to_context",
  "params": {
    "context_id": "db5e4da5-f4eb-40d0-a1da-712d17317cce",
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  },
  "id": "123"
}
```

**Server Response:**
```json
{
  "id": "123",
  "result": {
    "success": true,
    "agent_speaks_first": false,
    "agent": {
      "agent_id": "uuid",
      "agent_name": "Agent Name",
      "prompt": "System prompt",
      "tools": ["tool1", "tool2"],
      ...
    }
  }
}
```

### 2. Send Message

**Client Request:**
```json
{
  "method": "add_message",
  "params": {
    "message": "Hello, how are you?"
  },
  "id": "456"
}
```

**Server Response:**
```json
{
  "id": "456",
  "result": {
    "success": true
  }
}
```

### 3. Receive Streaming Tokens

**Server Notifications (multiple):**
```json
{"method": "on_token", "params": {"token": "Hello", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": ",", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": " how", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": " can", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": " I", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": " help", "response_id": "resp-abc"}}
{"method": "on_token", "params": {"token": "?", "response_id": "resp-abc"}}
```

### 4. Tool Calls (if agent uses tools)

**Server Notification (tool call):**
```json
{
  "method": "on_tool_call",
  "params": {
    "tool_call_id": "uuid",
    "tool_name": "web_search",
    "tool_input": {"query": "weather today"}
  }
}
```

**Server Notification (tool response):**
```json
{
  "method": "on_tool_response",
  "params": {
    "tool_call_id": "uuid",
    "tool_name": "web_search",
    "tool_output": "Weather results..."
  }
}
```

For complete WebSocket API documentation, see the [Token Streaming Server WebSocket API](./WEBSOCKET_API.md).

## Security Model

### Client API Key Security

✅ **Safe to pass to frontend** because:
- **Short-lived**: Expires after 2 minutes
- **Limited scope**: Only allows WebSocket connections to contexts
- **No API access**: Cannot access REST API endpoints
- **Context-specific**: Can only connect to contexts created by the parent token

❌ **Cannot be used for**:
- Creating agents or contexts
- Accessing other API endpoints
- Reading or modifying organization data
- Generating new API keys

### Backend Endpoint Security

⚠️ **Important**: Your backend endpoint that generates Client API Keys should be authenticated:

```javascript
// ✅ GOOD - Requires authentication
app.post('/api/get-client-token', authenticateUser, async (req, res) => {
  // Your authentication middleware ensures only logged-in users can access
  // ...
});

// ❌ BAD - Public endpoint
app.post('/api/get-client-token', async (req, res) => {
  // Anyone can generate tokens!
  // ...
});
```

**Why?** Even though Client API Keys are short-lived and limited in scope, you still want to control who can generate them. Your backend should verify:

1. The user is authenticated in your system
2. The user has permission to access the requested context
3. Rate limiting to prevent abuse

## Token Lifecycle

### Client API Key Lifespan

```
Create → Use (2 minutes) → Expire
   ↓         ↓                ↓
   0s      120s           ∞
```

- **Created**: Token is generated with 2-minute expiration
- **Valid**: Token can be used to connect to WebSocket
- **Expired**: Token becomes invalid, new connection attempts fail
- **Active Connections**: Existing WebSocket connections remain open even after token expires

### Best Practices

1. **Generate on-demand**: Create Client API Keys right before connecting to WebSocket
2. **Handle expiration**: If connection fails, generate a new token
3. **Reconnection logic**: Implement automatic reconnection with fresh tokens

```javascript
async function connectWithRetry(contextId, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      // Get fresh token
      const { clientToken } = await fetch('/api/get-client-token', {
        method: 'POST',
        body: JSON.stringify({ contextId })
      }).then(r => r.json());
      
      // Attempt connection
      const ws = await connectToWebSocket(contextId, clientToken);
      return ws; // Success!
      
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * (i + 1)); // Exponential backoff
    }
  }
}
```

## Complete Example: React Component

```javascript
import { useState, useEffect, useRef } from 'react';

function StreamingChat({ agentId }) {
  const [messages, setMessages] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [contextId, setContextId] = useState(null);
  const wsRef = useRef(null);
  
  useEffect(() => {
    initializeChatSession();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [agentId]);
  
  async function initializeChatSession() {
    try {
      // 1. Create a new context
      const contextResponse = await fetch('/api/create-context', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('userToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ agentId })
      });
      
      const { contextId } = await contextResponse.json();
      setContextId(contextId);
      
      // 2. Connect to the context
      await connectToContext(contextId);
      
    } catch (error) {
      console.error('Failed to initialize chat session:', error);
    }
  }
  
  async function connectToContext(contextId) {
    try {
      // 1. Get a fresh client token
      const tokenResponse = await fetch('/api/get-client-token', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('userToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ contextId })
      });
      
      const { clientToken } = await tokenResponse.json();
      
      // 2. Connect to WebSocket
      const ws = new WebSocket('wss://token-streaming-server.prod.token-streaming.ajentify.com/ws');
      wsRef.current = ws;
      
      ws.onopen = () => {
        ws.send(JSON.stringify({
          method: 'connect_to_context',
          params: {
            context_id: contextId,
            access_token: clientToken
          },
          id: 'connect-1'
        }));
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        // Connection response
        if (data.id === 'connect-1') {
          if (data.result.success) {
            setIsConnected(true);
            console.log('Connected to:', data.result.agent.agent_name);
          } else {
            console.error('Connection failed:', data.result.error);
          }
        }
        
        // Streaming tokens
        if (data.method === 'on_token') {
          setMessages(prev => {
            const lastMessage = prev[prev.length - 1];
            if (lastMessage && lastMessage.response_id === data.params.response_id) {
              return [
                ...prev.slice(0, -1),
                { 
                  ...lastMessage, 
                  content: lastMessage.content + data.params.token 
                }
              ];
            } else {
              return [...prev, { 
                content: data.params.token, 
                response_id: data.params.response_id,
                role: 'assistant',
                isStreaming: true
              }];
            }
          });
        }
        
        // Tool calls
        if (data.method === 'on_tool_call') {
          console.log('Agent calling:', data.params.tool_name);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setIsConnected(false);
      };
      
      ws.onclose = () => {
        console.log('WebSocket closed, attempting reconnection...');
        setIsConnected(false);
        
        // Automatically reconnect after 1 second
        setTimeout(() => {
          if (contextId) {
            connectToContext(contextId);
          }
        }, 1000);
      };
      
    } catch (error) {
      console.error('Failed to connect to context:', error);
    }
  }
  
  function sendMessage(message) {
    if (!wsRef.current || !isConnected) return;
    
    // Add user message to UI
    setMessages(prev => [...prev, { content: message, role: 'user' }]);
    
    // Send to agent
    wsRef.current.send(JSON.stringify({
      method: 'add_message',
      params: { message },
      id: `msg-${Date.now()}`
    }));
  }
  
  return (
    <div>
      <div>
        Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        {contextId && <span> | Context: {contextId.slice(0, 8)}...</span>}
      </div>
      <div>
        {messages.map((msg, i) => (
          <div key={i} className={msg.role}>
            {msg.content}
            {msg.isStreaming && <span className="cursor">▋</span>}
          </div>
        ))}
      </div>
      <input 
        type="text" 
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            sendMessage(e.target.value);
            e.target.value = '';
          }
        }}
        placeholder="Type a message..."
        disabled={!isConnected}
      />
    </div>
  );
}
```

**Key Features:**
- **Separate `connectToContext` function** - Can be called independently for reconnection
- **Automatic reconnection** - If WebSocket closes, automatically gets fresh token and reconnects
- **Preserved context** - Same `contextId` is used across reconnections, preserving conversation history
- **Two-endpoint pattern** - Creates context once, generates tokens as needed

## WebSocket Server URL

**Production**: `wss://token-streaming-server.prod.token-streaming.ajentify.com/ws`

The WebSocket server:
- Accepts both Org and Client API Keys
- Validates tokens using the same JWT secret
- Provides real-time token streaming for agent responses
- Automatically handles context ownership validation

## Troubleshooting

### Connection Refused

**Problem**: WebSocket connection fails immediately

**Solutions**:
- Verify the WebSocket URL is correct
- Check that the Client API Key hasn't expired (2-minute limit)
- Ensure you're using `wss://` (secure WebSocket) not `ws://`

### Invalid Token Error

**Problem**: Server rejects the Client API Key

**Solutions**:
- Generate a fresh token (may have expired)
- Verify the token was generated with the correct `org_id`
- Check that your Org API Key is valid

### Cannot Access Context

**Problem**: Connection accepted but can't access context

**Solutions**:
- Verify the context was created by the same org/user as the token
- Check that the `context_id` in the connection request matches the actual context
- Ensure the context hasn't been deleted

### Token Expired During Generation

**Problem**: Client token expires before frontend receives it

**Solutions**:
- Optimize backend response time
- Generate tokens in your frontend instead of backend (if your architecture allows)
- Implement retry logic with fresh token generation

## API Reference

### Generate Client API Key

**Endpoint**: `POST /generate-api-key`

**Headers**:
```
Authorization: Bearer YOUR_ORG_API_KEY
Content-Type: application/json
```

**Request Body**:
```json
{
  "org_id": "your-org-id",
  "type": "client"
}
```

**Response**:
```json
{
  "api_key_id": "b635e90a-af99-4aa1-9872-76cbedb0a8ee",
  "org_id": "8275b112-3323-4d87-bcda-c0f3d6c13cc6",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "valid": true,
  "type": "client",
  "user_id": "9f7da0b5-2e5c-42a1-ad8f-61de762c89d1",
  "created_at": 1763089120,
  "updated_at": 1763089120
}
```

## Related Documentation

- [Token Streaming Server](./token-streaming-server.md) - Full WebSocket API reference
- [Context Management](./context-management.md) - Creating and managing contexts
- [Message Control Endpoints](./message-control-endpoints.md) - Advanced context manipulation

## Support

Need help implementing Client API Keys or have questions?

📧 Contact the Ajentify team for support and assistance.

