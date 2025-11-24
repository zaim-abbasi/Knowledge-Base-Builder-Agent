# Supervisor Integration Guide

## Overview

This guide helps you integrate your **Knowledge Base Builder Agent** with the Supervisor system at [https://github.com/Huzaifa-2669/Supervisor-Integration-Agent](https://github.com/Huzaifa-2669/Supervisor-Integration-Agent).

Your agent is **already configured** to use Supervisor format natively, so integration should be straightforward.

---

## Supervisor JSON Contract (Verified)

Based on the Supervisor repository, your agent implements the exact contract:

### Supervisor → Worker (Request)
```json
{
  "request_id": "string (required)",
  "agent_name": "KnowledgeBaseBuilderAgent (required)",
  "intent": "update_wiki (required)",
  "input": {
    "text": "string - wiki content (required)",
    "metadata": {
      "update_mode": "overwrite | append (optional, default: overwrite)"
    }
  },
  "context": {
    "user_id": "string (required)",
    "conversation_id": "string (optional)",
    "timestamp": "string (optional)"
  }
}
```

### Worker → Supervisor (Success Response)
```json
{
  "request_id": "string",
  "agent_name": "KnowledgeBaseBuilderAgent",
  "status": "success",
  "output": {
    "result": "string - success message",
    "confidence": 0.95,
    "details": {
      "status": "success",
      "message": "Wiki updated successfully using overwrite mode",
      "wiki_size": 1234,
      "update_mode": "overwrite",
      "agent_id": "KnowledgeBaseBuilderAgent"
    }
  },
  "error": null
}
```

### Worker → Supervisor (Error Response)
```json
{
  "status": "error",
  "output": null,
  "error": {
    "type": "ERROR_CODE",
    "message": "Error description"
  }
}
```

---

## Agent Registry Entry

Add this entry to your Supervisor's agent registry:

```json
{
  "name": "KnowledgeBaseBuilderAgent",
  "description": "Updates team wiki from daily work interactions. Supports overwrite and append modes for wiki content management.",
  "intents": ["update_wiki"],
  "type": "http",
  "endpoint": "http://your-host:5000/message",
  "healthcheck": "http://your-host:5000/health",
  "timeout_ms": 10000
}
```

**Important Notes:**
- Replace `your-host` with your actual hostname/IP (e.g., `localhost`, `192.168.1.100`, or your cloud hostname)
- Default port is `5000` (configurable via `python api_server.py <port> <host>`)
- `timeout_ms` should be sufficient for wiki operations (10 seconds is recommended)

---

## Deployment Steps

### 1. Start Your Agent

```bash
# In your agent repository
cd "Knowledge Builder"
python api_server.py
```

The agent will start on `http://127.0.0.1:5000` by default.

### 2. Test Health Check

```bash
# Test health check endpoint
curl http://localhost:5000/health
```

Expected response:
```json
{
  "request_id": "...",
  "agent_name": "KnowledgeBaseBuilderAgent",
  "status": "success",
  "output": {
    "result": "I'm up and ready",
    "confidence": 1.0,
    "details": {...}
  },
  "error": null
}
```

### 3. Test Task Assignment

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "update_wiki",
    "input": {
      "text": "# Test Wiki\n\nThis is a test entry.",
      "metadata": {
        "update_mode": "overwrite"
      }
    },
    "context": {
      "user_id": "test_user",
      "timestamp": "2025-01-21T10:00:00Z"
    }
  }'
```

### 4. Register with Supervisor

Add the registry entry (from above) to your Supervisor's agent registry file.

---

## Network Configuration

### Local Development
- **Agent URL:** `http://localhost:5000`
- **Health Check:** `http://localhost:5000/health`
- **Note:** Supervisor and agent must be on the same machine or network

### Cloud/Remote Deployment
- **Agent URL:** `http://your-domain.com:5000` or `http://your-ip:5000`
- **Health Check:** `http://your-domain.com:5000/health`
- **Note:** Ensure firewall allows incoming connections on port 5000

