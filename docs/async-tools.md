# Async Tools

## Overview

Async tools enable agents to call functions that take an extended period of time to complete without blocking the conversation. When an agent calls an async tool, the function executes immediately and returns a quick acknowledgment response (e.g., "Request submitted"). This satisfies the LLM's requirement for immediate tool responses while allowing the actual processing to happen asynchronously in the background.

The agent can continue the conversation while the async operation processes. When the operation completes, the result is delivered via the `/on-tool-call-response` endpoint and added to a queue. On the next agent invocation, queued responses are automatically processed by creating simulated tool calls (e.g., `{tool_name}_response`) that deliver the actual results to the agent.

## Key Benefits

- **Non-Blocking Operations**: Agents can continue conversing while waiting for long-running operations
- **External System Integration**: Perfect for approval workflows, third-party API calls, and human-in-the-loop scenarios
- **Webhook Notifications**: Automatically notify your systems when async responses are ready
- **Graceful Handling**: Responses arrive when ready and are seamlessly integrated into the conversation

## Use Cases

### 1. Approval Workflows

An agent can request approval from a human admin before proceeding with an action:

```python
# Agent calls: get_admin_approval(action="send_quote", amount=5000)
# Admin receives notification, reviews, and approves/rejects
# Response comes back minutes or hours later
# Agent acknowledges approval and proceeds
```

### 2. Long-Running Computations

Tasks that take 10s of seconds or minutes to complete:

```python
# Agent calls: analyze_large_dataset(dataset_id="12345")
# External system processes the data
# Results return when ready
# Agent presents the analysis to the user
```

### 3. Third-Party API Calls

External APIs with slow response times or rate limits:

```python
# Agent calls: fetch_weather_forecast(location="New York", days=7)
# External weather API is queried
# Forecast returns asynchronously
# Agent provides the forecast to the user
```

### 4. Human-in-the-Loop

Scenarios requiring human judgment or input:

```python
# Agent calls: ask_expert(question="Should we proceed with this strategy?")
# Expert is notified and provides input
# Agent receives expert opinion
# Agent incorporates feedback into recommendations
```

## How Async Tools Work

### 1. Tool Configuration

Create a tool with `is_async=True`:

```python
from Models import Tool

async_tool = Tool.create_tool(
    org_id="your-org-id",
    name="get_approval",
    description="Request approval from an administrator",
    code="""
def get_approval(quote_amount, customer_id, tool_call_id, context):
    # tool_call_id is automatically passed to async tools
    # Use it to track which tool call this response belongs to
    
    # Send notification to admin system
    send_notification_to_admin(
        tool_call_id=tool_call_id,
        context_id=context['context_id'],
        quote_amount=quote_amount,
        customer_id=customer_id
    )
    
    return "Approval request submitted - awaiting manager response"
""",
    pass_context=True,  # Optional: receive context dict
    is_async=True       # Mark as async
)
```

**Important**: 
- Async tools automatically receive a `tool_call_id` parameter to track the request
- Async tools should return an immediate acknowledgment string (e.g., "Request submitted", "Processing started", "Awaiting approval")
- This immediate response is added as a ToolMessage, satisfying the LLM's requirement for tool call/response pairing

### 2. Agent Invocation - Immediate Response

When an agent calls an async tool:

1. The tool function executes immediately
2. The `tool_call_id` is passed as a parameter
3. The tool returns a quick acknowledgment string (e.g., "Approval request submitted")
4. A ToolMessage is created with this acknowledgment
5. The agent continues processing and can generate responses or call other tools
6. The actual async operation continues in the background

### 3. Response Delivery

External systems send the async tool response to:

**Endpoint**: `POST /on-tool-call-response`

**Request Body**:
```json
{
  "context_id": "ctx-12345",
  "tool_call_id": "call_abc123",
  "response": "Approved by admin. Proceed with quote."
}
```

**Response**:
```json
{
  "success": true,
  "message": "Async tool response added to queue"
}
```

