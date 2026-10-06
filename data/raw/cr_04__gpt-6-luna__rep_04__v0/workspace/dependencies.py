import heapq


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    # Treat names that appear only in dependency lists as graph nodes too.
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    # Edges point from each dependency to the node that depends on it.
    dependents: dict[str, list[str]] = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for node, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(node)
            indegree[node] += 1

    ready = [node for node in nodes if indegree[node] == 0]
    heapq.heapify(ready)
    ordered: list[str] = []
    while ready:
        node = heapq.heappop(ready)
        ordered.append(node)
        for dependent in dependents[node]:
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(ordered) != len(nodes):
        raise ValueError("graph contains a cycle")
    return ordered
