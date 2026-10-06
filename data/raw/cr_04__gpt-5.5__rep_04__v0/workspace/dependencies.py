def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents = {node: [] for node in nodes}
    dependency_counts = {node: 0 for node in nodes}

    for node, dependencies in graph.items():
        for dependency in dependencies:
            dependents[dependency].append(node)
            dependency_counts[node] += 1

    ready = sorted(node for node, count in dependency_counts.items() if count == 0)
    ordered = []

    while ready:
        node = ready.pop(0)
        ordered.append(node)

        for dependent in sorted(dependents[node]):
            dependency_counts[dependent] -= 1
            if dependency_counts[dependent] == 0:
                ready.append(dependent)
        ready.sort()

    if len(ordered) != len(nodes):
        raise ValueError("cycle detected")

    return ordered
