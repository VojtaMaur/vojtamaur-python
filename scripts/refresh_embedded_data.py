"""Refresh embedded package snapshots from the public vojtamaur endpoints.

Run this before creating a release when ALL_POSTS.txt or ARCHIVE.txt changed:

    python scripts/refresh_embedded_data.py

It intentionally uses only the Python standard library. Dependency creep is how
small tools get eaten alive by their own digestive tract.
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from vojtamaur.constants import DATASETS, USER_AGENT  # noqa: E402

DATA_DIR = ROOT / "src" / "vojtamaur" / "data"
EMBEDDED_KINDS = ("posts", "archive")


def fetch(url: str, timeout: float = 20.0) -> bytes:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        data = response.read()
    data.decode("utf-8-sig")
    return data


def main() -> int:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for kind in EMBEDDED_KINDS:
        dataset = DATASETS[kind]
        filename = str(dataset["cache_name"])
        url = str(dataset["urls"][0])  # canonical source only for embedded release snapshots
        print(f"fetching: {url}")
        data = fetch(url)
        path = DATA_DIR / filename
        path.write_bytes(data)
        print(f"saved: {path} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
