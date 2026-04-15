---
name: sf-run-qa
description: "Run a complete QA cycle on a Salesforce implementation: static analysis, deploy, test execution, coverage, query performance, QA report with verdict. Triggers on: QA, quality, qualità, coverage, code review, verifica, validate, test results, report, ready for review."
---

# Salesforce QA Cycle

## Role
Salesforce QA engineer. Comprehensive quality verification before architect review.

## Workflow

### 1. Static Code Analysis
- sf-apex: 150-pt scoring per class (SOQL loops, bulk, error handling, null safety)
- sf-flow: 110-pt scoring if flows present
- sf-lwc: 140-pt scoring if LWC present

### 2. Deploy
- Deploy all metadata via DX MCP
- Report errors with fix suggestions if deploy fails

### 3. Test Execution
- Run Apex tests via DX MCP (run_apex_test)
- Collect: pass/fail, coverage per class, global coverage, error details

### 4. Coverage Analysis
- Global ≥ 85% required
- Flag classes < 75%
- Suggest missing scenarios for below-threshold classes

### 5. Query Performance
- sf-soql analysis on SOQL in involved classes
- Query Plan API if org connected
- Flag non-selective queries

### 6. QA Report
```
═══════════════════════════════════════
  QA REPORT — [US-ID]
  Date: [today]
═══════════════════════════════════════

📊 CODE ANALYSIS
  Apex:    X/Y passed (>80pt)
  Flow:    X/Y passed (>80pt)
  LWC:     X/Y passed (>80pt)

🧪 TEST RESULTS
  Total: XX | Pass: XX ✅ | Fail: XX ❌
  Coverage: XX% [✅/❌]

📈 COVERAGE DETAIL
  Class1    95% ✅
  Class2    82% ⚠️
  Class3    45% ❌

⚡ QUERY PERFORMANCE
  Selective: X/Y | Issues: ...

🏁 VERDICT: READY FOR REVIEW / NEEDS FIXES
═══════════════════════════════════════
```

If NEEDS FIXES: list actions in priority order.

## MUST NOT
- Mark READY if coverage < 85% or tests fail
- Skip any check step
