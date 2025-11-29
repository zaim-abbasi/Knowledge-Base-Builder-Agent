# Knowledge Base Builder Agent

AI agent that creates and manages tasks using natural language input via Supervisor format.

**Key Features:**
- Natural language task parsing with LLM
- MongoDB task storage
- Supervisor format communication
- Health monitoring and logging
- Long-term memory caching

---

## Quick Start

### Installation
```bash
git clone <repository-url>
cd knowledge-base-builder-agent
pip install -r requirements.txt
```

### Configuration
Create `.env` file from `.env.example`:
```bash
cp .env.example .env
# Edit .env with your MongoDB and OpenAI credentials
```

### Run API Server
```bash
python api_server.py
# Server runs on http://127.0.0.1:5000
```

**API Endpoints:**
- `POST /message` - Handle Supervisor format messages
- `GET /health` - Health check
- `GET /` - API information

---

## API Reference

### Agent Information
- **Agent ID:** `KnowledgeBaseBuilderAgent`
- **Supported Intent:** `create_task`
- **Format:** Supervisor format (native)

### Create Task Request
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "KnowledgeBaseBuilderAgent",
  "intent": "create_task",
  "input": {
    "text": "Schedule meeting with CTO at 9 PM today"
  },
  "context": {
    "user_id": "user123",
    "conversation_id": "conv456",
    "timestamp": "2025-11-29T10:00:00Z"
  }
}
```

### Success Response
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_name": "KnowledgeBaseBuilderAgent",
  "status": "success",
  "output": {
    "result": "Task created successfully: 15",
    "confidence": 0.95,
    "details": "Task ID: 15, Task Name: Schedule Meeting With CTO, Status: todo"
  },
  "error": null
}
```

### Health Check
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "request_id": "...",
  "agent_name": "KnowledgeBaseBuilderAgent",
  "status": "success",
  "output": {
    "result": "I'm up and ready",
    "confidence": 1.0,
    "details": "Health check successful at 2025-11-29T10:00:00Z"
  },
  "error": null
}
```

---

## Error Codes

| Code | Description |
|------|-------------|
| `INVALID_JSON` | Malformed JSON |
| `MISSING_FIELD` | Required field missing |
| `INVALID_TYPE` | Wrong data type |
| `INVALID_AGENT` | Agent name mismatch |
| `UNSUPPORTED_INTENT` | Intent not supported (only `create_task` and `health_check`) |
| `MISSING_PARAMETER` | Missing `input.text` |
| `LLM_PARSING_ERROR` | Failed to parse task input |
| `DATABASE_ERROR` | MongoDB operation failed |

---

## Task Storage

Tasks are stored with the following fields:
- `task_id`: Auto-generated numeric ID (1, 2, 3, ...)
- `task_name`: Extracted task name
- `task_description`: Cleaned task description
- `task_deadline`: ISO date/datetime format
- `task_status`: Default "todo"
- `depends_on`: Default null

---

## Long-Term Memory (LTM)

- **Request-Response Caching**: Successful responses cached in `LTM/cache.json`
- **LTM Search First**: Agent checks cache before processing
- **Auto-Persist**: Cache saved to disk automatically

---

## Deployment

### Production (Gunicorn + Nginx)
```bash
gunicorn -c gunicorn_config.py api_server:app
```

See deployment documentation for full production setup.

---

## License
MIT License. See [LICENSE](LICENSE) for details.
