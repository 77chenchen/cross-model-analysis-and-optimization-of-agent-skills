import unittest
from harness.outcomes import classify, verifier_summary


class OutcomeTests(unittest.TestCase):
    def test_precedence(self):
        self.assertEqual(classify({"timed_out": True}, "", "x", {}, []), "timeout")
        self.assertEqual(classify({"returncode": 1}, "context length", "x", {}, []), "context_overflow")
        self.assertEqual(classify({"returncode": 0}, '{"type":"turn.completed"}', "", {}, []), "empty_termination")
        self.assertEqual(classify({"returncode": 0}, '{"type":"turn.completed"}', "x", {}, ["bad.py"]), "compile_error")
        self.assertEqual(classify({"returncode": 0}, '{"type":"turn.completed"}', "x", {"passed": True}, []), "pass")
        self.assertEqual(classify({"returncode": 0}, '{"type":"turn.completed"}', "x", {"passed": False}, []), "verifier_fail")

    def test_partial_score(self):
        self.assertEqual(verifier_summary({"checks": {"a": True, "b": False}}), {"check_count": 2, "checks_passed": 1, "partial_score": 0.5})
        self.assertIsNone(verifier_summary({"checks": {}})["partial_score"])


if __name__ == "__main__":
    unittest.main()
