"""Filesystem paths for vojtamaur cache."""

from __future__ import annotations

import os
import platform
from pathlib import Path

CACHE_ENV = "VOJTAMAUR_CACHE_DIR"
TIMEOUT_ENV = "VOJTAMAUR_TIMEOUT"
OFFLINE_ENV = "VOJTAMAUR_OFFLINE"


def cache_dir() -> Path:
    """Return the cache directory for the current platform.

    A user can override this with VOJTAMAUR_CACHE_DIR.
    """
    override = os.getenv(CACHE_ENV)
    if override:
        return Path(override).expanduser()

    system = platform.system().lower()
    if system == "windows":
        base = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        if base:
            return Path(base) / "vojtamaur"
        return Path.home() / "AppData" / "Local" / "vojtamaur"

    if system == "darwin":
        return Path.home() / "Library" / "Caches" / "vojtamaur"

    xdg_cache = os.getenv("XDG_CACHE_HOME")
    if xdg_cache:
        return Path(xdg_cache) / "vojtamaur"
    return Path.home() / ".cache" / "vojtamaur"


def dataset_cache_file(kind: str) -> Path:
    from .constants import DATASETS

    cache_name = str(DATASETS[kind]["cache_name"])
    return cache_dir() / cache_name


def dataset_state_file(kind: str) -> Path:
    return cache_dir() / f"{kind}.state.json"
