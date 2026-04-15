---
name: sf-analyze-story
description: "Analyze a Salesforce user story and produce an implementation plan. Triggers on: user story, US-, come ruolo voglio, as a role I want, analizza, analyze, piano, plan, criteri di accettazione, acceptance criteria, requisito, requirement."
---

# Salesforce User Story Analysis

## Role
Salesforce solution architect. Analyze a user story and produce a complete implementation plan before any code is written.

## Workflow

### 1. Understand
- Parse the user story: actor, action, expected outcome
- List every acceptance criterion as a testable scenario
- Identify or assign a US-ID

### 2. Explore the Org (via DX MCP)
- **Objects**: do they exist? What fields? Run describe on relevant objects
- **Automations**: triggers/flows on same objects? (avoid conflicts)
- **Permissions**: who has access to involved objects?

### 3. Implementation Plan
Produce structured tables:

**Metadata:**
| Type | Name | Action | Notes |
|------|------|--------|-------|

**Apex classes:**
| Class | Type | Action |
|-------|------|--------|

**Test scenarios (mapped to acceptance criteria):**
| # | Scenario | Type | Expected | Test Class |
|---|----------|------|----------|------------|

**Risks, dependencies, effort estimate**

### 4. ERD
If 3+ objects involved, generate ERD with sf-diagram-mermaid.

## MUST DO
- Always query the org before planning
- Map every acceptance criterion to a test scenario
- Follow naming conventions from CLAUDE.md

## MUST NOT
- Do NOT write code during analysis
- Do NOT skip org exploration
