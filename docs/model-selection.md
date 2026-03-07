# Model Selection — Frontend Integration Guide

## Overview

The backend now supports configurable LLM model selection for **Agents** and **Structured Response Endpoints (SREs)**. A `model_id` field has been added to both resources. When set, the backend uses the specified model for all LLM calls associated with that resource. When `null`, the backend falls back to the default model (`gpt-4.1`).

Models are sourced from a backend `models` table. Each model has a provider (`openai` or `anthropic`), and the backend automatically uses the correct LLM client based on the provider. The frontend does not need to concern itself with provider differences — it only needs to present the available models and pass the selected `model_id`.

---

## 1. Fetching Available Models

### `GET /models`

Authenticated endpoint. Returns all available models.

**Response:**

```json
[
  {
    "model": "gpt-4.1",
    "model_provider": "openai",
    "input_token_cost": 2.0,
    "output_token_cost": 8.0
  },
  {
    "model": "claude-sonnet-4-6",
    "model_provider": "anthropic",
    "input_token_cost": 3.0,
    "output_token_cost": 15.0
  }
]
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `model` | `string` | The model identifier. This is the value to use as `model_id`. |
| `model_provider` | `string` | Either `"openai"` or `"anthropic"`. Useful for display grouping or badges. |
| `input_token_cost` | `float` | Cost per million input tokens. |
| `output_token_cost` | `float` | Cost per million output tokens. |

**Recommendation:** Fetch this list once on app load or when the model selector is first opened, and cache it client-side. The list changes infrequently.

---

## 2. Agents — Model Selection

### What changed

The `Agent` model now has an optional `model_id` field:

```json
{
  "agent_id": "...",
  "agent_name": "My Agent",
  "model_id": "claude-sonnet-4-6",
  ...
}
```

When `model_id` is `null`, the agent uses the default model.

### Frontend implementation

Add a model selector (e.g. dropdown) to the **Create Agent** and **Edit Agent** forms. The selector should:

1. Display all models from `GET /models`
2. Include an option for "Default" (sends `null` as the `model_id`)
3. Optionally show the provider as a label/badge (e.g. "claude-sonnet-4-6 — Anthropic")
4. Pre-select the agent's current `model_id` when editing, or "Default" if `null`

### Create Agent — `POST /agent`

Include `model_id` in the request body:

```json
{
  "agent_name": "Support Bot",
  "agent_description": "Handles customer questions",
  "prompt": "You are a helpful support agent.",
  "is_public": false,
  "model_id": "claude-sonnet-4-6"
}
```

Pass `null` or omit the field entirely to use the default model.

### Update Agent — `PUT /agent/{agent_id}`

Include `model_id` in the request body. To change the model:

```json
{
  "model_id": "gpt-4.1"
}
```

To clear the model and revert to the default, explicitly send `null`:

```json
{
  "model_id": null
}
```

### Anthropic constraints

The backend validates the following when an Anthropic model is selected:

- **`agent_speaks_first` must be `false`** — Anthropic models require at least one human message before generating a response. The backend will reject create/update requests that set `agent_speaks_first: true` with an Anthropic model (400 error).

The frontend should ideally disable the "Agent speaks first" toggle when an Anthropic model is selected, or show a warning.

---

## 3. Structured Response Endpoints (SREs) — Model Selection

### What changed

The `StructuredResponseEndpoint` model now has an optional `model_id` field:

```json
{
  "sre_id": "...",
  "name": "Sentiment Analyzer",
  "model_id": "gpt-4.1",
  ...
}
```

### Frontend implementation

Add the same model selector to the **Create SRE** and **Edit SRE** forms. There are no Anthropic-specific constraints for SREs.

### Create SRE — `POST /sre`

```json
{
  "name": "Sentiment Analyzer",
  "pd_id": "...",
  "is_public": false,
  "model_id": "gpt-4.1"
}
```

### Update SRE — `PUT /sre/{sre_id}`

```json
{
  "model_id": "claude-sonnet-4-6"
}
```

To clear: `"model_id": null`.

---

## 4. Summary of API Changes

| Endpoint | Field Added | Notes |
|---|---|---|
| `GET /models` | — | New endpoint. Returns all available models. |
| `POST /agent` | `model_id` | Optional. Validated against models table. |
| `PUT /agent/{agent_id}` | `model_id` | Optional. Send `null` to clear. |
| `POST /sre` | `model_id` | Optional. Validated against models table. |
| `PUT /sre/{sre_id}` | `model_id` | Optional. Send `null` to clear. |
