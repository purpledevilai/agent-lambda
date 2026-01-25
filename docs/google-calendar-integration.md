# Google Calendar Integration

## Overview

The Google Calendar integration allows agents to view, create, update, and delete calendar events on behalf of users. This is accomplished through OAuth 2.0 authentication with Google's Calendar API.

## Setup

### 1. Google Cloud Project Setup

Before using the Google Calendar integration, you need to configure your Google Cloud project:

1. **Enable Calendar API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and click "Enable"

2. **Add Calendar Scopes to OAuth Consent Screen**
   - Go to "APIs & Services" > "OAuth consent screen"
   - Edit your existing OAuth consent screen
   - Add scopes:
     - `https://www.googleapis.com/auth/calendar.events` - For event CRUD operations
     - `https://www.googleapis.com/auth/calendar.readonly` - For viewing calendars

3. **Use Existing OAuth Credentials**
   - The Google Calendar integration uses the same OAuth client as Gmail
   - You just need a separate redirect URI for the Calendar OAuth flow

### 2. Environment Variables

Add these environment variables to your Lambda:

```bash
# Shared Google OAuth credentials (same as Gmail)
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret

# Calendar-specific redirect URI
GOOGLE_CALENDAR_REDIRECT_URI=https://yourapp.com/google-calendar/callback
```

## OAuth Flow

### Step 1: Get Authorization URL

```bash
GET /google-calendar/auth-url
Authorization: Bearer <user_token>
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with
- `state` (optional): State parameter to pass through OAuth flow

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=..."
}
```

Redirect the user to this URL. After authorization, Google redirects back to your `GOOGLE_CALENDAR_REDIRECT_URI` with a `code` parameter.

### Step 2: Exchange Code for Tokens

```bash
POST /google-calendar/auth
Authorization: Bearer <user_token>
Content-Type: application/json

{
  "code": "authorization_code_from_google"
}
```

**Query Parameters:**
- `org_id` (optional): Organization ID to associate the integration with

**Response:**
```json
{
  "integration_id": "uuid-of-integration",
  "org_id": "org-uuid",
  "type": "google_calendar",
  "integration_config": {
    "access_token": "...",
    "refresh_token": "...",
    "expires_at": 1234567890,
    "email": "user@gmail.com"
  },
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

Save the `integration_id` - this is what you'll pass to agents to use Google Calendar tools.

## Agent Tools

Once you have a Google Calendar integration, agents can use these tools. All tools require the `integration_id` parameter.

### Tool Reference Summary

| Tool ID | Description |
|---------|-------------|
| `list_calendar_events` | List and search events with date range filters |
| `get_calendar_event` | Get full details of a specific event |
| `create_calendar_event` | Create a new calendar event |
| `update_calendar_event` | Update an existing event |
| `delete_calendar_event` | Delete a calendar event |
| `list_calendars` | List all accessible calendars |

---

## Event Tools

### list_calendar_events

List events from a Google Calendar with powerful filtering options.

**Tool ID:** `list_calendar_events`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `calendar_id` | string | No | Calendar ID (default "primary" for main calendar) |
| `time_min` | string | No | Lower bound for event start time (RFC3339 format) |
| `time_max` | string | No | Upper bound for event start time (RFC3339 format) |
| `query` | string | No | Free text search query |
| `max_results` | int | No | Maximum events to return (default 10, max 250) |

**Time Format Examples (RFC3339):**
- With timezone offset: `2026-01-25T10:00:00-05:00` (Eastern Time)
- With UTC: `2026-01-25T15:00:00Z`
- For all-day queries: `2026-01-25T00:00:00Z`

**Example (get today's events):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "time_min": "2026-01-25T00:00:00Z",
  "time_max": "2026-01-26T00:00:00Z",
  "max_results": 20
}
```

