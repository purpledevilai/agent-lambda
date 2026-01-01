# Additional Agent Tools

## Overview

The `additional_agent_tools` feature allows you to dynamically add tools to a specific context when it's created, without modifying the agent's configuration. This enables context-specific tool availability, where different conversations with the same agent can have access to different sets of tools.

## Key Benefits

- **Context-Specific Tools**: Add tools to individual contexts without changing the agent
- **Dynamic Tool Selection**: Choose which tools to enable per conversation
- **Tool Combination**: Automatically combines with the agent's default tools
- **Flexible Permissions**: Supports both organization tools and built-in Ajentify tools

## How It Works

When you create a context, you can specify an optional `additional_agent_tools` parameter containing a list of tool IDs. These tools will be combined with the agent's default tools whenever the agent is invoked in that context.

### Tool Resolution

When the agent is invoked, the system:
1. Takes the agent's default tools (from `agent.tools`)
2. Adds the context's `additional_agent_tools`
3. Removes any duplicates (preserving order)
4. Makes all combined tools available to the agent

## API Usage

### Creating a Context with Additional Tools

**Endpoint**: `POST /context`

**Request Body**:
```json
{
  "agent_id": "your-agent-id",
  "additional_agent_tools": ["tool-id-1", "tool-id-2"]
}
```

**Complete Example**:
```json
{
  "agent_id": "customer-support-agent",
  "additional_agent_tools": [
    "search_orders",
    "process_refund",
    "web_search"
  ],
  "prompt_args": {
    "customer_name": "John Doe"
  }
}
```

### Response

The created context will include the `additional_agent_tools` field:

```json
{
  "context_id": "ctx-123",
  "agent_id": "customer-support-agent",
  "user_id": "user-456",
  "messages": [],
  "additional_agent_tools": [
    "search_orders",
    "process_refund",
    "web_search"
  ],
  "created_at": 1234567890,
  "updated_at": 1234567890
}
```

## Permission Model

### Tool Access Rules

Tools specified in `additional_agent_tools` must meet one of these criteria:

1. **Organization Tools**: The tool belongs to the agent's organization
2. **Built-in Tools**: The tool is registered in Ajentify's `tool_registry`

If a tool doesn't meet these requirements, the context creation will fail with a `403` permission error.

### Permission Validation

The system validates tools against the **agent's organization**, not the user's organization. This means:

- Tools must be owned by the agent's org or be built-in tools
- Public contexts can use `additional_agent_tools` with proper validation
- You cannot use tools from other organizations

## Use Cases

### 1. Customer Tier-Based Tools

Different customer tiers get access to different tools:

```javascript
// Premium customer context
const premiumContext = await createContext({
  agent_id: "support-agent",
  additional_agent_tools: [
    "priority_escalation",
    "expedited_shipping",
    "premium_support"
  ]
});

// Standard customer context
const standardContext = await createContext({
  agent_id: "support-agent",
  additional_agent_tools: [
    "standard_support"
  ]
});
```

### 2. Seasonal or Limited-Time Tools

Enable special tools for specific contexts:

```javascript
// Holiday season context
const holidayContext = await createContext({
  agent_id: "shopping-assistant",
  additional_agent_tools: [
    "gift_recommendations",
    "holiday_deals",
    "gift_wrapping_options"
  ]
});
```

### 3. Role-Based Access

Provide different tools based on user roles:

```javascript
// Admin user context
const adminContext = await createContext({
  agent_id: "company-assistant",
  additional_agent_tools: [
    "view_all_users",
    "modify_settings",
    "generate_reports"
  ]
});

// Regular user context
const userContext = await createContext({
  agent_id: "company-assistant",
  additional_agent_tools: [
    "view_profile",
    "submit_ticket"
  ]
});
```

### 4. Experiment and A/B Testing

Test new tools with specific users:

```javascript
// Test group gets experimental tool
const testContext = await createContext({
  agent_id: "assistant",
  additional_agent_tools: [
    "experimental_feature"
  ]
});

// Control group gets standard tools
const controlContext = await createContext({
  agent_id: "assistant",
  additional_agent_tools: []
});
```

## Tool Combination Behavior

### Example: Combining Agent Tools with Additional Tools

Given:
- Agent has tools: `["read_memory", "write_memory"]`
- Context specifies: `["web_search", "view_url"]`

Result when agent is invoked:
- Available tools: `["read_memory", "write_memory", "web_search", "view_url"]`

### Example: Duplicate Removal

Given:
- Agent has tools: `["read_memory", "web_search"]`
- Context specifies: `["web_search", "view_url"]`

Result when agent is invoked:
- Available tools: `["read_memory", "web_search", "view_url"]`
- Note: `web_search` appears only once

## Built-in Ajentify Tools

You can always use these built-in tools in `additional_agent_tools`:

- `pass_event` - Pass custom events to the frontend
- `append_memory` - Append data to memory
- `read_memory` - Read from memory
- `view_memory_shape` - View memory structure
- `delete_memory` - Delete memory entries
- `write_memory` - Write to memory
- `open_memory_window` - Open a Memory Window for auto-refreshing memory data ([docs](./memory-window.md))
- `web_search` - Search the web
- `view_url` - View web page contents
- `open_data_window` - Open a DataWindow for live data
- `list_emails` - List emails from Gmail ([docs](./gmail-integration.md))
- `get_email` - Get full email content from Gmail
- `send_email` - Send email via Gmail
- `mark_email_read` - Mark Gmail email as read
- `mark_email_unread` - Mark Gmail email as unread

