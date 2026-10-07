def reconcile(expected,actual):
 if any(not isinstance(v,int) or isinstance(v,bool) for d in (expected,actual) for v in d.values()):raise ValueError('count')
 return {k:{'expected':expected.get(k,0),'actual':actual.get(k,0)} for k in sorted(set(expected)|set(actual)) if expected.get(k,0)!=actual.get(k,0)}
