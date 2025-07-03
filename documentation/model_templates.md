# Model Chat Templates

This document outlines the chat templates for the different models used in DeepCoderX.

## Qwen Model Template

The Qwen models use a simple chat format. The system prompt is sent first, followed by the user's message.

**Example:**

```
<|im_start|>system
You are a helpful assistant.<|im_end|>
<|im_start|>user
Hello<|im_end|>
<|im_start|>assistant
```

## Llama-3.2-Instruct Model Template

The Llama-3.2-Instruct models use a more complex chat template with specific tokens to delineate roles.

**Template:**

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```

**Example:**

```
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful assistant.<|eot_id|><|start_header_id|>user<|end_header_id|>

Hello<|eot_id|><|start_header_id|>assistant<|end_header_id|>
```
