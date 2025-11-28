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
  "intent": "create_task (required)",
  "input": {
    "text": "string - plain English task description (required)",
    "metadata": {}
  },
  "context": {
    "user_id": "string (required)",
    "conversation_id": "string (optional)",
    "timestamp": "string (optional)"
  }
}
```

**Input.text Examples:**
- Structured: "Task ID: PROJ-001, Task Name: Build API, Description: Create REST API, Deadline: 2025-12-31"
- Plain English: "I need to implement user authentication by next week"
- Minimal: "authentication" or "fix bug" or "update docs"

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
      "message": "Task created successfully: TASK-001",
      "task_id": "TASK-001",
      "task_name": "Implement Authentication System",
      "task_status": "todo",
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
  "description": "Creates and manages tasks from plain English input. Uses LLM to parse task information and stores tasks in MongoDB. Handles any input format from structured to single words.",
  "intents": ["create_task"],
  "type": "http",
  "endpoint": "http://your-host:5000/message",
  "healthcheck": "http://your-host:5000/health",
  "timeout_ms": 30000
}
```

**Important Notes:**
- Replace `your-host` with your actual hostname/IP (e.g., `localhost`, `192.168.1.100`, or your cloud hostname like `vps.zaim-abbasi.tech`)
- Default port is `5000` (configurable via environment variables or command line)
- `timeout_ms` should be sufficient for LLM processing (30 seconds recommended for LLM calls)


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

### 3. Test Task Creation

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-123",
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "create_task",
    "input": {
      "text": "Task ID: TEST-001, Task Name: Test Integration, Description: Verify Supervisor integration works correctly, Deadline: 2025-12-31",
      "metadata": {}
    },
    "context": {
      "user_id": "test_user",
      "timestamp": "2025-01-21T10:00:00Z"
    }
  }'
```

Or with plain English:
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "request_id": "test-124",
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "create_task",
    "input": {
      "text": "I need to implement user authentication by next week",
      "metadata": {}
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

1. **`create_task`** - Creates a new task from plain English input
   - **Input.text:** Plain English task description (any format: structured, unstructured, single words, phrases, sentences)
   - **Input.metadata:** Optional metadata (currently unused, can be empty object)
   - **LLM Processing:** Automatically extracts task_id, task_name, task_description, task_deadline
   - **Storage:** Stores task in MongoDB with defaults: `task_status="todo"`, `depends_on=None`
   - **Input Examples:**
     - Structured: "Task ID: PROJ-001, Task Name: Build API, Deadline: 2025-12-31"
     - Plain English: "I need to fix the login bug by next Monday"
     - Minimal: "authentication" or "update docs"

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
| `UNSUPPORTED_INTENT` | Intent not supported (only `create_task` and `health_check` supported) |
| `MISSING_PARAMETER` | Missing `input.text` for task creation |
| `INITIALIZATION_ERROR` | Database or LLM parser not initialized |
| `LLM_PARSING_ERROR` | Failed to parse task input with LLM |
| `DATABASE_ERROR` | Failed to create task in MongoDB |
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

# Test 2: Task Creation
print("Testing task creation...")
request = {
    "request_id": str(uuid.uuid4()),
    "agent_name": "KnowledgeBaseBuilderAgent",
    "intent": "create_task",
    "input": {
        "text": "Task ID: INTEGRATION-TEST-001, Task Name: Test Supervisor Integration, Description: Verify that the agent works correctly with Supervisor, Deadline: 2025-12-31",
        "metadata": {}
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
4. Check that `intent` is `"create_task"` (not `"update_wiki"` or other intents)
5. Verify MongoDB connection and LLM API key are configured in `.env` file
6. Check that `input.text` contains task description (can be plain English)

### Issue: Timeout errors

**Solutions:**
1. Increase `timeout_ms` in registry entry (recommended: 30000ms for LLM processing)
2. Check agent processing time (LLM API calls can take 3-5 seconds)
3. Verify network latency
4. Check LLM API key and base URL in `.env` file

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

