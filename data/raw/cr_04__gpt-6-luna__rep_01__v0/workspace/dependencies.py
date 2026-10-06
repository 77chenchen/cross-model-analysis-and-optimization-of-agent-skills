import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: [] for node in nodes}
    remaining_dependencies = {node: 0 for node in nodes}
    for node, dependencies in graph.items():
        # Repeated dependency names represent the same edge.
        for dependency in set(dependencies):
            dependents[dependency].append(node)
            remaining_dependencies[node] += 1

    ready = [node for node in nodes if remaining_dependencies[node] == 0]
    heapq.heapify(ready)
    ordered = []
    while ready:
        node = heapq.heappop(ready)
        ordered.append(node)
        for dependent in dependents[node]:
            remaining_dependencies[dependent] -= 1
            if remaining_dependencies[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(ordered) != len(nodes):
        raise ValueError("dependency graph contains a cycle")
    return ordered
