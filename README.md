# vojtamaur

Malý `pip install` CLI nástroj pro práci s veřejnými textovými artefakty webu [vojtamaur.cz](https://vojtamaur.cz/):

- `ALL_POSTS.txt`
- `ARCHIVE.txt`
- dokumentace na `/documentation/`

Není to parser webu, crawler, CMS, synchronizační démon ani další pokus lidstva udělat z textového souboru platformu. Pracuje hlavně s publikovanými plaintext/HTML endpointy a drží poslední úspěšně staženou kopii v cache.

## Instalace

Lokálně z repozitáře:

```bash
python -m pip install .
```

Při vývoji:

```bash
python -m pip install -e .
```

Po publikaci na PyPI:

```bash
python -m pip install vojtamaur
```

## Rychlé použití

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

## Zdrojová logika

Pro každý artefakt se zkouší:

1. primární URL na `https://vojtamaur.cz/`
2. fallback URL na `https://vojtamaur.neocities.org/`
3. lokální cache

Pokud selže síť i cache, příkaz skončí chybou. Žádná magie, žádný nekonečný retry rituál, žádná služba běžící na pozadí.

## Cache

Cache se ukládá podle platformy:

- Windows: `%LOCALAPPDATA%/vojtamaur/`
- macOS: `~/Library/Caches/vojtamaur/`
- Linux/Unix: `$XDG_CACHE_HOME/vojtamaur/` nebo `~/.cache/vojtamaur/`

Override:

```bash
set VOJTAMAUR_CACHE_DIR=C:\temp\vojtamaur-cache
```

nebo na Unixu:

```bash
export VOJTAMAUR_CACHE_DIR=/tmp/vojtamaur-cache
```

## Offline režim

```bash
vojtamaur posts --offline
vojtamaur archive --offline
vojtamaur docs --offline
vojtamaur stats --offline
```

Nebo globálně přes prostředí:

```bash
export VOJTAMAUR_OFFLINE=1
```

Offline režim používá pouze poslední uloženou cache. Pokud cache neexistuje, skončí chybou. Šokující, ale prázdná cache neumí číst myšlenky.

## Timeout

Výchozí timeout je 3 sekundy.

```bash
vojtamaur status --timeout 5
```

Nebo:

```bash
export VOJTAMAUR_TIMEOUT=5
```

## Příkazy

### `posts`

Zobrazí nebo uloží `ALL_POSTS.txt`.

```bash
vojtamaur posts
vojtamaur posts --save
vojtamaur posts --save moje_kopie.txt
```

### `archive`

Zobrazí nebo uloží `ARCHIVE.txt`.

```bash
vojtamaur archive
vojtamaur archive --save
```

### `docs`

Stáhne dokumentaci z `/documentation/`. Bez parametrů vypíše jednoduchý textový výtah z HTML. S `--raw` vypíše původní HTML. S `--save` uloží raw HTML.

```bash
vojtamaur docs
vojtamaur docs --raw
vojtamaur docs --save
```

### `grep`

Prohledá `ALL_POSTS.txt` jako prostý text.

```bash
vojtamaur grep DullGPT
vojtamaur grep "Boltzmannovy mozky" --context 2
vojtamaur grep Metaweb --case-sensitive
```

### `search-url`

Prohledá URL nalezené v `ARCHIVE.txt`.

```bash
vojtamaur search-url arquivo
vojtamaur search-url archive.today
```

### `stats`

Vypíše základní statistiky: velikost, počet znaků, slov, řádků, záznamů, unikátních slugů, jazyků, sekcí a počet unikátních archivních odkazů.

```bash
vojtamaur stats
```

### `head`

Vypíše prvních N řádků `ALL_POSTS.txt`.

```bash
vojtamaur head
vojtamaur head 80
```

### `random`

Vybere náhodnou URL z `URL:` hlaviček v `ALL_POSTS.txt`.

```bash
vojtamaur random
vojtamaur random --print-only
```

Výchozí chování URL i otevře v prohlížeči.

### `status`

Zkontroluje URL nalezené v `ARCHIVE.txt`.

```bash
vojtamaur status
vojtamaur status --limit 10
```

Používá `HEAD`, při některých selháních zkusí `GET`. U plain HTTP odkazů vypíše `INSECURE_HTTP`.

### `verify`

Provede hrubý health check:

- primární a fallback zdroje pro `posts`, `archive`, `docs`
- čitelnost cache adresáře
- dekódování cache souborů, pokud existují
- parsování URL z `ALL_POSTS.txt` a `ARCHIVE.txt`

```bash
vojtamaur verify
```

### `open`

Otevře známý cíl nebo URL. U `posts`, `archive` a `docs` otevře normálně kanonickou online URL. S `--offline` otevře odpovídající soubor z lokální cache, tedy `ALL_POSTS.txt`, `ARCHIVE.txt` nebo `documentation.html`. Ano, offline režim konečně neotevírá internet. Civilizace udělala jeden krok vpřed.

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

## Co to nedělá

- neparsuje HTML webu jako zdroj článků
- nestahuje markdown source soubory
- nesynchronizuje repozitář
- nedělá diff
- neukládá databázi
- neběží na pozadí
- nepoužívá runtime závislosti

## Omezení

`ALL_POSTS.txt` je textový export, ne kompletní replika webu. Média, iframy, PDF a některé dlouhé bloky jsou v něm nahrazené placeholdery nebo vynechané. To je záměr. Nástroj pracuje s tímto textovým sedimentem, ne s plným renderovaným webem.

## Testy

```bash
python -m unittest
```

## Publikace

Build:

```bash
python -m pip install build
python -m build
```

Upload na TestPyPI/PyPI řeš přes Trusted Publishing v GitHub Actions nebo ručně přes Twine. PyPI účet bude potřeba. Ano, další účet. Digitální svět je v podstatě nekonečná sbírka branek s heslem.
