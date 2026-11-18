---
description: Riprende il lavoro da .claude/handoff/<ticket>.md dopo un /clear
argument-hint: "[numero ticket o chiave] [indicazioni]"
---

Più sessioni possono lavorare in parallelo nello stesso repository: leggi solo l'handoff del ticket su cui riprendiamo.

1. Se gli argomenti indicano un numero di ticket o una chiave, leggi `.claude/handoff/<chiave>.md` nella root del
   progetto/worktree corrente.
2. Se non c'è una chiave, elenca i file in `.claude/handoff/` (solo nome e prima riga, senza leggerli) e chiedimi quale
   riprendere. Se la cartella non esiste ma c'è il vecchio `.claude/HANDOFF.md`, dimmi di che ticket parla la prima riga
   e chiedi conferma prima di usarlo.
3. Non aprire gli handoff degli altri ticket.

- Non rileggere tutti i "File chiave": aprili solo quando servono per il passo che stai facendo.
- Riassumimi in 3-4 righe dove eravamo e qual è il prossimo passo.
- Poi aspetta conferma prima di procedere.

Indicazioni aggiuntive dell'utente: $ARGUMENTS
