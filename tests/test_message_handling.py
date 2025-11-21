"""
Test script for message handling functionality in KnowledgeBaseBuilderAgent.
"""

from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json


def main():
    # Create an instance of the KnowledgeBaseBuilderAgent
    agent = KnowledgeBaseBuilderAgent(
        agent_id="kb_builder_001",
        supervisor_id="supervisor_001"
    )
    
    print("=" * 70)
    print("KnowledgeBaseBuilderAgent Message Handling Test")
    print("=" * 70)
    print()
    
    # Test 1: Task Assignment Message
    print("Test 1: Task Assignment Message")
    print("-" * 70)
    task_assignment_message = {
        "message_id": "msg_task_001",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "type": "task_assignment",
        "task": {
            "task_id": "task_123",
            "parameters": {
                "wiki_update_content": "# Team Wiki\n\n## New Section\nThis is a new section added via task assignment.",
                "update_mode": "overwrite"
            }
        },
        "timestamp": "2024-01-15T10:00:00Z"
    }
    print("Sending task assignment message:")
    print(json.dumps(task_assignment_message, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(task_assignment_message))
    print()
    
    # Test 2: Health Check Message
    print("Test 2: Health Check Message")
    print("-" * 70)
    health_check_message = {
        "message_id": "msg_health_001",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "type": "health_check",
        "timestamp": "2024-01-15T10:05:00Z"
    }
    print("Sending health check message:")
    print(json.dumps(health_check_message, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(health_check_message))
    print()
    
    # Test 3: Task Assignment with Append Mode
    print("Test 3: Task Assignment with Append Mode")
    print("-" * 70)
    task_assignment_append = {
        "message_id": "msg_task_002",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "type": "task_assignment",
        "task": {
            "task_id": "task_124",
            "parameters": {
                "wiki_update_content": "\n## Additional Updates\n- Completed feature X\n- Fixed bug Y",
                "update_mode": "append"
            }
        },
        "timestamp": "2024-01-15T10:10:00Z"
    }
    print("Sending task assignment (append mode):")
    print(json.dumps(task_assignment_append, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(task_assignment_append))
    print()
    
    # Test 4: Invalid JSON
    print("Test 4: Invalid JSON Handling")
    print("-" * 70)
    invalid_json = '{"type": "task_assignment", "task": {invalid json}'
    print(f"Sending invalid JSON: {invalid_json}")
    print("\nAgent response:")
    try:
        agent.handle_incoming_message(invalid_json)
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    print()
    
    # Test 5: Missing Type Field
    print("Test 5: Missing Type Field")
    print("-" * 70)
    missing_type_message = {
        "message_id": "msg_invalid_001",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "timestamp": "2024-01-15T10:15:00Z"
    }
    print("Sending message without 'type' field:")
    print(json.dumps(missing_type_message, indent=2))
    print("\nAgent response:")
    try:
        agent.handle_incoming_message(json.dumps(missing_type_message))
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    print()
    
    # Test 6: Unknown Message Type
    print("Test 6: Unknown Message Type")
    print("-" * 70)
    unknown_type_message = {
        "message_id": "msg_unknown_001",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "type": "unknown_type",
        "timestamp": "2024-01-15T10:20:00Z"
    }
    print("Sending message with unknown type:")
    print(json.dumps(unknown_type_message, indent=2))
    print("\nAgent response:")
    try:
        agent.handle_incoming_message(json.dumps(unknown_type_message))
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    print()
    
    # Test 7: Task Assignment with Missing Task Field
    print("Test 7: Task Assignment with Missing Task Field")
    print("-" * 70)
    missing_task_message = {
        "message_id": "msg_invalid_002",
        "sender": "supervisor_001",
        "recipient": "kb_builder_001",
        "type": "task_assignment",
        "timestamp": "2024-01-15T10:25:00Z"
    }
    print("Sending task assignment without 'task' field:")
    print(json.dumps(missing_task_message, indent=2))
    print("\nAgent response:")
    try:
        agent.handle_incoming_message(json.dumps(missing_task_message))
    except ValueError as e:
        print(f"Caught expected ValueError: {e}")
    print()
    
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()

