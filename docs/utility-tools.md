# Utility Tools

## Overview

Utility tools are general-purpose built-in tools that provide common functionality useful across many agent use cases. These tools don't require any external integrations or API credentials.

## Tool Reference Summary

| Tool ID | Description |
|---------|-------------|
| `get_time` | Retrieve the current date and time (UTC or specific timezone) |
| `think` | Organize and articulate reasoning before taking action |

---

## get_time

Retrieve the current date and time. Returns UTC time by default, or the time in a specified timezone.

**Tool ID:** `get_time`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `timezone` | string | No | IANA timezone name (e.g., `America/New_York`, `Europe/London`, `Asia/Tokyo`). If not provided, returns UTC time. |

### Common Timezone Examples

| Region | Timezone Name |
|--------|---------------|
| US Eastern | `America/New_York` |
| US Central | `America/Chicago` |
| US Mountain | `America/Denver` |
| US Pacific | `America/Los_Angeles` |
| UK | `Europe/London` |
| Central Europe | `Europe/Paris` |
| Japan | `Asia/Tokyo` |
| Australia Eastern | `Australia/Sydney` |
| India | `Asia/Kolkata` |

### Returns

A formatted string containing:
- The timezone label (UTC or the specified timezone)
- Date in `YYYY-MM-DD` format
- Time in `HH:MM:SS` format
- Day of the week

**Example Return (UTC):**
```
Current time (UTC): 2026-01-25 15:30:45 (Saturday)
```

**Example Return (with timezone):**
```
Current time (America/New_York): 2026-01-25 10:30:45 (Saturday)
```

### Error Handling

If an invalid timezone is provided, returns an error message:
```
Error: Invalid timezone 'InvalidZone'. Please use a valid IANA timezone name (e.g., 'America/New_York', 'Europe/London', 'Asia/Tokyo').
```

### Use Cases

1. **Scheduling Awareness**: Help agents understand the current time when scheduling meetings or events
2. **Time-Sensitive Operations**: Validate deadlines or time-based conditions
3. **User Context**: Provide time-aware responses (e.g., "Good morning" vs "Good evening")
4. **Cross-Timezone Coordination**: Convert between timezones for international users

### Example Agent Usage

```
User: "What time is it in Tokyo right now?"

Agent calls: get_time(timezone="Asia/Tokyo")
Returns: "Current time (Asia/Tokyo): 2026-01-26 00:30:45 (Sunday)"

Agent: "It's currently 12:30 AM on Sunday in Tokyo."
```

---

## think

A reasoning tool that allows the agent to organize and articulate its thought process before taking action. Use this tool to plan steps, analyze information, or work through complex problems systematically.

**Tool ID:** `think`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `thoughts` | list of strings | Yes | A list where each string represents a single thought, observation, reasoning step, or planned action. Each item should be a complete thought that contributes to solving the current task. |

### Returns

A formatted string containing:
- Numbered list of all provided thoughts
- Confirmation that reasoning is complete

**Example Return:**
```
Thoughts processed:

1. The user wants to retrieve data from an external API
2. I need to determine the correct endpoint and required parameters
3. I have the base URL and authentication credentials
4. I should first make a GET request to fetch the available options
5. Then I can filter the results based on the user's criteria

Reasoning complete. Proceed with the planned actions.
```

### When to Use

Call this tool whenever you need to:

- **Break down complex tasks**: Split a multi-step request into manageable pieces
- **Reason through information**: Analyze what you know vs. what you need to find out
- **Plan action sequences**: Determine the order of API calls or operations
- **Analyze responses**: Process data or results before deciding next steps
- **Consider edge cases**: Think through potential issues or exceptions

### Use Cases

#### 1. Multi-Step Task Planning

When a user request requires multiple actions in sequence:

```
User: "Find all overdue invoices and send reminder emails to each customer"

Agent calls: think(thoughts=[
    "The user wants to handle overdue invoices",
    "First, I need to query the invoices database for overdue items",
    "For each overdue invoice, I'll need the customer's email address",
    "I should compose a polite reminder email template",
    "Then send individual emails to each affected customer",
    "Finally, I should report back how many reminders were sent"
])
```

#### 2. Information Analysis

When processing complex data or responses:

```
Agent calls: think(thoughts=[
    "The API returned 15 products matching the search",
    "3 products are out of stock and should be excluded",
    "Of the remaining 12, 5 are within the user's budget",
    "The highest-rated product in budget is the Model X500",
    "I should recommend this product with the price and rating details"
])
```

#### 3. Error Handling Strategy

When encountering unexpected situations:

```
Agent calls: think(thoughts=[
    "The calendar API returned a 401 unauthorized error",
    "This likely means the user's OAuth token has expired",
    "I should inform the user they need to re-authenticate",
    "I'll provide clear instructions on how to reconnect their calendar"
])
```

#### 4. Decision Making

When choosing between multiple options:

```
Agent calls: think(thoughts=[
    "The user asked for the 'best' shipping option",
    "Option A: $5.99, arrives in 5-7 days",
    "Option B: $12.99, arrives in 2-3 days",
    "Option C: $24.99, arrives next day",
    "The user didn't specify urgency, so I should present all options",
    "I'll highlight Option B as a balanced choice between cost and speed"
])
```

### Benefits

1. **Improved Accuracy**: Structured thinking reduces errors in complex tasks
2. **Transparency**: The reasoning process is logged and can be reviewed
3. **Better Planning**: Prevents the agent from jumping to conclusions
4. **Debugging Aid**: Helps identify where reasoning went wrong if issues occur

### Example Agent Workflow

```
User: "I need to prepare for my meeting with the Tokyo team tomorrow"

Agent calls: think(thoughts=[
    "The user has a meeting with a Tokyo team tomorrow",
    "I should check what time it is in Tokyo to understand the timezone difference",
    "I'll need to help them prepare materials or talking points",
    "I should ask what specific preparation they need help with"
])

Agent calls: get_time(timezone="Asia/Tokyo")

Agent: "I see you have a meeting with the Tokyo team tomorrow. Currently it's [time] in Tokyo. 
What would you like help preparing? I can assist with:
- Meeting agenda or talking points
- Background research on discussion topics  
- Time conversion for scheduling"
```

---

## Adding Utility Tools to Agents

### In Agent Configuration

Add utility tools to an agent's default tool set:

```json
{
  "name": "General Assistant",
  "tools": ["get_time", "think", "web_search"],
  "system_prompt": "You are a helpful assistant..."
}
```

### Via Additional Agent Tools

Add utility tools to a specific context:

```json
{
  "agent_id": "your-agent-id",
  "additional_agent_tools": ["get_time", "think"]
}
```

See [Additional Agent Tools](./additional-agent-tools.md) for more details on dynamic tool assignment.

---

## Related Documentation

- [Additional Agent Tools](./additional-agent-tools.md) - Dynamically add tools to contexts
- [Gmail Integration](./gmail-integration.md) - Email tools for agents
- [Google Calendar Integration](./google-calendar-integration.md) - Calendar tools for agents
- [Memory Window](./memory-window.md) - Memory management tools

