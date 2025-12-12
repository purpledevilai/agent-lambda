# Async Callbacks

## Overview

Some API operations—particularly chat and agent invocations—can take significant time to complete (10+ seconds, sometimes minutes). Rather than keeping an HTTP connection open and risking timeouts, you can use **async callbacks** to receive responses at a designated endpoint when processing completes.

When you include a `Callback-URL` header in your request, the API will:
1. Return immediately with a `202 Accepted` status and a `request_id`
2. Process your request in the background
3. POST the result to your callback URL when finished

## Making Async Requests

### Required Header

| Header | Description |
|--------|-------------|
| `Callback-URL` | The URL where results should be POSTed |

### Optional Headers

| Header | Description |
|--------|-------------|
| `Callback-Request-ID` | Your custom identifier for this request. If not provided, one will be generated automatically. |
| `Callback-Token` | A token that will be included as the `Authorization` header when POSTing to your callback URL. Use this to authenticate incoming callbacks. |

### Example Request

```bash
curl -X POST https://api.ajentify.com/chat \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Callback-URL: https://your-server.com/webhooks/ajentify" \
  -H "Callback-Request-ID: order-12345" \
  -H "Callback-Token: your-webhook-secret" \
  -d '{
    "context_id": "ctx-abc123",
    "message": "Analyze this dataset and provide recommendations"
  }'
```

### Immediate Response

When using async callbacks, you'll receive an immediate `202 Accepted` response:

```json
{
  "status": "processing",
  "request_id": "order-12345"
}
```

The `request_id` will be your `Callback-Request-ID` if you provided one, otherwise a generated UUID.

## Setting Up Your Callback Endpoint

Your callback endpoint will receive POST requests with the results of your API calls.

### Endpoint Requirements

- Must accept POST requests
- Must accept `application/json` content type
- Should respond quickly (the callback has a 30-second timeout)
- Should return a 2xx status code on success

### Success Response Format

When the API operation succeeds, your endpoint will receive:

```json
{
  "request_id": "order-12345",
  "status_code": 200,
  "response": {
    // The actual API response body
    // Same structure as if you had made a synchronous request
  }
}
```

### Error Response Format

If the API operation fails, your endpoint will receive:

```json
{
  "request_id": "order-12345",
  "status_code": 500,
  "error": "Error message describing what went wrong"
}
```

The `status_code` will match what you would have received from a synchronous request (400, 401, 403, 404, 500, etc.).

## Validating Callbacks

### Using the Callback-Token

If you provided a `Callback-Token` in your original request, it will be included as the `Authorization` header in the callback POST. Use this to verify that callbacks are legitimate:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

EXPECTED_TOKEN = "your-webhook-secret"

@app.route("/webhooks/ajentify", methods=["POST"])
def handle_callback():
    # Validate the authorization token
    auth_header = request.headers.get("Authorization")
    if auth_header != EXPECTED_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Process the callback
    data = request.json
    request_id = data["request_id"]
    status_code = data["status_code"]
    
    if "error" in data:
        # Handle error
        print(f"Request {request_id} failed: {data['error']}")
    else:
        # Handle success
        print(f"Request {request_id} succeeded: {data['response']}")
    
    return jsonify({"received": True}), 200
```

### Using the Request ID

The `request_id` helps you correlate callbacks with your original requests:

```python
# When making the request, store the request_id
pending_requests = {}

def make_async_request(context_id, message):
    request_id = f"chat-{uuid.uuid4()}"
    
    response = requests.post(
        "https://api.ajentify.com/chat",
        headers={
            "Authorization": f"Bearer {API_TOKEN}",
            "Callback-URL": "https://your-server.com/webhooks/ajentify",
            "Callback-Request-ID": request_id,
            "Callback-Token": WEBHOOK_SECRET
        },
        json={"context_id": context_id, "message": message}
    )
    
    # Store metadata about this pending request
    pending_requests[request_id] = {
        "context_id": context_id,
        "started_at": datetime.now()
    }
    
    return request_id

# In your callback handler
@app.route("/webhooks/ajentify", methods=["POST"])
def handle_callback():
    data = request.json
    request_id = data["request_id"]
    
    # Look up the original request
    original = pending_requests.get(request_id)
    if not original:
        return jsonify({"error": "Unknown request"}), 404
    
    # Process with context
    print(f"Response for context {original['context_id']}")
    
    # Clean up
    del pending_requests[request_id]
    
    return jsonify({"received": True}), 200
