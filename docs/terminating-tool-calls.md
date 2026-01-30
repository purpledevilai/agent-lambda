# Terminating Tool Calls

Terminating Tool Calls enable autonomous agent execution where the agent runs a series of tool calls without human interaction, stopping only when it calls a designated "terminating" tool. This is useful for sending an agent out on a task and having it return a structured result.

## Overview

When you provide a `terminating_config` to a chat endpoint request, the agent enters an autonomous execution mode:

1. The agent executes tool calls as normal
2. When it calls a tool that matches one of the `tool_ids` in the config, execution stops and that tool's output is returned as the final response
3. If the agent returns a content message instead of calling tools, it receives a "nudge" reminding it to call a terminating tool
4. Execution is capped by `max_invocations` to prevent runaway loops

## Configuration

Add `terminating_config` to any of the three chat endpoints:

- `POST /chat` - Chat with human message
- `POST /chat/invoke` - Invoke without human message
- `POST /chat/add-ai-message` - Add AI message with optional prompt

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tool_ids` | `string[]` | **required** | Array of tool IDs that can terminate execution. Use the tool's UUID for custom tools, or the registry key (e.g., `"pass_event"`) for built-in tools. When the agent calls any of these tools, execution stops and the tool's output is returned. |
| `consecutive_nudges` | `int` | `1` | Maximum consecutive content-only responses before raising an error. Resets when the agent calls any tool. |
| `nudge_message` | `string` | See below | System message injected when the agent returns content instead of calling a terminating tool. |
| `max_invocations` | `int` | `64` | Maximum number of LLM invocations allowed. Prevents infinite loops. |

**Default nudge_message:**
```
You are currently in an autonomous execution mode with no user interaction. You must complete your task by calling one of the terminating tools.
```

## Example Requests

### Basic Usage

```json
POST /chat
{
  "context_id": "abc-123",
  "message": "Analyze my last 5 emails and summarize them",
  "terminating_config": {
    "tool_ids": ["c3b3bbf3-92fc-4ce6-b483-489c0b01ffa2"]
  }
}
```

### With Custom Configuration

```json
POST /chat
{
  "context_id": "abc-123", 
  "message": "Research the topic and compile a report",
  "terminating_config": {
    "tool_ids": ["a1b2c3d4-...", "e5f6g7h8-..."],
    "consecutive_nudges": 3,
    "nudge_message": "Remember: You must call the terminating tool when finished.",
    "max_invocations": 20
  }
}
```

### Using with Invoke Endpoint

```json
POST /chat/invoke
{
  "context_id": "abc-123",
  "terminating_config": {
    "tool_ids": ["your-tool-uuid-here"]
  }
}
```

### Using with Add AI Message

```json
POST /chat/add-ai-message
{
  "context_id": "abc-123",
  "prompt": "Process the user's request and return results via the complete_task tool",
  "terminating_config": {
    "tool_ids": ["your-tool-uuid-here"],
    "max_invocations": 10
  }
}
```

## Behavior Details

### Execution Flow

1. Agent receives the message/prompt
2. Agent may call multiple non-terminating tools (e.g., search, read data)
3. When ready, agent calls a terminating tool with its final result
4. Execution stops immediately, tool's output becomes the response

### Nudge Behavior

If the agent returns a content message (text response) instead of calling tools:

1. The `consecutive_nudges` counter increments
2. If counter ≤ `consecutive_nudges`, a system message with `nudge_message` is injected and the agent is re-invoked
3. If counter > `consecutive_nudges`, an error is raised: `"Max consecutive nudges exceeded"`
4. Counter resets to 0 whenever the agent calls any tool

### Multiple Tool Calls

If the agent calls multiple tools in a single response and one of them is a terminating tool:

- Tools are executed in order
- Execution stops at the first terminating tool encountered
- Remaining tools in that response are not executed
- The AIMessage is cleaned up to only include the executed tool calls

### Error Conditions

- **Max invocations exceeded**: Raised when `max_invocations` limit is reached
- **Max consecutive nudges exceeded**: Raised when agent repeatedly returns content without calling tools

## Use Cases

### Autonomous Task Completion

Send an agent to complete a multi-step task and return a structured result:

```json
{
  "message": "Find all overdue invoices and create a summary report",
  "terminating_config": {
    "tool_ids": ["<submit_report_tool_id>"]
  }
}
```

### Data Processing Pipeline

Agent processes data through multiple steps before returning:

```json
{
  "message": "Fetch today's sales data, calculate metrics, and store results",
  "terminating_config": {
    "tool_ids": ["<save_results_tool_id>", "<report_error_tool_id>"],
    "max_invocations": 30
  }
}
```

### Research and Compilation

Agent researches a topic using multiple tools before compiling:

```json
{
  "message": "Research competitor pricing and compile analysis",
  "terminating_config": {
    "tool_ids": ["<complete_analysis_tool_id>"],
    "consecutive_nudges": 2
  }
}
```

## Creating Terminating Tools

Any tool can be a terminating tool - simply include its name in `tool_ids`. The tool's return value becomes the final response.

A common pattern is to create a dedicated "completion" tool:

```python
# Tool that returns structured results
class complete_task(BaseModel):
    result: str = Field(description="The final result of the completed task")

def complete_task_func(result: str) -> str:
    return f"Task completed: {result}"
```

## Response Format

When using `terminating_config`, the response structure remains the same:

```json
{
  "response": "Task completed: [tool output here]",
  "saved_ai_messages": true,
  "generated_messages": [
    {"sender": "human", "message": "..."},
    {"type": "tool_call", "tool_call_id": "...", "tool_name": "...", "tool_input": {}},
    {"type": "tool_response", "tool_call_id": "...", "tool_output": "..."}
  ]
}
```

The `response` field contains the terminating tool's output string.
