"""LLM utility for parsing task information from natural language input."""

import os
from typing import Dict, Any, Optional
from openai import OpenAI
from shared.utils import setup_logger
from dotenv import load_dotenv
import json

load_dotenv()

logger = setup_logger(__name__)


class LLMTaskParser:
    """LLM-based parser for extracting task information from natural language."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY", "")
        base_url = os.getenv("OPENAI_API_BASE_URL", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        timeout_ms = int(os.getenv("OPENAI_TIMEOUT_MS", "30000"))
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout_ms / 1000.0  # Convert ms to seconds
        )
        self.model = model
        self.timeout = timeout_ms / 1000.0
        
        logger.info(f"Initialized LLM parser with model: {model}")
    
    def _normalize_task_id(self, task_id: str) -> str:
        """Normalize task ID to be database-compatible.
        
        Args:
            task_id: Raw task ID string
        
        Returns:
            Normalized task ID (alphanumeric, hyphens, underscores only)
        """
        import re
        # Remove special characters, keep alphanumeric, hyphens, underscores
        normalized = re.sub(r'[^a-zA-Z0-9_-]', '', task_id)
        # Limit length to 100 characters for database compatibility
        normalized = normalized[:100]
        # Ensure it's not empty
        if not normalized:
            normalized = "TASK-UNKNOWN"
        return normalized
    
    def _normalize_string(self, text: str, max_length: int = 1000) -> str:
        """Normalize string for database storage.
        
        Args:
            text: Input text
            max_length: Maximum length allowed
        
        Returns:
            Normalized string
        """
        if not text:
            return ""
        # Strip whitespace and limit length
        normalized = text.strip()[:max_length]
        return normalized
    
    def _generate_task_id_from_text(self, text: str) -> str:
        """Generate a task ID from input text when none is provided.
        
        Args:
            text: Input text
        
        Returns:
            Generated task ID
        """
        import re
        # Extract meaningful words (remove common words)
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        # Remove common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        meaningful_words = [w for w in words if w not in stop_words][:5]  # Take first 5 meaningful words
        
        if meaningful_words:
            task_id = "-".join(meaningful_words)
        else:
            # Fallback: use first few characters
            task_id = re.sub(r'[^a-zA-Z0-9]', '', text.lower())[:20]
            if not task_id:
                task_id = "task"
        
        return f"TASK-{task_id}"[:50]  # Limit to 50 chars
    
    def parse_task_input(self, input_text: str, current_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Parse natural language input to extract task information.
        
        Handles any input format:
        - Structured format with labels
        - Unstructured plain English sentences
        - Single words or phrases
        - Minimal information
        
        Args:
            input_text: Natural language text containing task information in any format
            current_date: Current date in ISO format (YYYY-MM-DD) for relative date calculation
        
        Returns:
            Dictionary with database-compatible fields:
                - task_id: str (will be replaced with numeric ID by database)
                - task_name: str (normalized, max 1000 chars)
                - task_description: str (normalized, max 1000 chars)
                - task_deadline: str (normalized ISO date format, max 200 chars)
            Returns None if parsing fails
        """
        try:
            # Normalize input
            input_text = input_text.strip() if input_text else ""
            if not input_text:
                logger.warning("Empty input text provided")
                return None
            
            # Get current date if not provided
            if not current_date:
                from datetime import datetime
                current_date = datetime.now().strftime("%Y-%m-%d")
            
            prompt = f"""You are an intelligent task extraction assistant. Extract task information from the following input.
The input can be in ANY format:
- Structured: "Task ID: PROJ-001, Task Name: Build API, Deadline: 2025-12-31"
- Unstructured sentences: "I need to create a login system by next week"
- Single words/phrases: "authentication" or "fix bug" or "update docs"
- Minimal: "dashboard" or "payment module"

IMPORTANT DATE CONTEXT:
Today's date is: {current_date}
When processing deadlines, convert ALL relative dates to absolute ISO format (YYYY-MM-DD).
Examples:
- "tomorrow" -> next day from today
- "next week" -> 7 days from today
- "next Monday" -> actual date of next Monday
- "by 5PM tomorrow" -> date of tomorrow in YYYY-MM-DD format
- "in 3 days" -> today + 3 days in YYYY-MM-DD format
- "December 15" -> 2025-12-15 (use current year if not specified, or next year if date has passed)
- "ASAP" or "urgent" -> today's date
If no deadline is mentioned, return empty string "".

Your job is to intelligently extract and generate:
1. task_id: 
   - Ignore any task_id mentioned in input (it will be auto-generated as numeric).
   - Return empty string "" for this field (database will assign numeric ID).

2. task_name: 
   - If explicitly mentioned, extract it.
   - If input is a single word/phrase, expand it to a proper task name (e.g., "authentication" -> "Implement authentication system").
   - If input is a sentence, extract the main task/action as the name.
   - Make it clear and descriptive (title case preferred).

3. task_description: 
   - If detailed description is provided, use it.
   - If input is minimal (single word/phrase), create a reasonable description based on the task name.
   - If input is a sentence, use the full input as description.
   - IMPORTANT: Remove any filler phrases at the beginning like "Add task", "Create task", "Task to", "I need to", "We need to", etc.
   - Start the description directly with the actual task content (e.g., "eat dinner by 5PM tomorrow" not "Add task, to eat dinner by 5PM tomorrow").
   - Be descriptive but concise and direct.

4. task_deadline: 
   - Extract if mentioned in any format.
   - ALWAYS convert to ISO format YYYY-MM-DD based on today's date ({current_date}).
   - Convert relative dates to absolute dates using today as reference.
   - If not mentioned, return empty string "".

Input text:
{input_text}

Return ONLY a valid JSON object with these exact fields: task_id (empty string), task_name, task_description, task_deadline (ISO format YYYY-MM-DD).
No markdown, no code blocks, no explanations - just pure JSON."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task extraction assistant. Extract task information from any input format (structured, unstructured, single words, phrases, sentences) and return only valid JSON with fields: task_id, task_name, task_description, task_deadline. Always generate meaningful values even for minimal inputs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent output
                timeout=self.timeout
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                # Find the closing ```
                parts = response_text.split("```")
                if len(parts) >= 2:
                    response_text = parts[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                response_text = response_text.strip()
            
            # Remove any leading/trailing whitespace, newlines, or quotes
            response_text = response_text.strip().strip('"').strip("'")
            
            # Parse JSON
            task_data = json.loads(response_text)
            
            # Validate and normalize all fields for database compatibility
            # task_id: Set to empty string (database will assign numeric ID)
            task_data["task_id"] = ""
            
            # task_name: normalize string, max 1000 chars
            if "task_name" not in task_data or not task_data.get("task_name"):
                # Use input as fallback
                task_data["task_name"] = input_text[:100] if input_text else "Untitled Task"
            task_data["task_name"] = self._normalize_string(str(task_data["task_name"]), max_length=1000)
            
            # task_description: normalize string, max 1000 chars, remove filler words
            if "task_description" not in task_data or not task_data.get("task_description"):
                # Use input or task_name as description
                task_data["task_description"] = input_text if input_text else task_data["task_name"]
            task_data["task_description"] = self._clean_task_description(str(task_data["task_description"]))
            task_data["task_description"] = self._normalize_string(task_data["task_description"], max_length=1000)
            
            # task_deadline: normalize and validate ISO date format, max 200 chars
            if "task_deadline" not in task_data:
                task_data["task_deadline"] = ""
            else:
                deadline_str = str(task_data["task_deadline"]).strip()
                # Try to parse and normalize date format
                if deadline_str:
                    deadline_str = self._normalize_deadline_date(deadline_str, current_date)
                task_data["task_deadline"] = deadline_str[:200]
            
            logger.info(f"Successfully parsed task: {task_data.get('task_id')}")
            return task_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {str(e)}")
            logger.error(f"Response text: {response_text[:200] if 'response_text' in locals() else 'N/A'}")
            # Fallback: create minimal task from input
            return self._create_fallback_task(input_text)
        except Exception as e:
            logger.error(f"Error parsing task input with LLM: {str(e)}", exc_info=True)
            # Fallback: create minimal task from input
            return self._create_fallback_task(input_text)
    
    def _clean_task_description(self, description: str) -> str:
        """Remove filler words and phrases from task description.
        
        Removes common filler phrases like "Add task", "Create task", "Task to", etc.
        from the beginning of descriptions.
        
        Args:
            description: Raw task description
        
        Returns:
            Cleaned description without filler words
        """
        if not description:
            return ""
        
        description = description.strip()
        
        # List of filler phrases to remove (case-insensitive)
        filler_phrases = [
            r"^add task[,\s:]*",
            r"^create task[,\s:]*",
            r"^task to[,\s:]*",
            r"^task[,\s:]*",
            r"^i need to[,\s:]*",
            r"^we need to[,\s:]*",
            r"^please[,\s:]*",
            r"^can you[,\s:]*",
            r"^could you[,\s:]*",
            r"^i want to[,\s:]*",
            r"^we want to[,\s:]*",
            r"^let's[,\s:]*",
            r"^let us[,\s:]*",
        ]
        
        import re
        for phrase in filler_phrases:
            description = re.sub(phrase, "", description, flags=re.IGNORECASE)
        
        # Clean up any leading/trailing whitespace and punctuation
        description = description.strip().lstrip(",:;").strip()
        
        # Capitalize first letter if needed
        if description and description[0].islower():
            description = description[0].upper() + description[1:]
        
        return description
    
    def _normalize_deadline_date(self, deadline_str: str, current_date: str) -> str:
        """Normalize deadline string to ISO format (YYYY-MM-DD).
        
        Args:
            deadline_str: Raw deadline string from LLM
            current_date: Current date in YYYY-MM-DD format
        
        Returns:
            Normalized date in YYYY-MM-DD format, or empty string if invalid
        """
        try:
            from datetime import datetime, timedelta
            import re
            
            deadline_str = deadline_str.strip()
            if not deadline_str:
                return ""
            
            # Try to parse as ISO date first
            try:
                # Check if it's already in YYYY-MM-DD format
                datetime.strptime(deadline_str, "%Y-%m-%d")
                return deadline_str
            except ValueError:
                pass
            
            # Try other common formats
            date_formats = [
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
                "%m/%d/%Y",
                "%d/%m/%Y",
                "%B %d, %Y",
                "%b %d, %Y",
                "%d %B %Y",
                "%d %b %Y"
            ]
            
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(deadline_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
            
            # If parsing fails, return empty string
            logger.warning(f"Could not parse deadline date: {deadline_str}")
            return ""
            
        except Exception as e:
            logger.error(f"Error normalizing deadline date: {str(e)}")
            return ""
    
    def _create_fallback_task(self, input_text: str) -> Dict[str, Any]:
        """Create a fallback task when LLM parsing fails.
        
        Args:
            input_text: Original input text
        
        Returns:
            Dictionary with minimal task information
        """
        logger.warning("Using fallback task creation due to parsing error")
        input_text = input_text.strip() if input_text else "Untitled Task"
        
        task_name = input_text[:100] if len(input_text) > 3 else f"Task: {input_text}"
        
        return {
            "task_id": "",  # Database will assign numeric ID
            "task_name": self._normalize_string(task_name, max_length=1000),
            "task_description": self._normalize_string(input_text, max_length=1000),
            "task_deadline": ""
        }

