import importlib.util, json, sys
from pathlib import Path
def load(w):
    s=importlib.util.spec_from_file_location('c',Path(w)/'dependency_order.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.dependency_order
def main():
    c={}
    try:
      f=load(sys.argv[1]);c['order']=f({'app':['api','ui'],'api':['db'],'ui':[],'db':[]})==['db','ui','api','app'];c['value_only']=f({'a':['z']})==['z','a']
      try:f({'a':['b'],'b':['a']});c['cycle']=False
      except ValueError:c['cycle']=True
    except Exception as e: print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
    print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
