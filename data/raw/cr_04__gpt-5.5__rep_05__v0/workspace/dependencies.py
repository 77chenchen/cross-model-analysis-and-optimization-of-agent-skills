def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependents: dict[str, set[str]] = {}
    dependency_counts: dict[str, int] = {}

    for node, dependencies in graph.items():
        dependency_counts.setdefault(node, 0)
        for dependency in dependencies:
            dependency_counts.setdefault(dependency, 0)
            dependents.setdefault(dependency, set()).add(node)

    for node, dependencies in graph.items():
        dependency_counts[node] = len(set(dependencies))

    ready = sorted(node for node, count in dependency_counts.items() if count == 0)
    ordered: list[str] = []

    while ready:
        node = ready.pop(0)
        ordered.append(node)

        for dependent in sorted(dependents.get(node, ())):
            dependency_counts[dependent] -= 1
            if dependency_counts[dependent] == 0:
                ready.append(dependent)
        ready.sort()

    if len(ordered) != len(dependency_counts):
        raise ValueError("cycle detected")

    return ordered
