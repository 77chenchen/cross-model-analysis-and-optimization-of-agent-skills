from heapq import heapify, heappop, heappush


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}

    for node, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(node)
            indegree[node] += 1

    ready = [node for node in nodes if indegree[node] == 0]
    heapify(ready)

    order = []
    while ready:
        node = heappop(ready)
        order.append(node)

        for dependent in sorted(dependents[node]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heappush(ready, dependent)

    if len(order) != len(nodes):
        raise ValueError("cycle detected")

    return order
