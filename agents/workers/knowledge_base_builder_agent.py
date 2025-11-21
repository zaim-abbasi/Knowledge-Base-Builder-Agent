import json
import uuid
from datetime import datetime, timezone
from typing import Any, Optional, Dict, Tuple
from agents.workers.abstract_worker_agent import AbstractWorkerAgent
from shared.utils import setup_logger


class KnowledgeBaseBuilderAgent(AbstractWorkerAgent):
    """Worker agent that builds and maintains a team wiki knowledge base."""
    
    def __init__(self, agent_id: str, supervisor_id: str):
        """Initialize the agent.
        
        Args:
            agent_id: Unique identifier for this agent
            supervisor_id: Identifier of the supervisor agent
        """
        super().__init__(agent_id, supervisor_id)
        self.logger = setup_logger(self.__class__.__name__)
        self._ltm: Dict[str, Any] = {}
        self._wiki_key = "team_wiki_content"
        self.logger.info(f"Initialized {agent_id} with supervisor {supervisor_id}")
    
    def process_task(self, task_data: dict) -> dict:
        """Process wiki update task.
        
        Args:
            task_data: Dict with "wiki_update_content" (str) and optional "update_mode" ("append"|"overwrite")
            
        Returns:
            Dict with "status", "message", and optionally "wiki_size" and "update_mode"
        """
        try:
            self.logger.info("Processing wiki update task")
            wiki_content = task_data.get("wiki_update_content")
            if wiki_content is None:
                self.logger.warning("Missing required parameter: wiki_update_content")
                return {
                    "status": "error",
                    "message": "Missing required parameter: wiki_update_content",
                    "error_code": "MISSING_PARAMETER"
                }
            
            update_mode = task_data.get("update_mode", "overwrite").lower()
            self.logger.debug(f"Update mode: {update_mode}")
            
            if update_mode == "append":
                existing_content = self.read_from_ltm(self._wiki_key)
                if existing_content:
                    updated_content = f"{existing_content}\n\n{wiki_content}"
                    self.logger.debug("Appending to existing wiki content")
                else:
                    updated_content = wiki_content
                    self.logger.debug("No existing content, using new content")
            else:
                updated_content = wiki_content
                self.logger.debug("Overwriting wiki content")
            
            success = self.write_to_ltm(self._wiki_key, updated_content)
            
            if success:
                wiki_size = len(updated_content)
                self.logger.info(f"Wiki updated successfully: {wiki_size} characters using {update_mode} mode")
                
                return {
                    "status": "success",
                    "message": f"Wiki updated successfully using {update_mode} mode",
                    "wiki_size": wiki_size,
                    "update_mode": update_mode,
                    "agent_id": self.agent_id
                }
            else:
                self.logger.error("Failed to write wiki content to LTM")
                return {
                    "status": "error",
                    "message": "Failed to write wiki content to LTM",
                    "error_code": "LTM_WRITE_FAILED"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing task: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "message": f"Error processing task: {str(e)}",
                "error_code": "PROCESSING_ERROR"
            }
    
    def send_message(self, recipient: str, message_obj: dict):
        """Send a message to another agent (prints JSON to stdout).
        
        Args:
            recipient: Identifier of the recipient agent
            message_obj: Dictionary containing the message data
        """
        message_json = json.dumps({
            "from": self.agent_id,
            "to": recipient,
            "message": message_obj
        }, indent=2)
        
        print(f"[Message from {self.agent_id} to {recipient}]")
        print(message_json)
    
    def write_to_ltm(self, key: str, value: Any) -> bool:
        """Store a key-value pair in LTM (in-memory).
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ltm[key] = value
            return True
        except Exception:
            return False
    
    def read_from_ltm(self, key: str) -> Optional[Any]:
        """Retrieve a value from LTM.
        
        Args:
            key: The key to retrieve the value for
            
        Returns:
            The value associated with the key, or None if not found
        """
        return self._ltm.get(key, None)
    
    def get_wiki_content(self) -> Optional[str]:
        """Retrieve the current wiki content.
        
        Returns:
            The current wiki content, or None if not found
        """
        return self.read_from_ltm(self._wiki_key)
    
    def _generate_message_id(self) -> str:
        """Generate a new UUID string for message identification."""
        return str(uuid.uuid4())
    
    def _get_current_timestamp(self) -> str:
        """Get current UTC time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def _send_json_message(self, message_dict: dict):
        """Send a JSON message by printing it to stdout.
        
        Args:
            message_dict: Dictionary containing the message to send
        """
        message_json = json.dumps(message_dict, indent=2)
        message_type = message_dict.get('type', 'unknown')
        recipient = message_dict.get('recipient', 'unknown')
        self.logger.info(f"Sending {message_type} message to {recipient}")
        print(f"[Message from {message_dict.get('sender', self.agent_id)} to {recipient}]")
        print(message_json)
    
    def _create_completion_report(self, related_message_id: str, task_results: dict) -> dict:
        """Create a completion report message after processing a task.
        
        Args:
            related_message_id: The message_id of the original task assignment
            task_results: The dictionary returned from process_task
            
        Returns:
            Dictionary containing the completion report message
        """
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
        """Create a health check response message.
        
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
    
    def _create_error_report(self, related_message_id: str, error_code: str, error_message: str) -> dict:
        """Create an error report message for invalid or malformed incoming messages.
        
        Args:
            related_message_id: The message_id of the incoming message that caused the error
            error_code: Error code identifier (e.g., "INVALID_JSON", "MISSING_FIELD")
            error_message: Human-readable error message
            
        Returns:
            Dictionary containing the error report message
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
        """Validate an incoming message against the JSON handshake protocol.
        
        Args:
            message_dict: Dictionary containing the parsed message
            
        Returns:
            Tuple of (is_valid, error_code, error_message). If valid, returns (True, None, None)
        """
        required_fields = ["message_id", "sender", "recipient", "type", "timestamp"]
        for field in required_fields:
            if field not in message_dict:
                return (False, "MISSING_FIELD", f"Missing required field: '{field}'")
        
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
        
        message_type = message_dict.get("type")
        if message_type not in ["task_assignment", "health_check"]:
            return (False, "INVALID_MESSAGE_TYPE", 
                   f"Invalid message type: '{message_type}'. Must be 'task_assignment' or 'health_check'")
        
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
        """Handle incoming JSON messages from supervisor or other agents.
        
        Validates protocol, processes task_assignment/health_check messages, and sends
        completion_report/health_check_response/error_report messages.
        
        Args:
            json_message: JSON string containing the incoming message
        """
        original_message_id = ""
        
        try:
            message_dict = json.loads(json_message)
            original_message_id = message_dict.get("message_id", "")
            message_type = message_dict.get("type", "unknown")
            sender = message_dict.get("sender", "unknown")
            self.logger.info(f"Received {message_type} message from {sender} (ID: {original_message_id})")
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            error_report = self._create_error_report(
                related_message_id="",
                error_code="INVALID_JSON",
                error_message=f"Invalid JSON format: {str(e)}"
            )
            self._send_json_message(error_report)
            return
        
        is_valid, error_code, error_message = self._validate_incoming_message(message_dict)
        if not is_valid:
            self.logger.warning(f"Message validation failed: {error_code} - {error_message}")
            error_report = self._create_error_report(
                related_message_id=original_message_id,
                error_code=error_code or "VALIDATION_ERROR",
                error_message=error_message or "Message validation failed"
            )
            self._send_json_message(error_report)
            return
        
        message_type = message_dict.get("type")
        original_message_id = message_dict.get("message_id")
        
        if message_type == "task_assignment":
            task = message_dict.get("task")
            task_name = task.get("name")
            task_parameters = task.get("parameters", {})
            
            if task_name != "update_wiki":
                self.logger.warning(f"Unsupported task name: {task_name}")
                error_report = self._create_error_report(
                    related_message_id=original_message_id,
                    error_code="UNSUPPORTED_TASK",
                    error_message=f"Unsupported task name: '{task_name}'. This agent only supports 'update_wiki'"
                )
                self._send_json_message(error_report)
                return
            
            self.logger.info(f"Processing task: {task_name}")
            task_results = self.process_task(task_parameters)
            completion_report = self._create_completion_report(original_message_id, task_results)
            self._send_json_message(completion_report)
            
        elif message_type == "health_check":
            self.logger.info("Responding to health check")
            health_response = self._create_health_check_response()
            self._send_json_message(health_response)

