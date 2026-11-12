#!/usr/bin/env python3
"""Small CLI around the monday.com GraphQL API for a support-ticket board.

Board-agnostic: column titles, labels and group names are always passed in by the caller
(they come from the project configuration), nothing board-specific is hard-coded.

Usage (run with `python3 -I`):
  monday_ticket.py get  <item_id>
        item + updates + board schema (column titles, allowed labels, groups) as JSON
  monday_ticket.py set  <item_id> "Column title=Value" ...
        status/dropdown/people/date/checkbox/text columns, addressed by TITLE;
        people value = `me` or comma-separated monday user ids; status value = label text
  monday_ticket.py move <item_id> "<group title or unique part of it>"
  monday_ticket.py list <board_id> [options]
        open tickets, sorted by priority then age. Options:
          --where "Column=Value"        keep only items whose column text equals Value (repeatable)
          --unassigned "Column"         keep only items whose people column is empty
          --exclude-groups "a,b"        skip groups whose title contains any of these (case-insensitive)
          --priority "Column=L1,L2,.."  sort by this column, labels in priority order
          --show "Col1,Col2,.."         extra columns to print
          --json                        machine-readable output
  monday_ticket.py me
        id/name of the token owner

Token: $MONDAY_TOKEN, else MONDAY_TOKEN= in the .env of the current repo
(main checkout root, so it also works from git worktrees), else --env-file <path>.
"""
import json
import os
import subprocess
import sys

API = "https://api.monday.com/v2"


def _token(argv):
    if "--env-file" in argv:
        i = argv.index("--env-file")
        paths = [argv[i + 1]]
        del argv[i:i + 2]
    else:
        # .env in cwd or any parent, then in the main checkout of the repo (worktrees) and its parents
        starts = [os.getcwd()]
        try:
            common = subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
                                    capture_output=True, text=True, check=True).stdout.strip()
            starts.append(os.path.dirname(common))
        except Exception:
            pass
        paths = []
        for d in starts:
            while True:
                paths.append(os.path.join(d, ".env"))
                parent = os.path.dirname(d)
                if parent == d:
                    break
                d = parent
    if os.environ.get("MONDAY_TOKEN"):
        return os.environ["MONDAY_TOKEN"]
    for p in paths:
        if os.path.isfile(p):
            for line in open(p, encoding="utf-8"):
                line = line.strip()
                if line.startswith("MONDAY_TOKEN="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    sys.exit("MONDAY_TOKEN not found (env var, repo .env or --env-file)")


def gql(token, query, variables=None):
    # curl instead of urllib: python builds (e.g. Homebrew) often miss the CA bundle.
    body = json.dumps({"query": query, "variables": variables or {}})
    r = subprocess.run(["curl", "-sS", "--fail-with-body", API, "-H", f"Authorization: {token}",
                        "-H", "Content-Type: application/json", "-H", "API-Version: 2024-10",
                        "--data-binary", "@-"], input=body, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"monday API call failed: {r.stderr.strip()} {r.stdout.strip()}")
    d = json.loads(r.stdout)
    if d.get("errors") or d.get("error_message"):
        sys.exit(json.dumps(d.get("errors") or d, indent=2))
    return d["data"]


def board_of(token, item_id):
    d = gql(token, "query($i:[ID!]){ items(ids:$i){ board{ id name columns{ id title type settings_str } groups{ id title } } } }",
            {"i": [item_id]})
    if not d["items"]:
        sys.exit(f"item {item_id} not found")
    return d["items"][0]["board"]


def _labels(col):
    s = json.loads(col["settings_str"] or "{}").get("labels")
    if isinstance(s, dict):
        return [v for v in s.values() if v]
    if isinstance(s, list):
        return [x.get("name") for x in s if x.get("name")]
    return None


def cmd_get(token, item_id):
    q = """query($i:[ID!]){ items(ids:$i){ id name created_at url group{ title }
      column_values{ id type text column{ title } }
      updates(limit:30){ id created_at creator{ name } text_body assets{ name public_url }
        replies{ creator{ name } created_at text_body } }
      assets{ name public_url } } }"""
    it = gql(token, q, {"i": [item_id]})["items"][0]
    b = board_of(token, item_id)
    schema = []
    for c in b["columns"]:
        labels = _labels(c)
        schema.append({"title": c["title"], "id": c["id"], "type": c["type"], **({"labels": labels} if labels else {})})
    out = {
        "item": {"id": it["id"], "name": it["name"], "url": it["url"], "group": it["group"]["title"],
                 "created_at": it["created_at"],
                 "columns": {c["column"]["title"]: c["text"] for c in it["column_values"]},
                 "assets": it["assets"]},
        "updates": [{"at": u["created_at"], "by": (u["creator"] or {}).get("name"), "text": u["text_body"],
                     "assets": u["assets"], "replies": u["replies"]} for u in reversed(it["updates"])],
        "board": {"id": b["id"], "name": b["name"], "groups": [g["title"] for g in b["groups"]], "columns": schema},
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))


