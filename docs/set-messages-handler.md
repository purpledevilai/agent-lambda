# Set Messages Handler

This document explains how the `SetMessagesHandler` works and provides examples for all supported message types. Use this endpoint when you need to **replace all messages** in a context rather than appending to them.

## Overview

The `POST /context/set-messages` endpoint **replaces** every message in an existing context with the messages you provide. Unlike `add-messages`, which appends to the conversation, `set-messages` clears the existing history and sets a new one.

### Use Cases

- **Reset a conversation** – Start fresh with new messages
- **Load a pre-constructed history** – Restore a saved conversation state
- **Branch or replay conversations** – Set a specific point in a conversation and continue from there
- **Testing** – Seed a context with a known state before testing agent behavior

---

## Request Format

```json
{
  "context_id": "uuid-of-existing-context",
  "messages": [
    // Array of message objects (see types below)
  ]
}
```

| Parameter   | Type   | Required | Description                                                |
|------------|--------|----------|------------------------------------------------------------|
| `context_id` | string | Yes      | ID of the context whose messages you want to replace       |
| `messages`   | array  | Yes      | New messages to set. Replaces all existing messages.       |

---

## Message Types

There are three message types supported. Each has a different shape in the request body.

### 1. FilteredMessage (Human, AI, or System)

Standard conversational messages. Use `sender` to distinguish who sent the message.

```json
{
  "sender": "human" | "ai" | "system",
  "message": "The message content as a string"
}
```

| Field    | Type   | Description                                      |
|----------|--------|--------------------------------------------------|
| `sender` | string | One of: `"human"`, `"ai"`, `"system"`           |
| `message`| string | The text content of the message                  |

**Examples:**

```json
{ "sender": "human", "message": "Hello, how can you help me today?" }
{ "sender": "ai", "message": "I can help you with a variety of tasks. What would you like to do?" }
{ "sender": "system", "message": "You are a helpful assistant. Be concise." }
```

---

### 2. ToolCallMessage

Represents the AI calling a tool. Must be paired with a `ToolResponseMessage` that has the same `tool_call_id`.

```json
{
  "type": "tool_call",
  "tool_call_id": "unique-id-for-this-call",
  "tool_name": "name_of_the_tool",
  "tool_input": {}
}
```

| Field         | Type   | Required | Description                                  |
|---------------|--------|----------|----------------------------------------------|
| `type`        | string | Yes      | Must be `"tool_call"`                        |
| `tool_call_id`| string | Yes      | Unique ID that links to the tool response    |
| `tool_name`   | string | Yes      | Name of the tool being called                |
| `tool_input`  | object | No       | Arguments for the tool (defaults to `{}`)    |

**Examples:**

```json
{
  "type": "tool_call",
  "tool_call_id": "call_abc123",
  "tool_name": "search_database",
  "tool_input": { "query": "active users", "limit": 10 }
}
```

```json
{
  "type": "tool_call",
  "tool_call_id": "call_xyz789",
  "tool_name": "get_weather",
  "tool_input": { "location": "San Francisco" }
}
```

---

### 3. ToolResponseMessage

Represents the output returned by a tool. Must reference a `ToolCallMessage` with the same `tool_call_id` that appears earlier in the `messages` array.

```json
{
  "type": "tool_response",
  "tool_call_id": "same-id-as-corresponding-tool-call",
  "tool_output": "String output from the tool"
}
```

| Field         | Type   | Required | Description                                 |
|---------------|--------|----------|---------------------------------------------|
| `type`        | string | Yes      | Must be `"tool_response"`                   |
| `tool_call_id`| string | Yes      | Must match a preceding `tool_call` ID       |
| `tool_output` | string | Yes      | The tool's result as a string               |

**Example:**

```json
{
  "type": "tool_response",
  "tool_call_id": "call_abc123",
  "tool_output": "Found 5 active users: Alice, Bob, Carol, Dave, Eve."
}
```

---

## Validation Rules

The handler validates messages before saving:

1. **Tool responses need tool calls** – Every `tool_response` must have a matching `tool_call` with the same `tool_call_id` earlier in the list.
2. **Order** – A tool response must come after its tool call.
3. **No orphan tool calls** – Every `tool_call` must have a matching `tool_response`.

Violations raise a `ValueError` with a descriptive message, e.g.:

- `"Tool response with ID 'call_xyz' appears before its corresponding tool call"`
- `"Tool calls found without corresponding responses: {'call_abc'}"`
- `"Tool responses found without corresponding tool calls: {'call_xyz'}"`

---

## Complete Examples

### Example 1: Simple Reset (Human + AI)

Replace everything with a short conversation:

