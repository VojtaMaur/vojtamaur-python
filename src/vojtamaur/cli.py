"""Command-line interface for vojtamaur."""

from __future__ import annotations

import argparse
import os
import random as random_module
import shutil
import sys
from pathlib import Path

from .browser import ProbeResult, is_http_url, open_file_path, open_http_url, probe_url
from .constants import DATASETS, DEFAULT_HEAD_LINES, DEFAULT_TIMEOUT, FALLBACK_SITE, PRIMARY_SITE, __version__
from .fetch import FetchError, FetchResult, decode_utf8_sig, fetch_dataset, fetch_url, source_urls
from .parse import (
    compute_posts_stats,
    extract_archive_urls,
    extract_post_urls,
    first_lines,
    grep_lines,
    html_to_text,
    rewrite_to_active_host,
)
from .paths import OFFLINE_ENV, TIMEOUT_ENV, cache_dir, dataset_cache_file

EXIT_OK = 0
EXIT_NEGATIVE = 1
EXIT_USAGE = 2
EXIT_RUNTIME = 3


def configure_stdout() -> None:
    # Windows terminals with legacy encodings are still a thing, because apparently
    # suffering needed backward compatibility. This avoids crashing on Czech text.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass


def parse_timeout(value: str | None) -> float:
    if value is None:
        env_value = os.getenv(TIMEOUT_ENV)
        if env_value:
            try:
                return float(env_value)
            except ValueError:
                return DEFAULT_TIMEOUT
        return DEFAULT_TIMEOUT
    try:
        return float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number") from exc


def env_offline_default() -> bool:
    value = os.getenv(OFFLINE_ENV, "").strip().casefold()
    return value in {"1", "true", "yes", "on"}


def add_fetch_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--offline", action="store_true", default=env_offline_default(), help="use local cache only")
    parser.add_argument("--timeout", type=parse_timeout, default=parse_timeout(None), help="network timeout in seconds")


def save_or_print(result: FetchResult, save_path: str | None, *, display_text: str | None = None) -> int:
    if save_path is not None:
        target = Path(save_path)
        target.write_bytes(result.raw)
        print(f"saved: {target}")
        print(f"source: {result.source_url} ({result.source_kind})")
        return EXIT_OK

    print(display_text if display_text is not None else result.text, end="" if (display_text or result.text).endswith("\n") else "\n")
    return EXIT_OK


def command_posts(args: argparse.Namespace) -> int:
    result = fetch_dataset("posts", offline=args.offline, timeout=args.timeout)
    save_path = args.save if args.save is not None else None
    return save_or_print(result, save_path)


def command_archive(args: argparse.Namespace) -> int:
    result = fetch_dataset("archive", offline=args.offline, timeout=args.timeout)
    save_path = args.save if args.save is not None else None
    return save_or_print(result, save_path)


def command_docs(args: argparse.Namespace) -> int:
    result = fetch_dataset("docs", offline=args.offline, timeout=args.timeout)
    save_path = args.save if args.save is not None else None
    if save_path is not None:
        return save_or_print(result, save_path)
    if args.raw:
        return save_or_print(result, None)
    return save_or_print(result, None, display_text=html_to_text(result.text))


def command_head(args: argparse.Namespace) -> int:
    result = fetch_dataset("posts", offline=args.offline, timeout=args.timeout)
    print(first_lines(result.text, args.lines))
    return EXIT_OK


def command_grep(args: argparse.Namespace) -> int:
    result = fetch_dataset("posts", offline=args.offline, timeout=args.timeout)
    query = " ".join(args.query)
    matches = grep_lines(result.text, query, case_sensitive=args.case_sensitive, context=args.context)
    for line_no, line in matches:
        print(f"{line_no}: {line}")
    if not matches:
        print(f"no matches: {query}", file=sys.stderr)
        return EXIT_NEGATIVE
    return EXIT_OK


