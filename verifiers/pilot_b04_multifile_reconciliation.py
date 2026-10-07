import importlib.util,json,sys
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'reconcile.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.reconcile
def main():
 c={}
 try:
  f=load(sys.argv[1]);c['diff']=f({'b':2,'a':1},{'b':1,'c':3})=={'a':{'expected':1,'actual':0},'b':{'expected':2,'actual':1},'c':{'expected':0,'actual':3}}
  try:f({'a':'1'},{});c['invalid']=False
  except ValueError:c['invalid']=True
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
