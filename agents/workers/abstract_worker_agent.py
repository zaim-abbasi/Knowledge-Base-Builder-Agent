from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class AbstractWorkerAgent(ABC):
    """Abstract base class for worker agents in the system."""
    
    def __init__(self, agent_id: str, supervisor_id: str):
        """Initialize the worker agent.
        
        Args:
            agent_id: Unique identifier for this agent
            supervisor_id: Identifier of the supervisor agent
        """
        self.agent_id = agent_id
        self.supervisor_id = supervisor_id
    
    @abstractmethod
    def process_task(self, task_data: dict) -> dict:
        """Execute the core business logic for the agent.
        
        Args:
            task_data: Dictionary containing task parameters
            
        Returns:
            Dictionary with processing results, suitable for JSON serialization
        """
        pass
    
    @abstractmethod
    def send_message(self, recipient: str, message_obj: dict):
        """Send a message to another agent.
        
        Args:
            recipient: Identifier of the recipient agent
            message_obj: Dictionary containing the message data
        """
        pass
    
    @abstractmethod
    def write_to_ltm(self, key: str, value: Any) -> bool:
        """Store a key-value pair in Long-Term Memory (LTM).
        
        Args:
            key: The key to store the value under
            value: The value to store
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def read_from_ltm(self, key: str) -> Optional[Any]:
        """Retrieve a value from Long-Term Memory (LTM).
        
        Args:
            key: The key to retrieve the value for
            
        Returns:
            The value associated with the key, or None if not found
        """
        pass

