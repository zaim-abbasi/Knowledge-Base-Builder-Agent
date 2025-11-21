# Knowledge Base Builder Agent

A Python implementation of a `KnowledgeBaseBuilderAgent` that inherits from `AbstractWorkerAgent` and handles team wiki updates based on daily work interactions. This project is structured as a modular, production-ready multi-agent system following 2025 Python best practices.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Deployment](#deployment)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
- [JSON Handshake Protocol](#json-handshake-protocol)
- [Integration with Supervisor/Registry](#integration-with-supervisorregistry)
- [Configuration and Customization](#configuration-and-customization)
- [Logging and Health Monitoring](#logging-and-health-monitoring)
- [Best Practices and Troubleshooting](#best-practices-and-troubleshooting)
- [Extending the Agent](#extending-the-agent)
- [Quick Reference](#quick-reference)
- [Architecture](#architecture)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Project Structure

```
knowledge-base-builder-agent/
│
├── agents/                    # Agent implementations
│   ├── workers/              # Worker agent classes
│   │   ├── __init__.py
│   │   ├── abstract_worker_agent.py
│   │   └── knowledge_base_builder_agent.py
│   ├── __init__.py
│   └── demo.py               # Demonstration script
│
├── tests/                     # Test suite
│   ├── __init__.py
│   └── test_message_handling.py
│
├── communication/             # Inter-agent communication
│   ├── __init__.py
│   ├── protocol.py           # Message protocols (future)
│   └── models.py             # Message models (future)
│
├── config/                    # Configuration files
│   ├── settings.yaml         # System-wide settings
│   └── agent_config.json      # Agent configuration
│
├── LTM/                       # Long-Term Memory storage
│   └── __init__.py
│
├── shared/                    # Shared utilities
│   ├── __init__.py
│   └── utils.py              # Common utilities (future)
│
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT License
├── pyproject.toml            # Modern Python packaging config
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knowledge-base-builder-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install in development mode (optional)**
   ```bash
   pip install -e .
   ```

4. **Install with development tools (optional)**
   ```bash
   pip install -e ".[dev]"
   ```

## Deployment

### Environment Configuration

**Required:**
- Python 3.8 or higher
- pip package manager

**Optional (for development):**
- pytest (for running tests)
- black, flake8, mypy (for code quality)

### Running as Command-Line Application

The agent can be used directly in Python scripts or as a module:

#### Option 1: Direct Python Script

Create a script `run_agent.py`:

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json
import sys

# Initialize agent
agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

# Read message from stdin or command line
if len(sys.argv) > 1:
    message = sys.argv[1]
else:
    message = sys.stdin.read()

# Process message
agent.handle_incoming_message(message)
```

Run with:
```bash
python run_agent.py '{"message_id": "...", "type": "health_check", ...}'
```

Or pipe JSON:
```bash
echo '{"message_id": "...", "type": "health_check", ...}' | python run_agent.py
```

#### Option 2: Module Execution

Run the demo script:
```bash
python -m agents.demo
```

Run tests:
```bash
python -m tests.test_message_handling
```

### Running as HTTP API Server (Simple Implementation)

For integration with HTTP-based systems, create a simple Flask/FastAPI wrapper:

**Example with Flask** (requires `pip install flask`):

```python
# server.py
from flask import Flask, request, jsonify
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json

app = Flask(__name__)
agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "agent_id": agent.agent_id})

@app.route('/message', methods=['POST'])
def handle_message():
    try:
        message_json = request.get_json()
        if not message_json:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Process message (responses are printed to stdout)
        # In production, capture and return response
        agent.handle_incoming_message(json.dumps(message_json))
        return jsonify({"status": "processed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

Run the server:
```bash
python server.py
```

Send requests:
```bash
curl -X POST http://localhost:5000/message \
  -H "Content-Type: application/json" \
  -d '{"message_id": "...", "type": "health_check", ...}'
```

### Running Demo and Test Scripts

**Demo Script:**
```bash
python -m agents.demo
```
Demonstrates:
- Direct task processing
- Wiki content updates (overwrite/append)
- LTM operations
- Error handling

**Test Script:**
```bash
python -m tests.test_message_handling
```
Tests:
- Protocol-compliant message handling
- Task assignment processing
- Health check responses
- Error report generation
- Validation of malformed messages

## Quick Start

### Basic Usage

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json
import uuid
from datetime import datetime, timezone

# Create agent instance
agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

# Process a wiki update task directly
task_data = {
    "wiki_update_content": "# Team Wiki\n\n## Project Overview\n...",
    "update_mode": "overwrite"  # or "append"
}

result = agent.process_task(task_data)
print(result)

# Or send a protocol-compliant message
message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "task_assignment",
    "task": {
        "name": "update_wiki",
        "parameters": task_data
    },
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

agent.handle_incoming_message(json.dumps(message))
```

### Running the Demo

```bash
python -m agents.demo
```

### Running Tests

```bash
python -m tests.test_message_handling
```

## Usage Guide

### Scenario 1: Direct Method Invocation

Use `process_task()` for direct task execution without protocol overhead:

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent

agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

# Process task directly
result = agent.process_task({
    "wiki_update_content": "# Team Wiki\n\n## Update\nNew content here.",
    "update_mode": "overwrite"
})

print(result)
# Output: {'status': 'success', 'message': '...', 'wiki_size': 45, ...}
```

**Use Cases:**
- Standalone scripts
- Direct integration without supervisor
- Testing and development
- Batch processing

### Scenario 2: Protocol-Compliant Message Handling

Use `handle_incoming_message()` for supervisor integration:

```python
import json
import uuid
from datetime import datetime, timezone

# Create protocol-compliant message
message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "task_assignment",
    "task": {
        "name": "update_wiki",
        "parameters": {
            "wiki_update_content": "# Team Wiki\n\n## Update\nNew content.",
            "update_mode": "overwrite"
        }
    },
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

# Process message
agent.handle_incoming_message(json.dumps(message))
```

**Use Cases:**
- Supervisor-worker architecture
- Multi-agent systems
- Production deployments
- Protocol validation required

### Sample JSON Requests and Responses

#### Task Assignment Request

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
      "update_mode": "overwrite"
    }
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

#### Task Assignment Response (Success)

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
  "timestamp": "2024-01-15T10:00:05Z"
}
```

#### Health Check Request

```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "health_check",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

#### Health Check Response

```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "health_check_response",
  "status": "I'm up and ready",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

### Error Report Examples

#### Missing Required Field

**Request:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440002",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "timestamp": "2024-01-15T10:10:00Z"
}
```

**Response (error_report):**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440002",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "error_report",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440002",
  "status": "FAILURE",
  "results": {
    "error_code": "MISSING_FIELD",
    "message": "Missing required field: 'type'"
  },
  "timestamp": "2024-01-15T10:10:00Z"
}
```

#### Invalid JSON

**Request:** `{"type": "task_assignment", "task": {invalid json}`

**Response (error_report):**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440003",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "error_report",
  "related_message_id": "",
  "status": "FAILURE",
  "results": {
    "error_code": "INVALID_JSON",
    "message": "Invalid JSON format: Expecting property name..."
  },
  "timestamp": "2024-01-15T10:15:00Z"
}
```

#### Unsupported Task

**Request:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440004",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "task_assignment",
  "task": {
    "name": "unsupported_task",
    "parameters": {}
  },
  "timestamp": "2024-01-15T10:20:00Z"
}
```

**Response (error_report):**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440004",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "error_report",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440004",
  "status": "FAILURE",
  "results": {
    "error_code": "UNSUPPORTED_TASK",
    "message": "Unsupported task name: 'unsupported_task'. This agent only supports 'update_wiki'"
  },
  "timestamp": "2024-01-15T10:20:00Z"
}
```

## Architecture

### Class Hierarchy

#### AbstractWorkerAgent

Abstract base class located in `agents/workers/abstract_worker_agent.py` that defines the interface for all worker agents.

**Required Abstract Methods:**
- `process_task(task_data: dict) -> dict`: Execute core business logic
- `send_message(recipient: str, message_obj: dict)`: Send messages to other agents
- `write_to_ltm(key: str, value: Any) -> bool`: Store data in Long-Term Memory
- `read_from_ltm(key: str) -> Optional[Any]`: Retrieve data from Long-Term Memory

#### KnowledgeBaseBuilderAgent

Concrete implementation that:

1. **Processes Tasks**: Handles wiki update tasks with append/overwrite modes
2. **Message Handling**: Processes `task_assignment` and `health_check` messages
3. **Long-Term Memory**: Manages in-memory storage (upgradeable to persistent storage)
4. **Error Handling**: Comprehensive error handling with structured error responses

### Design Principles

- **Modularity**: Clear separation of concerns across packages
- **Extensibility**: Easy to add new agents and features
- **Type Safety**: Type hints throughout the codebase
- **Documentation**: Comprehensive docstrings and documentation
- **Testing**: Test coverage for critical functionality
- **Configuration**: Externalized configuration for flexibility

## JSON Handshake Protocol

The agent strictly enforces a JSON handshake protocol for all inter-agent communication. This ensures reliable, validated message exchange between the supervisor and worker agents.

### Protocol Overview

All messages must conform to a strict JSON structure with required fields validated before processing. The agent responds with protocol-compliant messages for all operations, including error conditions.

### Incoming Message Format

#### Task Assignment Message

```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "task_assignment",
  "task": {
    "name": "update_wiki",
    "parameters": {
      "wiki_update_content": "Today's team update ...",
      "update_mode": "overwrite"
    }
  },
  "timestamp": "2024-01-15T10:00:00Z"
}
```

**Required Fields:**
- `message_id`: UUID string identifying the message
- `sender`: Sender agent identifier (must be "SupervisorAgent_Main")
- `recipient`: Recipient agent identifier (must be "KnowledgeBaseBuilderAgent")
- `type`: Message type (must be "task_assignment" or "health_check")
- `task`: Object containing task information (required for task_assignment)
  - `name`: Task name (must be "update_wiki" for this agent)
  - `parameters`: Dictionary containing task-specific parameters
    - `wiki_update_content`: Required string with wiki content
    - `update_mode`: Optional string ("append" or "overwrite", default: "overwrite")
- `timestamp`: ISO 8601 timestamp in format YYYY-MM-DDTHH:MM:SSZ

#### Health Check Message

```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "health_check",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

**Required Fields:**
- `message_id`: UUID string
- `sender`: Sender agent identifier
- `recipient`: Recipient agent identifier
- `type`: Must be "health_check"
- `timestamp`: ISO 8601 timestamp

### Outgoing Message Formats

#### Completion Report (Success)

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
  "timestamp": "2024-01-15T10:00:05Z"
}
```

#### Completion Report (Failure)

```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "completion_report",
  "related_message_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILURE",
  "results": {
    "status": "error",
    "message": "Missing required parameter: wiki_update_content",
    "error_code": "MISSING_PARAMETER"
  },
  "timestamp": "2024-01-15T10:00:05Z"
}
```

#### Health Check Response

```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440002",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "health_check_response",
  "status": "I'm up and ready",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

#### Error Report

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
  "timestamp": "2024-01-15T10:00:05Z"
}
```

### Error Codes

The agent uses the following error codes in error_report messages:

- `INVALID_JSON`: Malformed JSON string
- `MISSING_FIELD`: Required field is missing
- `INVALID_TYPE`: Field has incorrect data type
- `INVALID_MESSAGE_TYPE`: Message type is not "task_assignment" or "health_check"
- `UNSUPPORTED_TASK`: Task name is not supported (only "update_wiki" is supported)

### Python Usage Examples

#### Sending a Task Assignment

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json
import uuid
from datetime import datetime, timezone

# Create agent
agent = KnowledgeBaseBuilderAgent(
    agent_id="KnowledgeBaseBuilderAgent",
    supervisor_id="SupervisorAgent_Main"
)

# Create task assignment message
task_message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "task_assignment",
    "task": {
        "name": "update_wiki",
        "parameters": {
            "wiki_update_content": "# Team Wiki\n\n## Daily Update\nToday we completed...",
            "update_mode": "overwrite"
        }
    },
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

# Send message
agent.handle_incoming_message(json.dumps(task_message))
```

#### Sending a Health Check

```python
health_check_message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    "type": "health_check",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

agent.handle_incoming_message(json.dumps(health_check_message))
```

#### Handling Invalid Messages

```python
# Missing required field
invalid_message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": "KnowledgeBaseBuilderAgent",
    # Missing "type" field
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

# Agent will respond with error_report
agent.handle_incoming_message(json.dumps(invalid_message))
```

### Technical Details

#### UUID Generation

Message IDs are generated using Python's `uuid.uuid4()` function, which creates RFC 4122 compliant UUIDs.

```python
import uuid
message_id = str(uuid.uuid4())
# Example: "550e8400-e29b-41d4-a716-446655440000"
```

#### Timestamp Format

Timestamps are generated in UTC and formatted as `YYYY-MM-DDTHH:MM:SSZ`:

```python
from datetime import datetime, timezone
timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
# Example: "2024-01-15T10:00:00Z"
```

#### Validation

The agent performs strict validation on all incoming messages:
1. JSON parsing validation
2. Required field presence check
3. Data type validation
4. Message type validation
5. Task-specific validation (for task_assignment messages)

Any validation failure results in an `error_report` message being sent back to the supervisor.

### Task Data Format

The `process_task` method expects:

- `wiki_update_content` (required): String containing wiki content
- `update_mode` (optional): "append" or "overwrite" (default: "overwrite")

### Return Format

Success response:
```python
{
    "status": "success",
    "message": "Wiki updated successfully using overwrite mode",
    "wiki_size": 72,
    "update_mode": "overwrite",
    "agent_id": "kb_builder_001"
}
```

Error response:
```python
{
    "status": "error",
    "message": "Missing required parameter: wiki_update_content",
    "error_code": "MISSING_PARAMETER"
}
```

## Integration with Supervisor/Registry

### Agent Registration

The `KnowledgeBaseBuilderAgent` is identified by its `agent_id` ("KnowledgeBaseBuilderAgent") in the supervisor/registry system. The supervisor uses this identifier to route messages to the correct agent.

**Agent Identification:**
- **Agent ID**: `KnowledgeBaseBuilderAgent`
- **Supervisor ID**: `SupervisorAgent_Main`
- **Supported Tasks**: `update_wiki`

### Message Routing

The supervisor/router selects the agent using the following process:

1. **Registry Lookup**: Supervisor queries the registry for agents matching the task requirements
2. **Agent Selection**: For wiki update tasks, supervisor selects `KnowledgeBaseBuilderAgent`
3. **Message Forwarding**: Supervisor creates a protocol-compliant JSON message and forwards it to the agent
4. **Response Handling**: Supervisor receives and processes the agent's response (completion_report, health_check_response, or error_report)

### Supervisor Integration Flow

```
Supervisor → Registry → KnowledgeBaseBuilderAgent
     ↓                        ↓
Task Request          Process Task
     ↓                        ↓
     ←─── Response ───────────┘
```

**Example Supervisor Code:**

```python
# Supervisor selects agent from registry
agent_id = "KnowledgeBaseBuilderAgent"
agent = registry.get_agent(agent_id)

# Create protocol-compliant message
message = {
    "message_id": str(uuid.uuid4()),
    "sender": "SupervisorAgent_Main",
    "recipient": agent_id,
    "type": "task_assignment",
    "task": {
        "name": "update_wiki",
        "parameters": {
            "wiki_update_content": "...",
            "update_mode": "overwrite"
        }
    },
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
}

# Forward message to agent
response = agent.handle_incoming_message(json.dumps(message))
```

### Contract Validation

The agent enforces the JSON handshake protocol contract through:

1. **Strict Validation**: All incoming messages are validated against the protocol schema
2. **Error Reporting**: Invalid messages receive structured `error_report` responses
3. **Type Safety**: All fields are type-checked (strings, objects, etc.)
4. **Required Fields**: Missing required fields trigger validation errors

### Integration Testing

To test supervisor-agent integration:

1. **Unit Tests**: Run `python -m tests.test_message_handling`
2. **Protocol Compliance**: Verify all messages conform to the JSON handshake protocol
3. **Error Handling**: Test with malformed messages to verify error_report responses
4. **End-to-End**: Test complete supervisor → agent → supervisor flow

**Integration Test Example:**

```python
def test_supervisor_agent_integration():
    # Supervisor creates message
    message = create_task_assignment_message(...)
    
    # Agent processes message
    agent.handle_incoming_message(json.dumps(message))
    
    # Supervisor receives response (captured from stdout or return value)
    # Verify response structure and content
```

## Configuration and Customization

### Configuration Files

The project includes configuration files in the `config/` directory:

#### `config/settings.yaml`

System-wide settings (currently placeholder):

```yaml
# System-wide configuration
agent:
  default_timeout: 30
  max_retries: 3

communication:
  message_queue_size: 100
  retry_interval: 5

ltm:
  storage_backend: "memory"  # or "database", "file", etc.
  persistence_enabled: false
```

#### `config/agent_config.json`

Agent-specific configuration:

```json
{
  "agent_id": "KnowledgeBaseBuilderAgent",
  "supervisor_id": "SupervisorAgent_Main",
  "description": "Knowledge Base Builder Agent Configuration",
  "capabilities": [
    "wiki_update",
    "knowledge_base_maintenance"
  ],
  "settings": {
    "default_update_mode": "overwrite",
    "max_wiki_size": 1000000
  }
}
```

### Updating Configuration

1. **System Settings**: Edit `config/settings.yaml` for system-wide changes
2. **Agent Settings**: Edit `config/agent_config.json` for agent-specific changes
3. **Reload**: Restart the agent to apply configuration changes

**Note**: Currently, configuration files are placeholders. Future implementations will load and use these settings.

### Adding New Agents

To add a new agent to the system:

1. **Create Agent Class**: Add new agent in `agents/workers/`
   ```python
   # agents/workers/my_new_agent.py
   from agents.workers.abstract_worker_agent import AbstractWorkerAgent
   
   class MyNewAgent(AbstractWorkerAgent):
       def process_task(self, task_data: dict) -> dict:
           # Implementation
           pass
       # ... implement other abstract methods
   ```

2. **Register Agent**: Add to `agents/workers/__init__.py`
   ```python
   from agents.workers.my_new_agent import MyNewAgent
   __all__ = [..., "MyNewAgent"]
   ```

3. **Add Configuration**: Update `config/agent_config.json` or create agent-specific config

4. **Add Tests**: Create tests in `tests/`

5. **Update Registry**: Register agent ID in supervisor/registry system

## Logging and Health Monitoring

### Health Check Mechanism

The agent supports health monitoring through the `health_check` message type:

**Health Check Request:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440001",
  "sender": "SupervisorAgent_Main",
  "recipient": "KnowledgeBaseBuilderAgent",
  "type": "health_check",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

**Health Check Response:**
```json
{
  "message_id": "660e8400-e29b-41d4-a716-446655440001",
  "sender": "KnowledgeBaseBuilderAgent",
  "recipient": "SupervisorAgent_Main",
  "type": "health_check_response",
  "status": "I'm up and ready",
  "timestamp": "2024-01-15T10:05:00Z"
}
```

### Health Monitoring Best Practices

1. **Regular Checks**: Supervisor should send health_check messages periodically (e.g., every 30 seconds)
2. **Response Time**: Monitor response time to detect performance issues
3. **Status Tracking**: Track agent availability based on health_check responses
4. **Alerting**: Set up alerts for missing or delayed health_check responses

### Logging Recommendations

**Current Implementation:**
- Messages are printed to stdout (simulated message sending)
- Error reports are sent as structured JSON messages

**Production Logging Setup:**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('KnowledgeBaseBuilderAgent')

# In agent methods:
logger.info(f"Processing task: {task_name}")
logger.error(f"Validation failed: {error_message}")
```

**Logging Levels:**
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages (e.g., validation warnings)
- **ERROR**: Error conditions (e.g., task failures)
- **CRITICAL**: Critical errors requiring immediate attention

**Recommended Log Locations:**
- Application logs: `logs/agent.log`
- Error logs: `logs/errors.log`
- Access logs: `logs/access.log` (for HTTP API)

## Best Practices and Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors

**Problem:**
```
ModuleNotFoundError: No module named 'agents'
```

**Solution:**
- Ensure you're running from the project root directory
- Install the package: `pip install -e .`
- Use module execution: `python -m agents.demo`

#### 2. Invalid JSON

**Problem:**
```
Agent responds with error_report: INVALID_JSON
```

**Solution:**
- Validate JSON before sending: Use `json.loads()` to test
- Check for trailing commas, unescaped quotes
- Use a JSON validator tool

**Example:**
```python
import json
try:
    json.loads(message_string)
except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
```

#### 3. Missing Parameters

**Problem:**
```
Task fails with error_code: MISSING_PARAMETER
```

**Solution:**
- Ensure `wiki_update_content` is provided in task parameters
- Check parameter structure matches expected format
- Verify task.parameters is a dictionary

**Example:**
```python
# Correct
task = {
    "name": "update_wiki",
    "parameters": {
        "wiki_update_content": "Content here",
        "update_mode": "overwrite"  # optional
    }
}
```

#### 4. Unsupported Task Name

**Problem:**
```
error_code: UNSUPPORTED_TASK
```

**Solution:**
- Use task name: `"update_wiki"` (exact match required)
- Check task.name field is present and correct

#### 5. Protocol Validation Errors

**Problem:**
```
error_code: MISSING_FIELD or INVALID_TYPE
```

**Solution:**
- Verify all required fields are present
- Check field types match protocol specification
- Use provided examples as templates

### Error Log Locations

**During Development:**
- Console output (stdout/stderr)
- Test output: `python -m tests.test_message_handling`

**In Production:**
- Application logs: Configure logging to file
- Error reports: Sent as JSON messages to supervisor
- System logs: Check system logging (syslog, journalctl, etc.)

### Debugging Tips

1. **Enable Verbose Output**: Add print statements or logging
2. **Test with Demo**: Run `python -m agents.demo` to verify basic functionality
3. **Validate Messages**: Use JSON validators before sending
4. **Check Agent ID**: Ensure agent_id matches exactly: "KnowledgeBaseBuilderAgent"
5. **Verify Timestamps**: Use correct format: `YYYY-MM-DDTHH:MM:SSZ`

### Performance Considerations

- **Memory**: LTM is currently in-memory; consider persistence for large datasets
- **Message Size**: Large wiki content may impact performance
- **Concurrency**: Current implementation is single-threaded
- **Validation**: Strict validation adds minimal overhead but ensures reliability

## Extending the Agent

### Adding New Functionality

#### Adding a New Task Type

1. **Update `process_task()` method:**
   ```python
   def process_task(self, task_data: dict) -> dict:
       task_name = task_data.get("task_name")
       if task_name == "new_task":
           return self._handle_new_task(task_data)
       # ... existing code
   ```

2. **Implement task handler:**
   ```python
   def _handle_new_task(self, task_data: dict) -> dict:
       # Task implementation
       pass
   ```

3. **Update validation** in `_validate_incoming_message()` if needed
4. **Add tests** for new task type

#### Adding Helper Utilities

1. **Add to `shared/utils.py`:**
   ```python
   def new_utility_function(param: str) -> str:
       """Utility function description."""
       # Implementation
       pass
   ```

2. **Import in agent:**
   ```python
   from shared.utils import new_utility_function
   ```

3. **Document** in docstrings and README

### Project Structure for Extensions

```
agents/
├── workers/
│   ├── knowledge_base_builder_agent.py  # Existing agent
│   └── new_agent.py                     # New agent
│
shared/
└── utils.py                             # Shared utilities

tests/
├── test_message_handling.py            # Existing tests
└── test_new_agent.py                   # New agent tests

config/
└── new_agent_config.json               # New agent config
```

### Forking and Contributing

1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/new-feature`
3. **Make Changes**: Follow project standards (see Development section)
4. **Add Tests**: Ensure all tests pass
5. **Update Documentation**: Update README and docstrings
6. **Submit Pull Request**: Include description of changes

### Development Workflow

1. **Clone and Setup:**
   ```bash
   git clone <repository-url>
   cd knowledge-base-builder-agent
   pip install -e ".[dev]"
   ```

2. **Make Changes:**
   - Follow naming conventions
   - Add type hints
   - Include docstrings
   - Write tests

3. **Test Changes:**
   ```bash
   python -m pytest tests/
   python -m agents.demo
   ```

4. **Code Quality:**
   ```bash
   black agents/ tests/
   flake8 agents/ tests/
   mypy agents/
   ```

## Quick Reference

### Agent Methods

| Method | Input | Output | Description |
|--------|-------|--------|-------------|
| `process_task(task_data)` | `dict` | `dict` | Process task directly (bypasses protocol) |
| `handle_incoming_message(json_str)` | `str` | `None` | Process protocol-compliant JSON message |
| `send_message(recipient, message_obj)` | `str, dict` | `None` | Send message to another agent |
| `write_to_ltm(key, value)` | `str, Any` | `bool` | Store data in Long-Term Memory |
| `read_from_ltm(key)` | `str` | `Any\|None` | Retrieve data from Long-Term Memory |
| `get_wiki_content()` | `None` | `str\|None` | Get current wiki content |

### Message Types

| Type | Direction | Purpose |
|------|-----------|---------|
| `task_assignment` | Incoming | Assign task to agent |
| `health_check` | Incoming | Check agent health |
| `completion_report` | Outgoing | Report task completion |
| `health_check_response` | Outgoing | Respond to health check |
| `error_report` | Outgoing | Report validation/task errors |

### Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `INVALID_JSON` | Malformed JSON | Validate JSON before sending |
| `MISSING_FIELD` | Required field missing | Check protocol specification |
| `INVALID_TYPE` | Wrong data type | Verify field types match protocol |
| `INVALID_MESSAGE_TYPE` | Unknown message type | Use "task_assignment" or "health_check" |
| `UNSUPPORTED_TASK` | Task name not supported | Use "update_wiki" |
| `MISSING_PARAMETER` | Task parameter missing | Provide "wiki_update_content" |
| `LTM_WRITE_FAILED` | LTM storage failed | Check memory/storage availability |
| `PROCESSING_ERROR` | Task processing error | Check task parameters and logs |

### Command Reference

| Command | Description |
|---------|-------------|
| `python -m agents.demo` | Run demonstration script |
| `python -m tests.test_message_handling` | Run message handling tests |
| `pip install -e .` | Install package in development mode |
| `pip install -e ".[dev]"` | Install with development tools |

### File Locations

| File/Directory | Purpose |
|----------------|---------|
| `agents/workers/knowledge_base_builder_agent.py` | Main agent implementation |
| `agents/workers/abstract_worker_agent.py` | Abstract base class |
| `config/agent_config.json` | Agent configuration |
| `config/settings.yaml` | System-wide settings |
| `tests/test_message_handling.py` | Protocol compliance tests |

## Development

### Project Standards

#### Naming Conventions

- **Packages**: Lowercase with underscores (`agents`, `communication`)
- **Modules**: Lowercase with underscores (`abstract_worker_agent.py`)
- **Classes**: PascalCase (`KnowledgeBaseBuilderAgent`)
- **Functions/Methods**: lowercase_with_underscores (`process_task`)
- **Constants**: UPPER_CASE (`MESSAGE_TYPES`)

#### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function signatures
- Include docstrings for all public classes and methods
- Keep functions focused and single-purpose
- Maximum line length: 100 characters (configurable in `pyproject.toml`)

#### Adding New Agents

1. Create a new file in `agents/workers/`
2. Inherit from `AbstractWorkerAgent`
3. Implement all required abstract methods
4. Add the agent to `agents/workers/__init__.py`
5. Create tests in `tests/`
6. Update relevant documentation

Example:
```python
from agents.workers.abstract_worker_agent import AbstractWorkerAgent

class MyNewAgent(AbstractWorkerAgent):
    def process_task(self, task_data: dict) -> dict:
        # Implementation
        pass
    
    # ... implement other abstract methods
```

#### Adding Shared Utilities

1. Add functions to `shared/utils.py`
2. Ensure utilities are truly shared (used by multiple components)
3. Add type hints and docstrings
4. Create tests
5. Update this README if needed

#### Configuration Management

- System-wide settings: `config/settings.yaml`
- Agent-specific config: `config/agent_config.json`
- Use environment variables for sensitive data
- Validate configuration on load

### Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m tests.test_message_handling

# Run with coverage
python -m pytest tests/ --cov=agents --cov-report=html
```

### Code Quality

```bash
# Format code (if black is installed)
black agents/ tests/

# Lint code (if flake8 is installed)
flake8 agents/ tests/

# Type checking (if mypy is installed)
mypy agents/
```

## Contributing

This project is licensed under the MIT License (see [LICENSE](LICENSE) file). Contributions are welcome!

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following project standards
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

### Contribution Guidelines

- Follow the project's code style and conventions (see [Development](#development) section)
- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation for user-facing changes
- Ensure backward compatibility when possible
- Reference the main README.md for standards and conventions

### Code Standards

Refer to the [Development](#development) section for:
- Naming conventions
- Code style guidelines
- Testing requirements
- Documentation standards

## Future Enhancements

The project structure includes placeholder modules for future development:

- **communication/protocol.py**: Standardized message protocols and validation
- **communication/models.py**: Type-safe message data models (Pydantic)
- **shared/utils.py**: Shared utilities for logging, timestamps, configuration
- **LTM/**: Persistent storage backends (SQLite, PostgreSQL, Redis)
- **Supervisor Agent**: Agent coordination and task distribution
- **Registry Service**: Agent discovery and registration

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built following 2025 Python best practices
- Structured for production use and scalability
- Designed for easy extension and maintenance
