# DataWindows Feature Documentation

## 🪟 Overview

**DataWindows** is a powerful feature that enables AI agents to access real-time cached data without accumulating redundant tool messages in the conversation context. DataWindows solve the token waste problem by automatically refreshing with fresh data on every agent invocation.

---

## 🎯 Problem Statement

### Traditional Approach Issues:
1. **Token Waste** - Each tool call to fetch data (e.g., activity feed) creates a new snapshot stored in context
2. **Data Duplication** - Same items appear across multiple snapshots
3. **Stale Data** - Old snapshots mix with current data
4. **Growing Context** - Token consumption increases linearly with each invocation

### Example of the Problem:
```
Turn 1: Tool call → Activity Feed (10 items) → 500 tokens
Turn 2: Tool call → Activity Feed (10 items, 8 duplicates) → 1000 tokens total
Turn 3: Tool call → Activity Feed (10 items, 9 duplicates) → 1500 tokens total
```

---

## ✅ DataWindows Solution

DataWindows provide:
- ✅ **Auto-refresh** on every model invocation
- ✅ **Constant token footprint** (replaces itself rather than accumulating)
- ✅ **Fresh data guarantee** (always current state)
- ✅ **Simple API** for external systems to push updates

### Example with DataWindows:
```
Turn 1: Open DataWindow → Activity Feed (10 items) → 500 tokens
Turn 2: Agent invoked → DataWindow refreshes → Activity Feed (latest 10) → 500 tokens
Turn 3: Agent invoked → DataWindow refreshes → Activity Feed (latest 10) → 500 tokens
```

---

## 🏗️ Architecture

### Database Model

**Table:** `DataWindows`

**Fields:**
- `data_window_id` (string) - Primary key
- `org_id` (string) - Organization ID (indexed for queries)
- `name` (string, optional) - Human-readable name
- `description` (string, optional) - What this DataWindow contains
- `data` (string) - The actual cached data
- `created_at` (int) - Unix timestamp
- `updated_at` (int) - Unix timestamp

### How It Works

1. **Opening a DataWindow** (one-time):
   ```python
   Agent calls: open_data_window(data_window_id="activity_feed_123")
   → Creates AIMessage with tool_call
   → Creates ToolMessage with current data from DataWindow table
   → Both saved to context
   ```

2. **Automatic Refresh** (every subsequent invocation):
   ```python
   User invokes agent
   → AgentChat.invoke() called
   → _refresh_data_windows() scans messages
   → Finds open_data_window tool calls
   → Extracts data_window_id from args
   → Fetches fresh data from database
   → Replaces ToolMessage.content with fresh data
   → Continues with normal invocation
   ```

3. **External Updates**:
   ```python
   External system → PUT /data-window/{id} → Updates data field
   Next agent invocation → Fresh data automatically loaded
   ```

---

## 🚀 API Endpoints

### Create DataWindow
```http
POST /data-window
Authorization: Bearer {token}

{
  "org_id": "org_123",
  "name": "Activity Feed",
  "description": "Recent user activities",
  "data": "Activity 1\nActivity 2\nActivity 3"
}
```

**Response:**
```json
{
  "data_window_id": "dw_456",
  "org_id": "org_123",
  "name": "Activity Feed",
  "description": "Recent user activities",
  "data": "Activity 1\nActivity 2\nActivity 3",
  "created_at": 1699564800,
  "updated_at": 1699564800
}
```

---

### Get DataWindow
```http
GET /data-window/{data_window_id}
Authorization: Bearer {token}
```

**Response:** DataWindow object

---

### Update DataWindow
```http
PUT /data-window/{data_window_id}
Authorization: Bearer {token}

{
  "data": "New Activity 1\nNew Activity 2\nNew Activity 3"
}
```

**Response:** Updated DataWindow object

**Note:** You can also update `name` and `description` fields.

---

### Delete DataWindow
```http
DELETE /data-window/{data_window_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "message": "DataWindow {data_window_id} deleted successfully"
}
```

---

### List DataWindows
```http
GET /data-windows
Authorization: Bearer {token}
```

**Response:** Array of DataWindow objects for user's organizations

---

## 🔧 Agent Tool

### `open_data_window`

**Tool ID:** `open_data_window` (built-in Ajentify tool)