### 4. Response Processing - Simulated Tool Calls

The response is added to the context's `async_tool_response_queue`. On the next agent invocation (via `/chat`, `/chat/add-ai-message`, or `/chat/invoke`):

1. All queued responses are processed
2. For each async response, a **simulated tool call** is created:
   - Tool name: `{original_tool_name}_response` (e.g., `get_approval_response`)
   - Tool args: `{"original_tool_call_id": "call_abc123"}`
   - This is followed by a ToolMessage containing the actual async result
3. All simulated tool calls and responses are added to the message stack
4. The queue is cleared
5. The agent is invoked and sees the async results as new tool responses

**Note**: The `_response` tools don't actually exist in your tool registry. They're automatically generated to maintain proper tool call/response pairing in the conversation history.

### 5. Webhook Notification (Optional)

If your organization has a `webhook_url` configured, Ajentify will POST to it when an async response is received:

**Webhook Payload**:
```json
{
  "event_name": "async_tool_response_received",
  "payload": {
    "context_id": "ctx-12345",
    "tool_call_id": "call_abc123"
  }
}
```

This allows your system to automatically re-invoke the agent when async responses arrive.

## Implementation Guide

### Step 1: Create an Async Tool

```python
approval_tool = Tool.create_tool(
    org_id=organization_id,
    name="request_approval",
    description="Request approval from a manager for actions requiring authorization",
    code="""
def request_approval(action, details, tool_call_id, context):
    import requests
    
    # Send to your approval system
    requests.post('https://your-system.com/approvals', json={
        'tool_call_id': tool_call_id,
        'context_id': context['context_id'],
        'action': action,
        'details': details,
        'agent_id': context['agent_id']
    })
    
    return f"Approval request submitted for: {action}"
""",
    pass_context=True,
    is_async=True
)
```

### Step 2: Create an Agent with the Async Tool

```python
agent = Agent.create_agent(
    agent_name="sales-agent",
    agent_description="Sales agent that requires approval for large quotes",
    prompt='''You are a sales assistant. 

When providing quotes over $1000, you MUST use the request_approval tool first.
Wait for the approval response before confirming the quote to the customer.

You can answer other questions while waiting for approval.''',
    org_id=organization_id,
    tools=[approval_tool.tool_id],
    is_public=False
)
```

### Step 3: Set Up Webhook (Optional)

Configure your organization with a webhook URL to receive notifications:

```python
org = Organization.get_organization(organization_id)
org.webhook_url = "https://your-backend.com/webhooks/ajentify"
Organization.save_organization(org)
```

Your webhook endpoint should:
1. Receive the `async_tool_response_received` event
2. Extract `context_id` from the payload
3. Re-invoke the agent via `/chat/invoke` to process the response

### Step 4: Handle Approval in Your System

When your approval system makes a decision:

```python
import requests

# User approved the action
requests.post(
    'https://api.ajentify.com/on-tool-call-response',
    headers={
        'Authorization': f'Bearer {your_api_key}',
        'Content-Type': 'application/json'
    },
    json={
        'context_id': 'ctx-12345',
        'tool_call_id': 'call_abc123',
        'response': 'APPROVED: Manager John Smith approved the $5000 quote for customer ABC Corp.'
    }
)
```

### Step 5: Re-invoke the Agent (Manual or via Webhook)

After receiving the webhook notification, re-invoke the agent:

```python
requests.post(
    'https://api.ajentify.com/chat/invoke',
    headers={
        'Authorization': f'Bearer {your_api_key}',
        'Content-Type': 'application/json'
    },
    json={
        'context_id': 'ctx-12345',
        'save_ai_messages': True
    }
)
```

The agent will now process the approval response and continue the conversation.

## Complete Example: Approval Workflow

### Backend Setup (Python/Flask)

