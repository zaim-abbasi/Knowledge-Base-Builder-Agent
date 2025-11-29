from abc import ABC, abstractmethod
from typing import Any, Optional, Dict


class AbstractWorkerAgent(ABC):
    
    def __init__(self, agent_id: str, supervisor_id: str):
        self.agent_id = agent_id
        self.supervisor_id = supervisor_id
    
    @abstractmethod
    def process_task(self, task_data: dict) -> dict:
        pass
    
    @abstractmethod
    def send_message(self, recipient: str, message_obj: dict):
        pass
    
    @abstractmethod
    def write_to_ltm(self, key: str, value: Any) -> bool:
        pass
    
    @abstractmethod
    def read_from_ltm(self, key: str) -> Optional[Any]:
        pass

