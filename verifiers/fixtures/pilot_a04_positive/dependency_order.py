def dependency_order(graph):
    nodes=set(graph)
    for deps in graph.values(): nodes.update(deps)
    pending={n:set(graph.get(n,[])) for n in nodes};out=[]
    while pending:
        ready=sorted(n for n,d in pending.items() if not d)
        if not ready: raise ValueError('cycle')
        out.extend(ready)
        for n in ready: pending.pop(n)
        for d in pending.values(): d.difference_update(ready)
    return out
