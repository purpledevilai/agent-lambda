# Message Control Endpoints

This document describes the new endpoints that give you fine-grained control over message generation and storage in conversations.

## Table of Contents
- [Overview](#overview)
- [POST /chat (Enhanced)](#post-chat-enhanced)
- [POST /chat/add-ai-message (Enhanced)](#post-chatadd-ai-message-enhanced)
- [POST /chat/invoke](#post-chatinvoke)
- [POST /context/add-messages](#post-contextadd-messages)
- [POST /context/set-messages](#post-contextset-messages)
- [Use Cases](#use-cases)
- [Message Types](#message-types)

---

## Overview

The message control endpoints allow you to:
- Generate AI responses without saving them (preview mode)
- Manually construct conversations with custom messages
- Approve or modify AI-generated messages before saving
- Continue conversations from manually-added messages
- Build complex multi-turn conversations with tool calls

### Key Concepts

**Human messages are always saved** - When you send a message to `/chat`, the human message is immediately saved to the context. Only the AI-generated response is controlled by the `save_ai_messages` flag.

**Generated messages include tool interactions** - The `generated_messages` field includes not just the final AI response, but also any tool calls and tool responses that occurred during generation.

---

## POST /chat (Enhanced)

The standard chat endpoint now supports conditional saving of AI-generated messages and returns detailed information about what was generated.

### Request

```json
{
  "context_id": "uuid",
  "message": "Your message here",
  "save_ai_messages": true  // Optional, defaults to true
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `context_id` | string | Yes | - | The context/conversation ID |
| `message` | string | Yes | - | The human message to send |
| `save_ai_messages` | boolean | No | `true` | Whether to save AI-generated messages to the context |

### Response

```json
{
  "response": "The final AI response text",
  "saved_ai_messages": true,
  "generated_messages": [
    {
      "type": "tool_call",
      "tool_call_id": "call_abc123",
      "tool_name": "search_database",
      "tool_input": { "query": "user data" }
    },
    {
      "type": "tool_response",
      "tool_call_id": "call_abc123",
      "tool_output": "Found 5 results"
    },
    {
      "sender": "ai",
      "message": "I found 5 matching results for you."
    }
  ],
  "events": []  // Optional, if the agent triggered any events
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `response` | string | The final AI response text (for backwards compatibility) |
| `saved_ai_messages` | boolean | Whether the AI messages were saved to the context |
| `generated_messages` | array | All messages generated during this turn (tool calls, tool responses, and AI messages) |
| `events` | array | Optional events triggered by tools during generation |

### Behavior

1. **Human message is saved immediately** to the context
2. **AI generates a response**, potentially calling tools
3. **If `save_ai_messages` is `true`** (default):
   - All AI-generated messages are saved to the context
4. **If `save_ai_messages` is `false`**:
   - AI-generated messages are NOT saved
   - The human message remains in the context
   - You receive the generated messages for review/approval

### Example: Preview Mode

```bash
# Generate a response without saving it
curl -X POST https://api.example.com/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "message": "What is the weather?",
    "save_ai_messages": false
  }'
```

**Use Case**: Preview the AI's response before committing it to the conversation history. You can then approve, modify, or regenerate.

---

## POST /chat/add-ai-message (Enhanced)

Add an AI message to the context, either as a pre-written message or by providing a prompt that causes the agent to generate a response.

### Request

```json
{
  "context_id": "uuid",
  "message": "Pre-written AI message",  // Optional, mutually exclusive with prompt
  "prompt": "Additional instructions",  // Optional, mutually exclusive with message
  "save_ai_messages": true,  // Optional, defaults to true (only applies when using prompt)
  "save_system_message": true  // Optional, defaults to true (only applies when using prompt)
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `context_id` | string | Yes | - | The context/conversation ID |
| `message` | string | No | - | A pre-written AI message to add directly (always saved) |
| `prompt` | string | No | - | A system prompt to add before invoking the agent |
| `save_ai_messages` | boolean | No | `true` | Whether to save AI-generated messages (only applies when using `prompt`) |
| `save_system_message` | boolean | No | `true` | Whether to save the system prompt message (only applies when using `prompt`) |

**Note**: You must provide either `message` OR `prompt`, but not both.

### Response

Same format as `/chat` endpoint:

```json
{
  "response": "The AI response or the message you provided",
  "saved_ai_messages": true,
  "generated_messages": [...],  // Empty if using 'message', populated if using 'prompt'
  "events": []
}
```

### Behavior

#### When using `message` parameter:
1. The pre-written message is added directly to the context as an AI message
2. **Always saved** (the `save_ai_messages` and `save_system_message` flags don't apply)
3. Returns empty `generated_messages` array
4. `saved_ai_messages` is always `true`

#### When using `prompt` parameter:

The behavior depends on the combination of `save_system_message` and `save_ai_messages` flags:

**Case 1: `save_system_message=true, save_ai_messages=true` (default)**
- System message with prompt is added and saved
- Agent is invoked to generate a response
- AI-generated messages are saved
- Result: Both system message and AI response are in the context

**Case 2: `save_system_message=true, save_ai_messages=false`**
- System message with prompt is added and saved
- Agent is invoked to generate a response
- AI-generated messages are NOT saved
- Result: Only the system message remains in the context
- Use case: Save the prompt for context but preview the AI response

**Case 3: `save_system_message=false, save_ai_messages=true`**
- System message with prompt is added temporarily (for generation only)
- Agent is invoked to generate a response
- System message is removed before saving
- AI-generated messages are saved
- Result: Only the AI response is in the context (prompt was temporary)
- Use case: **Temporary steering** - guide the agent without permanently affecting context

**Case 4: `save_system_message=false, save_ai_messages=false`**
- System message with prompt is added temporarily
- Agent is invoked to generate a response
- Neither system message nor AI messages are saved
- Result: Context remains unchanged
- Use case: **Full preview mode** - test prompts without any permanent changes

### Example 1: Add Pre-written Message

```bash
# Add a pre-written AI message directly
curl -X POST https://api.example.com/chat/add-ai-message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "message": "I have processed your request successfully."
  }'
```

**Use Case**: Manually insert AI messages for conversation construction or branching.

### Example 2: Temporary Steering (Most Powerful Use Case)

```bash
# Temporarily guide the agent without saving the prompt
curl -X POST https://api.example.com/chat/add-ai-message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "prompt": "Respond in a formal tone and keep it brief",
    "save_system_message": false,
    "save_ai_messages": true
  }'
```

**Use Case**: **Temporary steering** - The prompt guides the agent's response, but only the AI's response is saved. The prompt doesn't permanently affect the context. Perfect for one-time adjustments or style changes.

### Example 3: Full Preview Mode

```bash
# Test a prompt without saving anything
curl -X POST https://api.example.com/chat/add-ai-message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "prompt": "Respond with technical details",
    "save_system_message": false,
    "save_ai_messages": false
  }'
```

**Use Case**: Experiment with different prompts to see how the agent responds without making any changes to the context.

### Example 4: Save Prompt, Preview Response

```bash
# Save the prompt but not the AI response
curl -X POST https://api.example.com/chat/add-ai-message \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "prompt": "Consider the user is a beginner",
    "save_system_message": true,
    "save_ai_messages": false
  }'
```

**Use Case**: Add context for future messages but preview the immediate response before committing it.

---

## POST /chat/invoke

Invoke the agent to generate a response without adding a new human message. This is useful for continuing conversations after manually adding messages or having the agent respond to tool calls.

### Request

```json
{
  "context_id": "uuid",
  "save_ai_messages": true  // Optional, defaults to true
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `context_id` | string | Yes | - | The context/conversation ID |
| `save_ai_messages` | boolean | No | `true` | Whether to save AI-generated messages to the context |

### Response

Same format as `/chat` endpoint:

```json
{
  "response": "The AI response",
  "saved_ai_messages": true,
  "generated_messages": [...],
  "events": []
}
```

### Example: Continue After Manual Messages

```bash
# After adding messages manually, invoke the agent to respond
curl -X POST https://api.example.com/chat/invoke \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "save_ai_messages": true
  }'
```

**Use Case**: After manually constructing a conversation with tool calls, invoke the agent to generate the next response based on the tool outputs.

---

## POST /context/add-messages

Append messages to an existing context. Messages are validated to ensure tool calls and responses are properly paired.

### Request

```json
{
  "context_id": "uuid",
  "messages": [
    {
      "sender": "human",
      "message": "Hello!"
    },
    {
      "sender": "ai",
      "message": "Hi there! How can I help?"
    }
  ]
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context_id` | string | Yes | The context/conversation ID |
| `messages` | array | Yes | Array of message objects to append |

### Message Validation

The endpoint validates that:
1. Every tool response has a corresponding tool call with matching ID
2. Tool calls appear before their corresponding responses
3. All tool calls have matching tool responses

### Response

Returns the updated context with all messages (filtered format with tool calls visible):

```json
{
  "context_id": "ctx_123",
  "agent_id": "agent_456",
  "user_id": "user_789",
  "messages": [
    {
      "sender": "human",
      "message": "Hello!"
    },
    {
      "sender": "ai",
      "message": "Hi there! How can I help?"
    }
  ],
  "user_defined": {},
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

### Example: Approve Generated Messages

```bash
# After generating messages with save_ai_messages=false, approve and save them
curl -X POST https://api.example.com/context/add-messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "messages": [
      {
        "type": "tool_call",
        "tool_call_id": "call_abc",
        "tool_name": "search",
        "tool_input": {"query": "test"}
      },
      {
        "type": "tool_response",
        "tool_call_id": "call_abc",
        "tool_output": "Found results"
      },
      {
        "sender": "ai",
        "message": "Here are the results"
      }
    ]
  }'
```

**Use Case**: Save AI-generated messages after reviewing and approving them.

---

## POST /context/set-messages

Replace all messages in a context with new messages. Useful for resetting or completely reconstructing a conversation.

### Request

```json
{
  "context_id": "uuid",
  "messages": [
    {
      "sender": "human",
      "message": "Start fresh"
    }
  ]
}
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `context_id` | string | Yes | The context/conversation ID |
| `messages` | array | Yes | Array of message objects to replace all existing messages |

### Message Validation

Same validation as `/context/add-messages`.

### Response

Returns the updated context (same format as add-messages).

### Example: Reset Conversation

```bash
# Replace all messages with a fresh start
curl -X POST https://api.example.com/context/set-messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "messages": [
      {
        "sender": "system",
        "message": "This is a fresh conversation"
      },
      {
        "sender": "human",
        "message": "Hello, starting over"
      }
    ]
  }'
```

**Use Case**: Reset a conversation or load a pre-constructed conversation history.

---

## Use Cases

### 1. Preview and Approve Workflow

Generate AI responses for review before committing them:

```javascript
// Step 1: Generate without saving
const previewResponse = await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    message: 'What should I do?',
    save_ai_messages: false
  })
});

const preview = await previewResponse.json();
// Review preview.generated_messages

// Step 2: If approved, save them
if (userApproved) {
  await fetch('/context/add-messages', {
    method: 'POST',
    body: JSON.stringify({
      context_id: 'ctx_123',
      messages: preview.generated_messages
    })
  });
}
```

### 2. Manual Tool Call Construction

Manually construct a conversation with tool calls, then let the agent respond:

```javascript
// Step 1: Add manual tool interaction
await fetch('/context/add-messages', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    messages: [
      {
        sender: 'human',
        message: 'Search for user data'
      },
      {
        type: 'tool_call',
        tool_call_id: 'call_1',
        tool_name: 'database_search',
        tool_input: { table: 'users', query: 'active' }
      },
      {
        type: 'tool_response',
        tool_call_id: 'call_1',
        tool_output: 'Found 100 active users'
      }
    ]
  })
});

// Step 2: Invoke agent to respond to the tool results
const response = await fetch('/chat/invoke', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    save_ai_messages: true
  })
});
```

### 3. Multi-Agent Conversations

Construct conversations between multiple agents or personas:

```javascript
// Build a conversation with multiple agents
await fetch('/context/set-messages', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    messages: [
      { sender: 'human', message: 'Agent 1, what do you think?' },
      { sender: 'ai', message: 'I think option A is best.' },
      { sender: 'human', message: 'Agent 2, your opinion?' },
      { sender: 'ai', message: 'I prefer option B.' }
    ]
  })
});
```

### 4. Testing and Debugging

Test agent behavior with specific conversation states:

```javascript
// Set up a specific conversation state for testing
await fetch('/context/set-messages', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'test_ctx',
    messages: [
      // ... specific test scenario
    ]
  })
});

// Generate response and verify behavior
const response = await fetch('/chat/invoke', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'test_ctx',
    save_ai_messages: false
  })
});
```

---

## Message Types

### FilteredMessage

Represents a standard conversational message (human, AI, or system).

```json
{
  "sender": "human" | "ai" | "system",
  "message": "The message content"
}
```

### ToolCallMessage

Represents the agent calling a tool.

```json
{
  "type": "tool_call",
  "tool_call_id": "unique_call_id",
  "tool_name": "name_of_tool",
  "tool_input": {
    // Tool-specific parameters
  }
}
```

### ToolResponseMessage

Represents the output from a tool call.

```json
{
  "type": "tool_response",
  "tool_call_id": "matching_call_id",
  "tool_output": "The tool's output as a string"
}
```

### Message Ordering Rules

1. Tool responses must come after their corresponding tool calls
2. Tool call IDs must match between calls and responses
3. Every tool call must have a corresponding tool response (when using add-messages or set-messages)

---

## Authentication

All endpoints respect the same authentication strategy:
- **Authenticated requests**: Include `Authorization: Bearer <token>` header
- **Public contexts**: Can be accessed without authentication if the context is public
- **Private contexts**: Require authentication and ownership validation

---

## Error Responses

### Validation Errors

```json
{
  "error": "Tool responses found without corresponding tool calls: ['call_123']"
}
```

### Permission Errors

```json
{
  "error": "Context does not belong to user"
}
```

### Not Found Errors

```json
{
  "error": "Context with id: ctx_123 does not exist"
}
```

---

## Best Practices

1. **Use preview mode for sensitive operations**: Set `save_ai_messages: false` when generating responses that might need review
2. **Validate tool calls**: Ensure tool call IDs are unique and match between calls and responses
3. **Preserve message order**: When manually constructing conversations, maintain logical message flow
4. **Handle errors gracefully**: Check for validation errors when adding messages with tool calls
5. **Monitor context size**: Be mindful of conversation length when using set-messages to avoid token limits

---

## Migration Guide

If you're upgrading from the old `/chat` endpoint:

### Old Behavior
```javascript
// All messages were always saved
const response = await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    message: 'Hello'
  })
});
```

### New Behavior (Backwards Compatible)
```javascript
// Default behavior is the same (save_ai_messages defaults to true)
const response = await fetch('/chat', {
  method: 'POST',
  body: JSON.stringify({
    context_id: 'ctx_123',
    message: 'Hello'
    // save_ai_messages: true (implicit)
  })
});

// Response now includes additional fields
const data = await response.json();
console.log(data.saved_ai_messages);      // true
console.log(data.generated_messages);     // Array of generated messages
```

**Breaking Changes**: None - the default behavior is unchanged. The new features are opt-in.

---

## Support

For issues or questions about these endpoints, please refer to the test suite in:
- `tests/test_chat.py` - Chat and invoke endpoint tests
- `tests/test_context.py` - Add/set messages endpoint tests

