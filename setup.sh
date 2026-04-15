#!/bin/bash
# setup.sh — Aggiunge sf-claude-skills come submodule al progetto corrente
# Esegui dalla root del progetto Salesforce:
#   bash <(curl -s https://raw.githubusercontent.com/mao32/sf-claude-skills/main/setup.sh)
# oppure, se hai già clonato il repo:
#   bash .claude/sf-shared/setup.sh

set -e

REPO_URL="https://github.com/mao32/sf-claude-skills.git"
SUBMODULE_PATH=".claude/sf-shared"

echo "→ Creo .claude/ se non esiste..."
mkdir -p .claude

echo "→ Aggiungo submodule $REPO_URL in $SUBMODULE_PATH..."
git submodule add "$REPO_URL" "$SUBMODULE_PATH"

echo "→ Creo symlink .claude/skills e .claude/commands..."
ln -sf sf-shared/skills  .claude/skills
ln -sf sf-shared/commands .claude/commands

echo "→ Committo..."
git add .gitmodules .claude/
git commit -m "Add sf-claude-skills submodule (skills + commands)"

echo ""
echo "✓ Setup completato."
echo "  .claude/skills   → $SUBMODULE_PATH/skills"
echo "  .claude/commands → $SUBMODULE_PATH/commands"
echo ""
echo "Per aggiornare le skill in futuro:"
echo "  git submodule update --remote .claude/sf-shared"
echo "  git add .claude/sf-shared && git commit -m 'Update sf-claude-skills'"
