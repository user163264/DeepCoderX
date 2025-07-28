# DeepCoderX Model Requirements

This document describes the AI models required for DeepCoderX Phase 3 dual model system.

## Required Models (Not Included in Repository)

**Total Size:** 3.8GB  
**Storage Location:** `.cache/deepcoderx/models/`  
**Auto-Download:** Models are automatically downloaded on first run if missing  

### 1. Semantic Parser Model
- **File:** `Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf`
- **Size:** 2.0GB
- **Quantization:** Q4_K_S (optimal balance of quality and speed)
- **Role:** Intent classification, semantic analysis, conversational responses
- **Memory Usage:** ~3.3GB RAM (always loaded)
- **Context:** 2048 tokens

### 2. Code Specialist Model  
- **File:** `qwen2.5-coder-1.5b-instruct-q8_0.gguf`
- **Size:** 1.8GB
- **Quantization:** Q8_0 (high quality for code generation)
- **Role:** Specialized code generation, file operations, technical tasks
- **Memory Usage:** ~1.8GB RAM (lazy loaded on-demand)
- **Context:** 4096 tokens

## Model Setup Instructions

### Automatic Setup (Recommended)
1. Run DeepCoderX: `python3 app.py`
2. Models will be automatically downloaded to `.cache/deepcoderx/models/`
3. First run may take 5-10 minutes for model downloads

### Manual Setup
1. Create directory: `mkdir -p .cache/deepcoderx/models/`
2. Download models to the directory above
3. Verify files exist and have correct names
4. Run DeepCoderX normally

## Hardware Requirements

- **RAM:** 8GB minimum, 16GB+ recommended
- **Storage:** 4GB free space for models
- **CPU:** Apple Silicon (M1/M2/M3/M4) for Metal acceleration
- **Performance:** Optimized for MacBook Air M4 with 24GB RAM

## Model Performance

- **Semantic Analysis:** 1-2 seconds average
- **Code Generation:** 2-5 seconds depending on complexity
- **Memory Efficiency:** 5.1GB total usage (21% of 24GB available)
- **Local Processing:** 90% of requests handled without cloud APIs

## Troubleshooting

### Missing Models
```bash
# Check if models exist
ls -la .cache/deepcoderx/models/

# Expected output:
# Llama-3.2-3B-Instruct-uncensored.Q4_K_S.gguf
# qwen2.5-coder-1.5b-instruct-q8_0.gguf
```

### Memory Issues
- Close other applications if models fail to load
- Consider using smaller quantizations if memory is limited
- Monitor memory usage: `top -o mem`

### Performance Issues
- Ensure Metal acceleration is available (Apple Silicon)
- Check model quantization levels
- Verify sufficient RAM available

## Production Notes

- Models are excluded from git repository due to size
- Each developer must download models independently  
- Models are stable and rarely change
- Production deployments should include model management strategy

---

**Generated:** July 28, 2025  
**DeepCoderX Version:** Phase 3 Dual Model System  
**Hardware Target:** MacBook Air M4, 24GB RAM
