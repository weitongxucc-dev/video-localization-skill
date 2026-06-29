#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET="${1:-${HOME}/.codex/skills/video-localization-skill}"

mkdir -p "$(dirname "$TARGET")"
rm -rf "$TARGET"
cp -R "$REPO_DIR" "$TARGET"

echo "Installed video-localization-skill to: $TARGET"
echo "For tools without native skill support, reference:"
echo "  $TARGET/SKILL.md"
