#!/usr/bin/env bash
set -euo pipefail

SKILLS_DIR="skills"
ERRORS=0

echo "Validating skills..."
echo "===================="

echo ""
echo "Checking: repository root"
if [ ! -f "SKILL.md" ]; then
  echo "  ❌ Missing root SKILL.md"
  ERRORS=$((ERRORS + 1))
elif ! head -1 "SKILL.md" | grep -q "^---"; then
  echo "  ❌ Root SKILL.md missing YAML frontmatter (must start with ---)"
  ERRORS=$((ERRORS + 1))
elif ! grep -q "^name:" "SKILL.md"; then
  echo "  ❌ Root SKILL.md missing name in frontmatter"
  ERRORS=$((ERRORS + 1))
else
  echo "  ✅ Root SKILL.md present"
fi

if [ -f "$SKILLS_DIR/SKILL.md" ]; then
  echo "  ❌ Unexpected $SKILLS_DIR/SKILL.md; only skill subdirectories should contain SKILL.md files"
  ERRORS=$((ERRORS + 1))
fi

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name=$(basename "$skill_dir")
  skill_file="$skill_dir/SKILL.md"

  echo ""
  echo "Checking: $skill_name"

  # Check SKILL.md exists
  if [ ! -f "$skill_file" ]; then
    echo "  ❌ Missing SKILL.md"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check frontmatter exists
  if ! head -1 "$skill_file" | grep -q "^---"; then
    echo "  ❌ Missing YAML frontmatter (must start with ---)"
    ERRORS=$((ERRORS + 1))
    continue
  fi

  # Check name in frontmatter matches directory
  fm_name=$(grep "^name:" "$skill_file" | head -1 | sed 's/name: *//')
  if [ "$fm_name" != "$skill_name" ]; then
    echo "  ❌ Frontmatter name '$fm_name' doesn't match directory '$skill_name'"
    ERRORS=$((ERRORS + 1))
  fi

  # Check description exists and has trigger phrases
  if ! grep -q "^description:" "$skill_file"; then
    echo "  ❌ Missing description in frontmatter"
    ERRORS=$((ERRORS + 1))
  fi

  # Check description contains trigger phrases
  desc=$(grep "^description:" "$skill_file" | head -1)
  if ! echo "$desc" | grep -qi "when the user"; then
    echo "  ⚠️  Description should include 'When the user wants to...' trigger phrases"
  fi

  # Check line count
  lines=$(wc -l < "$skill_file" | tr -d ' ')
  if [ "$lines" -gt 500 ]; then
    echo "  ❌ Too long: $lines lines (max 500)"
    ERRORS=$((ERRORS + 1))
  else
    echo "  ✅ $lines lines"
  fi
done

echo ""
echo "===================="
if [ "$ERRORS" -eq 0 ]; then
  echo "✅ All skills valid!"
else
  echo "❌ $ERRORS error(s) found"
fi
exit "$ERRORS"
