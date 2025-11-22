# Context Initialization with Tools

## Overview

When creating a new context, you can now initialize it with one or more tool calls. This allows you to pre-populate the context with tool responses before the agent starts its conversation, providing it with essential data or state from the beginning.

## Endpoint

**POST** `/context`

## Request Body

```json
{
  "agent_id": "string (required)",
  "invoke_agent_message": "boolean (optional, default: false)",
  "prompt_args": "object (optional)",
  "user_defined": "object (optional)",
  "initialize_tools": [
    {
      "tool_id": "string (required)",
      "tool_input": "object (required)"
    }
  ]
}
```

### New Field: `initialize_tools`

An optional array of tools to execute when creating the context. Each tool is defined by:

- **`tool_id`**: The unique identifier of the tool to execute. This can be:
  - A custom tool belonging to the agent's organization
  - A built-in Ajentify tool (e.g., `open_data_window`, `web_search`, etc.)
  
- **`tool_input`**: An object containing the parameters to pass to the tool. The keys and values should match the tool's expected parameters.

## How It Works

### 1. Tool Permission Validation

When you provide `initialize_tools`, the system validates that each tool is accessible:

- **Organization Tools**: The tool must belong to the agent's organization
- **Built-in Tools**: The tool must be in the default Ajentify tool registry
- If a tool doesn't meet either criterion, a `403` permission error is thrown

### 2. Execution Order

Tools are executed in a specific order:

1. **Agent's Default Initialization Tool** (if configured)
   - If the agent has an `initialize_tool_id` set, it executes first
   - This tool is called with empty parameters: `{}`
   - This maintains backwards compatibility with existing agents

2. **User-Provided Initialization Tools**
   - Tools from the `initialize_tools` array execute in the order provided
   - Each tool receives its specified `tool_input` parameters

### 3. Message Structure

All initialization tools are grouped into a single AI message with multiple tool calls:

```
AIMessage (content: "", tool_calls: [...])
  ↓
ToolMessage (tool_call_id: "uuid-1", content: "result 1")
  ↓
ToolMessage (tool_call_id: "uuid-2", content: "result 2")
  ↓
... (additional tool messages)
```

This structure ensures the context history accurately reflects that the agent "called" these tools at initialization.

### 4. Context Passing

If a tool requires context (i.e., `tool.pass_context = True`), the system automatically passes the context dictionary to the tool function. This allows tools to access information like:
- `agent_id`
- `org_id`
- `user_id`
- `prompt_args`
- `user_defined`

### 5. Error Handling (Fail-Fast)

The system uses a **fail-fast** approach:

- If any tool execution fails, the entire context creation fails
- The error is raised immediately, preventing partial initialization
- This ensures contexts are only created when all initialization succeeds

## Use Cases

### 1. Opening a DataWindow

Pre-load fresh data into the agent's context:

```json
{
  "agent_id": "my-agent-id",
  "initialize_tools": [
    {
      "tool_id": "open_data_window",
      "tool_input": {
        "data_window_id": "activity-feed-123"
      }
    }
  ]
}
```

### 2. Multiple Tool Initialization

Initialize context with data from multiple sources:

```json
{
  "agent_id": "my-agent-id",
  "initialize_tools": [
    {
      "tool_id": "open_data_window",
      "tool_input": {
        "data_window_id": "user-profile-456"
      }
    },
    {
      "tool_id": "open_data_window",
      "tool_input": {
        "data_window_id": "recent-activity-789"
      }
    },
    {
      "tool_id": "read_memory",
      "tool_input": {
        "path": "user.preferences"
      }
    }
  ]
}
```

### 3. Custom Organization Tools

Use your own custom tools during initialization:

```json
{
  "agent_id": "my-agent-id",
  "initialize_tools": [
    {
      "tool_id": "fetch_customer_data",
      "tool_input": {
        "customer_id": "cust-123",
        "include_history": true
      }
    }
  ]
}
```

## Example: Complete Request

```bash
curl -X POST https://api.ajentify.com/context \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-abc-123",
    "invoke_agent_message": false,
    "initialize_tools": [
      {
        "tool_id": "open_data_window",
        "tool_input": {
          "data_window_id": "customer-feed-xyz"
        }
      }
    ]
  }'
```

## Example: Response

The response includes the initialized context with tool messages:

```json
{
  "context_id": "ctx-def-456",
  "agent_id": "agent-abc-123",
  "created_at": 1699999999,
  "updated_at": 1699999999,
  "messages": [
    {
      "type": "tool_call",
      "tool_call_id": "uuid-generated-1",
      "tool_name": "open_data_window",
      "tool_input": {
        "data_window_id": "customer-feed-xyz"
      }
    },
    {
      "type": "tool_response",
      "tool_call_id": "uuid-generated-1",
      "tool_output": "Customer feed data: ..."
    }
  ]
}
```

## Important Notes

### Backwards Compatibility

- Existing agents with `initialize_tool_id` continue to work
- The default initialization tool executes first, followed by any tools in `initialize_tools`
- If you only want to use `initialize_tools`, simply don't set `initialize_tool_id` on your agent

### Parameter Validation

- Tool parameters are validated when the tool executes
- If you provide incorrect parameters (wrong types, missing required fields, etc.), the tool execution will fail and raise an error
- Make sure your `tool_input` matches the tool's expected parameter schema

### Permission Model

- You can only use tools that either:
  - Belong to the agent's organization, OR
  - Are built-in Ajentify tools
- Attempting to use a tool from another organization will result in a `403` error

### Tool Call IDs

- The system automatically generates unique `tool_call_id` values for each tool
- These IDs link tool calls to their corresponding responses in the message history
- You don't need to provide or manage these IDs

## Related Documentation

- [DataWindows Guide](./data-windows.md) - Learn about auto-refreshing data in contexts
- [Message Control Endpoints](./message-control-endpoints.md) - Manipulate messages after creation
- [Custom Tools](./custom-tools.md) - Create your own initialization tools

