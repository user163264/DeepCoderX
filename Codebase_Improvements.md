# Codebase Improvement Suggestions for DeepCoderX

This document outlines concrete suggestions for improving the DeepCoderX project, ranging from immediate enhancements to more strategic additions.

## 1. Implement `cd` as a "Real" Command

-   **Problem:** The `cd` command is not currently functional. The `FilesystemCommandHandler` does not have an intent for changing the current working directory.
-   **Suggestion:**
    1.  Add a `change_directory` intent to the `NLUParser`'s system prompt.
    2.  Implement the logic in the `FilesystemCommandHandler` to handle this intent by updating the `self.ctx.current_dir` variable.

## 2. Enhance State Management & Configuration

-   **Problem:** The application's state and configuration could be more robustly managed.
-   **Suggestion:**
    1.  **Implement a `Session` Class:** Create a dedicated `Session` class to manage the application's state, including `current_directory`, `debug_mode`, `dry_run`, etc.
    2.  **Dynamic Configuration:** Allow the user to change settings during runtime (e.g., `config set sandbox_path /new/path`).

## 3. Improve NLU Parser Robustness

-   **Problem:** The `NLUParser` relies on a single LLM call, which can fail if the model's output is malformed.
-   **Suggestion:**
    1.  **Implement a Retry Mechanism:** If the `NLUParser` receives an invalid JSON response, it should automatically retry the request.
    2.  **Add a "Confidence Score":** Modify the NLU prompt to ask the model for a confidence score. If the confidence is below a certain threshold, the system should ask for clarification.

## 4. Introduce a More Powerful `run` Command

-   **Problem:** The ability to execute scripts or shell commands is a missing feature.
-   **Suggestion:**
    1.  **Create a `run_bash` Intent:** Add a `run_bash` intent to the `NLUParser`.
    2.  **Implement a `RunCommandHandler`:** Create a new handler for executing shell commands.
    3.  **Security:** This handler must strictly enforce that commands are run within the sandboxed directory, use a timeout, and scrub output for sensitive information.

## 5. Improve User Feedback and Asynchronous Operations

-   **Problem:** The UI shows a generic "Processing..." spinner for long-running commands.
-   **Suggestion:**
    1.  **Provide More Granular Feedback:** Offer more specific feedback, such as "Reading file..." or "Sending to DeepSeek for analysis...".
    2.  **Handle Long-Running Tasks Asynchronously:** For very long operations, consider running them in the background and notifying the user upon completion.

## Summary of Recommendations

1.  **Immediate Fix:** Implement the `cd` command properly.
2.  **Good Next Step:** Improve the NLU parser's robustness with retries and confidence scoring.
3.  **High-Impact Feature:** Add a secure `run_bash` command.
4.  **Architectural Improvement:** Refactor state management into a dedicated `Session` class.
5.  **UX Enhancement:** Improve feedback for long-running tasks.
