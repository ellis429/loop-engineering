"""The run store: one current state per repo and feature, history first (D3, D4)."""

from __future__ import annotations

import contextlib
import copy
import dataclasses
import errno
import fcntl
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

from loopctl import clock
from loopctl.next import derive

State = dict[str, Any]
Key = tuple[str, str]

SCHEMA_VERSION = 1


def home() -> Path:
    return Path(os.environ.get("LOOPCTL_HOME") or Path.home() / ".loopctl")


def run_dir(key: Key) -> Path:
    repo, feature = key
    return home() / "runs" / repo / feature


def objects_dir() -> Path:
    return home() / "objects"


def digest(value: Any) -> str:
    """sha256 of the canonical JSON of `value`."""
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


def _dump(value: Any) -> bytes:
    """The file form: sorted keys, indented."""
    text = json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False)
    return (text + "\n").encode()


class RunNotFound(Exception):
    """No run directory for this repo and feature."""


class RunExists(Exception):
    """`create` found the run directory already in place."""


class RevisionConflict(Exception):
    """The state is no longer at the expected revision; re-read and redo."""


class UntrustedState(Exception):
    """The run cannot be trusted: `reason`, and the files that exist."""

    def __init__(self, reason: str, files: list[str]) -> None:
        super().__init__(reason)
        self.reason = reason
        self.files = files


