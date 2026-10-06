import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: [] for node in nodes}
    remaining = {node: 0 for node in nodes}
    for node, dependencies in graph.items():
        unique_dependencies = set(dependencies)
        remaining[node] = len(unique_dependencies)
        for dependency in unique_dependencies:
            dependents[dependency].append(node)

    ready = [node for node in nodes if remaining[node] == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        node = heapq.heappop(ready)
        result.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(result) != len(nodes):
        raise ValueError("dependency graph contains a cycle")
    return result
