"""Network and cache helpers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json
import os
import tempfile

from .constants import DATASETS, DEFAULT_TIMEOUT, USER_AGENT
from .paths import dataset_cache_file, dataset_state_file


@dataclass(frozen=True)
class SourceAttempt:
    url: str
    ok: bool
    error: str | None = None


@dataclass(frozen=True)
class FetchResult:
    kind: str
    text: str
    raw: bytes
    source_url: str
    source_kind: str  # main | fallback | cache
    fetched_at: str
    attempts: tuple[SourceAttempt, ...] = ()


class FetchError(RuntimeError):
    """Raised when network and cache sources all fail."""


def decode_utf8_sig(raw: bytes) -> str:
    """Decode UTF-8 data, accepting and stripping a BOM if present."""
    return raw.decode("utf-8-sig")


def atomic_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    os.replace(tmp_path, path)


def write_state(path: Path, state: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(state, ensure_ascii=False, indent=2).encode("utf-8")
    atomic_write_bytes(path, data)


def read_state(path: Path) -> dict[str, object]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}


def fetch_url(url: str, timeout: float = DEFAULT_TIMEOUT) -> bytes:
    req = Request(url=url, headers={"User-Agent": USER_AGENT}, method="GET")
    with urlopen(req, timeout=timeout) as resp:
        return resp.read()


def load_cache(kind: str, attempts: tuple[SourceAttempt, ...] = ()) -> FetchResult:
    cache_file = dataset_cache_file(kind)
    state_file = dataset_state_file(kind)

    try:
        raw = cache_file.read_bytes()
        text = decode_utf8_sig(raw)
    except FileNotFoundError as exc:
        raise FetchError(f"No network source available and no cache exists for {kind}.") from exc
    except (OSError, UnicodeDecodeError) as exc:
        raise FetchError(f"Cache exists for {kind}, but cannot be read or decoded.") from exc

    state = read_state(state_file)
    return FetchResult(
        kind=kind,
        text=text,
        raw=raw,
        source_url=str(state.get("source_url", cache_file)),
        source_kind="cache",
        fetched_at=str(state.get("fetched_at", "")),
        attempts=attempts,
    )


def save_cache(kind: str, raw: bytes, source_url: str, source_kind: str) -> str:
    cache_file = dataset_cache_file(kind)
    state_file = dataset_state_file(kind)
    fetched_at = datetime.now(timezone.utc).isoformat()
    atomic_write_bytes(cache_file, raw)
    write_state(
        state_file,
        {
            "kind": kind,
            "source_url": source_url,
            "source_kind": source_kind,
            "fetched_at": fetched_at,
        },
    )
    return fetched_at


def fetch_dataset(kind: str, *, offline: bool = False, timeout: float = DEFAULT_TIMEOUT) -> FetchResult:
    if kind not in DATASETS:
        raise ValueError(f"Unknown dataset: {kind}")

    if offline:
        return load_cache(kind)

    attempts: list[SourceAttempt] = []
    urls = list(DATASETS[kind]["urls"])  # type: ignore[index]
    for idx, url in enumerate(urls):
        source_kind = "main" if idx == 0 else "fallback"
        try:
            raw = fetch_url(str(url), timeout=timeout)
            text = decode_utf8_sig(raw)
            fetched_at = save_cache(kind, raw, str(url), source_kind)
            attempts.append(SourceAttempt(url=str(url), ok=True))
            return FetchResult(
                kind=kind,
                text=text,
                raw=raw,
                source_url=str(url),
                source_kind=source_kind,
                fetched_at=fetched_at,
                attempts=tuple(attempts),
            )
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError) as exc:
            attempts.append(SourceAttempt(url=str(url), ok=False, error=f"{type(exc).__name__}: {exc}"))

    return load_cache(kind, attempts=tuple(attempts))


def source_urls(kind: str) -> list[str]:
    if kind not in DATASETS:
        raise ValueError(f"Unknown dataset: {kind}")
    return [str(url) for url in DATASETS[kind]["urls"]]  # type: ignore[index]
