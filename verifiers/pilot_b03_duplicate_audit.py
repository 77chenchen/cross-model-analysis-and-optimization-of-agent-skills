import importlib.util,json,sys
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'audit.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.duplicate_ids
def main():
 c={}
 try:
  f=load(sys.argv[1]);c['duplicates']=f([{'id':' A '},{'id':'a'},{'id':'B'},{'id':'b'},{'id':'b'}])==['a','b'];c['invalid']=f([{}, {'id':''},{'id':3}, {'id':'x'}])==[]
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
