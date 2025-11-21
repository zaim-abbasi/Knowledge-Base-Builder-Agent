import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Dict, Tuple
from agents.workers.abstract_worker_agent import AbstractWorkerAgent


class KnowledgeBaseBuilderAgent(AbstractWorkerAgent):
    """
    A concrete worker agent that builds and maintains a team wiki knowledge base
    based on daily work interactions.
    """
    
    def __init__(self, agent_id: str, supervisor_id: str):
        """
        Initialize the KnowledgeBaseBuilderAgent.
        
        Args:
            agent_id: Unique identifier for this agent
            supervisor_id: Identifier of the supervisor agent
        """
        super().__init__(agent_id, supervisor_id)
        # In-memory LTM storage as a dictionary
        self._ltm: Dict[str, Any] = {}
        # Store wiki content in LTM under a specific key
        self._wiki_key = "team_wiki_content"
    
    def process_task(self, task_data: dict) -> dict:
        """
        Process a task related to updating the team wiki.
        
        Expected task_data format:
        {
            "wiki_update_content": str,  # New wiki content to save
            "update_mode": str,  # Optional: "append" or "overwrite" (default: "overwrite")
            ...
        }
        
        Args:
            task_data: Dictionary containing task parameters
            
        Returns:
            Dictionary with processing results including:
            - status: "success" or "error"
            - message: Brief summary of the operation
            - wiki_size: Size of the updated wiki content (if successful)
        """
        try:
            # Extract wiki update content from task data
            wiki_content = task_data.get("wiki_update_content")
            if wiki_content is None:
                return {
                    "status": "error",
                    "message": "Missing required parameter: wiki_update_content",
                    "error_code": "MISSING_PARAMETER"
                }
            
            # Get update mode (append or overwrite)
            update_mode = task_data.get("update_mode", "overwrite").lower()
            
            # Retrieve existing wiki content if appending
            if update_mode == "append":
                existing_content = self.read_from_ltm(self._wiki_key)
                if existing_content:
                    # Append new content to existing content
                    updated_content = f"{existing_content}\n\n{wiki_content}"
                else:
                    # No existing content, just use new content
                    updated_content = wiki_content
            else:
                # Overwrite mode (default)
                updated_content = wiki_content
            
            # Store the updated wiki content in LTM
            success = self.write_to_ltm(self._wiki_key, updated_content)
            
            if success:
                # Calculate wiki size (character count)
                wiki_size = len(updated_content)
                
                return {
                    "status": "success",
                    "message": f"Wiki updated successfully using {update_mode} mode",
                    "wiki_size": wiki_size,
                    "update_mode": update_mode,
                    "agent_id": self.agent_id
                }
            else:
                return {
                    "status": "error",
                    "message": "Failed to write wiki content to LTM",
                    "error_code": "LTM_WRITE_FAILED"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing task: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def send_message(self, recipient: str, message_obj: dict):
        """
        Send a message to another agent.
        For demonstration, this simulates sending by printing the JSON message.
        
        Args:
            recipient: Identifier of the recipient agent
            message_obj: Dictionary containing the message data
        """
        # Simulate message sending by printing JSON to standard output
        message_json = json.dumps({
            "from": self.agent_id,
            "to": recipient,
            "message": message_obj
        }, indent=2)
        
        print(f"[Message from {self.agent_id} to {recipient}]")
        print(message_json)
    
    def write_to_ltm(self, key: str, value: Any) -> bool:
        """
        Store a key-value pair in Long-Term Memory (LTM).
        Currently implemented as an in-memory dictionary.
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            True if the operation was successful, False otherwise
        """
        try:
            self._ltm[key] = value
            return True
        except Exception:
            return False
    
    def read_from_ltm(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from Long-Term Memory (LTM).
        
        Args:
            key: The key to retrieve the value for
            
        Returns:
            The value associated with the key, or None if the key doesn't exist
        """
        return self._ltm.get(key, None)
    
    def get_wiki_content(self) -> Optional[str]:
        """
        Convenience method to retrieve the current wiki content.
        
        Returns:
            The current wiki content, or None if it doesn't exist
        """
        return self.read_from_ltm(self._wiki_key)
    
    def _generate_message_id(self) -> str:
        """
        Generate a new UUID string for message identification.
        
        Returns:
            UUID string
        """
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """
        Get current UTC time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ).
        
        Returns:
            ISO 8601 formatted timestamp string in format YYYY-MM-DDTHH:MM:SSZ
        """
        # Format: YYYY-MM-DDTHH:MM:SSZ (no microseconds, Z suffix)
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _send_json_message(self, message_dict: dict):
        """
        Send a JSON message by printing it to standard output.
        
        Args:
            message_dict: Dictionary containing the message to send
        """
        message_json = json.dumps(message_dict, indent=2)
        print(f"[Message from {message_dict.get('sender', self.agent_id)} to {message_dict.get('recipient', 'unknown')}]")
        print(message_json)
    
    def _create_completion_report(self, related_message_id: str, task_results: dict) -> dict:
        """
        Create a completion report message after processing a task.
        
        Protocol-compliant format:
        {
            "message_id": "uuid-string",
            "sender": "KnowledgeBaseBuilderAgent",
            "recipient": "SupervisorAgent_Main",
            "type": "completion_report",
            "related_message_id": "original-task-message-id",
            "status": "SUCCESS" or "FAILURE",
            "results": { /* task results or error info */ },
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
        }
        
        Args:
            related_message_id: The message_id of the original task assignment
            task_results: The dictionary returned from process_task
            
        Returns:
            Dictionary containing the completion report message conforming to protocol
        """
        # Determine status based on task results
        task_status = task_results.get("status", "error")
        report_status = "SUCCESS" if task_status == "success" else "FAILURE"
        
        return {
            "message_id": self._generate_message_id(),
            "sender": self.agent_id,
            "recipient": self.supervisor_id,
            "type": "completion_report",
            "related_message_id": related_message_id,
            "status": report_status,
            "results": task_results,
            "timestamp": self._get_current_timestamp()
        }
    
    def _create_health_check_response(self) -> dict:
        """
        Create a health check response message.
        
        Protocol-compliant format:
        {
            "message_id": "uuid-string",
            "sender": "KnowledgeBaseBuilderAgent",
            "recipient": "SupervisorAgent_Main",
            "type": "health_check_response",
            "status": "I'm up and ready",
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
        }
        
        Returns:
            Dictionary containing the health check response message conforming to protocol
        """
        return {
            "message_id": self._generate_message_id(),
            "sender": self.agent_id,
            "recipient": self.supervisor_id,
            "type": "health_check_response",
            "status": "I'm up and ready",
            "timestamp": self._get_current_timestamp()
        }
    
    def _create_error_report(self, related_message_id: str, error_code: str, error_message: str) -> dict:
        """
        Create an error report message for invalid or malformed incoming messages.
        
        Protocol-compliant format:
        {
            "message_id": "uuid-string",
            "sender": "KnowledgeBaseBuilderAgent",
            "recipient": "SupervisorAgent_Main",
            "type": "error_report",
            "related_message_id": "incoming-message-id",
            "status": "FAILURE",
            "results": {
                "error_code": "CODE",
                "message": "Human-readable error"
            },
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
        }
        
        Args:
            related_message_id: The message_id of the incoming message that caused the error
            error_code: Error code identifier (e.g., "INVALID_JSON", "MISSING_FIELD")
            error_message: Human-readable error message
            
        Returns:
            Dictionary containing the error report message conforming to protocol
        """
        return {
            "message_id": self._generate_message_id(),
            "sender": self.agent_id,
            "recipient": self.supervisor_id,
            "type": "error_report",
            "related_message_id": related_message_id,
            "status": "FAILURE",
            "results": {
                "error_code": error_code,
                "message": error_message
            },
            "timestamp": self._get_current_timestamp()
        }
    
    def _validate_incoming_message(self, message_dict: dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Validate an incoming message against the JSON handshake protocol.
        
        Required fields for all messages:
        - message_id: string (UUID format)
        - sender: string
        - recipient: string
        - type: string ("task_assignment" or "health_check")
        - timestamp: string (YYYY-MM-DDTHH:MM:SSZ format)
        
        Required fields for task_assignment:
        - task: object
          - name: string
          - parameters: object
        
        Args:
            message_dict: Dictionary containing the parsed message
            
        Returns:
            Tuple of (is_valid, error_code, error_message)
            If valid, returns (True, None, None)
            If invalid, returns (False, error_code, error_message)
        """
        # Check required top-level fields
        required_fields = ["message_id", "sender", "recipient", "type", "timestamp"]
        for field in required_fields:
            if field not in message_dict:
                return (False, "MISSING_FIELD", f"Missing required field: '{field}'")
        
        # Validate field types
        if not isinstance(message_dict.get("message_id"), str):
            return (False, "INVALID_TYPE", "Field 'message_id' must be a string")
        if not isinstance(message_dict.get("sender"), str):
            return (False, "INVALID_TYPE", "Field 'sender' must be a string")
        if not isinstance(message_dict.get("recipient"), str):
            return (False, "INVALID_TYPE", "Field 'recipient' must be a string")
        if not isinstance(message_dict.get("type"), str):
            return (False, "INVALID_TYPE", "Field 'type' must be a string")
        if not isinstance(message_dict.get("timestamp"), str):
            return (False, "INVALID_TYPE", "Field 'timestamp' must be a string")
        
        # Validate message type
        message_type = message_dict.get("type")
        if message_type not in ["task_assignment", "health_check"]:
            return (False, "INVALID_MESSAGE_TYPE", 
                   f"Invalid message type: '{message_type}'. Must be 'task_assignment' or 'health_check'")
        
        # Validate task_assignment specific fields
        if message_type == "task_assignment":
            if "task" not in message_dict:
                return (False, "MISSING_FIELD", "Missing required field: 'task' in task_assignment message")
            
            task = message_dict.get("task")
            if not isinstance(task, dict):
                return (False, "INVALID_TYPE", "Field 'task' must be a dictionary")
            
            if "name" not in task:
                return (False, "MISSING_FIELD", "Missing required field: 'task.name'")
            if not isinstance(task.get("name"), str):
                return (False, "INVALID_TYPE", "Field 'task.name' must be a string")
            
            if "parameters" not in task:
                return (False, "MISSING_FIELD", "Missing required field: 'task.parameters'")
            if not isinstance(task.get("parameters"), dict):
                return (False, "INVALID_TYPE", "Field 'task.parameters' must be a dictionary")
        
        return (True, None, None)
    
    def handle_incoming_message(self, json_message: str):
        """
        Handle incoming JSON messages from the supervisor or other agents.
        
        This method strictly enforces the JSON handshake protocol:
        - Validates all required fields and data types
        - Processes "task_assignment" messages and sends completion reports
        - Processes "health_check" messages and sends health check responses
        - Sends error_report messages for any validation failures
        
        Expected incoming message format:
        {
            "message_id": "uuid-string",
            "sender": "SupervisorAgent_Main",
            "recipient": "KnowledgeBaseBuilderAgent",
            "type": "task_assignment" | "health_check",
            "task": {  // Required only for task_assignment
                "name": "update_wiki",
                "parameters": {
                    "wiki_update_content": "...",
                    "update_mode": "overwrite" | "append"  // optional
                }
            },
            "timestamp": "YYYY-MM-DDTHH:MM:SSZ"
        }
        
        Args:
            json_message: JSON string containing the incoming message conforming to protocol
            
        Returns:
            None (messages are sent via _send_json_message)
            
        Note:
            All errors result in error_report messages being sent. This method does not raise
            exceptions for protocol violations - it responds with error_report messages instead.
        """
        original_message_id = ""
        
        try:
            # Parse the JSON message
            message_dict = json.loads(json_message)
            original_message_id = message_dict.get("message_id", "")
        except json.JSONDecodeError as e:
            # Send error report for invalid JSON
            error_report = self._create_error_report(
                related_message_id="",
                error_code="INVALID_JSON",
                error_message=f"Invalid JSON format: {str(e)}"
            )
            self._send_json_message(error_report)
            return
        
        # Validate message structure
        is_valid, error_code, error_message = self._validate_incoming_message(message_dict)
        if not is_valid:
            error_report = self._create_error_report(
                related_message_id=original_message_id,
                error_code=error_code or "VALIDATION_ERROR",
                error_message=error_message or "Message validation failed"
            )
            self._send_json_message(error_report)
            return
        
        # Extract validated fields
        message_type = message_dict.get("type")
        original_message_id = message_dict.get("message_id")
        
        # Handle different message types
        if message_type == "task_assignment":
            task = message_dict.get("task")
            task_name = task.get("name")
            task_parameters = task.get("parameters", {})
            
            # Validate task name (should be "update_wiki" for this agent)
            if task_name != "update_wiki":
                error_report = self._create_error_report(
                    related_message_id=original_message_id,
                    error_code="UNSUPPORTED_TASK",
                    error_message=f"Unsupported task name: '{task_name}'. This agent only supports 'update_wiki'"
                )
                self._send_json_message(error_report)
                return
            
            # Process the task using existing process_task method
            task_results = self.process_task(task_parameters)
            
            # Create and send completion report
            completion_report = self._create_completion_report(original_message_id, task_results)
            self._send_json_message(completion_report)
            
        elif message_type == "health_check":
            # Respond with health check response
            health_response = self._create_health_check_response()
            self._send_json_message(health_response)

