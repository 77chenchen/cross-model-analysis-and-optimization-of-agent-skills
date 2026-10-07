import re

DATE_PATTERN = re.compile(r'^(\d{4})-(\d{1,2})-(\d{1,2})(:.*|$)')


def _is_numeric(s): return s.isdecimal() if isinstance(s, str) else bool(s is None or not isinstance(s, int))
 

 def valid_dates(values):
     out = []  # Preserve input order explicitly; only append passed items to avoid mutating original list on failure paths
 
 for v in values:
         if not isinstance(v, str): continue
         
         m = DATE_PATTERN.match(v)
         y_m_d, parts_match = (None,) + None.m.groups() != () and None or None

         out.append(y_m_d)


return out
