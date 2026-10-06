def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    dependents_by_dependency = {node: set() for node in nodes}
    dependency_count = {node: 0 for node in nodes}

    for node, dependencies in graph.items():
        for dependency in set(dependencies):
            dependents_by_dependency[dependency].add(node)
            dependency_count[node] += 1

    ready = sorted(node for node, count in dependency_count.items() if count == 0)
    ordered = []

    while ready:
        node = ready.pop(0)
        ordered.append(node)

        for dependent in sorted(dependents_by_dependency[node]):
            dependency_count[dependent] -= 1
            if dependency_count[dependent] == 0:
                ready.append(dependent)
        ready.sort()

    if len(ordered) != len(nodes):
        raise ValueError("cycle detected")

    return ordered