**Description:** Opens a DataWindow to access real-time cached data. Once opened, the DataWindow automatically refreshes with the latest data on each subsequent invocation.

**Parameters:**
- `data_window_id` (string, required) - The unique identifier for the DataWindow

**Example Usage in Agent Prompt:**
```
You are a support agent with access to the activity feed via DataWindow ID: dw_456.
When users ask about recent activity, use the open_data_window tool to check it.
```

**Tool Configuration:**
```python
# Add to agent's tools list
agent = Agent.create_agent(
    agent_name="Support Agent",
    prompt="...",
    tools=["open_data_window"],  # Enable DataWindow access
    org_id="org_123"
)
```

---

## 📝 Usage Examples

### Example 1: Activity Feed

**Setup:**
```python
# Create DataWindow
data_window = DataWindow.create_data_window(
    org_id="org_123",
    name="Activity Feed",
    description="Recent user activities",
    data="1. User John logged in\n2. File uploaded\n3. Task completed"
)

# Create agent with DataWindow access
agent = Agent.create_agent(
    agent_name="Activity Monitor",
    prompt=f"You monitor user activity. Use DataWindow {data_window.data_window_id} to check recent activities.",
    tools=["open_data_window"],
    org_id="org_123"
)
```

**Conversation:**
```
User: "What's been happening recently?"
Agent: [calls open_data_window(data_window_id="dw_456")]
Agent: "Here are the recent activities:
       1. User John logged in
       2. File uploaded
       3. Task completed"

[External system updates DataWindow with new activities]

User: "Any updates?"
Agent: [DataWindow auto-refreshes with new data]
Agent: "Yes! New activities:
       1. User Sarah logged in
       2. Report generated
       3. Email sent"
```

---

### Example 2: Multiple DataWindows

**Setup:**
```python
# Create multiple DataWindows
activities_dw = DataWindow.create_data_window(
    org_id="org_123",
    name="Activities",
    data="Login, Upload, Download"
)

notifications_dw = DataWindow.create_data_window(
    org_id="org_123",
    name="Notifications",
    data="3 new messages, 1 alert"
)

# Agent with access to both
agent = Agent.create_agent(
    prompt=f"You have two DataWindows: {activities_dw.data_window_id} (activities) and {notifications_dw.data_window_id} (notifications).",
    tools=["open_data_window"]
)
```

**Behavior:**
- Both DataWindows open independently
- Both auto-refresh on every invocation
- Agent can reference both data sources

---

## 🔒 Security & Permissions

### Organization-Based Access Control

1. **Creation:** User must belong to the organization
2. **Access:** DataWindow must belong to user's organization
3. **Tool Invocation:** Context must include `org_id` for validation

### Permission Checks

**In Tool Function:**
```python
def open_data_window_func(data_window_id: str, context: dict) -> str:
    # Extract org_id from context
    org_id = context.get("user_defined", {}).get("org_id")
    
    # Fetch DataWindow
    data_window = DataWindow.get_data_window(data_window_id)
    
    # Validate ownership
    if data_window.org_id != org_id:
        raise Exception("Access denied", 403)
    
    return data_window.data
```

**In API Handlers:**
```python
# All handlers validate user belongs to DataWindow's organization
db_user = User.get_user(user.sub)
if data_window.org_id not in db_user.organizations:
    raise Exception("Access denied", 403)
```

---

## ⚙️ Implementation Details

### AgentChat Refresh Logic

**File:** `src/LLM/AgentChat.py`

**Method:** `_refresh_data_windows()`

**Algorithm:**
1. Scan all messages in context
2. Find AIMessages with `open_data_window` tool calls
3. Extract `data_window_id` from tool call args
4. Find corresponding ToolMessage (by tool_call_id)
5. Fetch fresh data from DataWindow table
6. Replace ToolMessage.content with fresh data
7. Handle errors gracefully (replace with error message)

**Recursive Protection:**
```python
def invoke(self, load_data_windows: bool = True):
    if load_data_windows:
        self._refresh_data_windows()
    
    # ... normal invocation ...
    
    if tool_calls:
        return self.invoke(load_data_windows=False)  # Prevent refresh on recursive calls
```

---

## 🧪 Testing

### Test Coverage

**File:** `tests/test_data_window.py`

