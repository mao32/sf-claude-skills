# /implement-story — Implementa una User Story completa

Ricevi una user story come input (da $ARGUMENTS o dalla conversazione).

## Istruzioni

Segui RIGOROSAMENTE questo ordine. Non saltare nessun passaggio.

### Fase 1: Analisi (NON scrivere codice ancora)

1. Leggi la user story e i criteri di accettazione
2. Usa le skill sf-metadata e sf-soql per esplorare lo schema dell'org:
   - Quali oggetti sono coinvolti? Esistono già?
   - Quali campi servono? Esistono già?
   - Ci sono trigger/flow esistenti sugli stessi oggetti che potrebbero confliggere?
3. Produci un **piano di implementazione** con:
   - Lista dei metadata da creare/modificare
   - Dipendenze e ordine di implementazione
   - Pattern architetturali che userai (trigger handler, service, selector)
   - Rischi e considerazioni
4. Se utile, genera un diagramma ERD con sf-diagram-mermaid
5. **Chiedi conferma** prima di procedere allo sviluppo

### Fase 2: Sviluppo

1. Crea/modifica i metadata seguendo le naming convention del CLAUDE.md
2. Segui i pattern architetturali (Service Layer, Trigger Handler, Selector)
3. Rispetta le regole Apex (no SOQL in loop, bulkification, null safety)
4. Per ogni file creato, verifica che gli hook di validazione sf-skills diano punteggio accettabile
5. Se il punteggio è sotto 80%, correggi prima di procedere

### Fase 3: Test

1. Crea/aggiorna la TestDataFactory con i metodi necessari
2. Genera test class per OGNI criterio di accettazione:
   - Test positivo (happy path)
   - Test negativo (condizioni di errore)
   - Test bulk (200+ record)
   - Test permessi (se applicabile)
   - Test boundary (null, vuoto, valori massimi)
3. Usa il pattern GIVEN / WHEN / THEN nei commenti
4. Usa Assert.areEqual, Assert.isTrue, Assert.isNotNull (non i vecchi System.assert)
5. Target coverage: 90%+

### Fase 4: Deploy e verifica

1. Deploya sull'org tramite DX MCP (`deploy_metadata`)
2. Esegui TUTTI i test tramite DX MCP (`run_apex_test`)
3. Verifica:
   - Tutti i test passano ✅
   - Coverage >= 85% globale ✅
   - Nessun errore di deploy ✅
4. Se qualcosa fallisce, correggi e ripeti il deploy

### Fase 5: Package.xml

1. Genera `release/pkg_<US-ID>.xml` con TUTTI i metadata creati/modificati
2. Includi: ApexClass, ApexTrigger, CustomObject, CustomField, ValidationRule, Flow, LightningComponentBundle, PermissionSet
3. NON includere: Profile, metadata di sistema non toccati
4. Verifica che il file sia valido XML

### Fase 6: Documentazione

1. Genera `docs/TECH_<US-ID>.docx` — documentazione tecnica:
   - Overview e criteri di accettazione
   - Data model (tabelle oggetti e campi)
   - Architettura e design pattern usati
   - Classi Apex con responsabilità
   - Test strategy con scenari e coverage
   - Deployment (contenuto package.xml)
   - Rischi e note per l'architetto
2. Genera `docs/FUNC_<US-ID>.docx` — documentazione funzionale:
   - Descrizione in linguaggio business
   - Cosa cambia per gli utenti
   - Regole di validazione spiegate
   - Scenari di test funzionali passo-passo
   - FAQ anticipate
3. Usa la docx skill (docx-js) con formato A4, Arial, tabelle con WidthType.DXA
4. I file si importano direttamente in Google Docs

### Fase 7: Riepilogo

Presenta un riepilogo finale:
- Lista file creati/modificati
- Risultati test (pass/fail, coverage %)
- Contenuto del package.xml
- Documenti generati (TECH + FUNC)
- Eventuali note per l'architetto
