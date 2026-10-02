"""The one clock of loopctl; tests replace `now` (D13)."""

from __future__ import annotations

import datetime


def now() -> str:
    """The current UTC time as ISO 8601."""
    return datetime.datetime.now(datetime.UTC).isoformat(timespec="seconds")