```json
{
  "context_id": "ctx_123",
  "messages": [
    { "sender": "human", "message": "Start fresh" },
    { "sender": "ai", "message": "Hello! How can I help you today?" }
  ]
}
```

---

### Example 2: System Prompt + Human + AI

Include a system message for instructions:

```json
{
  "context_id": "ctx_123",
  "messages": [
    { "sender": "system", "message": "You are a formal business assistant. Use professional language." },
    { "sender": "human", "message": "What's the status of project X?" },
    { "sender": "ai", "message": "I would need to check the project database to provide an accurate status update." }
  ]
}
```

---

### Example 3: Conversation with Tool Calls

Human asks for data, AI calls a tool, tool returns results, AI replies:

```json
{
  "context_id": "ctx_123",
  "messages": [
    { "sender": "human", "message": "Search for active users in the system" },
    {
      "type": "tool_call",
      "tool_call_id": "call_search_001",
      "tool_name": "search_users",
      "tool_input": { "status": "active" }
    },
    {
      "type": "tool_response",
      "tool_call_id": "call_search_001",
      "tool_output": "Found 3 active users: user1, user2, user3"
    },
    { "sender": "ai", "message": "I found 3 active users: user1, user2, and user3. Would you like details on any of them?" }
  ]
}
```

---

### Example 4: Multiple Tool Calls in One Turn

One AI turn with multiple tool calls, each with its own response:

```json
{
  "context_id": "ctx_123",
  "messages": [
    { "sender": "human", "message": "Get the weather and my calendar for today" },
    {
      "type": "tool_call",
      "tool_call_id": "call_weather_001",
      "tool_name": "get_weather",
      "tool_input": { "date": "today" }
    },
    {
      "type": "tool_call",
      "tool_call_id": "call_calendar_001",
      "tool_name": "get_calendar_events",
      "tool_input": { "date": "today" }
    },
    {
      "type": "tool_response",
      "tool_call_id": "call_weather_001",
      "tool_output": "Sunny, 72°F"
    },
    {
      "type": "tool_response",
      "tool_call_id": "call_calendar_001",
      "tool_output": "Meeting at 2pm, Dentist at 4pm"
    },
    {
      "sender": "ai",
      "message": "Today will be sunny (72°F). You have a meeting at 2pm and a dentist appointment at 4pm."
    }
  ]
}
```

---

### Example 5: Empty Context (Reset to Nothing)

Clear all messages by passing an empty array:

```json
{
  "context_id": "ctx_123",
  "messages": []
}
```

---

### Example 6: Loading a Pre-constructed History

Restore a saved multi-turn conversation:

```json
{
  "context_id": "ctx_123",
  "messages": [
    { "sender": "system", "message": "You are a travel assistant." },
    { "sender": "human", "message": "I want to visit Paris" },
    { "sender": "ai", "message": "Paris is a great choice! When are you planning to go?" },
    { "sender": "human", "message": "Next month" },
    { "sender": "ai", "message": "I can help you plan your trip for next month. Would you like flight recommendations, hotels, or both?" }
  ]
}
```

---

## API Request Example

```bash
curl -X POST https://api.example.com/context/set-messages \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "context_id": "ctx_123",
    "messages": [
      { "sender": "human", "message": "Hello" },
      { "sender": "ai", "message": "Hi there! How can I help?" }
    ]
  }'
```

---

## Response

Returns the updated context in filtered format (with tool calls visible):

```json
{
  "context_id": "ctx_123",
  "agent_id": "agent_456",
  "user_id": "user_789",
  "messages": [
    { "sender": "human", "message": "Hello" },
    { "sender": "ai", "message": "Hi there! How can I help?" }
  ],
  "user_defined": {},
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

---

## How It Works (Internal Flow)

1. **Parse request** – Extracts `context_id` and `messages` from the request body.
2. **Load context** – Fetches the context (user-specific or public based on auth).
3. **Validate messages** – Ensures tool calls and tool responses are correctly paired and ordered.
4. **Convert format** – Converts filtered message types to the internal dict format stored in DynamoDB.
5. **Replace messages** – Replaces `context.messages` with the new list (does not merge or append).
6. **Save** – Persists the context and returns the filtered representation.

---

## Authentication

- **Authenticated requests** – Replace messages in contexts owned by the authenticated user.
- **Public contexts** – Can be modified without auth if the context is public.

---

## Related Endpoints

| Endpoint | Behavior |
|----------|----------|
| `POST /context/add-messages` | **Appends** messages to the existing conversation |
| `POST /context/set-messages` | **Replaces** all messages in the conversation |

For more details on the broader message control API, see [message-control-endpoints.md](./message-control-endpoints.md).
