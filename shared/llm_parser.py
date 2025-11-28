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
    
    def parse_task_input(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Parse natural language input to extract task information.
        
        Handles any input format:
        - Structured format with labels
        - Unstructured plain English sentences
        - Single words or phrases
        - Minimal information
        
        Args:
            input_text: Natural language text containing task information in any format
        
        Returns:
            Dictionary with database-compatible fields:
                - task_id: str (normalized, max 100 chars)
                - task_name: str (normalized, max 1000 chars)
                - task_description: str (normalized, max 1000 chars)
                - task_deadline: str (normalized, max 200 chars)
            Returns None if parsing fails
        """
        try:
            # Normalize input
            input_text = input_text.strip() if input_text else ""
            if not input_text:
                logger.warning("Empty input text provided")
                return None
            
            prompt = f"""You are an intelligent task extraction assistant. Extract task information from the following input.
The input can be in ANY format:
- Structured: "Task ID: PROJ-001, Task Name: Build API, Deadline: 2025-12-31"
- Unstructured sentences: "I need to create a login system by next week"
- Single words/phrases: "authentication" or "fix bug" or "update docs"
- Minimal: "dashboard" or "payment module"

Your job is to intelligently extract and generate:
1. task_id: 
   - If explicitly mentioned (like "task id is TASK-123", "ID: TASK-123", "task-id: PROJ-001"), extract it exactly.
   - If not mentioned, generate a short, meaningful, URL-friendly ID based on the input (e.g., "authentication" -> "auth", "fix login bug" -> "fix-login-bug").
   - Use lowercase, hyphens for spaces, no special characters.
   - Examples: "dashboard" -> "dashboard", "user management" -> "user-management", "API docs" -> "api-docs"

2. task_name: 
   - If explicitly mentioned, extract it.
   - If input is a single word/phrase, expand it to a proper task name (e.g., "authentication" -> "Implement authentication system").
   - If input is a sentence, extract the main task/action as the name.
   - Make it clear and descriptive (title case preferred).

3. task_description: 
   - If detailed description is provided, use it.
   - If input is minimal (single word/phrase), create a reasonable description based on the task name.
   - If input is a sentence, use the full input as description.
   - Be descriptive but concise.

4. task_deadline: 
   - Extract if mentioned in any format: "by Dec 15", "deadline 2025-12-20", "due next week", "urgent", "ASAP", etc.
   - Convert relative dates to absolute when possible (e.g., "next Monday" -> actual date).
   - If not mentioned, return empty string "".
   - Keep the original format if conversion is unclear.

Input text:
{input_text}

Return ONLY a valid JSON object with these exact fields: task_id, task_name, task_description, task_deadline.
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
            # task_id: normalize to alphanumeric + hyphens/underscores, max 100 chars
            if "task_id" not in task_data or not task_data.get("task_id"):
                # Generate from task_name or input
                task_name = task_data.get("task_name", input_text)
                task_data["task_id"] = self._generate_task_id_from_text(task_name)
            task_data["task_id"] = self._normalize_task_id(str(task_data["task_id"]))
            
            # task_name: normalize string, max 1000 chars
            if "task_name" not in task_data or not task_data.get("task_name"):
                # Use input as fallback
                task_data["task_name"] = input_text[:100] if input_text else "Untitled Task"
            task_data["task_name"] = self._normalize_string(str(task_data["task_name"]), max_length=1000)
            
            # task_description: normalize string, max 1000 chars
            if "task_description" not in task_data or not task_data.get("task_description"):
                # Use input or task_name as description
                task_data["task_description"] = input_text if input_text else task_data["task_name"]
            task_data["task_description"] = self._normalize_string(str(task_data["task_description"]), max_length=1000)
            
            # task_deadline: normalize string, max 200 chars
            if "task_deadline" not in task_data:
                task_data["task_deadline"] = ""
            task_data["task_deadline"] = self._normalize_string(str(task_data["task_deadline"]), max_length=200)
            
            # Final validation - ensure task_id is not empty
            if not task_data["task_id"] or task_data["task_id"] == "TASK-UNKNOWN":
                task_data["task_id"] = self._generate_task_id_from_text(task_data["task_name"])
            
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
    
    def _create_fallback_task(self, input_text: str) -> Dict[str, Any]:
        """Create a fallback task when LLM parsing fails.
        
        Args:
            input_text: Original input text
        
        Returns:
            Dictionary with minimal task information
        """
        logger.warning("Using fallback task creation due to parsing error")
        input_text = input_text.strip() if input_text else "Untitled Task"
        
        task_id = self._generate_task_id_from_text(input_text)
        task_name = input_text[:100] if len(input_text) > 3 else f"Task: {input_text}"
        
        return {
            "task_id": self._normalize_task_id(task_id),
            "task_name": self._normalize_string(task_name, max_length=1000),
            "task_description": self._normalize_string(input_text, max_length=1000),
            "task_deadline": ""
        }

