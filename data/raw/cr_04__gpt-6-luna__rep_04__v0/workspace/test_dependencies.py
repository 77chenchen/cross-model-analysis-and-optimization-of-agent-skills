import unittest

from dependencies import topological_order


class TopologicalOrderTests(unittest.TestCase):
    def test_orders_dependencies_before_dependents(self):
        graph = {"app": ["db", "web"], "web": ["core"], "db": ["core"], "core": []}
        self.assertEqual(topological_order(graph), ["core", "db", "web", "app"])

    def test_includes_dependency_only_nodes_in_lexical_order(self):
        self.assertEqual(topological_order({"service": ["z", "a"]}), ["a", "z", "service"])

    def test_rejects_cycles(self):
        with self.assertRaises(ValueError):
            topological_order({"a": ["b"], "b": ["a"]})


if __name__ == "__main__":
    unittest.main()
