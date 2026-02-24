# Usage Endpoint

## Overview

The Usage endpoint returns token usage and cost data for an organization over a given date range. It is designed to power a daily usage bar chart and provide a cost breakdown by model.

## Endpoint

```
GET /usage
```

**Authentication:** Required (Cognito token or Org API Key)

## Query Parameters

| Parameter    | Required | Default | Description                                                                 |
|--------------|----------|---------|-----------------------------------------------------------------------------|
| `start_date` | Yes      | —       | Start of the date range (inclusive), formatted as `YYYY-MM-DD`.             |
| `end_date`   | Yes      | —       | End of the date range (inclusive), formatted as `YYYY-MM-DD`.               |
| `timezone`   | No       | `UTC`   | IANA timezone string (e.g. `America/New_York`, `Europe/London`).            |
| `org_id`     | No       | —       | Organization ID to query. Must be one of the user's orgs. Defaults to the user's first organization if omitted. |

## Example Request

```bash
curl -X GET \
  "https://api.ajentify.com/usage?start_date=2026-02-01&end_date=2026-02-24&timezone=America/New_York&org_id=abc-123" \
  -H "Authorization: <token>"
```

## Response

```json
{
  "daily_usage": [
    { "date": "2026-02-01", "total_tokens": 45230 },
    { "date": "2026-02-02", "total_tokens": 12080 },
    { "date": "2026-02-03", "total_tokens": 0 }
  ],
  "total_cost": "$1,234.56 USD",
  "model_costs": [
    {
      "model": "gpt-4.1-2025-04-14",
      "input_tokens": 980000,
      "output_tokens": 120000,
      "cost": "$1,234.56 USD"
    }
  ]
}
```

## Response Fields

### `daily_usage`

An array of objects, one per day in the requested range (including days with zero usage). Suitable for rendering a bar chart.

| Field          | Type    | Description                                              |
|----------------|---------|----------------------------------------------------------|
| `date`         | string  | The date in `YYYY-MM-DD` format, localized to the requested timezone. |
| `total_tokens` | integer | Sum of input and output tokens for that day.             |

### `total_cost`

The total cost across all models for the entire date range, formatted as `$X.XX USD`.

### `model_costs`

A breakdown of usage and cost per model.

| Field           | Type    | Description                                              |
|-----------------|---------|----------------------------------------------------------|
| `model`         | string  | The model name (e.g. `gpt-4.1-2025-04-14`).             |
| `input_tokens`  | integer | Total input tokens consumed by this model in the range.  |
| `output_tokens` | integer | Total output tokens consumed by this model in the range. |
| `cost`          | string  | Cost for this model, formatted as `$X.XX USD`.           |

## How Cost is Calculated

1. Token tracking records are grouped by model name.
2. For each model, the per-million token costs (`input_token_cost` and `output_token_cost`) are looked up from the `models` DynamoDB table.
3. Cost per model = `(input_tokens / 1,000,000) * input_token_cost + (output_tokens / 1,000,000) * output_token_cost`.
4. The `total_cost` is the sum of all model costs.
5. If a model is not found in the `models` table, its cost is treated as `$0.00`.

## Errors

| Status | Condition                                              |
|--------|--------------------------------------------------------|
| 400    | Missing `start_date` or `end_date`.                   |
| 400    | Invalid `timezone` value.                              |
| 400    | User does not belong to any organization.              |
| 401    | Missing or invalid authentication token.               |
| 403    | Specified `org_id` is not in the user's organizations. |