```python
from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)
AJENTIFY_API_KEY = os.environ['AJENTIFY_ORG_API_KEY']
AJENTIFY_API_BASE = 'https://api.ajentify.com'

# Store pending approvals (in production, use a database)
pending_approvals = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """Start a conversation with the sales agent"""
    data = request.json
    
    # Create context
    context_response = requests.post(
        f'{AJENTIFY_API_BASE}/context',
        headers={'Authorization': f'Bearer {AJENTIFY_API_KEY}'},
        json={'agent_id': 'your-sales-agent-id'}
    )
    context = context_response.json()
    
    # Send user message
    chat_response = requests.post(
        f'{AJENTIFY_API_BASE}/chat',
        headers={'Authorization': f'Bearer {AJENTIFY_API_KEY}'},
        json={
            'context_id': context['context_id'],
            'message': data['message'],
            'save_ai_messages': True
        }
    )
    
    return jsonify(chat_response.json())

@app.route('/webhooks/ajentify', methods=['POST'])
def ajentify_webhook():
    """Handle webhook from Ajentify when async tool response is received"""
    data = request.json
    
    if data['event_name'] == 'async_tool_response_received':
        context_id = data['payload']['context_id']
        tool_call_id = data['payload']['tool_call_id']
        
        # Re-invoke the agent to process the async response
        requests.post(
            f'{AJENTIFY_API_BASE}/chat/invoke',
            headers={'Authorization': f'Bearer {AJENTIFY_API_KEY}'},
            json={
                'context_id': context_id,
                'save_ai_messages': True
            }
        )
    
    return jsonify({'success': True})

@app.route('/approvals', methods=['POST'])
def receive_approval_request():
    """Receive approval requests from the async tool"""
    data = request.json
    
    # Store the approval request
    approval_id = data['tool_call_id']
    pending_approvals[approval_id] = {
        'context_id': data['context_id'],
        'action': data['action'],
        'details': data['details'],
        'status': 'pending'
    }
    
    # In production: send notification to admin via email, Slack, etc.
    print(f"Approval requested: {data['action']}")
    
    return jsonify({'success': True, 'approval_id': approval_id})

@app.route('/approvals/<approval_id>/respond', methods=['POST'])
def respond_to_approval(approval_id):
    """Admin approves or rejects the request"""
    data = request.json
    decision = data['decision']  # 'approved' or 'rejected'
    reason = data.get('reason', '')
    
    approval = pending_approvals.get(approval_id)
    if not approval:
        return jsonify({'error': 'Approval not found'}), 404
    
    # Send response back to Ajentify
    response_text = f"{decision.upper()}: {reason}" if reason else decision.upper()
    
    requests.post(
        f'{AJENTIFY_API_BASE}/on-tool-call-response',
        headers={'Authorization': f'Bearer {AJENTIFY_API_KEY}'},
        json={
            'context_id': approval['context_id'],
            'tool_call_id': approval_id,
            'response': response_text
        }
    )
    
    approval['status'] = decision
    
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(port=5000)
```

### Frontend (React)

```javascript
import React, { useState } from 'react';

function SalesChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  
  const sendMessage = async () => {
    if (!input.trim()) return;
    
    // Add user message to UI
    setMessages(prev => [...prev, { sender: 'user', text: input }]);
    
    // Send to backend
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input })
    });
    
    const data = await response.json();
    
    // Add agent response to UI
    setMessages(prev => [...prev, { sender: 'agent', text: data.response }]);
    
    setInput('');
  };
  
  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <input
        value={input}
        onChange={e => setInput(e.target.value)}
        onKeyPress={e => e.key === 'Enter' && sendMessage()}
        placeholder="Type a message..."
      />
    </div>
  );
}

export default SalesChat;
```

### Admin Approval Interface (React)

