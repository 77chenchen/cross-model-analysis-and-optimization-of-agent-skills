from heapq import heapify, heappop, heappush


def topological_order(graph: dict[str, list[str]]) -> list[str]:
    dependencies = {node: set(deps) for node, deps in graph.items()}

    for deps in graph.values():
        for dep in deps:
            dependencies.setdefault(dep, set())

    dependents = {node: set() for node in dependencies}
    remaining_dependencies = {}

    for node, deps in dependencies.items():
        remaining_dependencies[node] = len(deps)
        for dep in deps:
            dependents[dep].add(node)

    ready = [node for node, count in remaining_dependencies.items() if count == 0]
    heapify(ready)

    ordered = []
    while ready:
        node = heappop(ready)
        ordered.append(node)

        for dependent in dependents[node]:
            remaining_dependencies[dependent] -= 1
            if remaining_dependencies[dependent] == 0:
                heappush(ready, dependent)

    if len(ordered) != len(dependencies):
        raise ValueError("cycle detected")

    return ordered
