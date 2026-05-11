import unittest
from unittest import mock

from pathlib import Path
from tempfile import TemporaryDirectory

from vojtamaur.browser import is_http_url, open_file_path, open_http_url


class BrowserTests(unittest.TestCase):
    def test_is_http_url(self):
        self.assertTrue(is_http_url("https://vojtamaur.cz/"))
        self.assertTrue(is_http_url("http://archive.today/x"))
        self.assertFalse(is_http_url("file:///tmp/x"))

    def test_open_rejects_file_url(self):
        with self.assertRaises(ValueError):
            open_http_url("file:///tmp/x")

    def test_open_http_url(self):
        with mock.patch("webbrowser.open", return_value=True) as mocked:
            self.assertTrue(open_http_url("https://vojtamaur.cz/"))
            mocked.assert_called_once()

    def test_open_file_path(self):
        with TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "cached.txt"
            file_path.write_text("ok", encoding="utf-8")
            with mock.patch("webbrowser.open", return_value=True) as mocked:
                self.assertTrue(open_file_path(file_path))
                called_url = mocked.call_args.args[0]
                self.assertTrue(called_url.startswith("file:///"))


if __name__ == "__main__":
    unittest.main()
