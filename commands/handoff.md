---
description: Salva lo stato della sessione in .claude/handoff/<ticket>.md prima di un /clear
argument-hint: "[numero ticket o chiave] [note]"
---

Stiamo per chiudere questa sessione con /clear. Più sessioni possono lavorare in parallelo nello stesso repository,
quindi ogni attività ha il suo file di handoff.

**Chiave del file**, in quest'ordine:
1. il numero di ticket indicato negli argomenti (es. `29885`);
2. altrimenti il numero di ticket su cui abbiamo lavorato in questa sessione;
3. altrimenti il work item (es. `WI-000328`) o il nome del branch corrente, con `/` sostituito da `-`.
Se la chiave è ambigua (più ticket nella sessione), chiedi prima di scrivere.

Scrivi (sovrascrivendo solo se è lo stesso ticket) il file `.claude/handoff/<chiave>.md` nella root del
progetto/worktree corrente, in italiano, conciso (massimo ~60 righe). Prima riga: `# HANDOFF — <chiave> — <titolo breve>`.
Sezioni:

## Obiettivo
Una o due frasi: su cosa stavamo lavorando e perché.

## Fatto
Elenco puntato di ciò che è completato (con riferimento a commit/PR se esistono).

## Da fare
Prossimi passi concreti, in ordine. Il primo deve essere azionabile subito.

## Decisioni prese
Scelte architetturali o tecniche e il motivo, in una riga ciascuna. Includi le alternative scartate solo se rischiamo di riproporle.

## File chiave
Percorsi dei file rilevanti per riprendere (solo quelli necessari, non tutto ciò che è stato letto).

## Attenzione
Trappole, vincoli del cliente, comandi particolari, cose che non funzionano.

Regole:
- Non toccare i file di handoff di altri ticket né il vecchio `.claude/HANDOFF.md` condiviso.
- Non copiare codice nel file: indica percorso e, se serve, il nome del metodo/classe.
- Non includere credenziali, token o dati personali.
- Note aggiuntive dell'utente da includere: $ARGUMENTS

Alla fine rispondi solo: "Handoff salvato in .claude/handoff/<chiave>.md. Ora puoi fare /clear e poi /riprendi <chiave>."
