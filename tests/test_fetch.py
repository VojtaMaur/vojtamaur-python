import tempfile
import unittest
from pathlib import Path
from unittest import mock

from vojtamaur.fetch import FetchError, decode_utf8_sig, fetch_dataset


class FetchTests(unittest.TestCase):
    def test_decode_utf8_sig(self):
        self.assertEqual(decode_utf8_sig("čau".encode("utf-8-sig")), "čau")

    def test_fetch_fallback_then_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("vojtamaur.paths.cache_dir", return_value=Path(tmp)):
                with mock.patch("vojtamaur.fetch.cache_dir", return_value=Path(tmp), create=True):
                    calls = []

                    def fake_fetch(url, timeout=3.0):
                        calls.append(url)
                        if len(calls) == 1:
                            raise OSError("primary down")
                        return "fallback text".encode("utf-8-sig")

                    with mock.patch("vojtamaur.fetch.fetch_url", side_effect=fake_fetch):
                        result = fetch_dataset("posts")
                        self.assertEqual(result.text, "fallback text")
                        self.assertEqual(result.source_kind, "fallback")

                    with mock.patch("vojtamaur.fetch.fetch_url", side_effect=OSError("offline")):
                        cached = fetch_dataset("posts")
                        self.assertEqual(cached.text, "fallback text")
                        self.assertEqual(cached.source_kind, "cache")

    def test_offline_without_cache_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch("vojtamaur.paths.cache_dir", return_value=Path(tmp)):
                with self.assertRaises(FetchError):
                    fetch_dataset("docs", offline=True)


if __name__ == "__main__":
    unittest.main()