class ObjectError(Exception):
    """A stored object is missing or does not match its digest: `reason`."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class IOFailure(OSError):
    """An OSError of the store: the operation `op` that failed, and whether
    the change was already committed when it failed (D2, D4)."""

    def __init__(self, op: str, error: OSError, *, committed: bool) -> None:
        super().__init__(error.errno, error.strerror)
        self.op = op
        self.committed = committed


@dataclasses.dataclass
class _Progress:
    """The operation a store call is in, and whether its change is committed:
    after the history link of `commit`, or after the rename of `create`."""

    op: str
    committed: bool = False


@contextlib.contextmanager
def _reporting(op: str) -> Iterator[_Progress]:
    """Raise an OSError of the block as an IOFailure at its progress."""
    progress = _Progress(op)
    try:
        yield progress
    except IOFailure:
        raise
    except OSError as error:
        raise IOFailure(progress.op, error, committed=progress.committed) from error


def load(key: Key) -> tuple[int, State]:
    """The current (revision, state) of a run; reading never writes (D4)."""
    with _reporting("read_state"):
        return _load(key)


def _load(key: Key) -> tuple[int, State]:
    path = run_dir(key)
    if not path.is_dir():
        raise RunNotFound()

    def untrusted(reason: str) -> UntrustedState:
        return UntrustedState(reason, _files(path))

    try:
        state = json.loads((path / "feature.json").read_bytes())
    except FileNotFoundError:
        raise untrusted("state_missing") from None
    except ValueError:
        raise untrusted("state_corrupt") from None
    if not isinstance(state, dict):
        raise untrusted("state_corrupt")
    if state.get("schema_version") != SCHEMA_VERSION:
        raise untrusted(f"unknown_schema:{json.dumps(state.get('schema_version'))}")
    revision = state.get("revision")
    if type(revision) is not int or revision < 1:
        raise untrusted("state_corrupt")
    history = path / "history"
    try:
        current = _intact_record((history / f"{revision}.json").read_bytes())
    except FileNotFoundError:
        raise untrusted(f"history_missing:{revision}") from None
    # Only a state the store itself recorded is trusted; any other edit of
    # feature.json or of its record is a manual edit, never a decision.
    if current is None or current["state_digest"] != digest(state):
        raise untrusted("manual_edit")
    # Committed but not yet in feature.json: the next history record that
    # follows this state is the current one. Reading never writes.
    try:
        ahead = _intact_record((history / f"{revision + 1}.json").read_bytes())
    except FileNotFoundError:
        return revision, state
    if ahead is None or ahead["state"].get("revision") != revision + 1:
        raise untrusted("manual_edit")
    if ahead.get("prev_digest") != digest(state):
        raise untrusted(f"history_fork:{revision + 1}")
    return revision + 1, ahead["state"]


def _intact_record(data: bytes) -> State | None:
    """The history record in `data` if its state matches its state_digest."""
    try:
        record = json.loads(data)
    except ValueError:
        return None
    if (
        isinstance(record, dict)
        and isinstance(record.get("state"), dict)
        and record.get("state_digest") == digest(record["state"])
    ):
        return record
    return None


def create(key: Key, transition_id: str, payload: Any, state: State) -> int:
    """Build the run beside its place, then rename it there; revision 1.

    The rename is the commit point: an OSError before it leaves no run, one
    after it leaves revision 1 in place."""
    path = run_dir(key)
    payload_digest = digest(payload)
    state = derive(
        {
            **state,
            "schema_version": SCHEMA_VERSION,
            "revision": 1,
            "transitions": {
                transition_id: {"revision": 1, "payload_digest": payload_digest}
            },
        }
    )
    record = {
        "revision": 1,
        "transition_id": transition_id,
        "payload_digest": payload_digest,
        "prev_digest": None,
        "state_digest": digest(state),
        "committed_at": clock.now(),
        "state": state,
    }
    with _reporting("write_run") as progress:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp(dir=path.parent, prefix=f".tmp-{path.name}-"))
        try:
            (tmp / "history").mkdir()
            _write_new(tmp / "history" / "1.json", _dump(record))
            _write_new(tmp / "feature.json", _dump(state))
            _write_new(tmp / "lock", b"")
            _sync_dir(tmp / "history")
            _sync_dir(tmp)
            # rename would replace an empty directory; a non-empty one fails it.
            if path.exists():
                raise RunExists()
            progress.op = "rename_run"
            try:
                os.rename(tmp, path)
            except OSError as error:
                if error.errno in (errno.EEXIST, errno.ENOTEMPTY):
                    raise RunExists() from error
                raise
        except BaseException:
            shutil.rmtree(tmp, ignore_errors=True)
            raise
        progress.op, progress.committed = "sync_run_parent", True
        _sync_dir(path.parent)
    return 1


def commit(
    key: Key,
    expected_revision: int,
    transition_id: str,
    payload: Any,
    mutate: Callable[[State], State],
    *,
    authorize: Callable[[State], None],
) -> int:
    """Commit `mutate` of the current state as the next revision (D4).

    Every step before the history link writes nothing when it fails;
    `authorize` comes before any other check. Returns the new revision, or
    the current one when `mutate` changes nothing. An OSError is raised as
    an IOFailure that says whether the history link was already made."""
    with _reporting("read_state") as progress:
        # A missing or untrusted run fails here, before the lock file is touched.
        load(key)
        progress.op = "lock"
        with _locked(run_dir(key)):
            return _commit(
                key, expected_revision, transition_id, payload, mutate, authorize,
                progress,
            )


@contextlib.contextmanager
def _locked(path: Path) -> Iterator[None]:
    fd = os.open(path / "lock", os.O_RDWR | os.O_CREAT, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _commit(
    key: Key,
    expected_revision: int,
    transition_id: str,
    payload: Any,
    mutate: Callable[[State], State],
    authorize: Callable[[State], None],
    progress: _Progress,
) -> int:
    path = run_dir(key)
    revision, state = load(key)  # step 1
    authorize(state)  # step 2
    if revision != expected_revision:  # step 5
        raise RevisionConflict()
    new = derive(mutate(copy.deepcopy(state)))  # step 6
    if new == state:
        return revision
    for ref in _references(new):  # step 7
        try:
            get_object(ref)
        except ObjectError as error:
            raise UntrustedState(error.reason, _files(path)) from None
    # step 8
    payload_digest = digest(payload)
    new["revision"] = revision + 1
    new["transitions"] = {
        **state["transitions"],
        transition_id: {"revision": revision + 1, "payload_digest": payload_digest},
    }
    record = {
        "revision": revision + 1,
        "transition_id": transition_id,
        "payload_digest": payload_digest,
        "prev_digest": digest(state),
        "state_digest": digest(new),
        "committed_at": clock.now(),
        "state": new,
    }
    _link_history(path, revision + 1, record, progress)
    _replace_state(path, new, progress)
    return revision + 1


def put_object(data: bytes) -> str:
    """Store `data` under its sha256, write-once; returns `sha256:<hex>`."""
    hexdigest = hashlib.sha256(data).hexdigest()
    path = objects_dir() / hexdigest
    with _reporting("write_object"):
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = _write_tmp(path.parent, data)
            try:
                os.link(tmp, path)
            except FileExistsError:
                pass
            finally:
                os.unlink(tmp)
            _sync_dir(path.parent)
    return "sha256:" + hexdigest


OBJECT_REF = re.compile(r"sha256:([0-9a-f]{64})")


def get_object(ref: str) -> bytes:
    """The bytes stored as `ref`, checked against it."""
    match = OBJECT_REF.fullmatch(ref) if isinstance(ref, str) else None
    if match is None:
        raise ObjectError(f"object_missing:{ref}")
    with _reporting("read_object"):
        try:
            data = (objects_dir() / match[1]).read_bytes()
        except FileNotFoundError:
            raise ObjectError(f"object_missing:{ref}") from None
    if hashlib.sha256(data).hexdigest() != match[1]:
        raise ObjectError(f"object_corrupt:{ref}")
    return data


def _references(value: Any) -> Iterator[Any]:
    """Every `{"$object": d}` reference in a state, as d."""
    if isinstance(value, dict):
        if "$object" in value:
            yield value["$object"]
        for item in value.values():
            yield from _references(item)
    elif isinstance(value, list):
        for item in value:
            yield from _references(item)


def _files(path: Path) -> list[str]:
    """The files under a run directory, as sorted relative paths."""
    return sorted(
        item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()
    )


def _sync_file(fd: int) -> None:
    os.fsync(fd)
    if sys.platform == "darwin":
        fcntl.fcntl(fd, fcntl.F_FULLFSYNC)


def _sync_dir(path: Path) -> None:
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _write_synced(fd: int, data: bytes) -> None:
    with os.fdopen(fd, "wb") as file:
        file.write(data)
        file.flush()
        _sync_file(file.fileno())


def _write_new(path: Path, data: bytes) -> None:
    _write_synced(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), data)


def _write_tmp(directory: Path, data: bytes) -> Path:
    """A synced temporary file in `directory`; removed again if that fails."""
    fd, name = tempfile.mkstemp(dir=directory, prefix=".tmp-")
    try:
        _write_synced(fd, data)
    except BaseException:
        os.unlink(name)
        raise
    return Path(name)


def _link_history(
    path: Path, revision: int, record: State, progress: _Progress
) -> None:
    """Write-once: os.link fails if this revision is already committed.

    The link is the commit point; a failure after it leaves the revision
    committed."""
    progress.op = "write_history"
    tmp = _write_tmp(path, _dump(record))
    progress.op = "link_history"
    try:
        os.link(tmp, path / "history" / f"{revision}.json")
    except BaseException:
        os.unlink(tmp)
        raise
    progress.op, progress.committed = "sync_history", True
    os.unlink(tmp)
    _sync_dir(path / "history")


def _replace_state(path: Path, state: State, progress: _Progress) -> None:
    progress.op = "write_state"
    tmp = _write_tmp(path, _dump(state))
    progress.op = "replace_state"
    try:
        os.replace(tmp, path / "feature.json")
    except BaseException:
        os.unlink(tmp)
        raise
    progress.op = "sync_state"
    _sync_dir(path)
