#!/usr/bin/env bash
# Install the skills this repository uses into the agents' skill folders.
#
#   ./setup.sh            link every skill under skills/ into ~/.claude/skills, ~/.agents/skills
#                         and ~/.codex/skills; check the OpenSpec CLI
#   ./setup.sh --force    also re-point links that currently point somewhere else
#   ./setup.sh --update   re-fetch skills/third-party at the commits in skills/third-party/SOURCES.md
#   ./setup.sh --project <repo>
#                         copy the workflow's skills into <repo>/.claude/skills and <repo>/.agents/skills,
#                         so sessions started in that repository have them without any install
#
# Existing real folders are never touched. Superpowers skills are not linked into ~/.claude/skills
# when the Superpowers Claude Code plugin is enabled, to avoid duplicates.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
OPENSPEC_VERSION="1.13.1"
TARGETS=("$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.codex/skills")
FORCE=0
PROJECT=""
# Skills a product repository needs to run the workflow; copied, not linked, by --project.
PROJECT_SKILLS=(project-lead feature-to-spec research-codebase grilling domain-modeling grill-with-docs
                test-driven-development)
MANIFEST=".loop-engineering-skills"

# A vendored folder moved aside during --update is put back if the new one did not arrive,
# whatever interrupted the swap; the staging directory is removed afterwards.
restore_and_clean() {
  local old name
  for old in "$TMP"/old-*; do
    [ -e "$old" ] || continue
    name="${old##*/old-}"
    [ -e "$ROOT/skills/third-party/$name" ] || mv "$old" "$ROOT/skills/third-party/$name"
  done
  rm -rf "$TMP"
}

update_third_party() {
  local sources="$ROOT/skills/third-party/SOURCES.md" tp
  tp="$(cd "$ROOT/skills/third-party" && pwd -P)"
  if [ "$tp" != "$(cd "$ROOT" && pwd -P)/skills/third-party" ]; then
    echo "refusing to update: skills/third-party resolves outside the repository ($tp)" >&2; exit 1
  fi
  # Staging lives inside the repository so the final swap is a rename on the same filesystem.
  TMP="$(mktemp -d "$ROOT/.setup-update.XXXXXX")"
  trap restore_and_clean EXIT
  # Rows: | name | repo | upstream path | local path | commit | license |
  grep -E '^\| (mattpocock|superpowers) \|' "$sources" | while IFS='|' read -r _ name repo upath lpath commit _; do
    name="$(echo "$name" | xargs)"; repo="$(echo "$repo" | xargs)"; upath="$(echo "$upath" | xargs)"
    lpath="$(echo "$lpath" | xargs)"; commit="$(echo "$commit" | xargs)"
    if ! [[ "$name" =~ ^[A-Za-z0-9_-]+$ ]] || [ "$lpath" != "skills/third-party/$name" ]; then
      echo "refusing to replace '$lpath': the local path of source '$name' must be skills/third-party/$name" >&2; exit 1
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
  # Claude Code reports the effective state; run outside any project so only user scope applies,
  # which is the scope of the ~/.claude/skills links this script manages.
  command -v claude >/dev/null 2>&1 || return 1
  (cd "$HOME" && claude plugin list --json 2>/dev/null) | python3 -c '
import json, sys
plugins = json.load(sys.stdin)
sys.exit(0 if any(p["id"].startswith("superpowers@") and p.get("enabled") for p in plugins) else 1)' 2>/dev/null
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

# Copies each skill folder into the product repo. A folder that exists but is not listed in the
# manifest this script wrote was put there by someone else and is left alone unless --force.
install_project() {
  local repo dest name src commit copied
  repo="$(cd "$PROJECT" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "not a git repository: $PROJECT" >&2; exit 2; }
  commit="$(git -C "$ROOT" rev-parse --short HEAD)"
  if [ -n "$(git -C "$ROOT" status --porcelain -- skills)" ]; then
    commit="$commit+uncommitted"; echo "WARN     skills/ has uncommitted changes; recorded as $commit"
  fi
  for dest in "$repo/.claude/skills" "$repo/.agents/skills"; do
    mkdir -p "$dest"
    copied=()
    for name in "${PROJECT_SKILLS[@]}"; do
      src="$(find "$ROOT/skills" -type f -name SKILL.md -path "*/$name/SKILL.md" -exec dirname {} \; | head -1)"
      [ -n "$src" ] || { echo "missing skill in this repository: $name" >&2; exit 1; }
      if [ -e "$dest/$name" ] && ! grep -qx "$name" "$dest/$MANIFEST" 2>/dev/null && [ "$FORCE" -eq 0 ]; then
        echo "SKIP     $dest/$name (not installed by this script; use --force)"; continue
      fi
      rm -rf "${dest:?}/$name"
      cp -R "$src" "$dest/$name"
      copied+=("$name")
      echo "copied   $dest/$name"
    done
    # Only folders this script copied are listed, so a skipped folder stays protected next time.
    { echo "# Copied by loop-engineering setup.sh --project from commit $commit. Edit in loop-engineering, then re-run."
      [ ${#copied[@]} -eq 0 ] || printf '%s\n' "${copied[@]}"; } > "$dest/$MANIFEST"
  done
}

while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --update) update_third_party; exit 0 ;;
    --project) [ $# -ge 2 ] || { echo "--project needs a repository path" >&2; exit 2; }; PROJECT="$2"; shift ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if [ -n "$PROJECT" ]; then
  install_project
  exit 0
fi

install_skills
check_openspec
