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
PROJECT_SKILLS=(project-lead feature-to-spec spec-to-plan plan-to-code to-pr research-codebase
                grilling domain-modeling grill-with-docs brainstorming writing-plans test-driven-development
                subagent-driven-development using-git-worktrees requesting-code-review
                verification-before-completion finishing-a-development-branch)
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

# Fingerprint of a folder: every path with its permission string, symlink target and content, as a
# NUL-separated byte stream so names and targets with newlines are fingerprinted exactly. Non-zero when
# any entry cannot be read; the caller then discards the output.
tree_hash() {
  (cd "$1" || exit 1
   find . -print0 | LC_ALL=C sort -z | while IFS= read -r -d '' p; do
     mode="$(ls -ld "$p")" || exit 1
     printf '%s\0%s\0' "${mode%% *}" "$p"
     if [ -L "$p" ]; then readlink "$p" || exit 1; printf '\0'
     elif [ -f "$p" ]; then shasum < "$p" || exit 1
     fi
   done) | shasum | cut -d' ' -f1
}

# Unique scratch folders of the skill being swapped. On any exit, including an interrupt, the old copy is
# put back if the new one is not in place; if that fails, the backup is kept and its path reported.
STAGE=""
BACKUP=""
TARGET=""
MANIFEST_TMP=""
cleanup_project() {
  if [ -n "$BACKUP" ] && [ -e "$BACKUP/${TARGET##*/}" ] && [ ! -e "$TARGET" ]; then
    if ! mv "$BACKUP/${TARGET##*/}" "$TARGET"; then
      echo "could not restore $TARGET; the previous copy is kept at $BACKUP/${TARGET##*/}" >&2
      BACKUP=""
    fi
  fi
  [ -z "$STAGE" ] || rm -rf "$STAGE"
  [ -z "$BACKUP" ] || rm -rf "$BACKUP"
  [ -z "$MANIFEST_TMP" ] || rm -f "$MANIFEST_TMP"
  STAGE=""; BACKUP=""; TARGET=""; MANIFEST_TMP=""
}

# Rewrites the manifest of install_project's $dest atomically: the records read at the start of the run
# ($old) for folders not named in $2, then the lines in $1.
write_manifest() {
  MANIFEST_TMP="$(mktemp "$dest/.setup-manifest.XXXXXX")"
  { echo "# Written by loop-engineering setup.sh --project, last copy from commit $commit. Each line: a skill it copied and the fingerprints accepted as that copy (two only while it is being swapped). Edit skills in loop-engineering, then re-run."
    printf '%s\n' "$old" | awk -v c="$2" '!/^#/ && NF >= 2 && index(c, " " $1 " ") == 0'
    printf '%s' "$1"; } > "$MANIFEST_TMP"
  mv -f "$MANIFEST_TMP" "$dest/$MANIFEST"
  MANIFEST_TMP=""
}

# Copies each skill folder into the product repo. A folder is replaced only when the manifest this
# script wrote lists it with the same fingerprint, so a folder someone else put there or changed
# since is left alone unless --force. The old folder is moved aside and restored if the swap fails.
# The manifest keeps the record of every folder not replaced in this run, so a skipped folder is
# still known as this script's copy, changed since, on the next run. While a folder is swapped its
# record accepts the new fingerprint and, when the replaced folder was this script's unchanged copy,
# that copy's fingerprint, so a run that stops at any point leaves each folder matching its record.
install_project() {
  local repo dest name src commit recorded current entries rel hash copied old h prev
  repo="$(cd "$PROJECT" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)" \
    || { echo "not a git repository: $PROJECT" >&2; exit 2; }
  repo="$(cd "$repo" && pwd -P)"
  commit="$(git -C "$ROOT" rev-parse --short HEAD)"
  if [ -n "$(git -C "$ROOT" status --porcelain -- skills)" ]; then
    commit="$commit+uncommitted"; echo "WARN     skills/ has uncommitted changes; recorded as $commit"
  fi
  trap cleanup_project EXIT
  trap 'exit 129' HUP; trap 'exit 130' INT; trap 'exit 143' TERM
  for rel in .claude/skills .agents/skills; do
    dest="$repo/$rel"
    # Nothing is created, written or deleted through a symlink: checked before mkdir.
    if [ -L "$repo/${rel%%/*}" ] || [ -L "$dest" ] || [ -L "$dest/$MANIFEST" ]; then
      echo "refusing to write $dest: part of the path or its manifest is a symlink" >&2; exit 1
    fi
    if [ -e "$dest/$MANIFEST" ] && [ ! -f "$dest/$MANIFEST" ]; then
      echo "refusing to write $dest: $MANIFEST is not a regular file" >&2; exit 1
    fi
    mkdir -p "$dest"
    # Read once. A manifest that cannot be read stops the run before anything is written here, because
    # rewriting it would drop the records of the folders this run skips.
    old=""
    if [ -e "$dest/$MANIFEST" ]; then
      old="$(cat "$dest/$MANIFEST")" || { echo "refusing to write $dest: cannot read $MANIFEST" >&2; exit 1; }
    fi
    entries=""; copied=" "
    for name in "${PROJECT_SKILLS[@]}"; do
      src="$(find "$ROOT/skills" -type f -name SKILL.md -path "*/$name/SKILL.md" -exec dirname {} \; | head -1)"
      [ -n "$src" ] || { echo "missing skill in this repository: $name" >&2; exit 1; }
      if [ -L "$dest/$name" ]; then
        echo "SKIP     $dest/$name (a symlink; remove it to install a copy)"; continue
      fi
      recorded=""
      for h in $(printf '%s\n' "$old" | awk -v n="$name" '!/^#/ && $1 == n { for (i = 2; i <= NF; i++) print $i }'); do
        recorded="$recorded $h"
      done
      # prev: the folder's fingerprint when it is a copy this script made, kept on record during the swap.
      prev=""
      if [ -e "$dest/$name" ]; then
        # An unreadable fingerprint counts as no record: the folder is skipped, never replaced.
        if current="$(tree_hash "$dest/$name" 2>/dev/null)"; then
          case "$recorded " in *" $current "*) prev=" $current" ;; esac
        fi
        if [ -z "$prev" ] && [ "$FORCE" -eq 0 ]; then
          echo "SKIP     $dest/$name (not an unchanged copy from this script; use --force)"; continue
        fi
      fi
      TARGET="$dest/$name"
      STAGE="$(mktemp -d "$dest/.setup-stage.XXXXXX")"
      cp -R "$src" "$STAGE/$name"
      # Fingerprint the new copy before the old one is touched.
      if ! hash="$(tree_hash "$STAGE/$name")"; then
        echo "cannot fingerprint the new copy of $name; nothing was replaced" >&2; exit 1
      fi
      write_manifest "$entries$name $hash$prev
" "$copied$name "
      if [ -e "$TARGET" ]; then
        BACKUP="$(mktemp -d "$dest/.setup-old.XXXXXX")"
        mv "$TARGET" "$BACKUP/$name"
      fi
      if ! mv "$STAGE/$name" "$TARGET"; then
        echo "failed to install $TARGET" >&2; exit 1
      fi
      cleanup_project
      entries="$entries$name $hash
"
      copied="$copied$name "
      write_manifest "$entries" "$copied"
      echo "copied   $dest/$name"
    done
  done
}

while [ $# -gt 0 ]; do
  case "$1" in
    --force) FORCE=1 ;;
    --update) update_third_party; exit 0 ;;
    --project) [ $# -ge 2 ] && [ -n "$2" ] || { echo "--project needs a repository path" >&2; exit 2; }; PROJECT="$2"; shift ;;
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