### Docker Deployment (Optional)
If deploying in Docker:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "api_server.py", "5000", "0.0.0.0"]
```

---

## Supported Intents

Your agent currently supports:

1. **`update_wiki`** - Updates the team wiki
   - **Input.text:** Wiki content (markdown supported)
   - **Input.metadata.update_mode:** `"overwrite"` (default) or `"append"`

2. **`health_check`** - Health check (handled automatically by Supervisor)

---

## Error Codes

Your agent returns these error codes (matching Supervisor format):

| Error Code | Description |
|------------|-------------|
| `INVALID_JSON` | Malformed JSON in request |
| `INVALID_FORMAT` | Message not in Supervisor format |
| `MISSING_FIELD` | Required field missing |
| `INVALID_TYPE` | Wrong data type for field |
| `INVALID_AGENT` | Agent name doesn't match |
| `VALIDATION_ERROR` | Message validation failed |
| `UNSUPPORTED_INTENT` | Intent not supported (only `update_wiki` and `health_check` supported) |
| `MISSING_PARAMETER` | Missing `input.text` for wiki update |
| `LTM_WRITE_FAILED` | Failed to write to LTM |
| `PROCESSING_ERROR` | General processing error |
| `INVALID_CONTENT_TYPE` | Content-Type must be application/json (API level) |
| `NO_RESPONSE` | No response generated by agent (API level) |
| `INTERNAL_ERROR` | Internal server error (API level) |
| `HEALTH_CHECK_FAILED` | Health check processing failed (API level) |

---

## Testing Integration

### Manual Test Script

Create a test script to verify Supervisor integration:

```python
import requests
import json
import uuid
from datetime import datetime, timezone

AGENT_URL = "http://localhost:5000"

# Test 1: Health Check
print("Testing health check...")
response = requests.get(f"{AGENT_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
print()

# Test 2: Wiki Update
print("Testing wiki update...")
request = {
    "request_id": str(uuid.uuid4()),
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "update_wiki",
    "input": {
        "text": "# Test Wiki\n\nThis is a test entry from Supervisor integration.",
        "metadata": {
            "update_mode": "overwrite"
        }
    },
    "context": {
        "user_id": "integration_test",
        "conversation_id": "test_conv",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
}

response = requests.post(
    f"{AGENT_URL}/message",
    json=request,
    headers={"Content-Type": "application/json"}
)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")
```

---

## Troubleshooting

### Issue: Supervisor can't reach agent

**Solutions:**
1. Check agent is running: `curl http://localhost:5000/health`
2. Verify network connectivity between Supervisor and agent
3. Check firewall settings
4. Verify hostname/IP in registry entry

### Issue: Agent returns error responses

**Solutions:**
1. Check agent logs for detailed error messages
2. Verify request format matches Supervisor contract exactly
3. Ensure `agent_name` in request matches `"KnowledgeBaseBuilderAgent"`
4. Check that `intent` is `"update_wiki"` (not `"update_wiki"` with typos)

### Issue: Timeout errors

**Solutions:**
1. Increase `timeout_ms` in registry entry
2. Check agent processing time (LTM operations can be slow on first run)
3. Verify network latency

---

## Next Steps

1. ✅ **Deploy your agent** (start `api_server.py`)
2. ✅ **Test health check** (verify endpoint responds)
3. ✅ **Add to Supervisor registry** (use registry entry above)
4. ✅ **Test integration** (send test request from Supervisor)
5. ✅ **Monitor logs** (check both Supervisor and agent logs)

---

## Additional Resources

- **Supervisor Repository:** [https://github.com/Huzaifa-2669/Supervisor-Integration-Agent](https://github.com/Huzaifa-2669/Supervisor-Integration-Agent)
- **Agent API Documentation:** See `README.md` in your agent repository
- **Integration Guide:** This file (`SUPERVISOR_INTEGRATION.md`) contains all integration details

---

## Support

If you encounter issues:
1. Check agent logs: Look for error messages in console output
2. Verify JSON format: Use the examples above
3. Test endpoints individually: Health check first, then message endpoint
4. Review Supervisor logs: Check Supervisor's error messages

Your agent is **ready for integration** - it uses Supervisor format natively and matches the contract exactly! 🚀

