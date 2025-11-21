# Knowledge Base Builder Agent

A Python implementation of a `KnowledgeBaseBuilderAgent` that inherits from `AbstractWorkerAgent` and handles team wiki updates based on daily work interactions. This project is structured as a modular, production-ready multi-agent system following 2025 Python best practices.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Table of Contents

- [Project Structure](#project-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Usage](#usage)
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

## Quick Start

### Basic Usage

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent

# Create agent instance
agent = KnowledgeBaseBuilderAgent(
    agent_id="kb_builder_001",
    supervisor_id="supervisor_001"
)

# Process a wiki update task
task_data = {
    "wiki_update_content": "# Team Wiki\n\n## Project Overview\n...",
    "update_mode": "overwrite"  # or "append"
}

result = agent.process_task(task_data)
print(result)
```

### Running the Demo

```bash
python -m agents.demo
```

### Running Tests

```bash
python -m tests.test_message_handling
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

## Usage

### Task Processing

```python
from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent

agent = KnowledgeBaseBuilderAgent(
    agent_id="kb_builder_001",
    supervisor_id="supervisor_001"
)

# Overwrite mode (default)
result = agent.process_task({
    "wiki_update_content": "# New Wiki Content",
    "update_mode": "overwrite"
})

# Append mode
result = agent.process_task({
    "wiki_update_content": "## Additional Content",
    "update_mode": "append"
})
```

### Message Handling

```python
import json

# Task assignment message
message = {
    "message_id": "msg_001",
    "sender": "supervisor_001",
    "recipient": "kb_builder_001",
    "type": "task_assignment",
    "task": {
        "task_id": "task_123",
        "parameters": {
            "wiki_update_content": "# Wiki Update",
            "update_mode": "overwrite"
        }
    }
}

agent.handle_incoming_message(json.dumps(message))

# Health check message
health_check = {
    "message_id": "msg_002",
    "sender": "supervisor_001",
    "recipient": "kb_builder_001",
    "type": "health_check"
}

agent.handle_incoming_message(json.dumps(health_check))
```

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

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following project standards
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation as needed
7. Submit a pull request

### Contribution Guidelines

- Follow the project's code style and conventions
- Write clear, descriptive commit messages
- Add tests for new features
- Update documentation for user-facing changes
- Ensure backward compatibility when possible

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
