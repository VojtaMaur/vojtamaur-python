"""Parsing utilities for vojtamaur text artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser
from urllib.parse import urlsplit, urlunsplit
import re

POST_URL_RE = re.compile(r"^URL:\s*(https?://\S+)\s*$", re.MULTILINE)
ARCHIVE_URL_RE = re.compile(r"https?://[^\s<>'\")]+", re.IGNORECASE)
TITLE_RE = re.compile(r"^TITLE:\s*(.+?)\s*$", re.MULTILINE)
SLUG_RE = re.compile(r"^SLUG:\s*(.+?)\s*$", re.MULTILINE)
LANGUAGE_RE = re.compile(r"^LANGUAGE:\s*(.+?)\s*$", re.MULTILINE)
SECTION_RE = re.compile(r"^SECTION:\s*(.+?)\s*$", re.MULTILINE)
GENERATED_RE = re.compile(r"^Generated:\s*(.+?)\s*$", re.MULTILINE)
WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)

TRAILING_URL_CHARS = ".,;:!?)]}»”\"'"


def extract_post_urls(text: str) -> list[str]:
    return unique_preserve_order(POST_URL_RE.findall(text))


def extract_archive_urls(text: str) -> list[str]:
    urls = [m.group(0).rstrip(TRAILING_URL_CHARS) for m in ARCHIVE_URL_RE.finditer(text)]
    return unique_preserve_order(urls)


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def grep_lines(text: str, query: str, *, case_sensitive: bool = False, context: int = 0) -> list[tuple[int, str]]:
    lines = text.splitlines()
    haystack_query = query if case_sensitive else query.casefold()
    matches: list[int] = []
    for idx, line in enumerate(lines):
        haystack_line = line if case_sensitive else line.casefold()
        if haystack_query in haystack_line:
            matches.append(idx)

    if context <= 0:
        return [(idx + 1, lines[idx]) for idx in matches]

    wanted: set[int] = set()
    for idx in matches:
        start = max(0, idx - context)
        end = min(len(lines), idx + context + 1)
        wanted.update(range(start, end))
    return [(idx + 1, lines[idx]) for idx in sorted(wanted)]


def first_lines(text: str, count: int) -> str:
    return "\n".join(text.splitlines()[: max(0, count)])


@dataclass(frozen=True)
class PostsStats:
    size_bytes: int
    chars: int
    lines: int
    words: int
    entries: int
    unique_slugs: int
    languages: dict[str, int]
    sections: dict[str, int]
    generated: str | None


def compute_posts_stats(text: str, raw: bytes) -> PostsStats:
    languages = count_values(LANGUAGE_RE.findall(text))
    sections = count_values(SECTION_RE.findall(text))
    generated_match = GENERATED_RE.search(text)
    return PostsStats(
        size_bytes=len(raw),
        chars=len(text),
        lines=len(text.splitlines()),
        words=len(WORD_RE.findall(text)),
        entries=len(TITLE_RE.findall(text)),
        unique_slugs=len(set(SLUG_RE.findall(text))),
        languages=languages,
        sections=sections,
        generated=generated_match.group(1) if generated_match else None,
    )


def count_values(values: list[str]) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        out[value] = out.get(value, 0) + 1
    return dict(sorted(out.items()))


def rewrite_to_active_host(url: str, source_url: str) -> str:
    """Rewrite canonical vojtamaur.cz URLs to the active fallback host if needed."""
    source_host = urlsplit(source_url).netloc.lower()
    parsed = urlsplit(url)
    if source_host and source_host != "vojtamaur.cz" and parsed.netloc.lower() == "vojtamaur.cz":
        return urlunsplit((parsed.scheme, source_host, parsed.path, parsed.query, parsed.fragment))
    return url


class SimpleHTMLTextExtractor(HTMLParser):
    """Very small HTML-to-text extractor for the documentation command.

    It intentionally avoids complex rendering. It is just enough to make a static
    documentation page readable in a terminal without adding dependencies.
    """

    block_tags = {
        "article",
        "aside",
        "br",
        "div",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "main",
        "p",
        "pre",
        "section",
        "table",
        "tr",
        "ul",
        "ol",
    }

    ignore_tags = {"script", "style", "noscript", "svg"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in self.ignore_tags:
            self.ignored_depth += 1
            return
        if tag in self.block_tags:
            self._newline()
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in self.ignore_tags and self.ignored_depth:
            self.ignored_depth -= 1
            return
        if tag in self.block_tags:
            self._newline()

    def handle_data(self, data: str) -> None:
        if self.ignored_depth:
            return
        collapsed = re.sub(r"\s+", " ", data)
        if collapsed.strip():
            self.parts.append(collapsed.strip() + " ")

    def _newline(self) -> None:
        if not self.parts or self.parts[-1].endswith("\n\n"):
            return
        if self.parts[-1].endswith("\n"):
            self.parts.append("\n")
        else:
            self.parts.append("\n\n")

    def text(self) -> str:
        raw = "".join(self.parts)
        lines = [line.rstrip() for line in raw.splitlines()]
        compact: list[str] = []
        blank = False
        for line in lines:
            if not line.strip():
                if not blank:
                    compact.append("")
                blank = True
            else:
                compact.append(line.strip())
                blank = False
        return "\n".join(compact).strip() + "\n"


def html_to_text(html: str) -> str:
    parser = SimpleHTMLTextExtractor()
    parser.feed(html)
    parser.close()
    return parser.text()
