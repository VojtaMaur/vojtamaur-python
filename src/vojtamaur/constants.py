"""Constants for the vojtamaur CLI."""

from __future__ import annotations

__version__ = "0.1.1"

PRIMARY_SITE = "https://vojtamaur.cz"
FALLBACK_SITE = "https://vojtamaur.neocities.org"

DEFAULT_TIMEOUT = 3.0
DEFAULT_HEAD_LINES = 20
USER_AGENT = f"vojtamaur/{__version__} (+https://vojtamaur.cz/)"

DATASETS: dict[str, dict[str, object]] = {
    "posts": {
        "label": "ALL_POSTS.txt",
        "cache_name": "ALL_POSTS.txt",
        "default_save_name": "ALL_POSTS.txt",
        "urls": [
            f"{PRIMARY_SITE}/ALL_POSTS.txt",
            f"{FALLBACK_SITE}/ALL_POSTS.txt",
        ],
    },
    "archive": {
        "label": "ARCHIVE.txt",
        "cache_name": "ARCHIVE.txt",
        "default_save_name": "ARCHIVE.txt",
        "urls": [
            f"{PRIMARY_SITE}/ARCHIVE.txt",
            f"{FALLBACK_SITE}/ARCHIVE.txt",
        ],
    },
    "docs": {
        "label": "documentation HTML",
        "cache_name": "documentation.html",
        "default_save_name": "documentation.html",
        "urls": [
            f"{PRIMARY_SITE}/documentation/",
            f"{FALLBACK_SITE}/documentation/",
        ],
    },
}
