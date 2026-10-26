---
name: sf-devops-center-wi
description: "Giro completo e sicuro di un work item DevOps Center (Next Generation) via MCP: creazione WI, branch e worktree dedicato, modifiche, revisione, deploy sull'ambiente di sviluppo, commit MCP, push, PR, attesa del registro, promote. TRIGGER when: l'utente chiede di creare/aprire un work item, portare modifiche metadata in pipeline, committare su un WI, aprire la PR o promuovere un WI in DevOps Center. DO NOT TRIGGER per deploy diretti fuori pipeline concordati esplicitamente o per sole modifiche a docs/memorie."
---

# DevOps Center — giro del work item (via MCP)

## Ruolo
Portare modifiche di metadata dalla scrivania alla pipeline DevOps Center **senza fare danni**: niente merge manuali, niente commit git a mano, niente promote "al buio", niente cancellazioni pericolose. Ogni passo che scrive (org, git, DevOps Center) parte solo dopo la revisione dell'utente.

## Parametri del progetto (chiedere o leggere da CLAUDE.md / memoria del progetto)

| Parametro | Esempio | Note |
| --- | --- | --- |
| Org DevOps Center | `<alias_dc>` | l'org che ospita DevOps Center (spesso la produzione) |
| Progetto DC | `<nome progetto>` | quello della pipeline in uso: verificarlo sugli ultimi WI (`list_devops_center_work_items` → `PipelineId`, `TargetBranch`) |
| Ambiente di sviluppo | `<alias_dev>` | la sandbox da cui parte la pipeline: sorgente di verità da cui leggere |
| Org di validazione | `<alias_integration>` | dove si fanno i dry-run (primo stage della pipeline) |
| Radice dei worktree | `<repo>.worktrees/` | un worktree per WI |

## Il giro, passo per passo

1. **Contenuto prima di tutto.** Definire con l'utente cosa entra nel WI. Preferire file **nuovi** e modifiche mirate; niente layout/flexipage condivisi se non servono. Mai **cancellare** file di Flow in un WI (vedi Trappole).
2. **Creare il WI** con `create_devops_center_work_item` sull'org DC e il progetto giusto. L'oggetto lo sceglie l'utente (il tool lo impone): proporre 1–2 opzioni.
3. **Portarlo a In Progress** con `update_devops_center_work_item_status` → DevOps Center crea il branch `WI-xxxxxx` dal branch dello stage di integrazione. Verificare con `git ls-remote --heads origin WI-xxxxxx`.
4. **Worktree dedicato** sul branch del WI (mai lavorare nel worktree di un'altra attività):
   `git fetch origin WI-xxxxxx && git worktree add -b WI-xxxxxx <radice>/WI-xxxxxx origin/WI-xxxxxx`
5. **Preparare i file** nel worktree partendo dal **retrieve dell'ambiente di sviluppo** o da un file esistente dello stesso tipo (mai inventare la struttura). Controllare vincoli di piattaforma (es. lunghezze label, valori di picklist esatti).
6. **Dry-run** sull'org di validazione: `sf project deploy start --dry-run --ignore-conflicts -o <alias_integration> -d <file…>` — deve dare tutti i componenti OK.
7. **Revisione dell'utente.** Mostrare i file (tabella + un file di esempio). L'utente li conferma e li mette in stage. Non andare oltre senza conferma.
8. **Deploy sull'ambiente di sviluppo** dei soli file del WI (`-d` per ogni file, `--ignore-conflicts`): tiene allineata la sorgente di verità. Solo con l'ok dell'utente per questo WI.
9. **Commit via MCP**: `commit_devops_center_work_item` con `repoPath` = worktree del WI. Mai `git add/commit` manuali prima (DC non li registrerebbe). `hasUpdates:false` nella risposta è normale: non è un errore.
10. **Push**: `git push origin HEAD` dal worktree.
11. **PR**: `create_devops_center_pull_request` → restituisce l'URL della PR verso il branch di integrazione.
12. **Attendere il registro.** DevOps Center acquisisce le entry del WI **con qualche minuto di ritardo** dopo push e PR. Finché le righe non compaiono il promote non deploya nulla. Controllare in background (non a vista) con una query REST:
    ```
    Q='SELECT MemberType, MemberName, ChangeType, WorkItemComponentList.Name, CreatedDate
       FROM WorkItemComponent WHERE CreatedDate = TODAY AND MemberName LIKE '<prefisso>%''
    sf api request rest "/services/data/v66.0/query?q=<Q url-encoded>" -o <alias_dc>
    ```
    (la SOQL via `sf data query` può essere bloccata da hook che non conoscono gli oggetti DevOps Center: la chiamata REST funziona). Un registro vuoto subito dopo la PR **non** significa che il commit è andato perso.
13. **Promote** (`promote_devops_center_work_item`) solo quando il registro contiene tutti i componenti attesi, e solo con l'ok dell'utente. **Il merge della PR lo fa DevOps Center**: mai `gh pr merge` a mano.
14. **Verifica dopo il promote**: componenti realmente deployati (`sf project deploy report --job-id <id> --json` → `details.componentSuccesses`) e presenza nell'org target.

## Trappole note

- **Registro ≠ diff git.** DevOps Center deploya i componenti del suo registro, non tutto il diff della PR. Se dopo l'attesa il registro resta vuoto o incompleto, fermarsi e proporre all'utente le alternative (commit dalla UI DC sull'ambiente di sviluppo, oppure percorso ibrido merge + deploy diretto) — mai sceglierle da soli.
- **Modifiche a file già registrati in un WI** possono non aggiornare il pacchetto: per correzioni a componenti già nel registro valutare un WI nuovo.
- **Mai cancellare Flow in un WI**: il promote genera destructiveChanges che su molte org falliscono e rendono il WI irrecuperabile. La rimozione di un Flow si fa fuori pipeline (Tooling API), concordata.
- **Valori di picklist**: disattivare invece di cancellare; verificare prima che nessun record o metadata li usi.
- **Il promote deploya il candidato di merge** (sorgente fuso sul target): fix formali sul branch sorgente, valori per-org sul branch target.
- **"source control is checking the pull request"**: spesso è GitHub che non ha ancora calcolato la mergeability; `gh pr view <N> --json mergeable,mergeStateStatus` la forza.
- **WI in stato NEW** → la creazione della PR fallisce ("head wasn't supplied"): portarlo prima a In Progress.
- **File esclusi da `.forceignore`** non devono stare nel diff della PR (il promote fallisce con "not found in zipped directory").

## Cosa riportare all'utente a ogni passo
- Numero del WI, branch, percorso del worktree, URL della PR.
- Esito di dry-run/deploy con numero di componenti (es. 7/7, 0 errori).
- Stato del registro (quanti componenti, quali) prima di proporre il promote.
- Cosa è stato scritto e dove; cosa **non** è stato fatto e perché.