## Complete Implementation Example

### Backend (Node.js/Express)

```javascript
app.post('/api/start-chat', authenticateUser, async (req, res) => {
  const { agentId, userTier } = req.body;
  
  // Determine tools based on user tier
  const additionalTools = [];
  
  if (userTier === 'premium') {
    additionalTools.push('priority_support', 'advanced_analytics');
  } else if (userTier === 'enterprise') {
    additionalTools.push(
      'priority_support',
      'advanced_analytics',
      'custom_integrations',
      'dedicated_account_manager'
    );
  }
  
  // Create context with tier-specific tools
  const response = await fetch('https://api.ajentify.com/context', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.AJENTIFY_ORG_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      agent_id: agentId,
      additional_agent_tools: additionalTools,
      user_defined: {
        tier: userTier,
        user_id: req.user.id
      }
    })
  });
  
  const context = await response.json();
  res.json({ contextId: context.context_id });
});
```

### Backend (Python/Flask)

```python
@app.route('/api/start-chat', methods=['POST'])
@require_auth
def start_chat():
    agent_id = request.json.get('agent_id')
    user_tier = request.json.get('user_tier')
    
    # Determine tools based on user tier
    additional_tools = []
    
    if user_tier == 'premium':
        additional_tools = ['priority_support', 'advanced_analytics']
    elif user_tier == 'enterprise':
        additional_tools = [
            'priority_support',
            'advanced_analytics',
            'custom_integrations',
            'dedicated_account_manager'
        ]
    
    # Create context with tier-specific tools
    response = requests.post(
        'https://api.ajentify.com/context',
        headers={
            'Authorization': f'Bearer {os.environ["AJENTIFY_ORG_API_KEY"]}',
            'Content-Type': 'application/json'
        },
        json={
            'agent_id': agent_id,
            'additional_agent_tools': additional_tools,
            'user_defined': {
                'tier': user_tier,
                'user_id': current_user.id
            }
        }
    )
    
    context = response.json()
    return {'contextId': context['context_id']}
```

## Error Handling

### Permission Error (403)

Occurs when a tool doesn't belong to the agent's organization or isn't a built-in tool:

```json
{
  "error": "Tool 'unauthorized-tool-id' does not belong to organization 'org-123'"
}
```

**Solution**: Ensure all tools in `additional_agent_tools` are either:
- Created in the same organization as the agent
- Built-in Ajentify tools from the tool registry

### Tool Not Found (404)

Occurs when a tool ID doesn't exist:

```json
{
  "error": "Tool with id: 'non-existent-tool' does not exist"
}
```

**Solution**: Verify the tool ID is correct and the tool exists.

## Important Notes

1. **Optional Field**: `additional_agent_tools` is completely optional. If not provided, defaults to an empty list.

2. **Backward Compatibility**: Existing contexts without this field will have it default to an empty list automatically.

3. **Immutable After Creation**: Once a context is created, its `additional_agent_tools` cannot be modified. Create a new context if you need different tools.

4. **No Tool Removal**: You cannot use this feature to *remove* tools from the agent. It only *adds* tools. To restrict tools, create an agent without default tools and only specify `additional_agent_tools`.

5. **Order Preservation**: When combining tools, the agent's tools come first, followed by additional tools (with duplicates removed).

6. **Works with All Invocation Methods**: Additional tools are available when using:
   - `POST /chat` (normal chat)
   - `POST /chat/add-ai-message` (AI message generation)
   - `POST /chat/invoke` (direct invocation)

## Combining with Other Features

### With `initialize_tools`

You can use both `additional_agent_tools` and `initialize_tools` together:

```json
{
  "agent_id": "support-agent",
  "additional_agent_tools": ["search_orders", "process_refund"],
  "initialize_tools": [
    {
      "tool_id": "load_customer_data",
      "tool_input": {
        "customer_id": "cust-123"
      }
    }
  ]
}
```

This will:
1. Initialize the context by calling `load_customer_data` with the provided input
2. Make `search_orders` and `process_refund` available for all subsequent invocations

### With `prompt_args`

Combine dynamic tools with dynamic prompts:

```json
{
  "agent_id": "assistant",
  "additional_agent_tools": ["premium_feature"],
  "prompt_args": {
    "customer_name": "Alice",
    "tier": "Premium"
  }
}
```

## Testing

When writing tests, you can verify the feature by:

1. Creating a context with `additional_agent_tools`
2. Invoking the agent
3. Checking that the agent successfully uses the additional tools

Example test pattern:

```python
# Create tool
tool = Tool.create_tool(...)

# Create agent WITHOUT the tool
agent = Agent.create_agent(tools=[])

# Create context WITH the tool
context = Context.create_context(
    agent_id=agent.agent_id,
    additional_agent_tools=[tool.tool_id]
)

# Invoke agent and verify it can use the tool
# (Tool calls should appear in generated_messages)
```

## Related Documentation

- [Initialize Tools](./initialize-tools.md) - Pre-populate context with tool results
- [API Keys](./api-keys.md) - Authentication for API access
- [Message Control Endpoints](./message-control-endpoints.md) - Control message saving and generation

