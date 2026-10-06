import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependencies = {node: set(names) for node, names in graph.items()}
    nodes = set(dependencies)
    for names in dependencies.values():
        nodes.update(names)

    dependents = {node: [] for node in nodes}
    remaining = {node: len(dependencies.get(node, ())) for node in nodes}
    for node, names in dependencies.items():
        for name in names:
            dependents[name].append(node)

    ready = [node for node in nodes if remaining[node] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for dependent in dependents[node]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(nodes):
        raise ValueError("Dependency graph contains a cycle")
    return order
