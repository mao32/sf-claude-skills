#!/bin/bash
# setup.sh — Aggiunge sf-claude-skills come submodule al progetto corrente
# Esegui dalla root del progetto Salesforce:
#   bash <(curl -s https://raw.githubusercontent.com/mao32/sf-claude-skills/main/setup.sh)

set -e

REPO_URL="https://github.com/mao32/sf-claude-skills.git"
SUBMODULE_PATH=".claude/sf-shared"
GIT_MODULE_DIR=".git/modules/$SUBMODULE_PATH"

echo "→ Creo .claude/ se non esiste..."
mkdir -p .claude

# Controlla se il submodule è già registrato in .gitmodules
if git config --file .gitmodules --get "submodule.$SUBMODULE_PATH.url" > /dev/null 2>&1; then
  echo "→ Submodule già registrato — aggiorno con git submodule update --init --remote..."
  git submodule update --init --remote "$SUBMODULE_PATH"
elif [ -d "$GIT_MODULE_DIR" ]; then
  # La directory del modulo esiste ma non è registrata in .gitmodules (tentativo precedente parziale)
  echo "→ Trovata directory residua in $GIT_MODULE_DIR — aggiungo con --force..."
  git submodule add --force "$REPO_URL" "$SUBMODULE_PATH"
else
  echo "→ Aggiungo submodule $REPO_URL in $SUBMODULE_PATH..."
  git submodule add "$REPO_URL" "$SUBMODULE_PATH"
fi

echo "→ Creo symlink .claude/skills e .claude/commands..."
ln -sf sf-shared/skills  .claude/skills
ln -sf sf-shared/commands .claude/commands

echo "→ Committo..."
git add .gitmodules .claude/
git commit -m "Add sf-claude-skills submodule (skills + commands)" 2>/dev/null \
  || git commit -m "Update sf-claude-skills submodule" 2>/dev/null \
  || echo "  (nessuna modifica da committare — già aggiornato)"

echo ""
echo "✓ Setup completato."
echo "  .claude/skills   → $SUBMODULE_PATH/skills"
echo "  .claude/commands → $SUBMODULE_PATH/commands"
echo ""
echo "Per aggiornare le skill in futuro:"
echo "  git submodule update --remote .claude/sf-shared"
echo "  git add .claude/sf-shared && git commit -m 'Update sf-claude-skills'"
