"""Embedded package snapshots for vojtamaur text artifacts."""

from __future__ import annotations

from importlib import resources

from .constants import DATASETS

EMBEDDED_KINDS = {"posts", "archive"}


def embedded_filename(kind: str) -> str:
    if kind not in DATASETS:
        raise ValueError(f"Unknown dataset: {kind}")
    return str(DATASETS[kind]["cache_name"])


def has_embedded_dataset(kind: str) -> bool:
    if kind not in EMBEDDED_KINDS:
        return False
    try:
        path = resources.files("vojtamaur.data").joinpath(embedded_filename(kind))
        return path.is_file()
    except (FileNotFoundError, ModuleNotFoundError, AttributeError):
        return False


def read_embedded_dataset(kind: str) -> bytes:
    if kind not in EMBEDDED_KINDS:
        raise FileNotFoundError(f"No embedded package snapshot exists for {kind}.")
    path = resources.files("vojtamaur.data").joinpath(embedded_filename(kind))
    return path.read_bytes()


def embedded_source_url(kind: str) -> str:
    return f"package://vojtamaur/data/{embedded_filename(kind)}"
