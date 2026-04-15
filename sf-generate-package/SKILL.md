---
name: sf-generate-package
description: "Generate a package.xml manifest for a Salesforce user story release. Triggers on: package.xml, manifest, pkg_, rilascio, release, deployment, metadata list, cosa deployare, componenti."
---

# Salesforce Package.xml Generator

## Role
Generate accurate, complete package.xml manifests for user story releases.

## Workflow

### 1. Identify Metadata
Scan force-app/main/default/ for files created/modified:
- classes/ → ApexClass
- triggers/ → ApexTrigger
- objects/ → CustomObject, CustomField
- flows/ → Flow
- lwc/ → LightningComponentBundle
- permissionsets/ → PermissionSet
- customMetadata/ → CustomMetadata

### 2. Generate release/pkg_<US-ID>.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>ClassName</members>
        <n>ApexClass</n>
    </types>
    <version>62.0</version>
</Package>
```

### 3. Rules

**INCLUDE:** ApexClass (+ test classes), ApexTrigger, CustomObject (new), CustomField (format: `Object__c.Field__c`), ValidationRule (format: `Object__c.RuleName`), Flow, LightningComponentBundle, PermissionSet, CustomMetadata

**NEVER:** Profile, Layout (unless explicitly modified), unrelated system metadata

### 4. Validate XML + show grouped summary

## MUST DO
- Include ALL metadata for the user story (including test classes)
- Use correct member formats for fields and validation rules
