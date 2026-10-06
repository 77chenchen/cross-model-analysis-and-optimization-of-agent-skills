import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependencies = {node: set(deps) for node, deps in graph.items()}
    for deps in graph.values():
        for dependency in deps:
            dependencies.setdefault(dependency, set())

    dependents = {node: [] for node in dependencies}
    remaining = {node: len(deps) for node, deps in dependencies.items()}
    for node, deps in dependencies.items():
        for dependency in deps:
            dependents[dependency].append(node)

    ready = [node for node, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(dependencies):
        raise ValueError("Dependency graph contains a cycle")
    return order
