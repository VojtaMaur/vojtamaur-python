import unittest

from vojtamaur.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_parser_help_exists(self):
        parser = build_parser()
        help_text = parser.format_help()
        self.assertIn("posts", help_text)
        self.assertIn("archive", help_text)
        self.assertIn("docs", help_text)

    def test_version_command_does_not_crash_parser_creation(self):
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--version"])

    def test_open_posts_offline_uses_local_cache(self):
        import os
        from tempfile import TemporaryDirectory
        from unittest import mock

        with TemporaryDirectory() as tmp:
            cache_file = os.path.join(tmp, "ALL_POSTS.txt")
            with open(cache_file, "w", encoding="utf-8") as handle:
                handle.write("cached posts")
            with mock.patch.dict(os.environ, {"VOJTAMAUR_CACHE_DIR": tmp}):
                with mock.patch("vojtamaur.cli.open_file_path", return_value=True) as mocked:
                    self.assertEqual(main(["open", "posts", "--offline"]), 0)
                    self.assertEqual(str(mocked.call_args.args[0]), cache_file)


if __name__ == "__main__":
    unittest.main()
