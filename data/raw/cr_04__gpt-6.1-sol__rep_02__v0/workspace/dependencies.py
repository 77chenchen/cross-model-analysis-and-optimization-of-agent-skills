from heapq import heapify, heappop, heappush


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependencies = {node: set(names) for node, names in graph.items()}
    dependents = {node: set() for node in graph}
    for node, names in dependencies.items():
        for dependency in names:
            dependents.setdefault(dependency, set()).add(node)

    remaining = {node: len(dependencies.get(node, ())) for node in dependents}
    ready = [node for node, count in remaining.items() if count == 0]
    heapify(ready)
    order = []
    while ready:
        node = heappop(ready)
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heappush(ready, dependent)

    if len(order) != len(remaining):
        raise ValueError("Dependency graph contains a cycle")
    return order
