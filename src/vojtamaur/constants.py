"""Constants for the vojtamaur CLI."""

from __future__ import annotations

__version__ = "0.1.3"

# Deployment sources are ordered by priority. To add another live fallback,
# add another (label, base_url) tuple here. Everything else derives from this
# list, because copy-paste fallback topology is how small tools become swamps.
SITE_SOURCES: list[tuple[str, str]] = [
    ("main", "https://vojtamaur.cz"),
    ("fallback", "https://vojtamaur.neocities.org"),
]

PRIMARY_SITE = SITE_SOURCES[0][1]
FALLBACK_SITE = SITE_SOURCES[1][1]

DEFAULT_TIMEOUT = 3.0
DEFAULT_HEAD_LINES = 20
USER_AGENT = f"vojtamaur/{__version__} (+https://vojtamaur.cz/)"


def site_urls(path: str) -> list[str]:
    """Build ordered URLs for a path across all configured deployments."""
    return [f"{site}{path}" for _, site in SITE_SOURCES]


def source_kind_for_index(index: int) -> str:
    """Return the source label for a configured source index."""
    if index < len(SITE_SOURCES):
        return SITE_SOURCES[index][0]
    return f"fallback{index}"


DATASETS: dict[str, dict[str, object]] = {
    "posts": {
        "label": "ALL_POSTS.txt",
        "cache_name": "ALL_POSTS.txt",
        "default_save_name": "ALL_POSTS.txt",
        "urls": site_urls("/ALL_POSTS.txt"),
    },
    "archive": {
        "label": "ARCHIVE.txt",
        "cache_name": "ARCHIVE.txt",
        "default_save_name": "ARCHIVE.txt",
        "urls": site_urls("/ARCHIVE.txt"),
    },
    "docs": {
        "label": "documentation HTML",
        "cache_name": "documentation.html",
        "default_save_name": "documentation.html",
        "urls": site_urls("/documentation/"),
    },
}
