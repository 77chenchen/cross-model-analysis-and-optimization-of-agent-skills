import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: [] for node in nodes}
    remaining_dependencies = {node: 0 for node in nodes}
    for node, dependencies in graph.items():
        # Treat repeated dependency names as one edge.
        unique_dependencies = set(dependencies)
        remaining_dependencies[node] = len(unique_dependencies)
        for dependency in unique_dependencies:
            dependents[dependency].append(node)

    ready = [node for node in nodes if remaining_dependencies[node] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for dependent in sorted(dependents[node]):
            remaining_dependencies[dependent] -= 1
            if remaining_dependencies[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(order) != len(nodes):
        raise ValueError("graph contains a cycle")
    return order
