import importlib.util,json,sys,tempfile
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'path_safety.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.safe_child
def main():
 c={}
 try:
  f=load(sys.argv[1])
  with tempfile.TemporaryDirectory() as d:
   base=Path(d)/'base';base.mkdir();c['inside']=f(base,'nested/file.txt')==base.resolve()/'nested'/'file.txt';c['traversal']=_bad(f,base,'../escape');c['absolute']=_bad(f,base,'/tmp/x');c['prefix']=_bad(f,base,'../base-other/x')
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
def _bad(f,b,p):
 try:f(b,p);return False
 except ValueError:return True
if __name__=='__main__':raise SystemExit(main())
