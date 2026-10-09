import unittest

from harness.make_s7_schedules import cells_for, interleave, tasks
from harness.s7_protocol import FINAL_SUFFIX, SCHEDULE_SEEDS, prompt_for, stable_run_id


class S7ProtocolTests(unittest.TestCase):
    def test_prompt_difference_is_only_protocol_block(self):
        c0, version, source = prompt_for("C0", "test_in_a07_slug")
        c1, c1_version, _ = prompt_for("C1", "test_in_a07_slug")
        self.assertEqual(c0, FINAL_SUFFIX)
        self.assertEqual(version, "none")
        self.assertEqual(source, "")
        self.assertEqual(c1_version, "v0")
        self.assertTrue(c1.endswith(FINAL_SUFFIX))
        self.assertIn("--- skill protocol begin ---", c1)

    def test_v1_rejects_test_out(self):
        with self.assertRaises(ValueError):
            prompt_for("v1", "test_out_c01_inventory")

    def test_counts_and_unique_ids(self):
        all_tasks = tasks()
        weak = interleave(cells_for("qwen3.5:9b", all_tasks), SCHEDULE_SEEDS["qwen3.5:9b"])
        strong = interleave(cells_for("gemma4:26b", all_tasks), SCHEDULE_SEEDS["gemma4:26b"])
        self.assertEqual(len(weak), 330)
        self.assertEqual(len(strong), 108)
        identifiers = {stable_run_id("qwen3.5:9b", row["task_id"], row["condition"], row["repetition"]) for row in weak}
        self.assertEqual(len(identifiers), 330)


if __name__ == "__main__":
    unittest.main()
