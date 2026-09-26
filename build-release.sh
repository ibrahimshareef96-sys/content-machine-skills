#!/bin/zsh
# Build the release bundle: one ZIP per skill (folder at the ZIP root, as the Claude app
# expects) plus README and LICENSE, wrapped in dist/business-admin-skills.zip.
# Usage: ./build-release.sh
set -euo pipefail

ROOT="${0:A:h}"
SKILLS=(business-brain inbox-triage call-to-actions call-to-proposal)
OUT="$ROOT/dist"
STAGE="$OUT/business-admin-skills"

command -v zip >/dev/null || { echo "zip is not installed" >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$STAGE"

for s in $SKILLS; do
  [[ -f "$ROOT/$s/SKILL.md" ]] || { echo "missing $s/SKILL.md" >&2; exit 1; }
  head -1 "$ROOT/$s/SKILL.md" | grep -qx -- '---' || { echo "$s/SKILL.md has no frontmatter" >&2; exit 1; }
  grep -q "^name: $s\$" "$ROOT/$s/SKILL.md" || { echo "$s/SKILL.md name does not match its folder" >&2; exit 1; }
  [[ "$s" =~ '^[a-z0-9-]{1,64}$' ]] || { echo "$s: name must be 1-64 lowercase letters, digits or hyphens" >&2; exit 1; }
  desc=$(grep -m1 '^description: ' "$ROOT/$s/SKILL.md" | cut -c14-)
  (( ${#desc} > 0 && ${#desc} <= 1024 )) || { echo "$s: description must be 1-1024 characters" >&2; exit 1; }
  (cd "$ROOT" && zip -qrX "$STAGE/$s.zip" "$s" -x '*.DS_Store')
done

cp "$ROOT/README.md" "$ROOT/LICENSE" "$STAGE/"
(cd "$OUT" && zip -qrX business-admin-skills.zip business-admin-skills -x '*.DS_Store')
echo "built $OUT/business-admin-skills.zip"
unzip -l "$OUT/business-admin-skills.zip"
