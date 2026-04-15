# /run-qa — Esegui il ciclo di QA completo

Esegue il ciclo completo di quality assurance per una user story o per l'intero progetto.

## Input

$ARGUMENTS può contenere:
- Un ID user story (es. US-1234) → testa solo le classi della US
- "all" → esegue tutti i test del progetto
- Un nome classe (es. InvoiceService) → testa solo quella classe e le sue dipendenze

## Istruzioni

### Step 1: Code Analysis statica

1. Usa la skill sf-apex per validare tutte le classi Apex coinvolte:
   - Punteggio 150-pt per ogni classe
   - Verifica assenza SOQL in loop
   - Verifica bulkification
   - Verifica error handling
2. Se presenti Flow, usa sf-flow per la validazione 110-pt
3. Se presenti LWC, usa sf-lwc per la validazione 140-pt
4. Riporta i punteggi e le criticità trovate

### Step 2: Deploy su org di test

1. Deploya tutti i metadata modificati tramite DX MCP
2. Verifica che il deploy sia riuscito senza errori
3. Se ci sono errori di deploy, riportali e suggerisci fix

### Step 3: Esecuzione test Apex

1. Esegui i test tramite DX MCP (`run_apex_test`):
   - Se input è una US specifica: esegui solo le test class correlate
   - Se input è "all": esegui tutti i test
2. Raccogli i risultati:
   - Test passati / falliti
   - Coverage per classe
   - Coverage globale
   - Dettagli degli errori per test falliti

### Step 4: Analisi coverage

1. Verifica che la coverage globale sia >= 85%
2. Identifica classi con coverage < 75% individuale
3. Per le classi sotto soglia, suggerisci scenari di test mancanti

### Step 5: Verifica query performance

1. Usa sf-soql per analizzare le query SOQL nelle classi coinvolte
2. Se connesso all'org, usa il Query Plan API per verificare selettività
3. Segnala query non selettive o potenzialmente lente

### Step 6: Report finale

Genera un report strutturato:

```
═══════════════════════════════════════════════
  QA REPORT — [US-ID o "Full Project"]
  Data: [data odierna]
═══════════════════════════════════════════════

📊 CODE ANALYSIS
  Apex classes:    X/Y passed (>80pt)
  Flow:            X/Y passed (>80pt)
  LWC:             X/Y passed (>80pt)

🧪 TEST RESULTS
  Total tests:     XX
  Passed:          XX ✅
  Failed:          XX ❌
  Coverage:        XX% [✅ above 85% / ❌ below 85%]

📈 COVERAGE DETAIL
  Classe1            95% ✅
  Classe2            82% ⚠️
  Classe3            45% ❌ ← intervento necessario

⚡ QUERY PERFORMANCE
  Query selettive:   X/Y
  Segnalazioni:      ...

🏁 VERDICT: [READY FOR REVIEW / NEEDS FIXES]
═══════════════════════════════════════════════
```

Se il verdetto è NEEDS FIXES, elenca le azioni correttive in ordine di priorità.
