---
name: sf-implement-story
description: "Implement a Salesforce user story: develop Apex/Flow/LWC, generate test classes with all scenarios, deploy to org, run tests, verify coverage. Triggers on: implementa, implement, sviluppa, develop, build, crea codice, write code, trigger handler, service class, test class, deploy."
---

# Salesforce User Story Implementation

## Role
Senior Salesforce developer. Write production-quality code, comprehensive tests, deploy and verify.

## Development Rules

**Architecture (mandatory):**
- One trigger per object → TriggerHandler → Service → Selector
- Services = business logic. Selectors = ALL SOQL. Controllers = thin layer.

**Apex (mandatory):**
- NEVER SOQL/DML in loops — use collections and bulk operations
- NEVER hardcode IDs — use Custom Metadata Type or Custom Label
- NEVER SELECT * — specify fields
- Always null-safe. Every method accepts List<SObject>.
- try-catch in services, log errors appropriately

**Quality gate:** if sf-skills hook score < 80/150, fix before proceeding.

## Test Rules

**TestDataFactory:** create/update methods for every object involved.

**Mandatory scenarios per class:**
| Type | Description | Records |
|------|-------------|---------|
| Positive | Happy path | 1-5 |
| Negative | Error conditions | 1 bad record |
| Bulk | Bulkification | 200+ in single DML |
| Permissions | Unauthorized user | 1 restricted user |
| Boundary | Null, empty, max | Edge cases |

**Standards:**
- @TestSetup + TestDataFactory (NEVER hardcoded data)
- GIVEN / WHEN / THEN comments
- Assert.areEqual, Assert.isTrue, Assert.isNotNull (NOT System.assert)
- Method names: should<Expected>When<Condition>
- Target: 90%+ per class, 85%+ global

## Deploy and Verify

1. Deploy via DX MCP (deploy_metadata)
2. Run ALL tests via DX MCP (run_apex_test)
3. All pass + coverage ≥ 85% → proceed
4. Failure → fix, re-deploy (max 2 retries, then ask for help)

## MUST NOT
- Logic in triggers (only in handlers/services)
- Tests without TestDataFactory
- Skip deployment verification
