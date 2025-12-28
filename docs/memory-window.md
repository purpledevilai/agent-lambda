# Memory Windows

## Overview

Memory Windows provide agents with continuous access to JSON memory documents that automatically refresh with the latest data on each invocation. This eliminates the need for repeated `read_memory` calls when an agent needs to reference data that may be modified during a conversation.

## The Problem

When an agent uses memory tools (`write_memory`, `append_memory`, `delete_memory`) to modify a JSON document, the agent would normally need to call `read_memory` again to see the updated data. This leads to:

- Extra tool calls cluttering the conversation
- Increased latency from repeated database reads
- Potential for the agent to reference stale data

## The Solution

The `open_memory_window` tool opens a "window" into a memory document. Once opened:

1. The agent immediately sees the current data
2. On every subsequent invocation, the data **automatically refreshes** with the latest values
3. Modifications made by other memory tools are reflected without additional read calls

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│  Invocation 1                                                   │
│  ┌──────────────────┐    ┌───────────────────────────────────┐  │
│  │ Agent calls      │───▶│ open_memory_window returns:       │  │
│  │ open_memory_window│   │ {"tasks": ["Task 1"]}             │  │
│  └──────────────────┘    └───────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────┐    ┌───────────────────────────────────┐  │
│  │ Agent calls      │───▶│ append_memory adds "Task 2"       │  │
│  │ append_memory    │    │ (document cached in context)      │  │
│  └──────────────────┘    └───────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Invocation 2 (auto-refresh happens before agent sees messages) │
│                                                                 │
│  Memory Window automatically updated to:                        │
│  {"tasks": ["Task 1", "Task 2"]}                                │
│                                                                 │
│  Agent sees the updated data without calling read_memory!       │
└─────────────────────────────────────────────────────────────────┘
```

## Tool Definition

### `open_memory_window`

Opens a Memory Window to access a persisted JSON memory document.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `document_id` | string | Yes | The unique identifier for the memory document to open |
| `path` | string | No | A dot-separated path to a specific section (e.g., `user.preferences`, `tasks.0`). If blank, returns the entire document. |

**Returns:** JSON string of the data at the specified path (or entire document)

## Usage Examples

### Basic Usage - Open Entire Document

```json
{
  "tool_id": "open_memory_window",
  "tool_input": {
    "document_id": "mem-abc123"
  }
}
```

**Returns:**
```json
{
  "user": {
    "name": "John",
    "preferences": { "theme": "dark" }
  },
  "tasks": ["Task 1", "Task 2"]
}
```

### Open Specific Path

```json
{
  "tool_id": "open_memory_window",
  "tool_input": {
    "document_id": "mem-abc123",
    "path": "user.preferences"
  }
}
```

**Returns:**
```json
{
  "theme": "dark"
}
```

### Open Array Element

```json
{
  "tool_id": "open_memory_window",
  "tool_input": {
    "document_id": "mem-abc123",
    "path": "tasks.0"
  }
}
```

**Returns:**
```json
"Task 1"
```

## Context Initialization

You can open a Memory Window when creating a context using `initialize_tools`:

```bash
curl -X POST https://api.ajentify.com/context \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "my-agent-id",
    "initialize_tools": [
      {
        "tool_id": "open_memory_window",
        "tool_input": {
          "document_id": "user-memory-123",
          "path": "profile"
        }
      }
    ]
  }'
```

This ensures the agent has access to the memory data from the very first message.

## Combining with Other Memory Tools

Memory Windows work seamlessly with other memory tools:

```
Agent Prompt:
"You have access to a memory document {memory_id}. 
Open it with open_memory_window to see current data.
Use write_memory and append_memory to update it.
The memory window will always show the latest data."
```

### Example Conversation Flow

1. **User**: "What tasks do I have?"
2. **Agent**: Calls `open_memory_window(document_id="tasks-doc")`
   - Returns: `{"active": ["Buy groceries"], "completed": []}`
3. **Agent**: "You have one active task: Buy groceries"

4. **User**: "Add 'Call mom' to my tasks"
5. **Agent**: Calls `append_memory(document_id="tasks-doc", path="active", value="Call mom", type="string")`
   - Memory document updated, cached in context
6. **Agent**: "Added 'Call mom' to your active tasks"

7. **User**: "What are my tasks now?"
8. **Agent**: *(Memory Window auto-refreshed)*
   - Sees: `{"active": ["Buy groceries", "Call mom"], "completed": []}`
9. **Agent**: "You have two active tasks: Buy groceries and Call mom"
   - No need to call `read_memory`!

## Permission Model

Memory Windows use the same permission model as other memory tools:

- **User-based permissions**: The calling user must have access to the document
- **Organization check**: The document's org must be in the user's organizations list
- **Public documents**: Public documents (`is_public: true`) are accessible to all

If a user doesn't have access, the tool returns an error message.

## Handling Path Changes

If a path becomes invalid (e.g., after a `delete_memory` removes that section), the Memory Window will display an error on the next refresh:

```
Error: The specified memory path 'tasks.active' is no longer available.
```

The agent can then decide to:
- Open a different path
- Open the entire document
- Inform the user about the change

## Best Practices

### 1. Use Paths for Large Documents

If your memory document is large but you only need a section:

```json
{
  "document_id": "large-doc",
  "path": "user.settings"
}
```

This keeps the token count lower in the agent's context.

### 2. Initialize at Context Creation

For agents that always need memory access, use `initialize_tools`:

```json
{
  "agent_id": "my-agent",
  "initialize_tools": [
    {
      "tool_id": "open_memory_window",
      "tool_input": {
        "document_id": "user-memory-123"
      }
    }
  ]
}
```

### 3. Combine with Agent Prompt

Tell the agent about the memory document in its prompt:

```
You are a personal assistant with access to the user's memory document.
The memory document ID is {memory_id}.

At the start of each conversation, open the memory window to see current data.
When the user asks you to remember something, use write_memory or append_memory.
The memory window will automatically show you the latest data.
```

### 4. Multiple Memory Windows

You can open multiple memory windows in the same context:

```json
{
  "initialize_tools": [
    {
      "tool_id": "open_memory_window",
      "tool_input": { "document_id": "user-preferences" }
    },
    {
      "tool_id": "open_memory_window", 
      "tool_input": { "document_id": "user-tasks" }
    }
  ]
}
```

All windows will refresh automatically on each invocation.

## Related Memory Tools

| Tool | Purpose |
|------|---------|
| `read_memory` | One-time read of memory data |
| `write_memory` | Set/overwrite a value at a path |
| `append_memory` | Add item to a list |
| `delete_memory` | Remove a path from the document |
| `view_memory_shape` | See the structure/types of the document |
| `open_memory_window` | Continuous access with auto-refresh |

## Comparison: read_memory vs open_memory_window

| Feature | `read_memory` | `open_memory_window` |
|---------|---------------|----------------------|
| Data access | One-time snapshot | Continuous, auto-refreshing |
| Subsequent reads | Requires new tool call | Automatic on each invocation |
| Best for | One-off data lookups | Data that changes during conversation |
| Token efficiency | Good for infrequent reads | Better for frequent reference |

## Related Documentation

- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results
- [DataWindows](./data-windows-feature.md) - Similar auto-refresh for external data
- [Additional Agent Tools](./additional-agent-tools.md) - Built-in tool reference