def cmd_set(token, item_id, pairs):
    b = board_of(token, item_id)
    by_title = {c["title"].strip().lower(): c for c in b["columns"]}
    vals = {}
    for p in pairs:
        if "=" not in p:
            sys.exit(f"bad pair '{p}', expected 'Column title=Value'")
        title, value = (x.strip() for x in p.split("=", 1))
        col = by_title.get(title.lower())
        if not col:
            sys.exit(f"column '{title}' not on board. Columns: {[c['title'] for c in b['columns']]}")
        t = col["type"]
        if t in ("status", "color"):
            allowed = _labels(col) or []
            if value not in allowed:
                sys.exit(f"'{value}' not a label of '{col['title']}': {allowed}")
            vals[col["id"]] = {"label": value}
        elif t == "dropdown":
            vals[col["id"]] = {"labels": [v.strip() for v in value.split(",")]}
        elif t == "people":
            ids = [gql(token, "{ me { id } }")["me"]["id"] if v.strip() == "me" else v.strip() for v in value.split(",")]
            vals[col["id"]] = {"personsAndTeams": [{"id": int(i), "kind": "person"} for i in ids]}
        elif t == "date":
            vals[col["id"]] = {"date": value}
        elif t == "checkbox":
            vals[col["id"]] = {"checked": "true"} if value.lower() in ("true", "1", "yes") else None
        elif t == "long_text":
            vals[col["id"]] = {"text": value}
        else:
            vals[col["id"]] = value
    gql(token, "mutation($b:ID!,$i:ID!,$v:JSON!){ change_multiple_column_values(board_id:$b, item_id:$i, column_values:$v){ id } }",
        {"b": b["id"], "i": item_id, "v": json.dumps(vals)})
    print(f"updated {len(vals)} column(s) on {item_id}")


def cmd_move(token, item_id, group_title):
    b = board_of(token, item_id)
    key = group_title.strip().lower()
    g = [x for x in b["groups"] if x["title"].strip().lower() == key] or \
        [x for x in b["groups"] if key in x["title"].lower()]
    if len(g) != 1:
        sys.exit(f"group '{group_title}' ambiguous/not found: {[x['title'] for x in b['groups']]}")
    gql(token, "mutation($i:ID!,$g:String!){ move_item_to_group(item_id:$i, group_id:$g){ id } }",
        {"i": item_id, "g": g[0]["id"]})
    print(f"moved {item_id} to '{g[0]['title']}'")


def cmd_list(token, board_id, where, unassigned, exclude_groups, priority, show, as_json):
    b = gql(token, "query($b:[ID!]){ boards(ids:$b){ groups{ id title } } }", {"b": [board_id]})["boards"][0]
    groups = [g for g in b["groups"] if not any(x in g["title"].lower() for x in exclude_groups)]
    prio_col, prio_order = priority if priority else (None, [])
    rows = []
    q = """query($b:[ID!],$g:[String],$c:String){ boards(ids:$b){ groups(ids:$g){ title
             items_page(limit:200, cursor:$c){ cursor items{ id name created_at
               column_values{ text column{ title } } } } } } }"""
    for g in groups:
        cursor = None
        while True:
            grp = gql(token, q, {"b": [board_id], "g": [g["id"]], "c": cursor})["boards"][0]["groups"][0]
            page = grp["items_page"]
            for it in page["items"]:
                cv = {c["column"]["title"]: (c["text"] or "") for c in it["column_values"]}
                if any(cv.get(col, "") != val for col, val in where):
                    continue
                if unassigned and cv.get(unassigned):
                    continue
                rows.append({"id": it["id"], "name": it["name"], "group": grp["title"],
                             "created": it["created_at"][:16].replace("T", " "),
                             "priority": cv.get(prio_col, "") if prio_col else "",
                             **{k: cv.get(k, "") for k in show}})
            cursor = page["cursor"]
            if not cursor:
                break
    rank = {lab: i for i, lab in enumerate(prio_order)}
    rows.sort(key=lambda r: (rank.get(r["priority"], len(rank)), r["created"]))
    if as_json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return
    if not rows:
        print("no items match")
        return
    print(f"{len(rows)} item(s)\n")
    for r in rows:
        extra = " | ".join(f"{k}: {r[k] or '-'}" for k in show)
        print(f"- {r['id']} | {r['priority'] or '-'} | {r['group']} | created {r['created']} UTC"
              f"{' | ' + extra if extra else ''}\n    {r['name']}")


def _opt_all(opts, name):
    return [opts[i + 1] for i, o in enumerate(opts) if o == name and i + 1 < len(opts)]


def main():
    argv = sys.argv[1:]
    token = _token(argv)
    if not argv:
        sys.exit(__doc__)
    cmd = argv[0]
    if cmd == "get" and len(argv) == 2:
        cmd_get(token, argv[1])
    elif cmd == "set" and len(argv) >= 3:
        cmd_set(token, argv[1], argv[2:])
    elif cmd == "move" and len(argv) == 3:
        cmd_move(token, argv[1], argv[2])
    elif cmd == "list" and len(argv) >= 2:
        o = argv[2:]
        where = [tuple(x.strip() for x in w.split("=", 1)) for w in _opt_all(o, "--where")]
        unassigned = (_opt_all(o, "--unassigned") or [None])[0]
        excl = [x.strip().lower() for e in _opt_all(o, "--exclude-groups") for x in e.split(",") if x.strip()]
        pr = (_opt_all(o, "--priority") or [None])[0]
        priority = None
        if pr:
            col, labels = pr.split("=", 1)
            priority = (col.strip(), [x.strip() for x in labels.split(",")])
        show = [x.strip() for s in _opt_all(o, "--show") for x in s.split(",") if x.strip()]
        cmd_list(token, argv[1], where, unassigned, excl, priority, show, "--json" in o)
    elif cmd == "me":
        print(json.dumps(gql(token, "{ me { id name email } }")["me"], ensure_ascii=False))
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