def command_search_url(args: argparse.Namespace) -> int:
    result = fetch_dataset("archive", offline=args.offline, timeout=args.timeout)
    urls = extract_archive_urls(result.text)
    query = " ".join(args.query)
    needle = query.casefold()
    found = [url for url in urls if needle in url.casefold()]
    for idx, url in enumerate(found, start=1):
        print(f"{idx}: {url}")
    if not found:
        print(f"no URL matches: {query}", file=sys.stderr)
        return EXIT_NEGATIVE
    return EXIT_OK


def format_mapping(mapping: dict[str, int]) -> str:
    if not mapping:
        return "-"
    return ", ".join(f"{key}:{value}" for key, value in mapping.items())


def command_stats(args: argparse.Namespace) -> int:
    posts = fetch_dataset("posts", offline=args.offline, timeout=args.timeout)
    archive = fetch_dataset("archive", offline=args.offline, timeout=args.timeout)
    stats = compute_posts_stats(posts.text, posts.raw)
    archive_urls = extract_archive_urls(archive.text)

    print("vojtamaur stats")
    print("===============")
    print(f"posts_source: {posts.source_url} ({posts.source_kind})")
    print(f"archive_source: {archive.source_url} ({archive.source_kind})")
    print(f"posts_fetched_at: {posts.fetched_at or '-'}")
    print(f"archive_fetched_at: {archive.fetched_at or '-'}")
    print(f"posts_generated: {stats.generated or '-'}")
    print(f"posts_size_bytes: {stats.size_bytes}")
    print(f"posts_chars: {stats.chars}")
    print(f"posts_lines: {stats.lines}")
    print(f"posts_words: {stats.words}")
    print(f"posts_entries: {stats.entries}")
    print(f"posts_unique_slugs: {stats.unique_slugs}")
    print(f"languages: {format_mapping(stats.languages)}")
    print(f"sections: {format_mapping(stats.sections)}")
    print(f"archive_links_unique: {len(archive_urls)}")
    print(f"cache_dir: {cache_dir()}")
    return EXIT_OK


def print_probe(result: ProbeResult, index: int | None = None) -> None:
    prefix = f"{index}: " if index is not None else ""
    state = "OK" if result.ok else "FAIL"
    status = str(result.status) if result.status is not None else "-"
    warning = " INSECURE_HTTP" if result.insecure_http else ""
    error = f" | {result.error}" if result.error else ""
    print(f"{prefix}[{state}] {status} {result.method}{warning} {result.url}{error}")


def command_status(args: argparse.Namespace) -> int:
    archive = fetch_dataset("archive", offline=args.offline, timeout=args.timeout)
    urls = extract_archive_urls(archive.text)
    if args.limit is not None:
        urls = urls[: args.limit]

    failures = 0
    for idx, url in enumerate(urls, start=1):
        result = probe_url(url, timeout=args.timeout)
        print_probe(result, idx)
        if not result.ok:
            failures += 1

    print(f"summary: total={len(urls)} ok={len(urls) - failures} fail={failures}")
    return EXIT_OK if failures == 0 else EXIT_NEGATIVE


