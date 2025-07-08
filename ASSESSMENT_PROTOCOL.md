# DeepCoderX Assessment Protocol

## MANDATORY RULE: NEVER CLAIM FUNCTIONALITY WITHOUT PROOF

This protocol was created after a critical assessment failure where "PRODUCTION READY" was claimed without functional verification.

## Assessment Hierarchy (MUST FOLLOW)

1. **Code Review Only** → Max claim: "Implementation exists"
2. **Basic Execution** → Max claim: "Components load"  
3. **Functional Testing** → Max claim: "Verified working"
4. **Production Testing** → Max claim: "Production ready"

## MANDATORY Before Any Assessment

### Environment Check
```bash
# ALWAYS run diagnostics first
python verify_gguf_simple.py
python diagnostic_gguf.py

# If these fail → STOP assessment
# Fix environment before making ANY claims
```

### Required Language
- ❌ BANNED: "production ready", "fully functional" (without Level 3+ evidence)
- ✅ REQUIRED: "Code inspection suggests...", "Requires testing to confirm..."

### Evidence Documentation
Every assessment MUST include:
- CONFIDENCE LEVEL: [Low/Medium/High/Verified]
- TESTING COMPLETED: [None/Basic/Functional/Production] 
- LIMITATIONS: [What was NOT verified]

## Emergency Protocol

If assessment proves wrong:
1. STOP making claims immediately
2. ACKNOWLEDGE the specific error
3. EXPLAIN what went wrong methodologically
4. PROVIDE corrected, conservative assessment
5. IMPLEMENT prevention measures

Remember: **Accuracy over optimism. Trust over false confidence.**
