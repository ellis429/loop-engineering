#!/usr/bin/env bash
# Install the skills this repository uses into the agents' skill folders.
#
#   ./setup.sh            link every skill under skills/ into ~/.claude/skills, ~/.agents/skills
#                         and ~/.codex/skills; check the OpenSpec CLI
#   ./setup.sh --force    also re-point links that currently point somewhere else
#   ./setup.sh --update   re-fetch skills/third-party at the commits in skills/third-party/SOURCES.md
#
# Existing real folders are never touched. Superpowers skills are not linked into ~/.claude/skills
# when the Superpowers Claude Code plugin is enabled, to avoid duplicates.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OPENSPEC_VERSION="1.13.1"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills")
FORCE=0

update_third_party() {
  local sources="$ROOT/skills/third-party/SOURCES.md" tp
  tp="$(cd "$ROOT/skills/third-party" && pwd -P)"
  if [ "$tp" != "$(cd "$ROOT" && pwd -P)/skills/third-party" ]; then
    echo "refusing to update: skills/third-party resolves outside the repository ($tp)" >&2; exit 1
  fi
  # Staging lives inside the repository so the final swap is a rename on the same filesystem.
  TMP="$(mktemp -d "$ROOT/.setup-update.XXXXXX")"
  trap 'rm -rf "$TMP"' EXIT
  # Rows: | name | repo | upstream path | local path | commit | license |
  grep -E '^\| (mattpocock|superpowers) \|' "$sources" | while IFS='|' read -r _ name repo upath lpath commit _; do
    name="$(echo "$name" | xargs)"; repo="$(echo "$repo" | xargs)"; upath="$(echo "$upath" | xargs)"
    lpath="$(echo "$lpath" | xargs)"; commit="$(echo "$commit" | xargs)"
    if ! [[ "$lpath" =~ ^skills/third-party/[A-Za-z0-9_-][A-Za-z0-9._-]*$ ]]; then
      echo "refusing to replace '$lpath': local path must be one folder directly under skills/third-party/" >&2; exit 1
    fi
    echo "update $name: $repo@${commit:0:12} $upath -> $lpath"
    git clone -q --filter=blob:none --no-checkout "https://github.com/$repo.git" "$TMP/$name"
    git -C "$TMP/$name" sparse-checkout set --no-cone "/$upath/" "/LICENSE"
    git -C "$TMP/$name" checkout -q "$commit"
    # Build the complete new folder first; the old one is replaced only after every copy succeeded.
    cp -R "$TMP/$name/$upath" "$TMP/new-$name"
    cp "$TMP/$name/LICENSE" "$TMP/new-$name/LICENSE"
    if [ -e "$ROOT/$lpath" ]; then mv "$ROOT/$lpath" "$TMP/old-$name"; fi
    mv "$TMP/new-$name" "$ROOT/$lpath"
  done
}

check_openspec() {
  if ! command -v openspec >/dev/null 2>&1; then
    echo "MISSING  openspec CLI; install with: npm i -g @fission-ai/openspec@$OPENSPEC_VERSION"
    return
  fi
  local v; v="$(openspec --version 2>/dev/null || true)"
  if [ "$v" = "$OPENSPEC_VERSION" ]; then echo "ok       openspec CLI $v"
  else echo "WARN     openspec CLI $v (this repo is tested with $OPENSPEC_VERSION)"; fi
}

superpowers_plugin_enabled() {
  # Enabled plugins are listed in the user settings as "superpowers@<marketplace>": true.
  grep -Eqs '"superpowers@[^"]+"[[:space:]]*:[[:space:]]*true' \
    "$HOME/.claude/settings.json" "$HOME/.claude/settings.local.json"
}

link_skill() {
  local dir="$1" target="$2" name link current
  name="$(basename "$dir")"; link="$target/$name"
  if [ -L "$link" ]; then
    current="$(readlink "$link")"
    if [ "$current" = "$dir" ]; then echo "ok       $link"; return; fi
    if [ "$FORCE" -eq 0 ]; then
      echo "SKIP     $link -> $current (points elsewhere; use --force)"; return
    fi
  elif [ -e "$link" ]; then
    echo "SKIP     $link (real folder, left alone)"; return
  fi
  ln -sfn "$dir" "$link"; echo "linked   $link"
}

install_skills() {
  local skip_sp_claude=0 dir target
  superpowers_plugin_enabled && skip_sp_claude=1
  for target in "${TARGETS[@]}"; do
    mkdir -p "$target"
    while IFS= read -r dir; do
      if [ "$skip_sp_claude" -eq 1 ] && [ "$target" = "$HOME/.claude/skills" ] \
         && [[ "$dir" == "$ROOT/skills/third-party/superpowers/"* ]]; then
        continue
      fi
      link_skill "$dir" "$target"
    done < <(find "$ROOT/skills" -name SKILL.md -exec dirname {} \; | sort)
  done
}

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    --update) update_third_party; exit 0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

install_skills
check_openspec
