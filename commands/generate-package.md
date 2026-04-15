# /generate-package — Genera il package.xml per una User Story

Genera il file `release/pkg_<US-ID>.xml` per il rilascio di una user story.

## Input

$ARGUMENTS deve contenere l'ID della user story (es. US-1234).
Se non fornito, chiedi quale user story.

## Istruzioni

1. **Identifica tutti i metadata** creati o modificati per questa user story.
   Cerca nel progetto SFDX i file nuovi o modificati di recente:
   - `force-app/main/default/classes/` → ApexClass
   - `force-app/main/default/triggers/` → ApexTrigger
   - `force-app/main/default/objects/` → CustomObject, CustomField
   - `force-app/main/default/flows/` → Flow
   - `force-app/main/default/lwc/` → LightningComponentBundle
   - `force-app/main/default/permissionsets/` → PermissionSet
   - `force-app/main/default/validationRules/` → ValidationRule
   - `force-app/main/default/customMetadata/` → CustomMetadata

2. **Crea la cartella** `release/` se non esiste.

3. **Genera il file** `release/pkg_<US-ID>.xml` seguendo il template:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
    <types>
        <members>NomeClasse1</members>
        <members>NomeClasse2</members>
        <name>ApexClass</name>
    </types>
    <!-- Ripetere per ogni tipo di metadata -->
    <version>62.0</version>
</Package>
```

4. **Regole di inclusione**:
   - INCLUDI: ApexClass (anche le test class), ApexTrigger, CustomObject, CustomField, ValidationRule, Flow, LightningComponentBundle, PermissionSet, CustomMetadata, CustomLabel (solo se creati per la US)
   - ESCLUDI: Profile (usare solo PermissionSet), Layout (solo se esplicitamente modificato), metadata di sistema non toccati
   - Per CustomField, usa il formato `NomeOggetto__c.NomeCampo__c`
   - Per ValidationRule, usa il formato `NomeOggetto__c.NomeRegola`

5. **Verifica** che il file XML sia sintatticamente valido.

6. **Mostra un riepilogo** dei metadata inclusi, raggruppati per tipo.