**Tests:**
1. ✅ `test_create_data_window` - Create via API
2. ✅ `test_get_data_window` - Retrieve by ID
3. ✅ `test_update_data_window` - Update data field
4. ✅ `test_delete_data_window` - Delete and verify removal
5. ✅ `test_get_data_windows_for_user` - List all for user's orgs
6. ✅ `test_agent_opens_data_window` - Agent uses tool
7. ✅ `test_data_window_refresh_on_invoke` - Auto-refresh verification
8. ✅ `test_multiple_data_windows_in_context` - Multiple DataWindows
9. ✅ `test_data_window_permission_check` - Access control
10. ✅ `test_data_window_not_found` - Error handling

### Running Tests
```bash
cd /Users/keanuinterone/Projects/Ajentify/AgentLambda
python -m unittest tests.test_data_window.TestDataWindow
```

---

## 🎨 Best Practices

### 1. Data Format
- Keep data as **plain text** or **structured strings** (JSON, CSV, etc.)
- Make it **LLM-friendly** (clear, concise, well-formatted)
- Include **timestamps** if time-sensitivity matters

**Good:**
```
Recent Activities (Last 10):
- 2024-11-10 14:30: User John logged in
- 2024-11-10 14:25: File uploaded by Sarah
- 2024-11-10 14:20: Task #123 completed
```

**Bad:**
```
{unformatted blob of data}
```

### 2. Update Frequency
- Update DataWindows **as events occur** (event-driven)
- Or use **scheduled updates** (e.g., every 5 minutes)
- Avoid updating **too frequently** (unnecessary DB writes)

### 3. Data Size
- Keep DataWindows **reasonably sized** (< 2000 tokens recommended)
- Use **summarization** for large datasets
- Consider **pagination** or **filtering** for massive feeds

### 4. Naming & Description
- Use **descriptive names** for debugging
- Include **update frequency** in description
- Document **data format** in description

**Example:**
```python
DataWindow.create_data_window(
    name="Activity Feed (Live)",
    description="Last 10 user activities, updates every 30 seconds, format: timestamp - user - action",
    data="..."
)
```

---

## 🚨 Error Handling

### DataWindow Not Found
```python
# Returns 404
GET /data-window/non-existent-id
→ "DataWindow with id: non-existent-id does not exist"
```

### Permission Denied
```python
# Returns 403
GET /data-window/dw_from_another_org
→ "DataWindow does not belong to user's organizations"
```

### Refresh Errors
```python
# If DataWindow fetch fails during invoke:
# ToolMessage.content is replaced with error message
# Agent invocation continues (graceful degradation)

"Error refreshing DataWindow: DataWindow with id: dw_456 does not exist"
```

---

## 📊 Performance Considerations

### Token Efficiency
- **Traditional:** O(n) tokens per conversation turn (accumulating)
- **DataWindows:** O(1) tokens per conversation turn (constant)

### Database Load
- One fetch per DataWindow per agent invocation
- Negligible for typical use cases (< 10 DataWindows per context)
- Consider caching layer for high-traffic scenarios

### Latency
- DataWindow refresh adds **< 50ms** per fetch
- Parallel fetching possible (future optimization)
- Refresh happens **before** LLM invocation (no user-perceived delay)

---

## 🔮 Future Enhancements

### Potential Features:
1. **Batch Refresh** - Fetch multiple DataWindows in one DB call
2. **Client-Side Caching** - Cache DataWindows in AgentChat for same invocation
3. **Conditional Refresh** - Only refresh if `updated_at` changed
4. **DataWindow Subscriptions** - Agent auto-notifies on data changes
5. **Public DataWindows** - Allow read-only access across orgs
6. **DataWindow Templates** - Pre-configured DataWindows for common use cases

---

## 📚 Related Documentation

- [Message Control Endpoints](./message-control-endpoints.md)
- [Tool Registry](../src/Tools/ToolRegistry.py)
- [Agent Chat Implementation](../src/LLM/AgentChat.py)

---

## 🎉 Summary

DataWindows revolutionize how AI agents access live data by:
- ✅ Eliminating token waste from redundant tool calls
- ✅ Ensuring agents always have fresh, current data
- ✅ Maintaining constant context size regardless of conversation length
- ✅ Providing a simple API for external systems to push updates

Perfect for: Activity feeds, notifications, live metrics, real-time status, and any data that changes frequently!

