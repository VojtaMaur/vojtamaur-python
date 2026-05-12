# vojtamaur

A small `pip install` command-line tool for working with the public text artifacts of [vojtamaur.cz](https://vojtamaur.cz/):

- `ALL_POSTS.txt`
- `ARCHIVE.txt`
- the documentation page at `/documentation/`

The tool is not a website parser, crawler, CMS, sync daemon, or background service. It works mainly with published plaintext/HTML endpoints, keeps a local cache of the last successfully loaded artifacts, and also includes embedded package snapshots of `ALL_POSTS.txt` and `ARCHIVE.txt` as a final fallback.

## Installation

From a local repository checkout:

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

From GitHub:

```bash
python -m pip install git+https://github.com/VojtaMaur/vojtamaur-python.git
```

From a specific Git tag:

```bash
python -m pip install git+https://github.com/VojtaMaur/vojtamaur-python.git@v0.1.3
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
vojtamaur status --limit 10
vojtamaur verify
vojtamaur open site
vojtamaur open docs
vojtamaur open archive-link 1
```

## Source strategy

For each artifact, the tool tries to use the most current available source first.

For `posts` and `archive`, the fallback order is:

1. primary URL from `SITE_SOURCES`
2. additional live fallback URLs from `SITE_SOURCES`, in order
3. local cache
4. embedded package snapshot

For `docs`, the fallback order is:

1. primary URL from `SITE_SOURCES`
2. additional live fallback URLs from `SITE_SOURCES`, in order
3. local cache

`docs` is not embedded in the package. The package snapshot is intended only for the two compact plaintext artifacts.

If all available sources fail, the command exits with an error.


### Adding another live fallback

Live deployment fallbacks are configured in `src/vojtamaur/constants.py` through `SITE_SOURCES`:

```python
SITE_SOURCES = [
    ("main", "https://vojtamaur.cz"),
    ("fallback", "https://vojtamaur.neocities.org"),
]
```

To add another deployment, append another `(label, base_url)` tuple. The `posts`, `archive`, and `docs` endpoint URLs are generated from this list. The order is the priority order used by the fetch logic.

## Cache

The cache location is platform-specific:

- Windows: `%LOCALAPPDATA%/vojtamaur/`
- macOS: `~/Library/Caches/vojtamaur/`
- Linux/Unix: `$XDG_CACHE_HOME/vojtamaur/` or `~/.cache/vojtamaur/`

Override on Windows CMD:

```bat
set VOJTAMAUR_CACHE_DIR=C:\temp\vojtamaur-cache
```

Override on PowerShell:

```powershell
$env:VOJTAMAUR_CACHE_DIR = "C:\temp\vojtamaur-cache"
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

Or globally through the environment:

```bash
export VOJTAMAUR_OFFLINE=1
```

In offline mode, `posts` and `archive` use the local cache first and the embedded package snapshot if no cache exists. `docs` uses only the local cache because documentation HTML is not embedded.

## Timeout

The default network timeout is 3 seconds.

```bash
vojtamaur status --timeout 5
```

Or:

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

Downloads the documentation page from `/documentation/`. By default, it prints a simple plaintext extraction from the HTML. With `--raw`, it prints the original HTML. With `--save`, it saves the raw HTML.

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

Prints basic statistics: byte size, character count, word count, line count, entry count, unique slug count, languages, sections, and the number of unique archive links.

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

Selects a random URL from `URL:` headers in `ALL_POSTS.txt`.

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

The command uses `HEAD` first and falls back to `GET` for selected failures. Plain HTTP URLs are marked as `INSECURE_HTTP`.

### `verify`

Runs a basic health check:

- primary and fallback sources for `posts`, `archive`, and `docs`
- embedded package snapshots for `posts` and `archive`
- local cache writability
- cache decoding, if cache files exist
- URL parsing from `ALL_POSTS.txt` and `ARCHIVE.txt`

```bash
vojtamaur verify
```

### `open`

Opens a known target or explicit URL. For `posts`, `archive`, and `docs`, normal mode opens the canonical online URL. With `--offline`, it opens the corresponding local cache file.

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

## Embedded snapshots

The package includes bundled fallback copies of:

- `src/vojtamaur/data/ALL_POSTS.txt`
- `src/vojtamaur/data/ARCHIVE.txt`

These files make the installed package partially useful even if the website, fallback deployment, and cache are unavailable. They also make package distributions, wheels, source archives, PyPI mirrors, pip caches, and installed environments act as additional copies of the text artifacts.

Before publishing a new release, refresh the embedded snapshots:

```bash
python scripts/refresh_embedded_data.py
```

Then verify:

```bash
python -m unittest
vojtamaur verify
vojtamaur stats --offline
```

## What this tool does not do

- it does not parse the rendered website as the source of articles
- it does not download Markdown/MDX source files
- it does not synchronize the repository
- it does not compute diffs
- it does not store a database
- it does not run in the background
- it has no runtime dependencies outside the Python standard library

## Limitations

`ALL_POSTS.txt` is a text export, not a complete replica of the website. Media, iframes, PDFs, and selected long blocks are represented by placeholders or omitted. This is intentional. The tool works with the text sediment, not the full rendered website.

The embedded snapshots are release snapshots. The live endpoints remain the preferred source when available.

## Tests

```bash
python -m unittest
```

## Build

```bash
python -m pip install build
python -m build
```

## Embedded fallback snapshots

The Python CLI package also contains embedded fallback copies of selected text artifacts:

- `ALL_POSTS.txt`
- `ARCHIVE.txt`

These embedded files are bundled directly inside the package so the CLI can still function in degraded or offline situations even if the live website or mirrors become unavailable.

Before publishing a new package release, refresh the embedded snapshots:

```bash
python scripts/refresh_embedded_data.py

## Publishing

Publish through PyPI Trusted Publishing in GitHub Actions or upload manually with Twine. A PyPI account is required.
