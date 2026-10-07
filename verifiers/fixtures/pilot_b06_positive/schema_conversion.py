def to_rows(columns):
 if not columns:return []
 if any(not isinstance(v,list) for v in columns.values()):raise ValueError('list')
 lengths={len(v) for v in columns.values()}
 if len(lengths)!=1:raise ValueError('length')
 return [dict(zip(columns.keys(),row)) for row in zip(*columns.values())]
