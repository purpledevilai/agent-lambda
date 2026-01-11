# Prompt Arguments

This document explains how to create agents with dynamic prompt arguments that can be populated when creating a context.

## Overview

Prompt arguments allow you to create reusable agent prompts with placeholders that get replaced with actual values when a conversation context is created. This is useful for personalizing agent behavior based on user-specific data.

## How It Works

1. **Define placeholders in your prompt** - these can be ANY unique strings (e.g., `ARG_USER_NAME`, `{{name}}`, `__USER__`, etc.)
2. **Specify the exact placeholder strings** in the `prompt_arg_names` field when creating the agent
3. **Provide values** in the `prompt_args` field when creating a context, using the same keys as `prompt_arg_names`

The system performs a **simple string find-and-replace** for each argument name. This gives you complete flexibility in choosing your placeholder format.

## Recommended Style: ARG_* Prefix

We recommend using the `ARG_` prefix for new agents as it's clear and won't conflict with JSON or other content:

```
ARG_USER_NAME
ARG_COMPANY
ARG_USER_INTERESTS
```

## Creating an Agent with Prompt Arguments

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | The agent's system prompt containing placeholder strings |
| `prompt_arg_names` | string[] | List of exact placeholder strings to find and replace |
| `uses_prompt_args` | boolean | Set to `true` to enable prompt arguments |

### Example Request (Recommended ARG_* Style)

```json
POST /agent
{
  "agent_name": "Personalized Assistant",
  "agent_description": "An assistant personalized for each user",
  "prompt": "You are a helpful assistant for ARG_USER_NAME. They work at ARG_COMPANY as a ARG_JOB_TITLE.\n\nWhen providing data, use this JSON format:\n{\"status\": \"success\", \"data\": {...}}\n\nAlways be professional and address them by name.",
  "is_public": false,
  "uses_prompt_args": true,
  "prompt_arg_names": ["ARG_USER_NAME", "ARG_COMPANY", "ARG_JOB_TITLE"]
}
```

### Response

```json
{
  "agent_id": "abc123",
  "agent_name": "Personalized Assistant",
  "prompt": "You are a helpful assistant for ARG_USER_NAME...",
  "uses_prompt_args": true,
  "prompt_arg_names": ["ARG_USER_NAME", "ARG_COMPANY", "ARG_JOB_TITLE"],
  ...
}
```

## Creating a Context with Prompt Arguments

When creating a context for an agent that uses prompt arguments, provide the values in the `prompt_args` field. **The keys must exactly match the strings in `prompt_arg_names`**.

### Example Request

```json
POST /context
{
  "agent_id": "abc123",
  "prompt_args": {
    "ARG_USER_NAME": "Alice",
    "ARG_COMPANY": "Acme Corp",
    "ARG_JOB_TITLE": "Software Engineer"
  }
}
```

### Result

The agent's prompt will be transformed from:

```
You are a helpful assistant for ARG_USER_NAME. They work at ARG_COMPANY as a ARG_JOB_TITLE.
```

To:

```
You are a helpful assistant for Alice. They work at Acme Corp as a Software Engineer.
```

## Including JSON in Prompts

Since `prompt_arg_names` uses exact string matching, JSON in your prompts will **never** be accidentally modified:

### Example

```json
{
  "prompt": "You are an API assistant for ARG_USER_NAME.\n\nWhen returning data, format it as:\n{\"user\": \"...\", \"status\": \"active\"}\n\nThe JSON structure should always be valid.",
  "prompt_arg_names": ["ARG_USER_NAME"]
}
```

In this example:
- `ARG_USER_NAME` will be replaced with the provided value
- `{"user": "...", "status": "active"}` will remain completely unchanged

## Legacy Style: {name} Brackets

For backwards compatibility with existing agents, you can use the `{name}` style. In this case, **the brackets are part of the argument name**:

### Example (Legacy Style)

```json
POST /agent
{
  "prompt": "Hello {user_name}, welcome to {location}!",
  "uses_prompt_args": true,
  "prompt_arg_names": ["{user_name}", "{location}"]
}
```

When creating a context:

```json
POST /context
{
  "agent_id": "...",
  "prompt_args": {
    "{user_name}": "Alice",
    "{location}": "Melbourne"
  }
}
```

**Note**: The keys in `prompt_args` must include the brackets to match the `prompt_arg_names`.

## Updating an Agent's Prompt Arguments

You can update the `prompt_arg_names` field on an existing agent.

### Example Request

```json
POST /agent/{agent_id}
{
  "prompt": "Hello ARG_NAME, welcome to ARG_LOCATION!",
  "prompt_arg_names": ["ARG_NAME", "ARG_LOCATION"]
}
```

## Best Practices

1. **Use the ARG_* prefix for new agents**: It's clear, won't conflict with content, and is easy to spot in prompts

2. **Use descriptive argument names**: Choose clear names like `ARG_USER_NAME`, `ARG_COMPANY` rather than generic names like `ARG_1`, `ARG_2`

3. **Be consistent**: Pick one style and stick with it across your agents

4. **Document your arguments**: Keep track of which arguments each agent expects

5. **Validate on the frontend**: Ensure all required prompt arguments are provided when creating a context

6. **Handle missing arguments gracefully**: If an argument is defined but not provided, the placeholder will remain in the prompt as-is

## Migration Notes

Existing agents created with `uses_prompt_args: true` but without `prompt_arg_names` will be migrated automatically. The migration script:

1. Finds patterns like `{arg_name}` in the prompt
2. Extracts them **including the brackets** (e.g., `{user_name}` becomes `"{user_name}"` in the array)
3. Sets the `prompt_arg_names` field with these values

This ensures backwards compatibility - existing prompts will continue to work without changes.

## API Reference

### Agent Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `uses_prompt_args` | boolean | `false` | Whether this agent uses prompt arguments |
| `prompt_arg_names` | string[] | `[]` | List of exact placeholder strings to find and replace in the prompt |

### Context Creation Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `prompt_args` | object | No | Key-value pairs where keys exactly match `prompt_arg_names` and values are the replacement strings |

## Troubleshooting

### Argument not being replaced

- Verify the argument name in `prompt_arg_names` **exactly** matches the placeholder in the prompt (case-sensitive, including any brackets or special characters)
- Ensure `uses_prompt_args` is set to `true` on the agent
- Check that the key in `prompt_args` exactly matches the string in `prompt_arg_names`

### Legacy {name} style not working

- Make sure the brackets are included in both `prompt_arg_names` AND the keys in `prompt_args`
- Example: `prompt_arg_names: ["{name}"]` requires `prompt_args: {"{name}": "value"}`

### Placeholder appearing in agent responses

- The argument name might be misspelled in either `prompt_arg_names` or the `prompt_args` when creating the context
- Verify the context was created with the correct `prompt_args`
