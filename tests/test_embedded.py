import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vojtamaur.embedded import has_embedded_dataset, read_embedded_dataset
from vojtamaur.fetch import fetch_dataset


class EmbeddedTests(unittest.TestCase):
    def test_posts_and_archive_are_embedded(self):
        self.assertTrue(has_embedded_dataset("posts"))
        self.assertTrue(has_embedded_dataset("archive"))
        self.assertGreater(len(read_embedded_dataset("posts")), 1000)
        self.assertGreater(len(read_embedded_dataset("archive")), 100)

    def test_offline_without_cache_uses_package_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("vojtamaur.paths.cache_dir", return_value=Path(tmp)):
                with mock.patch("vojtamaur.fetch.cache_dir", return_value=Path(tmp), create=True):
                    result = fetch_dataset("posts", offline=True)
                    self.assertEqual(result.source_kind, "package")
                    self.assertIn("TITLE:", result.text)
                    self.assertTrue((Path(tmp) / "ALL_POSTS.txt").exists())

    def test_network_failure_uses_local_package_snapshot_when_cache_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("vojtamaur.paths.cache_dir", return_value=Path(tmp)):
                with mock.patch("vojtamaur.fetch.cache_dir", return_value=Path(tmp), create=True):
                    with mock.patch("vojtamaur.fetch.fetch_url", side_effect=OSError("offline")):
                        result = fetch_dataset("archive")
                        self.assertEqual(result.source_kind, "package")
                        self.assertIn("ENTRY POINTS", result.text)


if __name__ == "__main__":
    unittest.main()
