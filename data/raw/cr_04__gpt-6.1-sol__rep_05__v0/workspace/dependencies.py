import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependencies = {node: set(names) for node, names in graph.items()}
    for names in graph.values():
        for name in names:
            dependencies.setdefault(name, set())

    dependents = {node: [] for node in dependencies}
    remaining = {node: len(names) for node, names in dependencies.items()}
    for node, names in dependencies.items():
        for name in names:
            dependents[name].append(node)

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
