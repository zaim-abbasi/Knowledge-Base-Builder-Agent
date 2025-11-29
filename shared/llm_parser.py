import os
from typing import Dict, Any, Optional
from openai import OpenAI
from shared.utils import setup_logger
from dotenv import load_dotenv
import json

load_dotenv()

logger = setup_logger(__name__)


class LLMTaskParser:
    
    def __init__(self):
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
    
    def _normalize_string(self, text: str, max_length: int = 1000) -> str:
        if not text:
            return ""
        # Strip whitespace and limit length
        normalized = text.strip()[:max_length]
        return normalized
    
    def parse_task_input(self, input_text: str, current_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
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
            
            # Production-ready prompt: principle-based, no hardcoded stop words
            # LLM uses natural language understanding to distinguish task content from meta-language
            prompt = f"""Date: {current_date}. Extract JSON:
task_id: ""
task_name: title case, expand if needed
task_description: extract only the actual task content, remove any language about creating/managing the task itself
task_deadline: ISO YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS if time, convert relative dates, "" if none

Input: {input_text}"""

            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,  # Deterministic = faster + consistent
                "max_tokens": 150,  # Compact JSON responses
                "timeout": self.timeout
            }
            
            # Add JSON mode if supported (faster, more reliable parsing)
            try:
                # Check if model supports JSON mode (gpt-4o-mini and newer models)
                if "gpt-4" in self.model.lower() or "gpt-3.5" in self.model.lower():
                    request_params["response_format"] = {"type": "json_object"}
            except:
                pass  # Fallback if not supported
            
            response = self.client.chat.completions.create(**request_params)
            
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
            
            # task_description: normalize string, max 1000 chars
            # Note: LLM is responsible for removing filler words via prompt instructions
            if "task_description" not in task_data or not task_data.get("task_description"):
                # Use input or task_name as description
                task_data["task_description"] = input_text if input_text else task_data["task_name"]
            task_data["task_description"] = self._normalize_string(str(task_data["task_description"]), max_length=1000)
            
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
    
    def _normalize_deadline_date(self, deadline_str: str, current_date: str) -> str:
        try:
            from datetime import datetime, timedelta
            import re
            
            deadline_str = deadline_str.strip()
            if not deadline_str:
                return ""
            
            # Try to parse as ISO datetime first (YYYY-MM-DDTHH:MM:SS)
            try:
                dt = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M:%S")
                return deadline_str  # Already in correct format
            except ValueError:
                pass
            
            # Try to parse as ISO date (YYYY-MM-DD)
            try:
                dt = datetime.strptime(deadline_str, "%Y-%m-%d")
                return deadline_str  # Already in correct format
            except ValueError:
                pass
            
            # Try other common datetime formats
            datetime_formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d %H:%M",
                "%m/%d/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M",
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y %H:%M",
            ]
            
            for fmt in datetime_formats:
                try:
                    dt = datetime.strptime(deadline_str, fmt)
                    return dt.strftime("%Y-%m-%dT%H:%M:%S")
                except ValueError:
                    continue
            
            # Try date-only formats
            date_formats = [
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
        logger.warning("Using fallback task creation due to parsing error")
        input_text = input_text.strip() if input_text else "Untitled Task"
        
        task_name = input_text[:100] if len(input_text) > 3 else f"Task: {input_text}"
        
        return {
            "task_id": "",  # Database will assign numeric ID
            "task_name": self._normalize_string(task_name, max_length=1000),
            "task_description": self._normalize_string(input_text, max_length=1000),
            "task_deadline": ""
        }

