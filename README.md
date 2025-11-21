Here’s a concise version of your README, focusing on essentials and API details for the supervisor:

---

# Knowledge Base Builder Agent

A Python agent for handling team wiki updates in a multi-agent system.

**Key Features:**
- Processes wiki updates (append/overwrite)
- Strict JSON handshake protocol for supervisor-agent communication
- Health monitoring and error reporting

---

## **Quick Start**

### **Installation**
```bash
git clone <repository-url>
cd knowledge-base-builder-agent
pip install -r requirements.txt
```

---

## **Deployment**

### **Testing**
```bash
# Run integration tests
python tests/test_message_handling.py
```

### **As HTTP API (Flask)**
```bash
# Start API server (default: http://127.0.0.1:5000)
python api_server.py

# Custom host/port
python api_server.py 8080 0.0.0.0
```

**API Endpoints:**
- `POST /message` - Handle incoming JSON messages
- `GET /health` - Health check endpoint
- `GET /` - API information

**Example HTTP Request:**
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{"message_id": "...", "sender": "...", ...}'
```

---

## **API Reference for Supervisor**

### **Agent Identification**
- **Agent ID:** `KnowledgeBaseBuilderAgent`
- **Supervisor ID:** `SupervisorAgent_Main`
- **Supported Task:** `update_wiki`

---

### **Message Types**

#### **1. Task Assignment (Supervisor → Agent)**
**Request:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "task_assignment",
  "task": {
    "name": "update_wiki",
    "parameters": {
      "wiki_update_content": "# Team Wiki\n\n## Daily Update\nToday we...",
      "update_mode": "overwrite"  // or "append"
    }
  },
  "timestamp": "2025-11-21T10:00:00Z"
}
```

**Response (Success):**
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

---

#### **2. Health Check (Supervisor → Agent)**
**Request:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "health_check",
  "timestamp": "2025-11-21T10:05:00Z"
}
```

**Response:**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "health_check_response",
  "status": "I'm up and ready",
  "timestamp": "2025-11-21T10:05:00Z"
}
```

---

#### **3. Error Report (Agent → Supervisor)**
**Example:**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440003",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "error_report",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILURE",
  "results": {
    "error_code": "MISSING_FIELD",
    "message": "Missing required field: 'type'"
  },
  "timestamp": "2025-11-21T10:00:05Z"
}
```

---

### **Error Codes**
| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_JSON` | Malformed JSON | Validate JSON before sending |
| `MISSING_FIELD` | Required field missing | Check protocol specification |
| `INVALID_TYPE` | Wrong data type | Verify field types match protocol |
| `INVALID_MESSAGE_TYPE` | Unknown message type | Use "task_assignment" or "health_check" |
| `UNSUPPORTED_TASK` | Task name not supported | Use "update_wiki" |
| `MISSING_PARAMETER` | Task parameter missing | Provide "wiki_update_content" |

---

### **Python Usage Example**
```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json
import uuid
from datetime import datetime, timezone

# Initialize agent
agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

# Create and send a task assignment message
task_message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "task_assignment",
    "task": {
        "name": "update_wiki",
        "parameters": {
            "wiki_update_content": "# Team Wiki\n\n## Daily Update\nToday we...",
            "update_mode": "overwrite"
        }
    },
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

agent.handle_incoming_message(json.dumps(task_message))
```

---

## **Integration**

### **With Supervisor/Registry**
The agent communicates via JSON messages following the protocol:
1. Supervisor sends `task_assignment` or `health_check` messages
2. Agent validates and processes messages
3. Agent responds with `completion_report`, `health_check_response`, or `error_report`

### **Message Routing**
- Messages must include `sender` and `recipient` fields
- Agent validates `recipient` matches its `agent_id`
- All responses include `related_message_id` for correlation

### **Testing**
Run integration tests: `python tests/test_message_handling.py`

---

## **Error Handling**

The agent returns `error_report` messages for protocol violations:
- **Validation Errors:** Missing fields, wrong types, invalid message types
- **Task Errors:** Unsupported tasks, missing parameters
- **Processing Errors:** LTM write failures, exceptions

All errors include `error_code` and descriptive `message`. See Error Codes table above.

---

## **Configuration**

### **Logging**
Logs are output to stdout with timestamps. Configure via `shared/utils.py`.

Agent IDs and settings are configured directly in code (see `api_server.py` and agent initialization).

---

### **License**
MIT License. See [LICENSE](LICENSE) for details.