# NLU Module Implementation Plan

This document outlines the plan to refactor the command processing system in DeepCoderX from a rigid, rule-based parser to a flexible Natural Language Understanding (NLU) module.

## 1. Project Overview

### Goal
To improve the system's ability to understand natural language commands for file system operations, making the user experience more intuitive and robust. This will be achieved by using an LLM to parse user intent and extract entities, rather than relying on brittle regular expressions.

### Complexity & Time Estimate
- **Complexity:** **Moderate**. This involves refactoring a core component of the application.
- **Estimated Time:** **~1 Day**. This includes implementation, prompt engineering, and thorough testing.

---

## 2. Implementation Steps

### Step 1: Create the `NLUParser` Module

A new module will be created to handle the logic of converting raw text into a structured command.

- **File:** `services/nlu_parser.py`
- **Class:** `NLUParser`
- **Core Method:** `parse_intent(command_text: str) -> dict`
  - **Action:** Takes the raw user command as input.
  - **Process:**
    1.  Constructs a specific system prompt to instruct an LLM to act as an NLU parser.
    2.  Sends the prompt and the user's command to the configured LLM (local or DeepSeek).
    3.  Receives the response and validates that it is a valid JSON object.
    4.  If the JSON is malformed or the intent is to "clarify," it handles it gracefully.
    5.  Returns a structured dictionary, e.g., `{ "intent": "read_file", "entities": { "path": "sunny.txt" } }`.

#### **Example NLU System Prompt:**
```
You are a precise and efficient command-line NLU (Natural Language Understanding) parser. Your single task is to convert the user's request into a structured JSON object.

The user's command will be related to file system operations. You must identify the user's **intent** and extract the required **entities**.

**Available Intents & Their Entities:**
- "list_dir": {"path": "<directory_path>"}
- "read_file": {"path": "<file_path>"}
- "write_file": {"path": "<file_path>", "content": "<file_content>"}
- "delete_path": {"path": "<path_to_delete>"}
- "clarify": {"reason": "<why_clarification_is_needed>"}

**Rules:**
1.  Your response MUST be a single, valid JSON object and nothing else.
2.  If the user's intent is ambiguous or a required entity (like a filename) is missing, you MUST use the "clarify" intent.
3.  For "write_file", if the content is not specified, use an empty string for the "content" entity.
4.  The "path" entity should be the filename or path exactly as the user stated it.

User Request: "show me what is in the file 'sunny.txt'"
Your Response:
{"intent": "read_file", "entities": {"path": "sunny.txt"}}

User Request: "create a new file"
Your Response:
{"intent": "clarify", "entities": {"reason": "The filename is missing."}}
```

### Step 2: Refactor `FilesystemCommandHandler`

This handler will be dramatically simplified to act as a dispatcher, not a parser.

- **File:** `services/llm_handler.py`
- **`can_handle` Method:** Logic remains the same (checks for "use your tools" prefix).
- **`handle` Method (New Logic):**
  1.  Instantiates the new `NLUParser`.
  2.  Calls `nlu_parser.parse_intent()` with the user's command text.
  3.  Uses a simple `if/elif/else` block or a dictionary to map the returned `intent` to the appropriate `self.ctx.mcp_client` method.
  4.  If the intent is `clarify`, it prints the clarification reason to the user.
- **Code Removal:** The old, complex methods (`handle_ls`, `handle_cat`, `_parse_path`, `_parse_two_paths`, etc.) and the `ALIAS_MAP` will be completely removed from the class.

### Step 3: Testing

Thorough manual testing will be required to validate the new implementation.

- **Simple Commands:** `use your tools ls`
- **Natural Language Commands:** `use your tools and show me the sunny.txt file`
- **Commands with Content:** `use your tools put 'hello' into new.txt`
- **Ambiguous Commands:** `use your tools work on the config file` (should ask for clarification if multiple exist).
- **Commands with Missing Info:** `use yourtools create a file` (should ask for the filename).

---

## 3. Summary of Changes & Challenges

### Required Code Changes
- **New File:** `services/nlu_parser.py`
- **Major Refactoring:** `services/llm_handler.py`
- **Potential Minor Changes:** `app.py` for initialization if needed.

### Potential Challenges
- **Prompt Engineering:** The NLU system prompt will require careful tuning to ensure consistent and accurate JSON output.
- **Latency:** Adding an LLM call will introduce a minor delay. This is a necessary trade-off for gaining flexibility.
- **Model Reliability:** The parsing logic must be robust enough to handle cases where the LLM returns a malformed or unexpected response.
