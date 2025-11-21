import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Dict
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
        Get current UTC time in ISO 8601 format.
        
        Returns:
            ISO 8601 formatted timestamp string
        """
        return datetime.now(timezone.utc).isoformat()
    
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
        
        Args:
            related_message_id: The message_id of the original task assignment
            task_results: The dictionary returned from process_task
            
        Returns:
            Dictionary containing the completion report message
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
        
        Returns:
            Dictionary containing the health check response message
        """
        return {
            "message_id": self._generate_message_id(),
            "sender": self.agent_id,
            "recipient": self.supervisor_id,
            "type": "health_check_response",
            "status": "I'm up and ready",
            "timestamp": self._get_current_timestamp()
        }
    
    def handle_incoming_message(self, json_message: str):
        """
        Handle incoming JSON messages from the supervisor or other agents.
        
        This method parses the JSON message, identifies the message type,
        and processes it accordingly:
        - "task_assignment": Executes the task and sends a completion report
        - "health_check": Responds with a health check response
        
        Args:
            json_message: JSON string containing the incoming message
            
        Raises:
            ValueError: If the JSON is malformed or required fields are missing
        """
        try:
            # Parse the JSON message
            message_dict = json.loads(json_message)
        except json.JSONDecodeError as e:
            error_msg = {
                "message_id": self._generate_message_id(),
                "sender": self.agent_id,
                "recipient": self.supervisor_id,
                "type": "error",
                "error": f"Invalid JSON format: {str(e)}",
                "timestamp": self._get_current_timestamp()
            }
            self._send_json_message(error_msg)
            raise ValueError(f"Failed to parse JSON message: {str(e)}")
        
        # Extract message type
        message_type = message_dict.get("type")
        if not message_type:
            error_msg = {
                "message_id": self._generate_message_id(),
                "sender": self.agent_id,
                "recipient": self.supervisor_id,
                "type": "error",
                "error": "Missing required field: 'type'",
                "timestamp": self._get_current_timestamp()
            }
            self._send_json_message(error_msg)
            raise ValueError("Message missing required field: 'type'")
        
        # Extract message_id for task assignment completion reports
        original_message_id = message_dict.get("message_id", "")
        
        # Handle different message types
        if message_type == "task_assignment":
            # Extract task and parameters
            task = message_dict.get("task")
            if not task:
                error_msg = {
                    "message_id": self._generate_message_id(),
                    "sender": self.agent_id,
                    "recipient": self.supervisor_id,
                    "type": "error",
                    "error": "Missing required field: 'task' in task_assignment message",
                    "related_message_id": original_message_id,
                    "timestamp": self._get_current_timestamp()
                }
                self._send_json_message(error_msg)
                raise ValueError("Task assignment message missing required field: 'task'")
            
            task_parameters = task.get("parameters", {})
            if not isinstance(task_parameters, dict):
                error_msg = {
                    "message_id": self._generate_message_id(),
                    "sender": self.agent_id,
                    "recipient": self.supervisor_id,
                    "type": "error",
                    "error": "Invalid 'parameters' field: must be a dictionary",
                    "related_message_id": original_message_id,
                    "timestamp": self._get_current_timestamp()
                }
                self._send_json_message(error_msg)
                raise ValueError("Task parameters must be a dictionary")
            
            # Process the task using existing process_task method
            task_results = self.process_task(task_parameters)
            
            # Create and send completion report
            completion_report = self._create_completion_report(original_message_id, task_results)
            self._send_json_message(completion_report)
            
        elif message_type == "health_check":
            # Respond with health check response
            health_response = self._create_health_check_response()
            self._send_json_message(health_response)
            
        else:
            # Unknown message type
            error_msg = {
                "message_id": self._generate_message_id(),
                "sender": self.agent_id,
                "recipient": self.supervisor_id,
                "type": "error",
                "error": f"Unknown message type: '{message_type}'",
                "supported_types": ["task_assignment", "health_check"],
                "timestamp": self._get_current_timestamp()
            }
            self._send_json_message(error_msg)
            raise ValueError(f"Unsupported message type: '{message_type}'")

