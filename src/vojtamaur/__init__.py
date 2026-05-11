"""Vojtamaur CLI package."""

from __future__ import annotations

from .constants import __version__
from .fetch import fetch_dataset, FetchResult, FetchError
from .parse import extract_post_urls, extract_archive_urls, compute_posts_stats

__all__ = [
    "__version__",
    "fetch_dataset",
    "FetchResult",
    "FetchError",
    "extract_post_urls",
    "extract_archive_urls",
    "compute_posts_stats",
]
