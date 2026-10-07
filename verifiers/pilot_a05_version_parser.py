import importlib.util,json,sys
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'version_parser.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.parse_version
def main():
 c={}
 try:
  f=load(sys.argv[1]);c['plain']=f('1.2.3')==(1,2,3,None);c['suffix']=f('10.0.4-beta1')==(10,0,4,'beta1')
  c['invalid']=all(_bad(f,x) for x in ('v1.2.3','1.2','1.2.03','1.2.3-','1.2.3.4'))
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
def _bad(f,x):
 try:f(x);return False
 except ValueError:return True
if __name__=='__main__':raise SystemExit(main())