def command_verify(args: argparse.Namespace) -> int:
    failures = 0

    print("source checks")
    print("=============")
    for kind in ("posts", "archive", "docs"):
        for idx, url in enumerate(source_urls(kind)):
            source_kind = "main" if idx == 0 else "fallback"
            try:
                raw = fetch_url(url, timeout=args.timeout)
                decode_utf8_sig(raw)
                print(f"[OK] {kind}:{source_kind} {url}")
            except Exception as exc:
                failures += 1
                print(f"[FAIL] {kind}:{source_kind} {url} | {type(exc).__name__}: {exc}")

    print("\ncache checks")
    print("============")
    try:
        cdir = cache_dir()
        cdir.mkdir(parents=True, exist_ok=True)
        test_file = cdir / ".write-test"
        test_file.write_text("ok", encoding="utf-8")
        test_file.unlink(missing_ok=True)
        print(f"[OK] cache writable {cdir}")
    except Exception as exc:
        failures += 1
        print(f"[FAIL] cache writable | {type(exc).__name__}: {exc}")

    for kind in ("posts", "archive", "docs"):
        cache_file = dataset_cache_file(kind)
        if not cache_file.exists():
            print(f"[SKIP] cache missing {kind}: {cache_file}")
            continue
        try:
            decode_utf8_sig(cache_file.read_bytes())
            print(f"[OK] cache decodable {kind}: {cache_file}")
        except Exception as exc:
            failures += 1
            print(f"[FAIL] cache decodable {kind}: {type(exc).__name__}: {exc}")

    print("\nparser checks")
    print("=============")
    try:
        posts = fetch_dataset("posts", offline=False, timeout=args.timeout)
        post_urls = extract_post_urls(posts.text)
        if post_urls:
            print(f"[OK] post URLs parsed: {len(post_urls)}")
        else:
            failures += 1
            print("[FAIL] post URLs parsed: none")
    except Exception as exc:
        failures += 1
        print(f"[FAIL] post URLs parsed | {type(exc).__name__}: {exc}")

    try:
        archive = fetch_dataset("archive", offline=False, timeout=args.timeout)
        archive_urls = extract_archive_urls(archive.text)
        if archive_urls:
            print(f"[OK] archive URLs parsed: {len(archive_urls)}")
        else:
            failures += 1
            print("[FAIL] archive URLs parsed: none")
    except Exception as exc:
        failures += 1
        print(f"[FAIL] archive URLs parsed | {type(exc).__name__}: {exc}")

    print(f"\nsummary: {'OK' if failures == 0 else 'FAIL'} failures={failures}")
    return EXIT_OK if failures == 0 else EXIT_NEGATIVE


