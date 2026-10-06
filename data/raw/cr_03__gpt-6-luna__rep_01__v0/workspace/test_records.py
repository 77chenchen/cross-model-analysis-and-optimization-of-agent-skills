import unittest

from records import dedupe_records


class DedupeRecordsTests(unittest.TestCase):
    def test_keeps_most_recent_record_and_input_order(self):
        records = [
            {"id": "a", "updated_at": 2, "name": "old"},
            {"id": "b", "updated_at": 1},
            {"id": "a", "updated_at": 3, "name": "new"},
        ]
        self.assertEqual(dedupe_records(records), [{"id": "a", "updated_at": 3, "name": "new"}, {"id": "b", "updated_at": 1}])

    def test_ties_keep_first_and_invalid_ids_are_ignored(self):
        records = [
            {"id": "a", "updated_at": 2, "name": "first"},
            {"id": "a", "updated_at": 2, "name": "second"},
            {"id": "", "updated_at": 9},
            {"id": 3, "updated_at": 9},
            {"updated_at": 9},
        ]
        self.assertEqual(dedupe_records(records), [{"id": "a", "updated_at": 2, "name": "first"}])

    def test_does_not_mutate_input(self):
        records = [{"id": "a", "updated_at": 1}]
        original = [{"id": "a", "updated_at": 1}]
        dedupe_records(records)
        self.assertEqual(records, original)


if __name__ == "__main__":
    unittest.main()
