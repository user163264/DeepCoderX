### **Project: DeepCoderX - Two-Model Architecture Implementation Plan**

**Version:** 1.0
**Date:** June 27, 2025

#### **1. Objective**

To refactor the DeepCoderX application to support a dual-local-LLM architecture. This will involve separating the Natural Language Understanding (NLU) and the Code Generation tasks into two distinct, specialized models, leading to a significant improvement in accuracy, reliability, and overall capability.

---

#### **2. Core Architectural Changes**

*   **Model Roles:**
    1.  **Language Model (The "Router"):** A small, fast language model responsible for NLU, intent parsing, and tool-use planning.
    2.  **Code Model (The "Expert"):** The existing Qwen 1.5B model, which will now be dedicated exclusively to code generation and modification tasks.
*   **Workflow:**
    1.  User input is first sent to the **Language Model**.
    2.  The Language Model analyzes the input and, if a tool is needed, generates the appropriate JSON.
    3.  If the task requires code generation, the Language Model will generate a structured command to be executed by the **Code Model**.
    4.  The `LocalCodingHandler` will orchestrate this entire process.

---

#### **3. Detailed Implementation Plan (Step-by-Step)**

This plan is broken down into distinct phases to ensure a structured and testable implementation.

**Phase 1: Configuration and Model Setup**

1.  **Update `config.py`:**
    *   Add a new configuration section for the Language Model:
        ```python
        # Language Model (for NLU and Routing)
        LANGUAGE_MODEL_PATH = os.getenv("LANGUAGE_MODEL_PATH", "/path/to/your/language_model.gguf")
        ```
    *   Add a boolean flag to easily switch between the single-model and dual-model architecture:
        ```python
        DUAL_MODEL_MODE = os.getenv("DUAL_MODEL_MODE", "true").lower() == "true"
        ```

2.  **Update `requirements.txt`:**
    *   No changes are needed here, as we will continue to use the `llama-cpp-python` library, which can handle multiple model instances.

3.  **User Documentation:**
    *   Create a new document in the `documentation/` folder named `model_configuration.md`.
    *   This document will explain the new `LANGUAGE_MODEL_PATH` and `DUAL_MODEL_MODE` settings and provide links to recommended small language models that users can download (e.g., a small Llama 3 or Phi-3 model).

**Phase 2: Refactoring the `LocalCodingHandler`**

This is the most significant part of the implementation.

1.  **Update the `__init__` method:**
    *   It will now initialize **two** `Llama` instances:
        *   `self.language_model = Llama(model_path=config.LANGUAGE_MODEL_PATH, ...)`
        *   `self.code_model = Llama(model_path=config.LOCAL_MODEL_PATH, ...)`
    *   It should conditionally load the models based on the `DUAL_MODEL_MODE` flag to maintain backward compatibility.

2.  **Rewrite the `handle` method:**
    *   The logic will now be a multi-step process:
        1.  The initial user prompt (with file context) will be sent to `self.language_model`.
        2.  The handler will enter a tool-use loop with the **Language Model**.
        3.  If the Language Model decides that code needs to be generated, it will be instructed to respond with a special tool call, e.g.:
            ```json
            {"tool": "generate_code", "prompt": "Create a Python function that returns the factorial of a number."}
            ```
        4.  The `_execute_tool` method will be updated to recognize this new `generate_code` tool.

3.  **Create a new `_execute_code_generation` method:**
    *   When the `generate_code` tool is called, this new method will be invoked.
    *   It will take the prompt from the tool call and send it to `self.code_model`.
    *   The response from the Code Model (the actual code) will then be returned to the Language Model as the "result" of the tool call.

**Phase 3: Updating the System Prompts**

1.  **Language Model System Prompt:**
    *   The `ROLE_SYSTEM` in `config.py` will be updated to be the system prompt for the **Language Model**.
    *   It will be given a new tool in its prompt: `generate_code(prompt: str)`.
    *   It will be explicitly instructed to delegate all code generation tasks to this new tool.

2.  **Code Model System Prompt:**
    *   We will create a new, hard-coded system prompt within the `LocalCodingHandler` specifically for the Code Model. It will be very simple, something like: "You are an expert code generator. You will be given a prompt and you must return only the code that is requested."

**Phase 4: Testing**

1.  **Update Existing Tests:** The tests in `test_llm_handlers.py` and `test_tool_loop.py` will need to be updated to account for the new dual-model architecture. We will need to mock both the language model and the code model.

2.  **Create New Integration Tests:** A new test will be added to `test_integration.py` to simulate a full, end-to-end conversation that involves both the Language Model and the Code Model working together.

---

#### **4. Timeline and Execution**

This is a significant undertaking. I recommend we proceed in the order outlined above, phase by phase. I will communicate with you at the end of each step to ensure we are aligned before proceeding to the next.

This structured approach will minimize the risk of errors and ensure that we build a robust, reliable, and powerful new architecture for DeepCoderX.