**Example (search for events):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "query": "team meeting",
  "max_results": 10
}
```

**Returns:**
```json
{
  "events": [
    {
      "id": "event-id-123",
      "summary": "Team Standup",
      "description": "Daily standup meeting",
      "location": "Conference Room A",
      "start": "2026-01-25T09:00:00-05:00",
      "end": "2026-01-25T09:30:00-05:00",
      "is_all_day": false,
      "timezone": "America/New_York",
      "status": "confirmed",
      "html_link": "https://calendar.google.com/event?eid=...",
      "attendees": [
        {
          "email": "colleague@company.com",
          "response_status": "accepted",
          "display_name": "John Doe"
        }
      ],
      "organizer": "user@gmail.com",
      "created": "2026-01-20T10:00:00Z",
      "updated": "2026-01-24T15:30:00Z"
    }
  ],
  "count": 1,
  "calendar_id": "primary",
  "time_zone": "America/New_York"
}
```

---

### get_calendar_event

Get the full details of a specific calendar event.

**Tool ID:** `get_calendar_event`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `event_id` | string | Yes | The event ID from list_calendar_events |
| `calendar_id` | string | No | Calendar ID (default "primary") |

**Returns:**
```json
{
  "id": "event-id-123",
  "summary": "Project Kickoff Meeting",
  "description": "Discuss project goals, timeline, and responsibilities.",
  "location": "Main Conference Room",
  "start": "2026-01-25T14:00:00-05:00",
  "end": "2026-01-25T15:30:00-05:00",
  "is_all_day": false,
  "timezone": "America/New_York",
  "status": "confirmed",
  "html_link": "https://calendar.google.com/event?eid=...",
  "attendees": [
    {
      "email": "teammate@company.com",
      "response_status": "accepted",
      "display_name": "Jane Smith"
    }
  ],
  "organizer": "user@gmail.com",
  "created": "2026-01-20T10:00:00Z",
  "updated": "2026-01-24T15:30:00Z",
  "recurrence": null,
  "recurring_event_id": null,
  "visibility": "default",
  "conference_data": null,
  "reminders": {
    "useDefault": true
  },
  "attachments": null
}
```

---

### create_calendar_event

Create a new event in Google Calendar. Supports timed events, all-day events, and recurring events.

**Tool ID:** `create_calendar_event`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `summary` | string | Yes | Event title |
| `start_time` | string | Yes | Start time (RFC3339) or date (YYYY-MM-DD for all-day) |
| `end_time` | string | Yes | End time (RFC3339) or date (YYYY-MM-DD for all-day) |
| `calendar_id` | string | No | Calendar ID (default "primary") |
| `description` | string | No | Detailed description of the event |
| `location` | string | No | Event location (address or place name) |
| `attendees` | array | No | List of attendee email addresses |
| `timezone` | string | No | Timezone (e.g., "America/New_York") |
| `all_day` | bool | No | Set true for all-day events (default false) |
| `recurrence` | array | No | List of RRULE strings for recurring events (see examples below) |

**Example (timed event):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "summary": "Project Review",
  "start_time": "2026-01-27T14:00:00-05:00",
  "end_time": "2026-01-27T15:00:00-05:00",
  "description": "Review Q1 project progress",
  "location": "Conference Room B",
  "attendees": ["colleague@company.com", "manager@company.com"]
}
```

**Example (all-day event):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "summary": "Company Holiday",
  "start_time": "2026-02-15",
  "end_time": "2026-02-16",
  "all_day": true,
  "description": "Presidents Day - Office Closed"
}
```

**Example (multi-day event):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "summary": "Annual Conference",
  "start_time": "2026-03-10",
  "end_time": "2026-03-13",
  "all_day": true,
  "location": "Las Vegas Convention Center"
}
```

