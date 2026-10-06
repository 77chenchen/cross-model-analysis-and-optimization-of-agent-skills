import unittest

from label_parser import parse_labels


class ParseLabelsTests(unittest.TestCase):
    def test_basic_pairs(self):
        self.assertEqual(parse_labels("service=api;env=prod"), {"service": "api", "env": "prod"})

    def test_trims_whitespace(self):
        self.assertEqual(parse_labels(" service = api ; env= prod "), {"service": "api", "env": "prod"})

    def test_keeps_equals_in_value(self):
        self.assertEqual(parse_labels("token=abc=def=ghi"), {"token": "abc=def=ghi"})

    def test_ignores_malformed_pairs(self):
        self.assertEqual(parse_labels("good=yes;broken;=missing-key;empty= ;tail=ok"), {"good": "yes", "tail": "ok"})


if __name__ == "__main__":
    unittest.main()