```javascript
import React, { useState, useEffect } from 'react';

function ApprovalDashboard() {
  const [approvals, setApprovals] = useState([]);
  
  useEffect(() => {
    // In production: fetch pending approvals from backend
    // For now, using mock data
  }, []);
  
  const handleApproval = async (approvalId, decision, reason) => {
    await fetch(`/approvals/${approvalId}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decision, reason })
    });
    
    // Remove from pending list
    setApprovals(prev => prev.filter(a => a.id !== approvalId));
  };
  
  return (
    <div className="approval-dashboard">
      <h2>Pending Approvals</h2>
      {approvals.map(approval => (
        <div key={approval.id} className="approval-card">
          <h3>{approval.action}</h3>
          <p>{approval.details}</p>
          <div className="approval-actions">
            <button
              onClick={() => handleApproval(approval.id, 'approved', 'Looks good')}
              className="btn-approve"
            >
              Approve
            </button>
            <button
              onClick={() => handleApproval(approval.id, 'rejected', 'Need more information')}
              className="btn-reject"
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ApprovalDashboard;
```

## Conversation Flow Example

### Step 1: Initial Request (Async Tool Called)
**User**: "I'd like a quote for 100 units at $50 each"

**Agent** calls `request_approval(amount=5000, customer="...")`
- Tool executes and returns: `"Approval request submitted - awaiting manager response"`
- ToolMessage created with this acknowledgment
- Messages: `[HumanMessage, AIMessage(tool_calls=[request_approval]), ToolMessage("Approval request submitted..."), AIMessage]`

**Agent**: "I've submitted your $5,000 quote for manager approval. While we wait, is there anything else I can help you with?"

### Step 2: Continued Conversation
**User**: "What's your delivery time?"

**Agent**: "Our standard delivery time is 2-3 business days. Expedited shipping is available for an additional fee."

*(Approval processing in background)*

### Step 3: Approval Response Received
*Admin approves the quote*
*External system calls* `/on-tool-call-response`:
```json
{
  "context_id": "ctx-123",
  "tool_call_id": "call_abc",
  "response": "APPROVED: Manager John Smith approved the $5,000 quote"
}
```
*Response added to `async_tool_response_queue`*
*Webhook triggers re-invocation*

### Step 4: Processing Async Response
On next invocation, `process_async_tool_response_queue()` creates:
- **Simulated tool call**: `request_approval_response(original_tool_call_id="call_abc")`
- **Tool response**: `"APPROVED: Manager John Smith approved the $5,000 quote"`
- Messages: `[..., AIMessage(tool_calls=[request_approval_response]), ToolMessage("APPROVED...")]`

**Agent** sees the approval and responds: "Great news! Your quote for $5,000 has been approved by Manager John Smith. Would you like me to proceed with the order?"

## Important Notes

### 1. Tool Call ID Parameter

- Async tools **always** receive `tool_call_id` as a parameter
- This is in addition to any custom parameters and the optional `context` parameter
- Use `tool_call_id` to track which tool call a response belongs to

### 2. Two-Phase Tool Responses

**Phase 1 - Immediate Acknowledgment:**
- Async tools return immediately with an acknowledgment string (e.g., "Request submitted", "Processing started")
- A ToolMessage is created with this acknowledgment
- This satisfies the LLM's requirement for tool call/response pairing
- The agent can continue conversing

**Phase 2 - Actual Result:**
- Later, the actual result arrives via `/on-tool-call-response`
- Response is queued in `async_tool_response_queue`
- On next invocation, a simulated tool call `{tool_name}_response` is created
- A ToolMessage with the actual result follows the simulated call
- The agent processes the real result

### 3. Queue Processing

- The `async_tool_response_queue` is processed **before** every agent invocation
- All queued responses are added as ToolMessages
- The queue is cleared after processing
- Responses appear at the end of the message history (maintaining chronological order)

### 4. Duplicate Responses

- If the same `tool_call_id` receives multiple responses, the **latest one replaces the old one**
- This prevents duplicate responses in the queue
- Useful if an approval is updated or corrected

### 5. Mixing Sync and Async Tools

- Agents can call both sync and async tools in the same turn
- **Sync tools**: Execute and return result immediately, ToolMessage created with result
- **Async tools**: Execute and return acknowledgment immediately, ToolMessage created with acknowledgment
- Both types create ToolMessages that satisfy the LLM's tool call/response requirements
- The agent continues processing after all tools (sync and async) return their immediate responses

### 6. Webhook Reliability

- Webhooks are "fire and forget" with a 5-second timeout
- If a webhook fails, it's logged but doesn't affect the response queuing
- Consider implementing manual re-invocation as a fallback

### 7. Authentication

- The `/on-tool-call-response` endpoint requires authentication
- The caller must have access to the organization that owns the context
- Use org API keys or user tokens with appropriate permissions

### 8. Agent Prompt Design

- Clearly instruct the agent on when to use async tools
- Explain that async tools return acknowledgments immediately (e.g., "request submitted")
- Guide the agent to inform users that processing is happening and they can continue conversing
- Prompt the agent to recognize and act on `{tool_name}_response` results when they arrive

### 9. Error Handling

- If an async tool throws an error during execution, the error is **not** captured as a ToolMessage
- External systems should send error messages via `/on-tool-call-response` if something goes wrong
- Format errors clearly so the agent can communicate them to the user

### 10. Context Management

- Long-running conversations with many async calls can grow the context
- Consider creating new contexts for new topics/sessions
- The `tool_call_id` only needs to be unique within a context

## API Reference

### Create Async Tool

**Endpoint**: `POST /tool`

**Request**:
```json
{
  "org_id": "org-123",
  "name": "async_operation",
  "description": "Performs an async operation",
  "code": "def async_operation(param, tool_call_id, context):\n    return 'Started'",
  "pass_context": true,
  "is_async": true
}
```

### Submit Async Tool Response

**Endpoint**: `POST /on-tool-call-response`

**Headers**:
```
Authorization: Bearer {your_api_key}
Content-Type: application/json
```

**Request**:
```json
{
  "context_id": "ctx-12345",
  "tool_call_id": "call_abc123",
  "response": "Operation completed successfully"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Async tool response added to queue"
}
```

### Configure Webhook

Update your organization with a webhook URL:

```python
org = Organization.get_organization(org_id)
org.webhook_url = "https://your-backend.com/webhooks"
Organization.save_organization(org)
```

**Webhook Event Format**:
```json
{
  "event_name": "async_tool_response_received",
  "payload": {
    "context_id": "ctx-12345",
    "tool_call_id": "call_abc123"
  }
}
```

## Troubleshooting

### Async Response Not Appearing

**Symptom**: Sent response via `/on-tool-call-response`, but agent doesn't acknowledge it

**Solutions**:
1. Verify the response was added to the queue: check `context.async_tool_response_queue`
2. Ensure the agent is re-invoked after the response is sent
3. Check that the `tool_call_id` matches an actual tool call in the context

### Webhook Not Being Called

**Symptom**: `/on-tool-call-response` succeeds, but webhook isn't triggered

**Solutions**:
1. Verify `organization.webhook_url` is set correctly
2. Check logs for webhook errors (they're logged but not raised)
3. Ensure your webhook endpoint is accessible and responding quickly (< 5s)

### Agent Doesn't Use Async Tool

**Symptom**: Agent never calls the async tool

**Solutions**:
1. Improve the tool's description to make its purpose clearer
2. Update the agent's prompt to explicitly mention when to use the tool
3. Provide examples in the prompt showing the tool in action

### Tool Call ID Mismatch

**Symptom**: Error about tool_call_id when calling async tool

**Solutions**:
1. Ensure `tool_call_id` is listed as a parameter in your tool's function signature
2. Don't pass `tool_call_id` manually - it's automatically injected

## Related Documentation

- [Additional Agent Tools](./additional-agent-tools.md) - Add context-specific tools
- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results
- [Message Control Endpoints](./message-control-endpoints.md) - Control message saving and generation
- [API Keys](./api-keys.md) - Authentication for API access

