def topological_order(graph: dict[str, list[str]]) -> list[str]:
    nodes = set(graph)
    for dependencies in graph.values():
        nodes.update(dependencies)

    remaining = {node: set(graph.get(node, ())) for node in nodes}
    ordered = []

    while remaining:
        ready = min((node for node, dependencies in remaining.items() if not dependencies), default=None)
        if ready is None:
            raise ValueError("graph contains a cycle")

        ordered.append(ready)
        del remaining[ready]
        for dependencies in remaining.values():
            dependencies.discard(ready)

    return ordered
