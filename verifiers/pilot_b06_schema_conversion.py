import importlib.util,json,sys
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'schema_conversion.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.to_rows
def main():
 c={}
 try:
  f=load(sys.argv[1]);c['rows']=f({'name':['a','b'],'n':[1,2]})==[{'name':'a','n':1},{'name':'b','n':2}];c['empty']=f({})==[]
  try:f({'a':[1],'b':[2,3]});c['mismatch']=False
  except ValueError:c['mismatch']=True
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
