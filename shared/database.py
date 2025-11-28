"""MongoDB database utilities for task storage."""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from typing import Optional, Dict, Any, List
from shared.utils import setup_logger
import os
from dotenv import load_dotenv

load_dotenv()

logger = setup_logger(__name__)


class TaskDatabase:
    """MongoDB database handler for task collection."""
    
    def __init__(self):
        """Initialize MongoDB connection."""
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
        """Establish connection to MongoDB."""
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
        """Get the next numeric task ID.
        
        Finds the maximum numeric task_id in the database and returns the next number.
        If no tasks exist, returns "1".
        
        Returns:
            Next task ID as string (e.g., "1", "2", "3")
        """
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
        """Create a new task in the database.
        
        Automatically assigns a numeric task_id if not provided.
        Prevents duplicate task_ids.
        
        Args:
            task_data: Dictionary containing task fields:
                - task_id: str (optional, will be auto-generated as numeric if not provided)
                - task_name: str
                - task_description: str
                - task_deadline: str
                - task_status: str (default: 'todo')
                - depends_on: list (default: None)
        
        Returns:
            Inserted task_id if successful, None otherwise
        """
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
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a task by task_id.
        
        Args:
            task_id: The task ID to retrieve
        
        Returns:
            Task document if found, None otherwise
        """
        try:
            task = self.collection.find_one({"task_id": task_id})
            if task:
                # Convert ObjectId to string for JSON serialization
                task.pop("_id", None)
            return task
        except Exception as e:
            logger.error(f"Error retrieving task: {str(e)}")
            return None
    
    def update_task(self, task_id: str, update_data: Dict[str, Any]) -> bool:
        """Update an existing task.
        
        Args:
            task_id: The task ID to update
            update_data: Dictionary containing fields to update
        
        Returns:
            True if successful, False otherwise
        """
        try:
            result = self.collection.update_one(
                {"task_id": task_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return False
    
    def list_tasks(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all tasks, optionally filtered by status.
        
        Args:
            status: Optional status filter
        
        Returns:
            List of task documents
        """
        try:
            query = {"task_status": status} if status else {}
            tasks = list(self.collection.find(query))
            # Remove _id for JSON serialization
            for task in tasks:
                task.pop("_id", None)
            return tasks
        except Exception as e:
            logger.error(f"Error listing tasks: {str(e)}")
            return []
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

