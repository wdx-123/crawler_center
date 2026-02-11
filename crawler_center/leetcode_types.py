from __future__ import annotations

from dataclasses import dataclass
import time


@dataclass(frozen=True)
class ACSubmission:
    title: str
    slug: str
    timestamp: int


def format_local_time(ts: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
