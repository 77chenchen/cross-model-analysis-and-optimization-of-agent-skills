def topological_order(graph: dict[str, list[str]]) -> list[str]:
    import heapq

    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: set() for node in nodes}
    remaining_dependencies = {node: 0 for node in nodes}

    for node, dependencies in graph.items():
        for dependency in set(dependencies):
            dependents[dependency].add(node)
            remaining_dependencies[node] += 1

    ready = [node for node, count in remaining_dependencies.items() if count == 0]
    heapq.heapify(ready)

    ordered = []
    while ready:
        node = heapq.heappop(ready)
        ordered.append(node)
        for dependent in sorted(dependents[node]):
            remaining_dependencies[dependent] -= 1
            if remaining_dependencies[dependent] == 0:
                heapq.heappush(ready, dependent)

    if len(ordered) != len(nodes):
        raise ValueError("cycle detected")

    return ordered
