"""Test script for message handling functionality in KnowledgeBaseBuilderAgent."""

from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json


def main():
    agent = KnowledgeBaseBuilderAgent(
        agent_id="KnowledgeBaseBuilderAgent",
        supervisor_id="SupervisorAgent_Main"
    )
    
    print("=" * 70)
    print("KnowledgeBaseBuilderAgent Message Handling Test")
    print("JSON Handshake Protocol Compliance Tests")
    print("=" * 70)
    print()
    
    print("Test 1: Valid Task Assignment Message")
    print("-" * 70)
    task_assignment_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440000",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "name": "update_wiki",
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
    
    print("Test 2: Health Check Message")
    print("-" * 70)
    health_check_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440001",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "health_check",
        "timestamp": "2024-01-15T10:05:00Z"
    }
    print("Sending health check message:")
    print(json.dumps(health_check_message, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(health_check_message))
    print()
    
    print("Test 3: Task Assignment with Append Mode")
    print("-" * 70)
    task_assignment_append = {
        "message_id": "550e8400-e29b-41d4-a716-446655440002",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "name": "update_wiki",
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
    
    print("Test 4: Invalid JSON Handling")
    print("-" * 70)
    invalid_json = '{"type": "task_assignment", "task": {invalid json}'
    print(f"Sending invalid JSON: {invalid_json}")
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(invalid_json)
    print()
    
    print("Test 5: Missing Type Field")
    print("-" * 70)
    missing_type_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440003",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "timestamp": "2024-01-15T10:15:00Z"
    }
    print("Sending message without 'type' field:")
    print(json.dumps(missing_type_message, indent=2))
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(json.dumps(missing_type_message))
    print()
    
    print("Test 6: Unknown Message Type")
    print("-" * 70)
    unknown_type_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440004",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "unknown_type",
        "timestamp": "2024-01-15T10:20:00Z"
    }
    print("Sending message with unknown type:")
    print(json.dumps(unknown_type_message, indent=2))
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(json.dumps(unknown_type_message))
    print()
    
    print("Test 7: Task Assignment with Missing Task Field")
    print("-" * 70)
    missing_task_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440005",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "timestamp": "2024-01-15T10:25:00Z"
    }
    print("Sending task assignment without 'task' field:")
    print(json.dumps(missing_task_message, indent=2))
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(json.dumps(missing_task_message))
    print()
    
    print("Test 8: Task Assignment with Missing Task Name")
    print("-" * 70)
    missing_task_name_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440006",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "parameters": {
                "wiki_update_content": "Some content"
            }
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    print("Sending task assignment without 'task.name' field:")
    print(json.dumps(missing_task_name_message, indent=2))
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(json.dumps(missing_task_name_message))
    print()
    
    print("Test 9: Unsupported Task Name")
    print("-" * 70)
    unsupported_task_message = {
        "message_id": "550e8400-e29b-41d4-a716-446655440007",
        "sender": "SupervisorAgent_Main",
        "recipient": "KnowledgeBaseBuilderAgent",
        "type": "task_assignment",
        "task": {
            "name": "unsupported_task",
            "parameters": {
                "some_param": "value"
            }
        },
        "timestamp": "2024-01-15T10:35:00Z"
    }
    print("Sending task assignment with unsupported task name:")
    print(json.dumps(unsupported_task_message, indent=2))
    print("\nAgent response (error_report):")
    agent.handle_incoming_message(json.dumps(unsupported_task_message))
    print()
    
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
