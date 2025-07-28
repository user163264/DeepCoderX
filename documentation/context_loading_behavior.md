# Documentation: Context Loading Behavior

This document outlines how the DeepCoderX application handles project context, specifically regarding the `project_context.md` file. This behavior was updated on June 27, 2025, to improve application stability and efficiency.

## 1. Local Model (`LocalCodingHandler`)

The local model (e.g., Qwen) **no longer automatically loads the `project_context.md` file on startup.**

### Why was this change made?

The primary reason was to prevent critical errors related to the model's context window limit. The `project_context.md` file can become very large (e.g., >19,000 tokens). Eagerly loading this entire file into the model's memory on startup would frequently exceed its capacity (e.g., 8,192 tokens), causing the application to crash.

### How does it work now?

The local model now starts with a "clean buffer." It is initialized with only its core system prompt, which instructs it on its capabilities and how to use its tools.

- **On-Demand Context:** When a user asks a question that requires knowledge of the project's files, the model is expected to use its tools (`read_file`, `list_dir`, etc.) to gather the necessary information in real-time.
- **Efficiency:** This "lazy loading" approach is much more efficient. It only consumes memory for the context that is relevant to the immediate task, preventing crashes and allowing the model to handle much larger projects.

## 2. DeepSeek Model (`DeepSeekAnalysisHandler`)

The behavior of the DeepSeek handler remains unchanged. It **does** still load the `project_context.md` file when a command like `@deepseek` is used.

### Why is it different?

The DeepSeek model is intended for high-level, complex analysis across the entire codebase. For these tasks, providing the full project context upfront is highly beneficial and allows the model to generate more comprehensive and insightful architectural reviews and suggestions. Cloud-based models typically have much larger context windows, making this approach feasible.