def command_random(args: argparse.Namespace) -> int:
    result = fetch_dataset("posts", offline=args.offline, timeout=args.timeout)
    urls = extract_post_urls(result.text)
    if not urls:
        print("no post URLs found", file=sys.stderr)
        return EXIT_RUNTIME
    url = random_module.choice(urls)
    url = rewrite_to_active_host(url, result.source_url)
    print(url)
    if args.print_only:
        return EXIT_OK
    try:
        ok = open_http_url(url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_NEGATIVE
    if not ok:
        print("browser did not report successful launch", file=sys.stderr)
        return EXIT_NEGATIVE
    return EXIT_OK


def command_open(args: argparse.Namespace) -> int:
    target = args.target[0]

    if is_http_url(target):
        url = target
    elif target == "site":
        url = PRIMARY_SITE + "/"
    elif target == "fallback":
        url = FALLBACK_SITE + "/"
    elif target in {"posts", "archive", "docs"}:
        if args.offline:
            # Offline means offline. Shocking concept, apparently worth encoding.
            # Ensure the cache exists and is decodable, then open the cached file.
            fetch_dataset(target, offline=True, timeout=args.timeout)
            path = dataset_cache_file(target)
            print(path)
            try:
                ok = open_file_path(path)
            except OSError as exc:
                print(f"could not open cached file: {exc}", file=sys.stderr)
                return EXIT_NEGATIVE
            return EXIT_OK if ok else EXIT_NEGATIVE
        url = str(DATASETS[target]["urls"][0])  # type: ignore[index]
    elif target == "random":
        args.print_only = False
        args.offline = getattr(args, "offline", env_offline_default())
        args.timeout = getattr(args, "timeout", DEFAULT_TIMEOUT)
        return command_random(args)
    elif target == "archive-link":
        if len(args.target) < 2:
            print("open archive-link requires an index", file=sys.stderr)
            return EXIT_USAGE
        try:
            index = int(args.target[1])
        except ValueError:
            print("archive-link index must be an integer", file=sys.stderr)
            return EXIT_USAGE
        archive = fetch_dataset("archive", offline=args.offline, timeout=args.timeout)
        urls = extract_archive_urls(archive.text)
        if index < 1 or index > len(urls):
            print(f"archive-link index out of range: 1..{len(urls)}", file=sys.stderr)
            return EXIT_USAGE
        url = urls[index - 1]
    else:
        print(f"unknown open target: {target}", file=sys.stderr)
        return EXIT_USAGE

    print(url)
    try:
        ok = open_http_url(url)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return EXIT_NEGATIVE
    return EXIT_OK if ok else EXIT_NEGATIVE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vojtamaur",
        description="CLI access to vojtamaur.cz text artifacts: ALL_POSTS.txt, ARCHIVE.txt and documentation.",
    )
    parser.add_argument("--version", action="version", version=f"vojtamaur {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_posts = subparsers.add_parser("posts", help="show or download ALL_POSTS.txt")
    add_fetch_options(p_posts)
    p_posts.add_argument("--save", nargs="?", const=str(DATASETS["posts"]["default_save_name"]), help="save raw file instead of printing")
    p_posts.set_defaults(func=command_posts)

    p_archive = subparsers.add_parser("archive", help="show or download ARCHIVE.txt")
    add_fetch_options(p_archive)
    p_archive.add_argument("--save", nargs="?", const=str(DATASETS["archive"]["default_save_name"]), help="save raw file instead of printing")
    p_archive.set_defaults(func=command_archive)

    p_docs = subparsers.add_parser("docs", help="show documentation text or download documentation HTML")
    add_fetch_options(p_docs)
    p_docs.add_argument("--save", nargs="?", const=str(DATASETS["docs"]["default_save_name"]), help="save raw documentation HTML instead of printing")
    p_docs.add_argument("--raw", action="store_true", help="print raw HTML instead of a simple text extraction")
    p_docs.set_defaults(func=command_docs)

    p_head = subparsers.add_parser("head", help="print first lines of ALL_POSTS.txt")
    add_fetch_options(p_head)
    p_head.add_argument("lines", nargs="?", type=int, default=DEFAULT_HEAD_LINES, help="number of lines to print")
    p_head.set_defaults(func=command_head)

    p_grep = subparsers.add_parser("grep", help="search ALL_POSTS.txt")
    add_fetch_options(p_grep)
    p_grep.add_argument("query", nargs="+", help="text to search for")
    p_grep.add_argument("--case-sensitive", action="store_true", help="use case-sensitive search")
    p_grep.add_argument("--context", type=int, default=0, help="number of context lines around matches")
    p_grep.set_defaults(func=command_grep)

    p_search_url = subparsers.add_parser("search-url", help="search URLs inside ARCHIVE.txt")
    add_fetch_options(p_search_url)
    p_search_url.add_argument("query", nargs="+", help="text to search for inside archive URLs")
    p_search_url.set_defaults(func=command_search_url)

    p_stats = subparsers.add_parser("stats", help="show basic statistics")
    add_fetch_options(p_stats)
    p_stats.set_defaults(func=command_stats)

    p_status = subparsers.add_parser("status", help="check status of URLs listed in ARCHIVE.txt")
    add_fetch_options(p_status)
    p_status.add_argument("--limit", type=int, default=None, help="only check the first N URLs")
    p_status.set_defaults(func=command_status)

    p_verify = subparsers.add_parser("verify", help="run source, cache and parser checks")
    p_verify.add_argument("--timeout", type=parse_timeout, default=parse_timeout(None), help="network timeout in seconds")
    p_verify.set_defaults(func=command_verify)

    p_random = subparsers.add_parser("random", help="open a random post from ALL_POSTS.txt")
    add_fetch_options(p_random)
    p_random.add_argument("--print-only", action="store_true", help="print URL without opening browser")
    p_random.set_defaults(func=command_random)

    p_open = subparsers.add_parser("open", help="open site, fallback, posts, archive, docs, random, archive-link N or an explicit URL")
    add_fetch_options(p_open)
    p_open.add_argument("target", nargs="+", help="target to open")
    p_open.set_defaults(func=command_open)

    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdout()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except FetchError as exc:
        print(f"runtime error: {exc}", file=sys.stderr)
        return EXIT_RUNTIME
    except BrokenPipeError:
        return EXIT_OK
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return EXIT_NEGATIVE


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
