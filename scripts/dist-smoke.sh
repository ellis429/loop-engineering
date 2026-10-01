#!/bin/sh
# Build the loopctl wheel, install it into a fresh venv and check, outside
# the checkout, that the installed package works (design D12):
#   help      loopctl --help exits 0 and prints "usage: loopctl"
#   envelope  loopctl status prints exactly one JSON line with the six
#             envelope keys
#   isolation the delivery package is not importable
# Prints "dist-smoke: ok" or "dist-smoke: FAIL: <check>" and exits 1.
set -eu

root=$(cd "$(dirname "$0")/.." && pwd)
work=$(mktemp -d "${TMPDIR:-/tmp}/dist-smoke.XXXXXX")
trap 'rm -rf "$work"' EXIT INT TERM

fail() {
    echo "dist-smoke: FAIL: $1"
    exit 1
}

uv build --quiet --wheel --out-dir "$work/dist" "$root" || fail build
uv venv --quiet --python 3.12 "$work/venv" || fail install
uv pip install --quiet --python "$work/venv/bin/python" "$work"/dist/*.whl ||
    fail install

cd "$work"
export LOOPCTL_HOME="$work/home"
python="$work/venv/bin/python"
loopctl="$work/venv/bin/loopctl"

# help
"$loopctl" --help >"$work/help.out" 2>&1 || fail help
grep -q "usage: loopctl" "$work/help.out" || fail help

# envelope: the exit code is the command's; only the output shape is checked.
"$loopctl" status --repo a/b --feature F-1 >"$work/envelope.out" 2>/dev/null || true
"$python" - "$work/envelope.out" <<'EOF' || fail envelope
import json, sys

text = open(sys.argv[1], encoding="utf-8").read()
lines = text.splitlines()
assert len(lines) == 1 and text.endswith("\n"), lines
envelope = json.loads(lines[0])
keys = ["ok", "revision", "result", "blocked", "next", "safety"]
assert isinstance(envelope, dict) and sorted(envelope) == sorted(keys), envelope
EOF

# isolation
if "$python" -c "import delivery" >/dev/null 2>&1; then
    fail isolation
fi

echo "dist-smoke: ok"
