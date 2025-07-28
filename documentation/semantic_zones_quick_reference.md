# Semantic Zones Quick Reference

## 🎯 Zone Triggers

| Zone | Trigger | Example | Routing | Tools |
|------|---------|---------|---------|-------|
| **🔧 Tool Operation** | `use your tools` | `@deepseek use your tools and read config.py` | qwen_coder | ✅ |
| **💬 Conversational** | `explain` | `@deepseek explain how functions work` | conversation | ❌ |
| **🔍 Analysis** | `analyze` | `@deepseek analyze this project structure` | qwen_coder | ✅ |
| **🐛 Debug** | `debug` | `@deepseek debug this authentication error` | qwen_coder | ✅ |
| **✨ Creative** | `create` | `@deepseek create a backup script` | qwen_coder | ✅ |

---

## 📝 Quick Examples

### Tool Operations (File Access)
```bash
@deepseek use your tools and audit the entire codebase
@deepseek file operations: read all Python files
@deepseek access files and check project structure
```

### Conversations (No Tools)
```bash
@deepseek explain what REST APIs are
@deepseek what is the difference between async and sync?
@deepseek help me understand this error message
```

### Analysis (Smart Routing)
```bash
@deepseek analyze the database schema design
@deepseek review this code for best practices
@deepseek summarize what this module accomplishes
```

### Debugging (Problem Solving)
```bash
@deepseek debug why the tests are failing
@deepseek fix this broken authentication function
@deepseek troubleshoot the database connection issue
```

### Creative (Code Generation)
```bash
@deepseek create unit tests for this module
@deepseek generate a REST API endpoint for users
@deepseek build a simple file backup script
```

---

## ⚡ Common Workflows

### Learning Something New
1. `@deepseek explain [concept]` → Learn fundamentals
2. `@deepseek analyze [real example]` → See it in practice  
3. `@deepseek use your tools and examine [files]` → Study implementation

### Debugging Issues
1. `@deepseek explain what [error] means` → Understand the problem
2. `@deepseek use your tools and read [relevant files]` → Investigate
3. `@deepseek debug [specific issue]` → Get solution

### Code Review
1. `@deepseek analyze [code/project]` → Get overview
2. `@deepseek use your tools and audit [specific files]` → Detailed review
3. `@deepseek create [improvements]` → Implement fixes

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| Zone not detected | Use explicit triggers: `use your tools`, `explain`, `analyze`, etc. |
| Wrong zone detected | Be more specific with your trigger words |
| Tools not working | Check file paths exist and you have permissions |
| Unexpected routing | Enable debug mode: `export DEEPCODERX_DEBUG_MODE=true` |

---

## 🔧 Environment Variables

```bash
export DEEPCODERX_SEMANTIC_ZONES_ENABLED=true  # Enable/disable zones
export DEEPCODERX_DEBUG_MODE=true              # See zone detection details
```

---

## 📖 Full Documentation

For complete details, see: `/documentation/semantic_zones.md`