**Example (recurring weekly meeting):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "summary": "Team Standup",
  "start_time": "2026-01-27T09:00:00-05:00",
  "end_time": "2026-01-27T09:30:00-05:00",
  "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR"],
  "location": "Conference Room A"
}
```

**Example (recurring monthly meeting with end count):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "summary": "Monthly Review",
  "start_time": "2026-02-15T14:00:00-05:00",
  "end_time": "2026-02-15T15:00:00-05:00",
  "recurrence": ["RRULE:FREQ=MONTHLY;BYMONTHDAY=15;COUNT=12"],
  "description": "Monthly project review for 12 months"
}
```

**Returns:**
```json
{
  "status": "created",
  "event_id": "new-event-id",
  "summary": "Project Review",
  "html_link": "https://calendar.google.com/event?eid=...",
  "start": {
    "dateTime": "2026-01-27T14:00:00-05:00",
    "timeZone": "America/New_York"
  },
  "end": {
    "dateTime": "2026-01-27T15:00:00-05:00",
    "timeZone": "America/New_York"
  },
  "attendees_count": 2
}
```

---

### update_calendar_event

Update an existing calendar event. Only the fields you provide will be updated; other fields remain unchanged.

**Tool ID:** `update_calendar_event`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `event_id` | string | Yes | The event ID to update (use series ID for recurring events) |
| `calendar_id` | string | No | Calendar ID (default "primary") |
| `summary` | string | No | New event title |
| `start_time` | string | No | New start time |
| `end_time` | string | No | New end time |
| `description` | string | No | New description |
| `location` | string | No | New location |
| `attendees` | array | No | New attendee list (replaces existing) |
| `timezone` | string | No | Timezone for time values |
| `all_day` | bool | No | Set true when changing to all-day event |
| `recurrence` | array | No | New recurrence rules (empty list `[]` removes recurrence) |

**Example (reschedule event):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "event_id": "event-id-123",
  "start_time": "2026-01-28T10:00:00-05:00",
  "end_time": "2026-01-28T11:00:00-05:00"
}
```

**Example (update title and location):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "event_id": "event-id-123",
  "summary": "Updated Meeting Title",
  "location": "Virtual - Zoom"
}
```

