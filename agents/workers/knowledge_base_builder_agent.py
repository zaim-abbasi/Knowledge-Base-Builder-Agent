import json
import uuid
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
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
        self._cache_key = "request_response_cache"
        
        # Setup LTM directory
        self._ltm_dir = Path("LTM")
        self._ltm_dir.mkdir(exist_ok=True)
        self._wiki_file = self._ltm_dir / "wiki.json"
        self._cache_file = self._ltm_dir / "cache.json"
        
        # Load LTM from disk on startup
        self._load_ltm_from_disk()
        
        self.logger.info(f"Initialized {agent_id} with supervisor {supervisor_id}")
    
    def _generate_request_hash(self, task_data: dict) -> str:
        """Generate a hash for the request to use as cache key.
        
        Args:
            task_data: Dictionary containing task parameters
            
        Returns:
            SHA256 hash string of the request
        """
        request_str = json.dumps(task_data, sort_keys=True)
        return hashlib.sha256(request_str.encode()).hexdigest()
    
    def _search_ltm_cache(self, task_data: dict) -> Optional[dict]:
        """Search LTM cache for a matching request.
        
        Args:
            task_data: Dictionary containing task parameters
            
        Returns:
            Cached response if found, None otherwise
        """
        cache = self.read_from_ltm(self._cache_key)
        if not cache:
            return None
        
        request_hash = self._generate_request_hash(task_data)
        cached_response = cache.get(request_hash)
        
        if cached_response:
            self.logger.info(f"Found cached response in LTM for request hash: {request_hash[:8]}...")
            return cached_response
        
        return None
    
    def _store_in_ltm_cache(self, task_data: dict, response: dict):
        """Store successful request-response pair in LTM cache.
        
        Args:
            task_data: Dictionary containing task parameters
            response: Dictionary containing the response
        """
        cache = self.read_from_ltm(self._cache_key) or {}
        request_hash = self._generate_request_hash(task_data)
        
        cache[request_hash] = {
            "request": task_data,
            "response": response,
            "timestamp": self._get_current_timestamp()
        }
        
        self.write_to_ltm(self._cache_key, cache)
        self.logger.debug(f"Stored response in LTM cache: {request_hash[:8]}...")
    
    def process_task(self, task_data: dict) -> dict:
        """Process wiki update task.
        
        Per project requirements: First searches LTM for cached response,
        otherwise executes the agent flow and stores successful response.
        
        Args:
            task_data: Dict with "wiki_update_content" (str) and optional "update_mode" ("append"|"overwrite")
            
        Returns:
            Dict with "status", "message", and optionally "wiki_size" and "update_mode"
        """
        try:
            self.logger.info("Processing wiki update task")
            
            # Step 1: Search LTM first (project requirement)
            cached_response = self._search_ltm_cache(task_data)
            if cached_response:
                self.logger.info("Returning cached response from LTM")
                return cached_response.get("response")
            
            # Step 2: Execute agent flow (not found in LTM)
            self.logger.info("Request not found in LTM cache, executing agent flow")
            
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
                
                response = {
                    "status": "success",
                    "message": f"Wiki updated successfully using {update_mode} mode",
                    "wiki_size": wiki_size,
                    "update_mode": update_mode,
                    "agent_id": self.agent_id
                }
                
                # Step 3: Store successful response in LTM cache (project requirement)
                self._store_in_ltm_cache(task_data, response)
                
                return response
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
    
    def _load_ltm_from_disk(self):
        """Load LTM data from disk files on startup."""
        try:
            # Load wiki content
            if self._wiki_file.exists():
                with open(self._wiki_file, 'r', encoding='utf-8') as f:
                    wiki_data = json.load(f)
                    self._ltm[self._wiki_key] = wiki_data.get("content", "")
                    self.logger.info(f"Loaded wiki content from LTM: {len(self._ltm.get(self._wiki_key, ''))} characters")
            else:
                self.logger.info("No existing wiki content found in LTM")
            
            # Load request-response cache
            if self._cache_file.exists():
                with open(self._cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self._ltm[self._cache_key] = cache_data
                    cache_size = len(cache_data) if isinstance(cache_data, dict) else 0
                    self.logger.info(f"Loaded {cache_size} cached responses from LTM")
            else:
                self._ltm[self._cache_key] = {}
                self.logger.info("No existing cache found in LTM, starting fresh")
                
        except Exception as e:
            self.logger.error(f"Error loading LTM from disk: {str(e)}", exc_info=True)
            # Initialize empty if load fails
            if self._wiki_key not in self._ltm:
                self._ltm[self._wiki_key] = ""
            if self._cache_key not in self._ltm:
                self._ltm[self._cache_key] = {}
    
    def _save_ltm_to_disk(self):
        """Save LTM data to disk files."""
        try:
            # Save wiki content
            wiki_content = self._ltm.get(self._wiki_key, "")
            wiki_data = {
                "content": wiki_content,
                "last_updated": self._get_current_timestamp(),
                "size": len(wiki_content) if isinstance(wiki_content, str) else 0
            }
            with open(self._wiki_file, 'w', encoding='utf-8') as f:
                json.dump(wiki_data, f, indent=2, ensure_ascii=False)
            
            # Save request-response cache
            cache_data = self._ltm.get(self._cache_key, {})
            with open(self._cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Error saving LTM to disk: {str(e)}", exc_info=True)
    
    def write_to_ltm(self, key: str, value: Any) -> bool:
        """Store a key-value pair in LTM (in-memory and persistent).
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._ltm[key] = value
            
            # Persist to disk if it's wiki content or cache
            if key == self._wiki_key or key == self._cache_key:
                self._save_ltm_to_disk()
            
            return True
        except Exception as e:
            self.logger.error(f"Error writing to LTM: {str(e)}")
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
    
    def _create_supervisor_success_response(self, request_id: str, task_results: dict) -> dict:
        """Create a Supervisor format success response.
        
        Supervisor success format:
        {
          "request_id": "...",
          "agent_name": "...",
          "status": "success",
          "output": {
            "result": "...",
            "confidence": 0.95,
            "details": {...}
          },
          "error": null
        }
        
        Args:
            request_id: The request_id from the original request
            task_results: The dictionary returned from process_task
            
        Returns:
            Dictionary containing the Supervisor format success response
        """
        return {
            "request_id": request_id,
            "agent_name": self.agent_id,
            "status": "success",
            "output": {
                "result": task_results.get("message", "Task completed successfully"),
                "confidence": 0.95,
                "details": task_results
            },
            "error": None
        }
    
    def _create_supervisor_error_response(self, request_id: Optional[str], error_code: str, error_message: str) -> dict:
        """Create a Supervisor format error response.
        
        Supervisor error format:
        {
          "status": "error",
          "output": null,
          "error": {
            "type": "...",
            "message": "..."
          }
        }
        
        Args:
            request_id: The request_id from the original request (optional for errors)
            error_code: Error code identifier
            error_message: Human-readable error message
            
        Returns:
            Dictionary containing the Supervisor format error response
        """
        response = {
            "status": "error",
            "output": None,
            "error": {
                "type": error_code,
                "message": error_message
            }
        }
        # Include request_id if provided (for correlation)
        if request_id:
            response["request_id"] = request_id
            response["agent_name"] = self.agent_id
        return response
    
    def _create_supervisor_health_response(self, request_id: Optional[str] = None) -> dict:
        """Create a Supervisor format health check response.
        
        Args:
            request_id: Optional request_id from health check request
            
        Returns:
            Dictionary containing the Supervisor format health response
        """
        response = {
            "request_id": request_id or "health-check",
            "agent_name": self.agent_id,
            "status": "success",
            "output": {
                "result": "I'm up and ready",
                "confidence": 1.0,
                "details": {
                    "type": "health_check",
                    "timestamp": self._get_current_timestamp()
                }
            },
            "error": None
        }
        return response
    
    
    def _is_supervisor_format(self, message_dict: dict) -> bool:
        """Check if message is in Supervisor format.
        
        Supervisor format has: request_id, agent_name, intent, input, context
        Legacy format has: message_id, sender, recipient, type, task
        
        Args:
            message_dict: Dictionary containing the message
            
        Returns:
            True if message is in Supervisor format, False otherwise
        """
        return "request_id" in message_dict and "agent_name" in message_dict and "intent" in message_dict
    
    def _validate_supervisor_message(self, message_dict: dict) -> Tuple[bool, Optional[str], Optional[str]]:
        """Validate an incoming Supervisor format message.
        
        Supervisor format:
        {
          "request_id": "...",
          "agent_name": "...",
          "intent": "...",
          "input": {
            "text": "...",
            "metadata": {...}
          },
          "context": {
            "user_id": "...",
            "conversation_id": "...",
            "timestamp": "..."
          }
        }
        
        Args:
            message_dict: Dictionary containing the parsed message
            
        Returns:
            Tuple of (is_valid, error_code, error_message). If valid, returns (True, None, None)
        """
        # Required top-level fields
        required_fields = ["request_id", "agent_name", "intent", "input", "context"]
        for field in required_fields:
            if field not in message_dict:
                return (False, "MISSING_FIELD", f"Missing required field: '{field}'")
        
        # Validate types
        if not isinstance(message_dict.get("request_id"), str):
            return (False, "INVALID_TYPE", "Field 'request_id' must be a string")
        if not isinstance(message_dict.get("agent_name"), str):
            return (False, "INVALID_TYPE", "Field 'agent_name' must be a string")
        if not isinstance(message_dict.get("intent"), str):
            return (False, "INVALID_TYPE", "Field 'intent' must be a string")
        
        # Validate input structure
        input_data = message_dict.get("input")
        if not isinstance(input_data, dict):
            return (False, "INVALID_TYPE", "Field 'input' must be a dictionary")
        if "text" not in input_data:
            return (False, "MISSING_FIELD", "Missing required field: 'input.text'")
        if not isinstance(input_data.get("text"), str):
            return (False, "INVALID_TYPE", "Field 'input.text' must be a string")
        if "metadata" in input_data and not isinstance(input_data.get("metadata"), dict):
            return (False, "INVALID_TYPE", "Field 'input.metadata' must be a dictionary")
        
        # Validate context structure
        context = message_dict.get("context")
        if not isinstance(context, dict):
            return (False, "INVALID_TYPE", "Field 'context' must be a dictionary")
        if "user_id" not in context:
            return (False, "MISSING_FIELD", "Missing required field: 'context.user_id'")
        if not isinstance(context.get("user_id"), str):
            return (False, "INVALID_TYPE", "Field 'context.user_id' must be a string")
        
        # Validate agent_name matches this agent
        if message_dict.get("agent_name") != self.agent_id:
            return (False, "INVALID_AGENT", 
                   f"Agent name '{message_dict.get('agent_name')}' does not match this agent '{self.agent_id}'")
        
        return (True, None, None)
    
    def handle_incoming_message(self, json_message: str):
        """Handle incoming JSON messages from supervisor in Supervisor format.
        
        Supervisor format:
        - Request: { request_id, agent_name, intent, input { text, metadata }, context { user_id, ... } }
        - Response: { request_id, agent_name, status: success, output { result, confidence, details }, error: null }
          or { status: error, output: null, error { type, message } }
        
        Args:
            json_message: JSON string containing the incoming Supervisor format message
        """
        request_id = ""
        
        try:
            message_dict = json.loads(json_message)
            
            # Check if it's Supervisor format
            if not self._is_supervisor_format(message_dict):
                self.logger.error("Message is not in Supervisor format")
                error_response = self._create_supervisor_error_response(
                    request_id=None,
                    error_code="INVALID_FORMAT",
                    error_message="Message must be in Supervisor format: { request_id, agent_name, intent, input, context }"
                )
                self._send_json_message(error_response)
                return
            
            request_id = message_dict.get("request_id", "")
            intent = message_dict.get("intent", "")
            agent_name = message_dict.get("agent_name", "")
            self.logger.info(f"Received Supervisor format message: intent={intent}, agent={agent_name}, request_id={request_id[:8]}...")
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format: {str(e)}")
            error_response = self._create_supervisor_error_response(
                request_id=None,
                error_code="INVALID_JSON",
                error_message=f"Invalid JSON format: {str(e)}"
            )
            self._send_json_message(error_response)
            return
        
        # Validate Supervisor format
        is_valid, error_code, error_message = self._validate_supervisor_message(message_dict)
        if not is_valid:
            self.logger.warning(f"Message validation failed: {error_code} - {error_message}")
            error_response = self._create_supervisor_error_response(
                request_id=request_id,
                error_code=error_code or "VALIDATION_ERROR",
                error_message=error_message or "Message validation failed"
            )
            self._send_json_message(error_response)
            return
        
        # Extract Supervisor format fields
        intent = message_dict.get("intent")
        input_data = message_dict.get("input", {})
        text = input_data.get("text", "")
        metadata = input_data.get("metadata", {})
        
        # Handle different intents
        if intent == "update_wiki" or intent == "health_check":
            if intent == "update_wiki":
                # Build task parameters from Supervisor format
                task_parameters = {
                    "wiki_update_content": text,
                    "update_mode": metadata.get("update_mode", "overwrite")
                }
                
                # Process the task
                self.logger.info(f"Processing task: {intent}")
                task_results = self.process_task(task_parameters)
                
                # Create Supervisor format response
                if task_results.get("status") == "success":
                    success_response = self._create_supervisor_success_response(request_id, task_results)
                    self._send_json_message(success_response)
                else:
                    error_response = self._create_supervisor_error_response(
                        request_id=request_id,
                        error_code=task_results.get("error_code", "PROCESSING_ERROR"),
                        error_message=task_results.get("message", "Task processing failed")
                    )
                    self._send_json_message(error_response)
            
            elif intent == "health_check":
                # Health check
                self.logger.info("Responding to health check")
                health_response = self._create_supervisor_health_response(request_id)
                self._send_json_message(health_response)
        
        else:
            # Unsupported intent
            self.logger.warning(f"Unsupported intent: {intent}")
            error_response = self._create_supervisor_error_response(
                request_id=request_id,
                error_code="UNSUPPORTED_INTENT",
                error_message=f"Unsupported intent: '{intent}'. This agent only supports 'update_wiki' and 'health_check'"
            )
            self._send_json_message(error_response)

