# Client Side Tools

## Overview

Client Side Tools allow an agent's tool calls to be routed to the frontend for processing instead of being executed on the server. This is useful when a tool's behavior depends on the client environment -- for example, showing a confirmation dialog, rendering a custom UI component, accessing device APIs, or triggering browser-side logic.

When the LLM calls a tool that is marked as a client-side tool, the server does **not** execute it. Instead, the tool call parameters are returned to the client. The client processes the tool, then sends the result back to the server, which continues the agent's invocation.

## How It Works

```
1. Client sends a chat message
2. LLM responds with tool calls (may include server-side and client-side tools)
3. Server executes all server-side tools normally
4. Server returns client-side tool calls to the client (without executing them)
5. Client processes the client-side tools
6. Client sends tool responses back to the server
7. Server adds the responses as ToolMessages and continues invocation
8. LLM produces a final response (or triggers more tool calls)
```

If the LLM calls multiple tools in a single turn, the server processes all server-side tools first, then returns any client-side tools to the client. The client must respond with results for **all** client-side tool calls at once.

## Creating a Client Side Tool

A client-side tool is created like any other tool, but with `is_client_side_tool` set to `true` and no `code` field.

### REST API

```
POST /tool
```

```json
{
  "name": "show_confirmation_dialog",
  "description": "Show a confirmation dialog to the user and return their response",
  "pd_id": "<parameter_definition_id>",
  "is_client_side_tool": true
}
```

The `code` field is not required (and is ignored) for client-side tools. The `pd_id` field defines the tool's parameters, which the LLM will populate and pass to the client.

### Programmatically

```python
tool = Tool.create_tool(
    org_id="...",
    name="show_confirmation_dialog",
    description="Show a confirmation dialog to the user",
    pd_id="...",
    is_client_side_tool=True
)
```

## REST API Flow

### 1. Chat triggers client-side tool calls

When the agent calls a client-side tool, the `ChatResponse` includes a `client_side_tool_calls` field:

```
POST /chat
```

```json
{
  "context_id": "...",
  "message": "Please confirm that I want to delete my account"
}
```

Response:

```json
{
  "response": "",
  "saved_ai_messages": true,
  "generated_messages": [...],
  "client_side_tool_calls": [
    {
      "tool_call_id": "call_abc123",
      "tool_name": "show_confirmation_dialog",
      "tool_input": {
        "message": "Are you sure you want to delete your account?"
      }
    }
  ]
}
```

The `client_side_tool_calls` field is `null` when no client-side tools were called.

### 2. Submit client-side tool responses

After the client processes the tool calls, it sends the results back:

```
POST /chat/client-side-tool-responses
```

```json
{
  "context_id": "...",
  "tool_responses": [
    {
      "tool_call_id": "call_abc123",
      "response": "User confirmed: yes, delete the account"
    }
  ]
}
```

Response (standard `ChatResponse`):

```json
{
  "response": "Your account has been deleted.",
  "saved_ai_messages": true,
  "generated_messages": [...],
  "client_side_tool_calls": null
}
```

The response may contain another round of `client_side_tool_calls` if the agent decides to call more client-side tools after processing the previous responses.

**All client-side tool calls from the last AI message must be included.** The endpoint returns a 400 error if any are missing.

## WebSocket (Token Streaming) Flow

For the TokenStreamingServer, client-side tools work over the existing WebSocket connection.

### 1. Server sends `on_client_side_tool_calls` event

After processing a message (via `add_message` or other handlers), if client-side tools are pending, the server sends:

```json
{
  "method": "on_client_side_tool_calls",
  "params": {
    "tool_calls": [
      {
        "tool_call_id": "call_abc123",
        "tool_name": "show_confirmation_dialog",
        "tool_input": { "message": "Are you sure?" }
      }
    ],
    "response_id": "uuid"
  }
}
```

This event fires after `on_stop_token`, so the client knows streaming is complete before handling tool calls.

### 2. Client sends `client_side_tool_responses`

The client calls back with the results:

```json
{
  "method": "client_side_tool_responses",
  "params": {
    "tool_responses": [
      {
        "tool_call_id": "call_abc123",
        "response": "User confirmed: yes"
      }
    ]
  }
}
```

The server then continues invocation and streams the agent's response back via `on_token` / `on_stop_token` as usual.

### Frontend (TypeScript)

The `TokenStreamingService` class provides built-in support:

```typescript
import { TokenStreamingService, ClientSideToolCall, ClientSideToolResponse } from './TokenStreamingService';

const service = new TokenStreamingService(url, contextId, accessToken);

service.setOnClientSideToolCalls(async (toolCalls: ClientSideToolCall[], responseId: string) => {
  const responses: ClientSideToolResponse[] = toolCalls.map(tc => ({
    tool_call_id: tc.tool_call_id,
    response: processToolLocally(tc.tool_name, tc.tool_input)
  }));

  await service.sendClientSideToolResponses(responses);
});

await service.connect();
```

## Mixed Tools

An agent can have both server-side and client-side tools. When the LLM calls multiple tools in a single turn:

1. Server-side tools execute immediately on the server
2. Client-side tools are collected and returned to the client
3. The client sends all client-side tool responses at once
4. The server adds ToolMessages for the client-side responses and continues invocation

Async tools and terminating tools are always server-side and are unaffected by this feature.

## Model Changes

| Model | Field | Type | Default |
|-------|-------|------|---------|
| `Tool` | `is_client_side_tool` | `bool` | `False` |
| `CreateToolParams` | `is_client_side_tool` | `bool` | `False` |
| `UpdateToolParams` | `is_client_side_tool` | `Optional[bool]` | `None` |
| `AgentTool` | `is_client_side_tool` | `bool` | `False` |
| `ChatResponse` | `client_side_tool_calls` | `Optional[List[ClientSideToolCall]]` | `None` |

## Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat/client-side-tool-responses` | POST | Submit client-side tool responses and continue invocation |

WebSocket handler: `client_side_tool_responses`

WebSocket event: `on_client_side_tool_calls`
