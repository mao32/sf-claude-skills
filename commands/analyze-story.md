# /analyze-story — Analizza una User Story e produci il piano di implementazione

Analizza una user story SENZA implementarla. Produce un piano dettagliato per la review.

## Input

$ARGUMENTS contiene la user story o il suo ID. Se è un ID, chiedi i dettagli.

## Istruzioni

### Step 1: Comprensione

1. Leggi la user story e i criteri di accettazione
2. Identifica: attore, azione, risultato atteso
3. Elenca ogni criterio di accettazione come scenario testabile

### Step 2: Esplorazione org

Usa DX MCP e le skill per esplorare lo schema:

1. **Oggetti coinvolti**: esistono già? Quali campi hanno?
   - `sf-metadata`: descrivi gli oggetti
   - `sf-soql`: query per capire volumi e relazioni
2. **Automazioni esistenti**: ci sono trigger/flow sugli stessi oggetti?
   - Verifica per evitare conflitti
3. **Permessi attuali**: chi ha accesso agli oggetti coinvolti?
   - `sf-permissions`: analizza permission set esistenti

### Step 3: Piano di implementazione

Produci un documento strutturato:

```markdown
## Piano di implementazione — [US-ID]

### Oggetti e campi
| Tipo     | Nome                    | Azione  | Note                    |
|----------|-------------------------|---------|-------------------------|
| Object   | Invoice__c              | CREATE  | Nuovo oggetto custom     |
| Field    | Invoice__c.Amount__c    | CREATE  | Currency, 2 decimali     |
| Field    | Opportunity.StageName   | EXIST   | Già presente             |

### Classi Apex
| Classe                    | Tipo            | Azione  |
|---------------------------|-----------------|---------|
| InvoiceTrigger            | Trigger         | CREATE  |
| InvoiceTriggerHandler     | Handler         | CREATE  |
| InvoiceService            | Service         | CREATE  |
| InvoiceSelector           | Selector        | CREATE  |
| InvoiceServiceTest        | Test            | CREATE  |
| TestDataFactory           | Test utility    | MODIFY  |

### Flow
| Flow                      | Tipo            | Azione  |
|---------------------------|-----------------|---------|

### LWC
| Componente               | Scopo            | Azione  |
|---------------------------|-----------------|---------|

### Permission Set
| Permission Set            | Target           |
|---------------------------|------------------|
| PS_InvoiceManager_Full    | Full CRUD Invoice|

### Scenari di test
| #  | Scenario                           | Tipo     | Atteso              |
|----|------------------------------------|----------|---------------------|
| 1  | Opp Closed Won con billing addr    | Positivo | Invoice creata       |
| 2  | Opp Closed Won senza billing addr  | Negativo | Errore su stage      |
| 3  | 251 Opp aggiornate in bulk         | Bulk     | 251 Invoice create   |
| 4  | Utente senza PS_Invoice            | Permessi | Errore permessi      |

### Rischi e dipendenze
- ...

### Stima effort
- Sviluppo: X ore
- Test: X ore
- Deploy + verifica: X ore
```

### Step 4: Diagramma

Se la user story coinvolge 3+ oggetti o ha un flusso complesso, genera un diagramma ERD o di flusso con sf-diagram-mermaid.

### Step 5: Conferma

Chiedi conferma del piano prima di procedere all'implementazione. Suggerisci di usare `/implement-story` per passare alla fase di sviluppo.
