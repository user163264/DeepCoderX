
import json
import re
import time
import requests
from typing import Dict, Any

from config import config
from models.session import CommandContext
from utils.logging import console

class NLUParser:
    """
    Parses natural language commands into structured MCP commands using an LLM.
    """
    def __init__(self, context: CommandContext):
        self.ctx = context
        self.system_prompt = """
You are a precise and efficient command-line NLU (Natural Language Understanding) parser.
Your single task is to convert the user's request into a structured JSON object.

You must identify the user's **intent**, extract the required **entities**, and provide a **confidence score** (from 0.0 to 1.0) for your interpretation.

**Available Intents & Their Entities:**
- "run_bash": {"command": "<shell_command>"}
- "change_directory": {"path": "<directory_path>"}
- "list_dir": {"path": "<directory_path>"}
- "read_file": {"path": "<file_path>"}
- "write_file": {"path": "<file_path>", "content": "<file_content>"}
- "delete_path": {"path": "<path_to_delete>"}
- "clarify": {"reason": "<why_clarification_is_needed>"}

**Rules:**
1. Your response MUST be a single, valid JSON object and nothing else. Do not add any explanatory text or markdown formatting.
2. Include a `confidence` field in your response, representing your certainty.
3. If the user's intent is ambiguous or a required entity is missing, you MUST use the "clarify" intent and set `confidence` to a low value (e.g., 0.2).
4. For "write_file", if the content is not specified, use an empty string for the "content" entity.
5. The "path" entity should be the filename or path exactly as the user stated it.

User Request: "show me what is in the file 'sunny.txt'"
Your Response:
{"intent": "read_file", "entities": {"path": "sunny.txt"}, "confidence": 0.95}

User Request: "create a new file"
Your Response:
{"intent": "clarify", "entities": {"reason": "The filename is missing."}, "confidence": 0.4}
"""

    def parse_intent(self, command_text: str) -> Dict[str, Any]:
        """
        Sends the command to an LLM to get a structured intent and entities.
        Includes a retry mechanism for robustness.
        """
        if self.ctx.debug_mode:
            console.print(f"[bold red]DEBUG:[/] NLU Parsing: '{command_text}'", style="dim")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": command_text}
        ]
        
        max_retries = 3
        for attempt in range(max_retries):
            self.ctx.status = f"Parsing command (attempt {attempt + 1}/{max_retries})..."
            try:
                # Using DeepSeek API instead since LMSTUDIO_URL is not configured
                if not config.DEEPSEEK_API_KEY:
                    return {"intent": "clarify", "entities": {"reason": "NLU parsing requires API configuration"}}
                
                payload = {
                    "model": "deepseek-coder",
                    "messages": messages,
                    "temperature": 0.1,
                    "max_tokens": 256,
                }
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}"
                }
                response = requests.post(
                    config.DEEPSEEK_API_URL,
                    headers=headers,
                    json=payload,
                    timeout=20
                )
                response.raise_for_status()
                
                raw_response = response.json()["choices"][0]["message"]["content"]
                
                # Clean up the response to extract only the JSON object
                json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
                if not json_match:
                    raise ValueError("Response did not contain a valid JSON object.")

                parsed_json = json.loads(json_match.group(0))
                
                if self.ctx.debug_mode:
                    console.print(f"[bold red]DEBUG:[/] NLU Response: {parsed_json}", style="dim")

                # Basic validation
                if "intent" not in parsed_json or "entities" not in parsed_json or "confidence" not in parsed_json:
                     raise ValueError("Model response was missing required fields: intent, entities, or confidence.")

                # Confidence check
                confidence = float(parsed_json.get("confidence", 0.0))
                if confidence < 0.8:
                    return {"intent": "clarify", "entities": {"reason": f"Model confidence ({confidence:.2f}) was below the 0.8 threshold. Please rephrase your command."}}

                return parsed_json

            except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError, ValueError) as e:
                console.print(f"[bold yellow]NLU Parser Warning:[/] Attempt {attempt + 1} failed: {e}", style="dim")
                if attempt < max_retries - 1:
                    time.sleep(1) # Wait 1 second before retrying
                else:
                    console.print(f"[bold red]NLU Parser Error:[/] All {max_retries} attempts failed.", style="dim")
                    return {"intent": "clarify", "entities": {"reason": f"Failed to parse command after {max_retries} attempts: {e}"}}
        
        # This part should be unreachable but is here as a fallback
        return {"intent": "clarify", "entities": {"reason": "An unexpected error occurred in the NLU parser."}}

