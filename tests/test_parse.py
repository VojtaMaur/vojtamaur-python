import unittest

from vojtamaur.parse import (
    compute_posts_stats,
    extract_archive_urls,
    extract_post_urls,
    grep_lines,
    html_to_text,
    rewrite_to_active_host,
)


SAMPLE_POSTS = """Plain-text export
Generated: 2026-05-09T07:46:16.995Z

============================================================
TITLE: Test
SLUG: test
URL: https://vojtamaur.cz/test/
LANGUAGE: cs
SECTION: volna-tvorba
============================================================

Ahoj metaprogram.

============================================================
TITLE: Test EN
SLUG: test
URL: https://vojtamaur.cz/en/test/
LANGUAGE: en
SECTION: volna-tvorba
============================================================

Hello metaprogram.
"""


class ParseTests(unittest.TestCase):
    def test_extract_post_urls_only_metadata_urls(self):
        urls = extract_post_urls(SAMPLE_POSTS + "\nhttps://example.com/body\n")
        self.assertEqual(urls, ["https://vojtamaur.cz/test/", "https://vojtamaur.cz/en/test/"])

    def test_extract_archive_urls(self):
        text = "A https://archive.today/abc, B http://example.com/x). A https://archive.today/abc"
        self.assertEqual(extract_archive_urls(text), ["https://archive.today/abc", "http://example.com/x"])

    def test_grep_lines_casefold(self):
        matches = grep_lines(SAMPLE_POSTS, "METAPROGRAM")
        self.assertEqual(len(matches), 2)

    def test_stats(self):
        raw = SAMPLE_POSTS.encode("utf-8-sig")
        stats = compute_posts_stats(SAMPLE_POSTS, raw)
        self.assertEqual(stats.entries, 2)
        self.assertEqual(stats.unique_slugs, 1)
        self.assertEqual(stats.languages["cs"], 1)
        self.assertEqual(stats.languages["en"], 1)
        self.assertEqual(stats.generated, "2026-05-09T07:46:16.995Z")

    def test_rewrite_to_active_host(self):
        out = rewrite_to_active_host("https://vojtamaur.cz/test/", "https://vojtamaur.neocities.org/ALL_POSTS.txt")
        self.assertEqual(out, "https://vojtamaur.neocities.org/test/")

    def test_html_to_text(self):
        html = "<html><head><style>x</style></head><body><h1>Title</h1><p>Hello <b>world</b>.</p></body></html>"
        text = html_to_text(html)
        self.assertIn("Title", text)
        self.assertIn("Hello", text)
        self.assertIn("world", text)
        self.assertNotIn("style", text)


if __name__ == "__main__":
    unittest.main()
