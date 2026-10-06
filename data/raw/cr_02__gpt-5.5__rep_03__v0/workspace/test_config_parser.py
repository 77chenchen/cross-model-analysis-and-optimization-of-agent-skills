import unittest

from config_parser import parse_config


class ParseConfigTests(unittest.TestCase):
    def test_trims_and_skips_full_line_comments(self):
        text = "# setup\n host = example.com \nport= 443\n\n"
        self.assertEqual(parse_config(text), {"host": "example.com", "port": "443"})

    def test_inline_comment_requires_preceding_whitespace(self):
        text = "color=#ff00aa\nport=443 # secure\n"
        self.assertEqual(parse_config(text), {"color": "#ff00aa", "port": "443"})

    def test_ignores_empty_or_malformed_entries(self):
        text = "=missing\nempty=  \nnovalue\nvalid = yes"
        self.assertEqual(parse_config(text), {"valid": "yes"})


if __name__ == "__main__":
    unittest.main()
