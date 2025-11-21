"""Example supervisor script for KnowledgeBaseBuilderAgent communication."""

import requests
import json
import uuid
from datetime import datetime, timezone

AGENT_URL = "http://localhost:5000"


def send_task_to_agent(wiki_content: str, update_mode: str = "overwrite"):
    """Send a task assignment to the agent.
    
    Args:
        wiki_content: The wiki content to update
        update_mode: "overwrite" or "append"
        
    Returns:
        Agent's response as a dictionary
    """
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
    
    try:
        response = requests.post(
            f"{AGENT_URL}/message",
            json=message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with agent: {e}")
        return None


def check_agent_health():
    """Check if the agent is healthy. Returns health check response."""
    try:
        response = requests.get(f"{AGENT_URL}/health", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error checking agent health: {e}")
        return None


def main():
    """Example supervisor workflow."""
    print("=" * 60)
    print("Supervisor Example - Communicating with KnowledgeBaseBuilderAgent")
    print("=" * 60)
    print()
    
    print("Step 1: Checking agent health...")
    health = check_agent_health()
    if health:
        print(f"✓ Agent is healthy: {health.get('status', 'unknown')}")
    else:
        print("✗ Agent health check failed")
        return
    print()
    
    print("Step 2: Sending task assignment (overwrite mode) - Initial Wiki Setup")
    initial_wiki = """# Team Knowledge Base

## Project Overview
**Project Name:** Multi-Agent System for Workplace Productivity
**Status:** Active Development
**Team:** Software Engineering Team Alpha

### Project Goals
- Develop a distributed multi-agent system
- Implement supervisor-worker architecture
- Enable seamless agent communication via HTTP API
- Build knowledge base for team collaboration

### Key Features
- Real-time task assignment and processing
- Persistent long-term memory (LTM)
- Health monitoring and error reporting
- Protocol-compliant JSON message exchange

## Team Members
- **Project Lead:** Sarah Johnson
- **Backend Developer:** Michael Chen
- **Frontend Developer:** Emily Rodriguez
- **DevOps Engineer:** David Kim

## Technology Stack
- **Language:** Python 3.8+
- **Framework:** Flask (HTTP API)
- **Storage:** JSON-based LTM
- **Communication:** RESTful API with JSON protocol"""
    
    result1 = send_task_to_agent(initial_wiki, "overwrite")
    if result1:
        print(f"✓ Task completed: {result1.get('status', 'unknown')}")
        if result1.get('status') == 'SUCCESS':
            results = result1.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Update mode: {results.get('update_mode', 'N/A')}")
    else:
        print("✗ Task failed")
    print()
    
    print("Step 3: Sending task assignment (append mode) - Daily Standup Updates")
    daily_updates = """
## Daily Standup - November 21, 2025

### Completed Today
- ✅ Implemented persistent LTM storage with file-based persistence
- ✅ Added request-response caching for improved performance
- ✅ Integrated LTM search before processing (project requirement)
- ✅ Created comprehensive test suite for supervisor-agent communication
- ✅ Deployed agent as HTTP API server on port 5000

### In Progress
- 🔄 Finalizing integration with supervisor registry
- 🔄 Writing project documentation and API contracts
- 🔄 Preparing presentation materials

### Blockers
- ⚠️ Waiting for supervisor registry endpoint details
- ⚠️ Need clarification on health check response format

### Notes
- Agent successfully handles overwrite and append modes
- LTM persistence working correctly across restarts
- Cache retrieval improving response time by ~80%
- All protocol validation tests passing"""
    
    result2 = send_task_to_agent(daily_updates, "append")
    if result2:
        print(f"✓ Task completed: {result2.get('status', 'unknown')}")
        if result2.get('status') == 'SUCCESS':
            results = result2.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Update mode: {results.get('update_mode', 'N/A')}")
    else:
        print("✗ Task failed")
    print()
    
    print("Step 3.5: Sending task assignment (append mode) - Meeting Notes")
    meeting_notes = """
## Team Meeting Notes - November 20, 2025

### Agenda
1. Project status review
2. Integration planning
3. Next sprint planning

### Decisions Made
- **LTM Implementation:** Agreed on file-based JSON storage for simplicity
- **API Contract:** Standardized on JSON message format with required fields
- **Deployment:** Each agent will run as independent HTTP API server
- **Testing:** Comprehensive integration tests required before Phase-3

### Action Items
- [ ] Complete LTM persistence implementation (DONE)
- [ ] Update supervisor registry with agent endpoints
- [ ] Conduct end-to-end integration testing
- [ ] Prepare final project presentation

### Next Steps
- Schedule integration testing session
- Update project documentation
- Prepare demo for final presentation"""
    
    result3 = send_task_to_agent(meeting_notes, "append")
    if result3:
        print(f"✓ Task completed: {result3.get('status', 'unknown')}")
        if result3.get('status') == 'SUCCESS':
            results = result3.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Update mode: {results.get('update_mode', 'N/A')}")
    else:
        print("✗ Task failed")
    print()
    
    print("Step 4: Testing LTM cache retrieval (same request as Step 2)...")
    result4 = send_task_to_agent(initial_wiki, "overwrite")
    if result4:
        print(f"✓ Task completed: {result4.get('status', 'unknown')}")
        if result4.get('status') == 'SUCCESS':
            results = result4.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Note: This should be retrieved from LTM cache (check logs)")
    else:
        print("✗ Task failed")
    print()
    
    print("Step 5: Testing error handling (unsupported task)...")
    error_message = {
        "message_id": str(uuid.uuid4()),
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "name": "unsupported_task",
            "parameters": {}
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
    
    try:
        response = requests.post(
            f"{AGENT_URL}/message",
            json=error_message,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        error_result = response.json()
        print(f"✓ Error handled correctly: {error_result.get('type', 'unknown')}")
        if error_result.get('type') == 'error_report':
            error_info = error_result.get('results', {})
            print(f"  Error code: {error_info.get('error_code', 'N/A')}")
            print(f"  Message: {error_info.get('message', 'N/A')}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Error: {e}")
    print()
    
    print("=" * 60)
    print("Supervisor example completed!")
    print("=" * 60)


if __name__ == "__main__":
    print("Make sure the agent is running: python api_server.py")
    print()
    main()

