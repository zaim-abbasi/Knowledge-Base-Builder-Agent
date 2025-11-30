from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import Optional, Dict, Any
from shared.utils import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)


class TaskDatabase:
    
    def __init__(self):
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING", "")
        self.db_password = os.getenv("MONGODB_DB_PASSWORD", "")
        self.database_name = os.getenv("MONGODB_DATABASE_NAME", "knowledge_builder")
        self.collection_name = os.getenv("MONGODB_COLLECTION_NAME", "task")
        
        # Replace password placeholder in connection string
        if self.connection_string and "<db_password>" in self.connection_string:
            self.connection_string = self.connection_string.replace(
                "<db_password>", self.db_password
            )
        
        self.client: Optional[MongoClient] = None
        self.db = None
        self.collection = None
        
        self._connect()
    
    def _connect(self):
        try:
            if not self.connection_string:
                raise ValueError("MongoDB connection string not configured")
            
            self.client = MongoClient(self.connection_string)
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            logger.info(f"Connected to MongoDB: {self.database_name}.{self.collection_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise
    
    def _get_next_numeric_task_id(self) -> str:
        try:
            # Get all tasks and extract numeric IDs
            all_tasks = list(self.collection.find({}, {"task_id": 1}))
            max_id = 0
            
            for task in all_tasks:
                task_id = task.get("task_id", "")
                # Try to parse as integer
                try:
                    numeric_id = int(task_id)
                    if numeric_id > max_id:
                        max_id = numeric_id
                except (ValueError, TypeError):
                    # Skip non-numeric IDs
                    continue
            
            # Return next ID
            next_id = str(max_id + 1)
            logger.debug(f"Generated next numeric task ID: {next_id}")
            return next_id
            
        except Exception as e:
            logger.error(f"Error getting next task ID: {str(e)}")
            # Fallback to 1 if error
            return "1"
    
    def create_task(self, task_data: Dict[str, Any]) -> Optional[str]:
        try:
            # Generate numeric task_id if not provided
            provided_task_id = task_data.get("task_id", "")
            if not provided_task_id:
                task_id = self._get_next_numeric_task_id()
            else:
                # Check if task_id already exists
                existing = self.collection.find_one({"task_id": provided_task_id})
                if existing:
                    logger.warning(f"Task ID '{provided_task_id}' already exists, generating new numeric ID")
                    task_id = self._get_next_numeric_task_id()
                else:
                    task_id = provided_task_id
            
            # Ensure defaults
            task_doc = {
                "task_id": task_id,
                "task_name": task_data.get("task_name", ""),
                "task_status": task_data.get("task_status", "todo"),
                "task_description": task_data.get("task_description", ""),
                "task_deadline": task_data.get("task_deadline", ""),
                "depends_on": task_data.get("depends_on", None)
            }
            
            # Final check: ensure task_id doesn't exist (race condition protection)
            existing = self.collection.find_one({"task_id": task_id})
            if existing:
                logger.warning(f"Task ID '{task_id}' exists, generating new numeric ID")
                task_id = self._get_next_numeric_task_id()
                task_doc["task_id"] = task_id
            
            # Insert into collection
            result = self.collection.insert_one(task_doc)
            
            if result.inserted_id:
                logger.info(f"Task created successfully with ID: {task_id}")
                return task_id
            else:
                logger.error("Failed to insert task")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}", exc_info=True)
            return None
    
    def list_tasks(self) -> list:
        try:
            tasks = list(self.collection.find({}, {"_id": 0}))
            return tasks
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return []
    
    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

