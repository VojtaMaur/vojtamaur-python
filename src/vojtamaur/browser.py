"""Browser and URL status helpers."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
import webbrowser

from .constants import DEFAULT_TIMEOUT, USER_AGENT


@dataclass(frozen=True)
class ProbeResult:
    url: str
    ok: bool
    status: int | None
    method: str
    error: str | None = None
    insecure_http: bool = False


def is_http_url(url: str) -> bool:
    return urlsplit(url).scheme.lower() in {"http", "https"}


def open_http_url(url: str) -> bool:
    if not is_http_url(url):
        raise ValueError("Only http(s) URLs are allowed.")
    return webbrowser.open(url, new=2, autoraise=True)


def open_file_path(path: str | Path) -> bool:
    """Open a local file in the default browser/application."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(file_path)
    return webbrowser.open(file_path.as_uri(), new=2, autoraise=True)


def probe_url(url: str, *, timeout: float = DEFAULT_TIMEOUT) -> ProbeResult:
    if not is_http_url(url):
        return ProbeResult(url=url, ok=False, status=None, method="SKIP", error="unsupported scheme")

    insecure = urlsplit(url).scheme.lower() == "http"
    last_error: str | None = None
    last_status: int | None = None
    last_method = "HEAD"

    for method in ("HEAD", "GET"):
        last_method = method
        try:
            req = Request(url, headers={"User-Agent": USER_AGENT}, method=method)
            with urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                return ProbeResult(
                    url=url,
                    ok=200 <= int(status) < 400,
                    status=int(status),
                    method=method,
                    insecure_http=insecure,
                )
        except HTTPError as exc:
            last_status = exc.code
            last_error = str(exc.reason)
            if method == "HEAD" and exc.code in {403, 405, 429, 500, 501}:
                continue
            return ProbeResult(
                url=url,
                ok=200 <= exc.code < 400,
                status=exc.code,
                method=method,
                error=last_error,
                insecure_http=insecure,
            )
        except (URLError, TimeoutError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"
            if method == "HEAD":
                continue
            return ProbeResult(
                url=url,
                ok=False,
                status=last_status,
                method=method,
                error=last_error,
                insecure_http=insecure,
            )

    return ProbeResult(
        url=url,
        ok=False,
        status=last_status,
        method=last_method,
        error=last_error or "unknown failure",
        insecure_http=insecure,
    )
