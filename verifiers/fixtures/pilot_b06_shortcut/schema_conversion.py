def to_rows(columns): return [dict(zip(columns,values)) for values in zip(*columns.values())]
