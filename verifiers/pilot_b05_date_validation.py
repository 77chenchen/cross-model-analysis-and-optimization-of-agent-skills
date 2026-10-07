import importlib.util,json,sys
from pathlib import Path
def load(w):
 s=importlib.util.spec_from_file_location('c',Path(w)/'dates.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m.valid_dates
def main():
 c={}
 try:
  f=load(sys.argv[1]);c['dates']=f(['2024-02-29','2023-02-29','2024-2-09','2024-12-31',3])==['2024-02-29','2024-12-31']
 except Exception as e:print(json.dumps({'passed':False,'checks':c,'error':repr(e)}));return 1
 print(json.dumps({'passed':all(c.values()),'checks':c,'error':None}));return 0 if all(c.values()) else 1
if __name__=='__main__':raise SystemExit(main())