```

## Complete Example: Node.js/Express

```javascript
const express = require('express');
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(express.json());

const WEBHOOK_SECRET = process.env.WEBHOOK_SECRET;
const API_TOKEN = process.env.AJENTIFY_API_TOKEN;
const pendingRequests = new Map();

// Make an async chat request
async function sendAsyncChat(contextId, message) {
  const requestId = `chat-${uuidv4()}`;
  
  await axios.post('https://api.ajentify.com/chat', {
    context_id: contextId,
    message: message
  }, {
    headers: {
      'Authorization': `Bearer ${API_TOKEN}`,
      'Callback-URL': 'https://your-server.com/webhooks/ajentify',
      'Callback-Request-ID': requestId,
      'Callback-Token': WEBHOOK_SECRET
    }
  });
  
  pendingRequests.set(requestId, { contextId, timestamp: Date.now() });
  return requestId;
}

// Handle callbacks
app.post('/webhooks/ajentify', (req, res) => {
  // Validate token
  if (req.headers.authorization !== WEBHOOK_SECRET) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  
  const { request_id, status_code, response, error } = req.body;
  
  // Find original request
  const original = pendingRequests.get(request_id);
  if (!original) {
    return res.status(404).json({ error: 'Unknown request' });
  }
  
  if (error) {
    console.error(`Request ${request_id} failed (${status_code}): ${error}`);
  } else {
    console.log(`Request ${request_id} succeeded:`, response);
    // Do something with the response...
  }
  
  pendingRequests.delete(request_id);
  res.json({ received: true });
});

app.listen(3000);
```

## Best Practices

### 1. Always Use a Callback-Token

Without a token, anyone who discovers your callback URL could send fake responses. Always include a secret token and validate it.

### 2. Use Meaningful Request IDs

Instead of relying on auto-generated UUIDs, use request IDs that include context about the operation:

```
chat-user123-1702345678
approval-order456-abc
```

This makes debugging and log analysis much easier.

### 3. Handle Timeouts Gracefully

If you don't receive a callback within a reasonable time (e.g., 15 minutes), assume something went wrong. Implement timeout handling:

```python
# Check for stale pending requests periodically
def cleanup_stale_requests():
    now = datetime.now()
    stale = [
        rid for rid, data in pending_requests.items()
        if (now - data["started_at"]).seconds > 900  # 15 minutes
    ]
    for rid in stale:
        print(f"Request {rid} timed out")
        del pending_requests[rid]
```

### 4. Respond Quickly

Your callback endpoint should respond within a few seconds. If you need to do heavy processing, accept the callback, store the data, and process it asynchronously:

```python
@app.route("/webhooks/ajentify", methods=["POST"])
def handle_callback():
    # Validate quickly
    if request.headers.get("Authorization") != WEBHOOK_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Queue for async processing
    queue.enqueue(process_callback, request.json)
    
    # Respond immediately
    return jsonify({"received": True}), 200
```

### 5. Implement Idempotency

In rare cases, you might receive duplicate callbacks. Design your handler to be idempotent:

```python
processed_requests = set()

@app.route("/webhooks/ajentify", methods=["POST"])
def handle_callback():
    request_id = request.json["request_id"]
    
    if request_id in processed_requests:
        # Already handled, just acknowledge
        return jsonify({"received": True}), 200
    
    processed_requests.add(request_id)
    # Process...
```

## Troubleshooting

### Callback Not Received

1. **Check your endpoint is publicly accessible** - The callback comes from AWS Lambda, not your local machine
2. **Verify your URL is correct** - Typos in `Callback-URL` will silently fail
3. **Check your server logs** - Look for incoming POST requests
4. **Ensure HTTPS** - Use HTTPS for your callback URL in production

### Unauthorized Errors in Your Logs

If you're seeing 401 errors when callbacks arrive:
- Verify your `Callback-Token` matches what your endpoint expects
- Check for whitespace or encoding issues in the token

### Missing Request ID

If `request_id` is null or missing:
- Ensure you're reading from `request.json["request_id"]`, not from headers
- The request ID is in the POST body, not a header

