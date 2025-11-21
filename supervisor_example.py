"""Example supervisor script showing how to communicate with KnowledgeBaseBuilderAgent via HTTP."""

import requests
import json
import uuid
from datetime import datetime, timezone

# Agent API URL
AGENT_URL = "http://localhost:5000"


def send_task_to_agent(wiki_content: str, update_mode: str = "overwrite"):
    """Send a task assignment to the Knowledge Base Builder Agent.
    
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
    """Check if the agent is healthy.
    
    Returns:
        Health check response as a dictionary
    """
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
    
    # Step 1: Health check
    print("Step 1: Checking agent health...")
    health = check_agent_health()
    if health:
        print(f"✓ Agent is healthy: {health.get('status', 'unknown')}")
    else:
        print("✗ Agent health check failed")
        return
    print()
    
    # Step 2: Send task assignment (overwrite mode)
    print("Step 2: Sending task assignment (overwrite mode)...")
    result1 = send_task_to_agent(
        "# Team Wiki\n\n## Project Overview\nThis is the main project documentation.",
        "overwrite"
    )
    if result1:
        print(f"✓ Task completed: {result1.get('status', 'unknown')}")
        if result1.get('status') == 'SUCCESS':
            results = result1.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Update mode: {results.get('update_mode', 'N/A')}")
    else:
        print("✗ Task failed")
    print()
    
    # Step 3: Send task assignment (append mode)
    print("Step 3: Sending task assignment (append mode)...")
    result2 = send_task_to_agent(
        "\n## Daily Updates\n- Completed feature X\n- Fixed bug Y",
        "append"
    )
    if result2:
        print(f"✓ Task completed: {result2.get('status', 'unknown')}")
        if result2.get('status') == 'SUCCESS':
            results = result2.get('results', {})
            print(f"  Wiki size: {results.get('wiki_size', 'N/A')} characters")
            print(f"  Update mode: {results.get('update_mode', 'N/A')}")
    else:
        print("✗ Task failed")
    print()
    
    # Step 4: Test error handling (missing parameter)
    print("Step 4: Testing error handling (unsupported task)...")
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

