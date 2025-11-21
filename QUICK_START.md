# Quick Start Guide - Knowledge Base Builder Agent

## How to Start the Agent

### Option 1: HTTP API Server (For Supervisor Communication)

```bash
# Start on default port 5000
python api_server.py

# Start on custom port
python api_server.py 8080

# Start on custom host and port (for remote access)
python api_server.py 8080 0.0.0.0
```

The agent will start listening on `http://127.0.0.1:5000` (or your specified host/port).

### Option 2: Testing

```bash
# Run integration tests (tests full protocol via direct method calls)
python tests/test_message_handling.py
```

---

## How Supervisor Communicates with Agent (HTTP)

The agent exposes a REST API that the supervisor can call via HTTP POST requests.

### API Endpoints

1. **POST `/message`** - Send task assignments or health checks
2. **GET `/health`** - Quick health check
3. **GET `/`** - API information

### Example: Supervisor Sending a Task Assignment

```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "task_assignment",
    "task": {
      "name": "update_wiki",
      "parameters": {
        "wiki_update_content": "# Team Wiki\n\n## Daily Update\nToday we completed feature X.",
        "update_mode": "overwrite"
      }
    },
    "timestamp": "2025-11-21T10:00:00Z"
  }'
```

**Agent Response:**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440000",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "completion_report",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "SUCCESS",
  "results": {
    "status": "success",
    "message": "Wiki updated successfully using overwrite mode",
    "wiki_size": 72,
    "update_mode": "overwrite",
    "agent_id": "KnowledgeBaseBuilderAgent"
  },
  "timestamp": "2025-11-21T10:00:05Z"
}
```

### Example: Supervisor Health Check

```bash
curl -X GET http://localhost:5000/health
```

Or via POST message:
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "550e8400-e29b-41d4-a716-446655440001",
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "health_check",
    "timestamp": "2025-11-21T10:05:00Z"
  }'
```

---

## Supervisor Integration Example (Python)

```python
import requests
import json
import uuid
from datetime import datetime, timezone

AGENT_URL = "http://localhost:5000"

def send_task_to_agent(wiki_content: str, update_mode: str = "overwrite"):
    """Send a task assignment to the Knowledge Base Builder Agent."""
    
    message = {
        "message_id": str(uuid.uuid4()),
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "name": "update_wiki",
            "parameters": {
                "wiki_update_content": wiki_content,
                "update_mode": update_mode
            }
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    response = requests.post(
        f"{AGENT_URL}/message",
        json=message,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()

def check_agent_health():
    """Check if the agent is healthy."""
    response = requests.get(f"{AGENT_URL}/health")
    return response.json()

# Example usage
if __name__ == "__main__":
    # Health check
    health = check_agent_health()
    print("Health:", health)
    
    # Send task
    result = send_task_to_agent(
        "# Team Wiki\n\n## Update\nNew content here.",
        "overwrite"
    )
    print("Task result:", result)
```

---

## Communication Flow

```
Supervisor                    Agent (HTTP API)
    |                              |
    |  POST /message               |
    |  (task_assignment)           |
    |------------------------------>|
    |                              | Process task
    |                              | Update wiki
    |                              |
    |  JSON Response                |
    |  (completion_report)          |
    |<------------------------------|
    |                              |
```

---

## Notes

- The agent runs as a **Flask HTTP server**
- All communication is **JSON over HTTP**
- The agent validates all incoming messages against the protocol
- Errors are returned as `error_report` messages
- The agent logs all operations to stdout