**Example (make event recurring):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "event_id": "event-id-123",
  "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=TU,TH"]
}
```

**Example (remove recurrence from event):**
```json
{
  "integration_id": "calendar-integration-uuid",
  "event_id": "event-id-123",
  "recurrence": []
}
```

**Returns:**
```json
{
  "status": "updated",
  "event_id": "event-id-123",
  "summary": "Updated Meeting Title",
  "html_link": "https://calendar.google.com/event?eid=...",
  "start": {
    "dateTime": "2026-01-28T10:00:00-05:00"
  },
  "end": {
    "dateTime": "2026-01-28T11:00:00-05:00"
  },
  "updated": "2026-01-25T16:45:00Z"
}
```

---

### delete_calendar_event

Delete a calendar event permanently. This action cannot be undone.

**Tool ID:** `delete_calendar_event`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `event_id` | string | Yes | The event ID to delete |
| `calendar_id` | string | No | Calendar ID (default "primary") |

**Example:**
```json
{
  "integration_id": "calendar-integration-uuid",
  "event_id": "event-id-123"
}
```

**Returns:**
```json
{
  "status": "deleted",
  "event_id": "event-id-123",
  "calendar_id": "primary"
}
```

---

## Calendar Tools

### list_calendars

List all calendars accessible to the user, including their primary calendar, secondary calendars, and subscribed calendars.

**Tool ID:** `list_calendars`

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `integration_id` | string | Yes | The Google Calendar integration ID |
| `max_results` | int | No | Maximum calendars to return (default 100) |

**Returns:**
```json
{
  "calendars": [
    {
      "id": "user@gmail.com",
      "summary": "My Calendar",
      "description": null,
      "primary": true,
      "access_role": "owner",
      "background_color": "#9fe1e7",
      "foreground_color": "#000000",
      "selected": true,
      "time_zone": "America/New_York"
    },
    {
      "id": "work-calendar-id@group.calendar.google.com",
      "summary": "Work Projects",
      "description": "Calendar for work projects",
      "primary": false,
      "access_role": "owner",
      "background_color": "#f83a22",
      "foreground_color": "#000000",
      "selected": true,
      "time_zone": "America/New_York"
    },
    {
      "id": "en.usa#holiday@group.v.calendar.google.com",
      "summary": "Holidays in United States",
      "description": null,
      "primary": false,
      "access_role": "reader",
      "background_color": "#92e1c0",
      "foreground_color": "#000000",
      "selected": false,
      "time_zone": "America/New_York"
    }
  ],
  "count": 3
}
```

**Access Roles:**
- `owner` - Full control (create, edit, delete events)
- `writer` - Can edit events
- `reader` - Read-only access
- `freeBusyReader` - Can only see free/busy information

---

## Agent Configuration

To give an agent access to Google Calendar, include the Calendar tools and provide the integration ID in the prompt:

### Adding Tools to Agent

When creating or updating an agent, include the Google Calendar tools you want the agent to use:

```json
{
  "agent_name": "Calendar Assistant",
  "prompt": "You are a calendar assistant. You have access to Google Calendar via integration ID {google_calendar_integration_id}. Help the user manage their schedule.",
  "tools": [
    "list_calendar_events",
    "get_calendar_event",
    "create_calendar_event",
    "update_calendar_event",
    "delete_calendar_event",
    "list_calendars"
  ]
}
```

**Recommended tool sets by use case:**

| Use Case | Recommended Tools |
|----------|-------------------|
| Read-only calendar access | `list_calendar_events`, `get_calendar_event`, `list_calendars` |
| Schedule management | Above + `create_calendar_event`, `update_calendar_event` |
| Full calendar management | All tools (use `delete_calendar_event` with caution) |

### Using with Context

When creating a context, pass the integration ID via `prompt_args`:

```json
{
  "agent_id": "calendar-assistant-uuid",
  "prompt_args": {
    "google_calendar_integration_id": "actual-calendar-integration-uuid"
  }
}
```

The agent will then use this integration ID when calling Google Calendar tools.

## Recurrence Rule (RRULE) Reference

Recurring events use the iCalendar RFC 5545 RRULE format. The `recurrence` parameter accepts an array of RRULE strings.

### Basic Frequency Patterns
| Pattern | RRULE | Description |
|---------|-------|-------------|
| Daily | `RRULE:FREQ=DAILY` | Every day |
| Weekly | `RRULE:FREQ=WEEKLY` | Every week (same day) |
| Monthly | `RRULE:FREQ=MONTHLY` | Every month (same date) |
| Yearly | `RRULE:FREQ=YEARLY` | Every year (same date) |

### Interval Patterns
| Pattern | RRULE | Description |
|---------|-------|-------------|
| Every 2 days | `RRULE:FREQ=DAILY;INTERVAL=2` | Every other day |
| Every 2 weeks | `RRULE:FREQ=WEEKLY;INTERVAL=2` | Bi-weekly |
| Every 3 months | `RRULE:FREQ=MONTHLY;INTERVAL=3` | Quarterly |

### Day-of-Week Patterns
| Pattern | RRULE | Description |
|---------|-------|-------------|
| Weekdays | `RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR` | Monday through Friday |
| Mon/Wed/Fri | `RRULE:FREQ=WEEKLY;BYDAY=MO,WE,FR` | Three days a week |
| Weekends | `RRULE:FREQ=WEEKLY;BYDAY=SA,SU` | Saturday and Sunday |

### Monthly Patterns
| Pattern | RRULE | Description |
|---------|-------|-------------|
| 15th of month | `RRULE:FREQ=MONTHLY;BYMONTHDAY=15` | Same date each month |
| First Monday | `RRULE:FREQ=MONTHLY;BYDAY=1MO` | First Monday of month |
| Last Friday | `RRULE:FREQ=MONTHLY;BYDAY=-1FR` | Last Friday of month |

### End Conditions
| Pattern | RRULE | Description |
|---------|-------|-------------|
| 10 occurrences | `RRULE:FREQ=WEEKLY;COUNT=10` | Ends after 10 times |
| Until date | `RRULE:FREQ=DAILY;UNTIL=20261231T000000Z` | Ends on Dec 31, 2026 |

### Combined Examples
| Use Case | RRULE |
|----------|-------|
| Daily standup for 3 months | `RRULE:FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;UNTIL=20260430T000000Z` |
| Bi-weekly team meeting | `RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=TU` |
| Monthly review on 1st | `RRULE:FREQ=MONTHLY;BYMONTHDAY=1;COUNT=12` |
| Quarterly planning | `RRULE:FREQ=MONTHLY;INTERVAL=3;BYDAY=1MO` |

### BYDAY Values
| Code | Day |
|------|-----|
| `MO` | Monday |
| `TU` | Tuesday |
| `WE` | Wednesday |
| `TH` | Thursday |
| `FR` | Friday |
| `SA` | Saturday |
| `SU` | Sunday |

## Time Format Reference

Google Calendar API uses RFC3339 format for times:

### Timed Events
| Format | Example | Description |
|--------|---------|-------------|
| With timezone offset | `2026-01-25T14:00:00-05:00` | 2 PM Eastern Time |
| With UTC | `2026-01-25T19:00:00Z` | Same time in UTC |
| With positive offset | `2026-01-25T20:00:00+01:00` | 8 PM Central European Time |

### All-Day Events
| Format | Example | Description |
|--------|---------|-------------|
| Single day | start: `2026-01-25`, end: `2026-01-26` | One day (end is exclusive) |
| Multi-day | start: `2026-01-25`, end: `2026-01-28` | Three days |

**Important:** For all-day events, the end date is exclusive. A single-day event on January 25th should have `end_time` of `2026-01-26`.

### Common Timezones
| Timezone ID | Description |
|-------------|-------------|
| `America/New_York` | Eastern Time (US) |
| `America/Chicago` | Central Time (US) |
| `America/Denver` | Mountain Time (US) |
| `America/Los_Angeles` | Pacific Time (US) |
| `Europe/London` | UK Time |
| `Europe/Paris` | Central European Time |
| `Asia/Tokyo` | Japan Time |
| `UTC` | Coordinated Universal Time |

## Token Refresh

Access tokens expire after 1 hour. The system automatically refreshes tokens when needed:

1. Before each API call, the token expiry is checked
2. If expired (or expiring within 60 seconds), the refresh token is used to get a new access token
3. The new tokens are saved to the integration

This happens transparently - agents don't need to handle token refresh.

## Error Handling

Common errors:

| Error | Cause | Solution |
|-------|-------|----------|
| `Integration not found` | Invalid integration_id | Verify the integration ID exists |
| `Not a Google Calendar integration` | Wrong integration type | Use a Google Calendar integration ID |
| `Failed to refresh token` | Refresh token revoked | User needs to re-authorize |
| `Calendar API error: 403` | Insufficient permissions | Check OAuth scopes |
| `Calendar API error: 404` | Event or calendar not found | Verify event_id and calendar_id |
| `Calendar API error: 429` | Rate limited | Implement backoff/retry |

## Security Considerations

1. **Store integration IDs securely** - Don't expose them in client-side code
2. **Scope limitation** - The integration requests only necessary scopes (events, readonly)
3. **Organization isolation** - Integrations are tied to organizations
4. **Token encryption** - Consider encrypting tokens at rest in DynamoDB

## Related Documentation

- [Gmail Integration](./gmail-integration.md) - Email integration using the same OAuth app
- [Additional Agent Tools](./additional-agent-tools.md) - Built-in tool reference
- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results

