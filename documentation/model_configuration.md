# Model Configuration Guide

This document explains how to configure the dual-model architecture for DeepCoderX.

---

### **Dual-Model Architecture**

DeepCoderX can operate in two modes:

1.  **Single-Model Mode:** Uses a single, local coding model for all tasks.
2.  **Dual-Model Mode:** Uses two separate local models:
    *   A **Language Model** for understanding user intent and routing commands.
    *   A **Code Model** for generating and modifying code.

This dual-model architecture is highly recommended as it significantly improves the application's accuracy and reliability.

---

### **Configuration**

To enable and configure the dual-model mode, you will need to set the following variables in your `.env` file:

1.  **`DUAL_MODEL_MODE`**
    *   Set this to `true` to enable the dual-model architecture.
    *   Set this to `false` to use the original, single-model architecture.
    *   **Default:** `true`

2.  **`LANGUAGE_MODEL_PATH`**
    *   This must be the **full, absolute path** to the GGUF file for your chosen language model.
    *   **This is a required setting for dual-model mode.**

3.  **`LOCAL_MODEL_PATH`**
    *   This is the path to your **coding model** (e.g., Qwen).

---

### **Recommended Language Models**

For the `LANGUAGE_MODEL_PATH`, you should use a small, fast, and high-quality language model. The following are excellent choices that are known to work well for instruction-following and routing tasks:

*   **[Phi-3 Mini (3.8B)](https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf):** A very powerful and popular small model from Microsoft.
*   **[Llama 3 8B Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct-GGUF):** A slightly larger but extremely capable model from Meta.
*   **[Mistral 7B Instruct](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.2-GGUF):** Another excellent choice that is known for its speed and quality.

You can download the GGUF versions of these models from their Hugging Face pages and then update the `LANGUAGE_MODEL_PATH` in your `.env` file with the correct path.
