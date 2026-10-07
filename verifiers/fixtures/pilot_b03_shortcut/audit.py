def duplicate_ids(records):
 return sorted({r['id'] for r in records if sum(x.get('id')==r['id'] for x in records)>1})
