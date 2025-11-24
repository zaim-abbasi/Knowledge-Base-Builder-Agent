"""Test script for message handling functionality in KnowledgeBaseBuilderAgent."""

from agents.workers.knowledge_base_builder_agent import KnowledgeBaseBuilderAgent
import json
from datetime import datetime, timezone
import uuid


def main():
    agent = KnowledgeBaseBuilderAgent(
        agent_id="KnowledgeBaseBuilderAgent",
        supervisor_id="SupervisorAgent_Main"
    )
    
    print("=" * 70)
    print("KnowledgeBaseBuilderAgent Message Handling Test")
    print("Supervisor Format Protocol Compliance Tests")
    print("=" * 70)
    print()
    
    print("Test 1: Valid Supervisor Format - Task Assignment (Update Wiki)")
    print("-" * 70)
    supervisor_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "# Team Wiki\n\n## New Section\nThis is a new section added via Supervisor format.",
            "metadata": {
                "update_mode": "overwrite"
            }
        },
        "context": {
            "user_id": "test_user_123",
            "conversation_id": "conv_456",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending Supervisor format message:")
    print(json.dumps(supervisor_message, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(supervisor_message))
    print()
    
    print("Test 2: Supervisor Format - Health Check")
    print("-" * 70)
    health_check_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "health_check",
        "input": {
            "text": "",
            "metadata": {}
        },
        "context": {
            "user_id": "system",
            "conversation_id": None,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending Supervisor format health check:")
    print(json.dumps(health_check_message, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(health_check_message))
    print()
    
    print("Test 3: Supervisor Format - Task Assignment with Append Mode")
    print("-" * 70)
    supervisor_append = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "\n## Additional Updates\n- Completed feature X\n- Fixed bug Y",
            "metadata": {
                "update_mode": "append"
            }
        },
        "context": {
            "user_id": "test_user_123",
            "conversation_id": "conv_456",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending Supervisor format message (append mode):")
    print(json.dumps(supervisor_append, indent=2))
    print("\nAgent response:")
    agent.handle_incoming_message(json.dumps(supervisor_append))
    print()
    
    print("Test 4: Invalid JSON Handling")
    print("-" * 70)
    invalid_json = '{"request_id": "test", "agent_name": "KnowledgeBaseBuilderAgent", invalid json}'
    print(f"Sending invalid JSON: {invalid_json}")
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(invalid_json)
    print()
    
    print("Test 5: Missing Required Field (request_id)")
    print("-" * 70)
    missing_field_message = {
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "Some content"
        },
        "context": {
            "user_id": "test_user"
        }
    }
    print("Sending message without 'request_id' field:")
    print(json.dumps(missing_field_message, indent=2))
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(json.dumps(missing_field_message))
    print()
    
    print("Test 6: Unsupported Intent")
    print("-" * 70)
    unsupported_intent_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "unsupported_intent",
        "input": {
            "text": "Some content",
            "metadata": {}
        },
        "context": {
            "user_id": "test_user",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending message with unsupported intent:")
    print(json.dumps(unsupported_intent_message, indent=2))
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(json.dumps(unsupported_intent_message))
    print()
    
    print("Test 7: Missing Input Field")
    print("-" * 70)
    missing_input_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "context": {
            "user_id": "test_user",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending message without 'input' field:")
    print(json.dumps(missing_input_message, indent=2))
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(json.dumps(missing_input_message))
    print()
    
    print("Test 8: Missing Context Field")
    print("-" * 70)
    missing_context_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "Some content",
            "metadata": {}
        }
    }
    print("Sending message without 'context' field:")
    print(json.dumps(missing_context_message, indent=2))
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(json.dumps(missing_context_message))
    print()
    
    print("Test 9: Wrong Agent Name")
    print("-" * 70)
    wrong_agent_message = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "WrongAgent",
        "intent": "update_wiki",
        "input": {
            "text": "Some content",
            "metadata": {}
        },
        "context": {
            "user_id": "test_user",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
    print("Sending message with wrong agent_name:")
    print(json.dumps(wrong_agent_message, indent=2))
    print("\nAgent response (Supervisor error format):")
    agent.handle_incoming_message(json.dumps(wrong_agent_message))
    print()
    
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
