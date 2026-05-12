import unittest

from vojtamaur.constants import DATASETS, SITE_SOURCES, site_urls, source_kind_for_index


class ConstantsTests(unittest.TestCase):
    def test_dataset_urls_are_built_from_site_sources(self):
        expected = [f"{site}/ALL_POSTS.txt" for _, site in SITE_SOURCES]
        self.assertEqual(DATASETS["posts"]["urls"], expected)

    def test_source_kind_for_index_uses_configured_labels(self):
        self.assertEqual(source_kind_for_index(0), "main")
        self.assertEqual(source_kind_for_index(1), "fallback")
        self.assertEqual(source_kind_for_index(7), "fallback7")

    def test_site_urls(self):
        urls = site_urls("/ARCHIVE.txt")
        self.assertEqual(len(urls), len(SITE_SOURCES))
        self.assertTrue(urls[0].endswith("/ARCHIVE.txt"))


if __name__ == "__main__":
    unittest.main()
