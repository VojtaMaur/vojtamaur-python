# vojtamaur

A small `pip install` CLI tool for working with the public text artifacts of [vojtamaur.cz](https://vojtamaur.cz/):

- `ALL_POSTS.txt`
- `ARCHIVE.txt`
- the documentation page at `/documentation/`

This is not a website parser, crawler, CMS, sync daemon, or another heroic attempt to turn a text file into a platform. It works mainly with published plaintext/HTML endpoints and keeps the last successfully fetched copy in a local cache.

## Installation

Install locally from the repository:

```bash
python -m pip install .
```

For development:

```bash
python -m pip install -e .
```

After publication on PyPI:

```bash
python -m pip install vojtamaur
```

## Quick usage

```bash
vojtamaur --help
vojtamaur posts
vojtamaur posts --save
vojtamaur archive
vojtamaur archive --save
vojtamaur docs
vojtamaur docs --save
vojtamaur grep metaprogram
vojtamaur search-url archive.today
vojtamaur stats
vojtamaur head 40
vojtamaur random
vojtamaur random --print-only
vojtamaur status
vojtamaur verify
vojtamaur open site
vojtamaur open docs
vojtamaur open archive-link 1
```

## Source logic

For each artifact, the tool tries:

1. the primary URL on `https://vojtamaur.cz/`
2. the fallback URL on `https://vojtamaur.neocities.org/`
3. the local cache

If both the network and the cache fail, the command exits with an error. No magic, no infinite retry ritual, no background service quietly doing suspicious little things.

## Cache

The cache is stored according to the platform:

- Windows: `%LOCALAPPDATA%/vojtamaur/`
- macOS: `~/Library/Caches/vojtamaur/`
- Linux/Unix: `$XDG_CACHE_HOME/vojtamaur/` or `~/.cache/vojtamaur/`

Override on Windows CMD:

```bat
set VOJTAMAUR_CACHE_DIR=C:\temp\vojtamaur-cache
```

Override on Unix-like systems:

```bash
export VOJTAMAUR_CACHE_DIR=/tmp/vojtamaur-cache
```

## Offline mode

```bash
vojtamaur posts --offline
vojtamaur archive --offline
vojtamaur docs --offline
vojtamaur stats --offline
```

Or globally through the environment.

Windows CMD:

```bat
set VOJTAMAUR_OFFLINE=1
```

Unix-like systems:

```bash
export VOJTAMAUR_OFFLINE=1
```

Offline mode uses only the latest cached copy. If the cache does not exist, the command exits with an error. Shocking, but an empty cache cannot read minds.

## Timeout

The default timeout is 3 seconds.

```bash
vojtamaur status --timeout 5
```

Or through the environment.

Windows CMD:

```bat
set VOJTAMAUR_TIMEOUT=5
```

Unix-like systems:

```bash
export VOJTAMAUR_TIMEOUT=5
```

## Commands

### `posts`

Prints or saves `ALL_POSTS.txt`.

```bash
vojtamaur posts
vojtamaur posts --save
vojtamaur posts --save my_copy.txt
```

### `archive`

Prints or saves `ARCHIVE.txt`.

```bash
vojtamaur archive
vojtamaur archive --save
```

### `docs`

Fetches the documentation from `/documentation/`. Without options, it prints a simple plain-text extraction from the HTML. With `--raw`, it prints the original HTML. With `--save`, it saves the raw HTML.

```bash
vojtamaur docs
vojtamaur docs --raw
vojtamaur docs --save
```

### `grep`

Searches `ALL_POSTS.txt` as plain text.

```bash
vojtamaur grep DullGPT
vojtamaur grep "Boltzmannovy mozky" --context 2
vojtamaur grep Metaweb --case-sensitive
```

### `search-url`

Searches URLs found in `ARCHIVE.txt`.

```bash
vojtamaur search-url arquivo
vojtamaur search-url archive.today
```

### `stats`

Prints basic statistics: size, character count, word count, line count, entry count, unique slugs, languages, sections, and the number of unique archive links.

```bash
vojtamaur stats
```

### `head`

Prints the first N lines of `ALL_POSTS.txt`.

```bash
vojtamaur head
vojtamaur head 80
```

### `random`

Selects a random URL from the `URL:` headers in `ALL_POSTS.txt`.

```bash
vojtamaur random
vojtamaur random --print-only
```

By default, the selected URL is also opened in the browser.

### `status`

Checks URLs found in `ARCHIVE.txt`.

```bash
vojtamaur status
vojtamaur status --limit 10
```

It uses `HEAD` first and falls back to `GET` for some failures. Plain HTTP links are marked as `INSECURE_HTTP`.

### `verify`

Runs a rough health check:

- primary and fallback sources for `posts`, `archive`, and `docs`
- cache directory writability
- cache file decoding, if cache files exist
- URL parsing from `ALL_POSTS.txt` and `ARCHIVE.txt`

```bash
vojtamaur verify
```

### `open`

Opens a known target or an explicit URL. For `posts`, `archive`, and `docs`, the normal behavior is to open the canonical online URL. With `--offline`, it opens the corresponding local cache file: `ALL_POSTS.txt`, `ARCHIVE.txt`, or `documentation.html`. In other words, offline mode does not open the internet. A modest but meaningful civilizational improvement.

```bash
vojtamaur open site
vojtamaur open fallback
vojtamaur open posts
vojtamaur open archive
vojtamaur open docs
vojtamaur open posts --offline
vojtamaur open archive --offline
vojtamaur open docs --offline
vojtamaur open random
vojtamaur open archive-link 1
vojtamaur open https://vojtamaur.cz/metawebovy-clanek/
```

## What it does not do

- it does not parse the rendered website as the source of articles
- it does not download Markdown source files
- it does not synchronize the repository
- it does not generate diffs
- it does not store a database
- it does not run in the background
- it does not use runtime dependencies

## Limitations

`ALL_POSTS.txt` is a text export, not a complete replica of the website. Media, iframes, PDFs, and some long blocks are replaced by placeholders or omitted. This is intentional. The tool works with this text sediment, not with the full rendered website.

## Tests

```bash
python -m unittest
```

## Publishing

Build:

```bash
python -m pip install build
python -m build
```

Upload to TestPyPI/PyPI either through Trusted Publishing in GitHub Actions or manually with Twine. A PyPI account is required. Yes, another account. The digital world is basically an infinite collection of password-protected gates.
