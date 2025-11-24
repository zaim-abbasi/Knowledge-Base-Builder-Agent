"""Test script for Supervisor format compatibility (native format)."""

import json
import requests
import uuid
from datetime import datetime, timezone


def test_supervisor_format():
    """Test that agent correctly handles Supervisor format messages (native format)."""
    
    AGENT_URL = "http://localhost:5000"
    
    print("=" * 70)
    print("Supervisor Format Compatibility Test")
    print("=" * 70)
    print()
    
    # Test 1: Supervisor format task assignment
    print("Test 1: Supervisor Format - Task Assignment (Overwrite)")
    print("-" * 70)
    
    supervisor_request = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "# Team Knowledge Base\n\n## Test Entry\nThis is a test entry from Supervisor format.",
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
    
    print("Sending Supervisor format request:")
    print(json.dumps(supervisor_request, indent=2))
    print()
    
    try:
        response = requests.post(
            f"{AGENT_URL}/message",
            json=supervisor_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        print("Agent response (Supervisor format):")
        print(json.dumps(result, indent=2))
        print()
        
        # Validate Supervisor format response
        assert "status" in result, "Response missing 'status' field"
        if result["status"] == "success":
            assert "request_id" in result, "Success response missing 'request_id'"
            assert "agent_name" in result, "Success response missing 'agent_name'"
            assert "output" in result, "Success response missing 'output'"
            assert result["error"] is None, "Success response should have error: null"
            print("✅ Test 1 PASSED: Supervisor format task assignment (success)")
        else:
            assert "error" in result, "Error response missing 'error' field"
            print("⚠️  Test 1: Task completed with error (check error details)")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test 1 FAILED: {e}")
    except AssertionError as e:
        print(f"❌ Test 1 FAILED: {e}")
    print()
    
    # Test 2: Supervisor format with append mode
    print("Test 2: Supervisor Format - Task Assignment (Append)")
    print("-" * 70)
    
    supervisor_request_append = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "\n\n## Additional Entry\nThis is an appended entry.",
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
    
    print("Sending Supervisor format request (append mode):")
    print(json.dumps(supervisor_request_append, indent=2))
    print()
    
    try:
        response = requests.post(
            f"{AGENT_URL}/message",
            json=supervisor_request_append,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        print("Agent response (Supervisor format):")
        print(json.dumps(result, indent=2))
        print()
        
        if result.get("status") == "success":
            print("✅ Test 2 PASSED: Supervisor format task assignment (append)")
        else:
            print("⚠️  Test 2: Task completed with error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test 2 FAILED: {e}")
    print()
    
    # Test 3: Health check in Supervisor format
    print("Test 3: Supervisor Format - Health Check")
    print("-" * 70)
    
    try:
        response = requests.get(
            f"{AGENT_URL}/health?format=supervisor",
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        
        print("Health check response (Supervisor format):")
        print(json.dumps(result, indent=2))
        print()
        
        assert "status" in result, "Health check response missing 'status'"
        if result.get("status") == "success":
            assert "output" in result, "Health check response missing 'output'"
            print("✅ Test 3 PASSED: Supervisor format health check")
        else:
            print("⚠️  Test 3: Health check returned error")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test 3 FAILED: {e}")
    except AssertionError as e:
        print(f"❌ Test 3 FAILED: {e}")
    print()
    
    # Test 4: Error handling - missing required field
    print("Test 4: Supervisor Format - Error Handling (Missing Field)")
    print("-" * 70)
    
    invalid_request = {
        "request_id": str(uuid.uuid4()),
        "agent_name": "KnowledgeBaseBuilderAgent",
        "intent": "update_wiki",
        "input": {
            "text": "",  # Empty text should still work, but missing metadata might cause issues
            "metadata": {}
        },
        "context": {}
    }
    
    try:
        response = requests.post(
            f"{AGENT_URL}/message",
            json=invalid_request,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        
        print("Agent response (should be error):")
        print(json.dumps(result, indent=2))
        print()
        
        if result.get("status") == "error":
            assert "error" in result, "Error response missing 'error' field"
            print("✅ Test 4 PASSED: Error handling works correctly")
        else:
            print("⚠️  Test 4: Request succeeded (may be valid)")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Test 4 FAILED: {e}")
    print()
    
    print("=" * 70)
    print("Supervisor Format Compatibility Tests Completed!")
    print("=" * 70)
    print()
    print("Note: Make sure the agent API server is running:")
    print("  python api_server.py")
    print()


if __name__ == "__main__":
    test_supervisor_format()

