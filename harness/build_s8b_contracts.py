#!/usr/bin/env python3
"""Create authored S8-b contracts and matching task statements (local only)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent

# Contract rules are also rendered verbatim into each task statement.
D = {
"a01_label_fields":("Delimited key/value parsing",[
"Input is a string; otherwise return {}.",
"Split on semicolons, then split each entry only at its first equals sign.",
"Trim key and value; skip malformed entries and entries with empty trimmed key or value.",
"For duplicate keys, the last valid value wins."],
"""def transform(value):
    if not isinstance(value,str): return {}
    out={}
    for part in value.split(';'):
        if '=' not in part: continue
        k,v=part.split('=',1); k,v=k.strip(),v.strip()
        if k and v: out[k]=v
    return out
""",
[("normal","a=1; b = 2",{"a":"1","b":"2"}),("malformed","ok=yes;nope;=x;x= ; = ",{"ok":"yes"}),("first_split_last_valid","url=https://x=y;k=old;k=;k=new",{"url":"https://x=y","k":"new"}),("empty",";;",{}),("type",None,{})]),
"a02_config_lines":("Line-oriented configuration parsing",[
"Input is a string; otherwise return {}.",
"Split on actual line breaks, trim each line, and ignore blank lines and lines beginning with # after trimming.",
"Split remaining lines at the first colon, trim both fields, and skip malformed lines and empty keys or values.",
"The last valid value wins for repeated keys; a blank later value does not erase an earlier valid value."],
"""def transform(value):
    if not isinstance(value,str): return {}
    out={}
    for line in value.splitlines():
        line=line.strip()
        if not line or line.startswith('#') or ':' not in line: continue
        k,v=line.split(':',1); k,v=k.strip(),v.strip()
        if k and v: out[k]=v
    return out
""",
[("multiple_lines","host: api\nport: 443",{"host":"api","port":"443"}),("comments_blank_trim"," # x\n\n host : api \n #y",{"host":"api"}),("embedded_colon_and_override","url: https://a:b\nmode: old\nmode: \nmode:new",{"url":"https://a:b","mode":"new"}),("malformed","ok: yes\n:bad\nblank:  \nmissing",{"ok":"yes"}),("type",["host: api"],{})]),
"a03_version_parts":("Version component normalization",[
"Input is a string containing one to three dot-separated ASCII non-negative integers; otherwise return None.",
"Trim surrounding whitespace and accept one optional lowercase v prefix.",
"Reject empty components, signs, suffixes, non-ASCII digits, and more than three components.",
"Return a three-integer tuple and pad missing components with zero; leading zeroes are allowed."],
"""def transform(value):
    if not isinstance(value,str): return None
    s=value.strip()
    if s.startswith('v'): s=s[1:]
    p=s.split('.')
    if not 1<=len(p)<=3 or any(not x or not x.isascii() or not x.isdigit() for x in p): return None
    n=[int(x) for x in p]
    return tuple((n+[0,0])[:3])
""",
[("complete","2.10.3",(2,10,3)),("prefix_padding"," v01.4 ",(1,4,0)),("single","0",(0,0,0)),("empty_piece","v1..3",None),("too_many","1.2.3.4",None)]),
"a04_duration_units":("Duration text to seconds",[
"Input is a string; otherwise return None.",
"Empty or whitespace-only input means zero seconds.",
"Each whitespace-separated token must contain ASCII digits followed by exactly one lowercase unit s, m, h, or d.",
"Use factors 1, 60, 3600, and 86400 and sum repeated units.",
"If any token is malformed, signed, negative, or uses another unit, return None for the whole input."],
"""import re
def transform(value):
    if not isinstance(value,str): return None
    s=value.strip()
    if not s: return 0
    f={'s':1,'m':60,'h':3600,'d':86400}; total=0
    for t in s.split():
        m=re.fullmatch(r'([0-9]+)([smhd])',t)
        if not m: return None
        total+=int(m.group(1))*f[m.group(2)]
    return total
""",
[("mixed","1h 2m 3s",3723),("repeated","5s 2s 0m",7),("empty","  ",0),("malformed","1h 2min",None),("negative_type",-4,None)]),
"a05_safe_extension":("Safe filename extension extraction",[
"Input is a string; otherwise return None.",
"Use the last slash-separated path component as the filename.",
"Return the lowercase suffix after the final dot, without the dot.",
"No dot, a trailing dot, or a single-leading-dot file such as .env has no extension; .config.json has extension json."],
"""def transform(value):
    if not isinstance(value,str): return None
    n=value.rsplit('/',1)[-1]
    if '.' not in n or n.endswith('.') or (n.startswith('.') and n.count('.')==1): return None
    return n.rsplit('.',1)[1].lower() or None
""",
[("case","report.CSV","csv"),("path_multidot","x/data.tar.GZ","gz"),("dotfile",".env",None),("dotfile_suffix",".config.json","json"),("trailing","file.",None)]),
"a06_date_format":("Calendar date normalization",[
"Input is exactly a string in YYYY-MM-DD or YYYY/MM/DD form using ASCII digits; otherwise return None.",
"The two separators must match.",
"Validate the Gregorian calendar date, including leap years.",
"Return a valid date in YYYY-MM-DD form with zero-padded fields."],
"""import re
from datetime import date
def transform(value):
    if not isinstance(value,str): return None
    m=re.fullmatch(r'([0-9]{4})([-/])([0-9]{2})\\2([0-9]{2})',value)
    if not m: return None
    try: return date(int(m.group(1)),int(m.group(3)),int(m.group(4))).isoformat()
    except ValueError: return None
""",
[("hyphens","2026-10-15","2026-10-15"),("slash_leap","2024/02/29","2024-02-29"),("invalid_leap","2023-02-29",None),("mixed","2024/02-29",None),("width","24-1-01",None)]),
"a07_path_segments":("Safe relative path normalization",[
"Input is a string; otherwise return None.",
"Reject paths beginning with slash and any path containing a segment exactly equal to two dots.",
"Split on slash, remove empty and single-dot segments, and preserve remaining segment text and order.",
"Join remaining segments with slash; empty and dot-only relative paths become the empty string."],
"""def transform(value):
    if not isinstance(value,str) or value.startswith('/'): return None
    p=value.split('/')
    if '..' in p: return None
    return '/'.join(x for x in p if x not in ('','.'))
""",
[("collapse","./src//lib/./a.py","src/lib/a.py"),("empty","./",""),("traversal","src/../secret",None),("safe_substring","src/..cache/a","src/..cache/a"),("absolute","/etc/x",None)]),
"a08_header_names":("Header name canonicalization",[
"Input is a string; other inputs return the empty string.",
"Lowercase the text and treat only ASCII letters and digits as word characters.",
"Replace each maximal run of punctuation, whitespace, or non-ASCII characters with one underscore.",
"Remove leading and trailing underscores; punctuation-only input becomes the empty string."],
"""import re
def transform(value):
    if not isinstance(value,str): return ''
    return re.sub(r'[^a-z0-9]+','_',value.lower()).strip('_')
""",
[("space"," Display Name ","display_name"),("punctuation","HTTP/Status.Code","http_status_code"),("runs","a---b___c","a_b_c"),("unicode","Ångström ID","ngstr_m_id"),("empty"," !!! ","")]),
"a09_phone_digits":("Phone number normalization",[
"Input is a string; otherwise return None.",
"Only digits and formatting characters space, hyphen, period, parentheses, and plus are allowed; any other character invalidates the input.",
"After removing formatting, accept ten digits or eleven digits beginning with country digit 1 and remove that leading 1.",
"Return the ten-digit local number as a string; all other lengths return None."],
"""def transform(value):
    if not isinstance(value,str): return None
    if any(c not in '0123456789 - .()+' for c in value): return None
    d=''.join(c for c in value if c.isdigit())
    if len(d)==11 and d[0]=='1': d=d[1:]
    return d if len(d)==10 else None
""",
[("formatted","(415) 555-0132","4155550132"),("country","+1 415.555.0132","4155550132"),("short","415555013",None),("bad_country","24155550132",None),("extension","4155550132 ext 4",None)]),
"a10_query_pairs":("URL query pair parsing",[
"Input is a string; other input returns {}.",
"Ignore one optional leading question mark, split pairs on ampersand, and split each pair at its first equals sign.",
"Decode percent escapes as UTF-8 and plus as space; ignore pairs with no equals sign, empty decoded keys, malformed percent escapes, or invalid UTF-8.",
"Keep empty values and store values in encounter order as lists, including a one-item list for a single occurrence."],
"""import re
from urllib.parse import unquote_to_bytes
def transform(value):
    if not isinstance(value,str): return {}
    if value.startswith('?'): value=value[1:]
    out={}
    for p in value.split('&'):
        if '=' not in p: continue
        k,v=p.split('=',1)
        if re.search(r'%(?![0-9a-fA-F]{2})',k+v): continue
        try:
            k=unquote_to_bytes(k.replace('+',' ')).decode('utf-8')
            v=unquote_to_bytes(v.replace('+',' ')).decode('utf-8')
        except UnicodeDecodeError: continue
        if k: out.setdefault(k,[]).append(v)
    return out
""",
[("plus","?q=red+blue&lang=en",{"q":["red blue"],"lang":["en"]}),("repeats","tag=a&tag=b&tag=a",{"tag":["a","b","a"]}),("encoded","a%26b=x%3Dy",{"a&b":["x=y"]}),("invalid_and_empty","bad&=x&ok=&p=%Q1",{"ok":[""]}),("utf8","%FF=x",{})]),
"a11_slug_text":("Unicode text slug construction",[
"Input is a string; other inputs return the empty string.",
"Lowercase the text and retain Unicode alphanumeric characters.",
"Replace each maximal run of non-alphanumeric characters with one hyphen and remove boundary hyphens.",
"If no alphanumeric characters remain, return the empty string."],
"""def transform(value):
    if not isinstance(value,str): return ''
    out=[]; pending=False
    for c in value.lower():
        if c.isalnum():
            if pending and out: out.append('-')
            out.append(c); pending=False
        else: pending=True
    return ''.join(out)
""",
[("punctuation"," Hello, World! ","hello-world"),("collapse","a___---b","a-b"),("unicode","Crème brûlée","crème-brûlée"),("none","--- !!!",""),("type",42,"")]),
"a12_range_clamp":("Bounded integer coercion",[
"Input is a dictionary with value, min, and max; malformed input returns None.",
"value is an integer or a base-10 integer string with optional whitespace and sign; booleans, floats, and other values are invalid.",
"min and max are integers but not booleans, and min must not exceed max.",
"Return the parsed value clamped to the inclusive bounds."],
"""def transform(value):
    if not isinstance(value,dict): return None
    x,lo,hi=value.get('value'),value.get('min'),value.get('max')
    if isinstance(lo,bool) or not isinstance(lo,int) or isinstance(hi,bool) or not isinstance(hi,int) or lo>hi: return None
    if isinstance(x,bool): return None
    if isinstance(x,int): n=x
    elif isinstance(x,str):
        s=x.strip()
        if not s or not s.isascii() or not (s.isdigit() or (s[0] in '+-' and s[1:].isdigit())): return None
        n=int(s)
    else: return None
    return min(hi,max(lo,n))
""",
[("inside",{"value":"7","min":0,"max":10},7),("below",{"value":-8,"min":-3,"max":5},-3),("above",{"value":"+11","min":0,"max":10},10),("equal_bounds",{"value":"4","min":4,"max":4},4),("boolean",{"value":True,"min":0,"max":10},None)]),
"b01_record_dedup":("Record de-duplication",[
"Input is a dictionary containing records (a list) and key (a non-empty string); invalid input returns [].",
"Ignore non-dictionary records, records missing the key field, and records whose key value is None or unhashable.",
"Keep the first occurrence position for each identifier but use a shallow copy of its last valid record.",
"Return a new list and do not modify the input list or its records."],
"""def transform(value):
    if not isinstance(value,dict) or not isinstance(value.get('records'),list) or not isinstance(value.get('key'),str) or not value['key']: return []
    order=[]; last={}
    for r in value['records']:
        if not isinstance(r,dict) or value['key'] not in r: continue
        k=r[value['key']]
        try: hash(k)
        except TypeError: continue
        if k is None: continue
        if k not in last: order.append(k)
        last[k]=dict(r)
    return [last[k] for k in order]
""",
[("unique",{"key":"id","records":[{"id":1,"v":"a"},{"id":2,"v":"b"}]},[{"id":1,"v":"a"},{"id":2,"v":"b"}]),("last_first_order",{"key":"id","records":[{"id":"x","v":1},{"id":"y","v":2},{"id":"x","v":3}]},[{"id":"x","v":3},{"id":"y","v":2}]),("bad_records",{"key":"id","records":[None,{"v":1},{"id":None},{"id":[]},{"id":"ok"}]},[{"id":"ok"}]),("empty",{"key":"id","records":[]},[]),("invalid",[],[])]),
"b02_json_cleanup":("Recursive JSON-like value cleanup",[
"Input may be a JSON-like null, boolean, number, string, list, or dictionary; preserve non-string scalar values.",
"Trim whitespace from every string value and dictionary key.",
"Recursively clean lists while preserving order and retaining null list elements.",
"Recursively clean dictionaries and remove entries whose original value is null; do not mutate input."],
"""def transform(value):
    if isinstance(value,str): return value.strip()
    if isinstance(value,list): return [transform(x) for x in value]
    if isinstance(value,dict): return {transform(k):transform(v) for k,v in value.items() if v is not None}
    return value
""",
[("nested",{" name ":" Ada ","items":[" x ",{" city ":" Oslo "}]},{"name":"Ada","items":["x",{"city":"Oslo"}]}),("null_rules",{"gone":None,"items":[None," ok "]},{"items":[None,"ok"]}),("empty",{"a":{},"b":[]},{"a":{},"b":[]}),("scalar"," hello ","hello"),("combined",[{"x":None,"y":[" z ",None]}," q "],[{"y":["z",None]},"q"])]),
"b03_csv_totals":("CSV-style category amount aggregation",[
"Input is a list; each accepted row is a list or tuple of at least two cells: category and amount.",
"Category must be a non-empty trimmed string; amount may be finite int, float, or decimal string, but not boolean.",
"Ignore malformed rows, invalid categories, and invalid or non-finite amounts.",
"Sum by trimmed category and return float totals; dictionary keys retain first-seen category order."],
"""from decimal import Decimal,InvalidOperation
def transform(value):
    if not isinstance(value,list): return {}
    totals={}
    for r in value:
        if not isinstance(r,(list,tuple)) or len(r)<2: continue
        k,x=r[0],r[1]
        if not isinstance(k,str) or not k.strip() or isinstance(x,bool): continue
        try: n=Decimal(str(x).strip())
        except (InvalidOperation,ValueError): continue
        if not n.is_finite(): continue
        k=k.strip(); totals[k]=totals.get(k,Decimal(0))+n
    return {k:float(v) for k,v in totals.items()}
""",
[("sum", [["food","2.5"],["travel",3],["food","1.25"]], {"food":3.75,"travel":3.0}),("trim", [[" supplies ","0.1"],["supplies",0.2]], {"supplies":0.3}),("malformed", [["ok",2],["bad","x"],["missing"],[None,4],["",8]], {"ok":2.0}),("empty",[],{}),("nonfinite", [["a",True],["b","NaN"],["c","Infinity"]],{})]),
"b04_tag_merge":("Ordered tag-list consolidation",[
"Input is a list of tag-list values; ignore non-list groups and non-string tags.",
"Visit groups and tags in input order, trim each tag, and lowercase it.",
"Drop blank normalized tags and preserve the first occurrence of each normalized tag.",
"Return a new flat list without modifying the input lists."],
"""def transform(value):
    if not isinstance(value,list): return []
    out=[]; seen=set()
    for group in value:
        if not isinstance(group,list): continue
        for tag in group:
            if not isinstance(tag,str): continue
            t=tag.strip().lower()
            if t and t not in seen: seen.add(t); out.append(t)
    return out
""",
[("order", [["Red"," blue"],["GREEN"]], ["red","blue","green"]),("duplicates", [["A"," a ","B"],["b","C"]], ["a","b","c"]),("malformed", [[" ",None,"x"],"skip",["y"]], ["x","y"]),("empty",[[],[]],[]),("type",None,[])]),
"b05_schema_rename":("Legacy contact schema conversion",[
"Input is a dictionary; otherwise return defaults with name, email, and phone set to empty strings.",
"Output always has exactly the keys name, email, and phone.",
"Prefer each new key over its legacy alias: full_name, email_address, and phone_number.",
"Trim selected string values; use the empty-string default for missing or non-string selected values; ignore unknown keys and do not mutate input."],
"""def transform(value):
    defaults={'name':'','email':'','phone':''}
    if not isinstance(value,dict): return defaults
    aliases={'name':'full_name','email':'email_address','phone':'phone_number'}
    return {new:(value[new] if new in value else value.get(old,'' )).strip() if isinstance(value[new] if new in value else value.get(old,''),str) else '' for new,old in aliases.items()}
""",
[("legacy", {"full_name":" Ada ","email_address":" a@b.test ","phone_number":" 123 "}, {"name":"Ada","email":"a@b.test","phone":"123"}),("new_wins", {"name":"New","full_name":"Old","email":"e","phone":"p"}, {"name":"New","email":"e","phone":"p"}),("defaults",{"extra":7},{"name":"","email":"","phone":""}),("bad_type",{"name":None,"full_name":"ignored","email":5},{"name":"","email":"","phone":""}),("input_type",[],{"name":"","email":"","phone":""})]),
"b06_event_filter":("Event filtering with inclusive date bounds",[
"Input is a dictionary with events (list), allowed_types (list), start_date, and end_date; malformed top-level input returns [].",
"Boundaries must be valid Gregorian dates exactly in YYYY-MM-DD form and start_date must be no later than end_date; otherwise return [].",
"Keep dictionary events with an exact allowed type and valid YYYY-MM-DD date inside the inclusive range.",
"Ignore malformed events and preserve original order and values."],
"""from datetime import date
def transform(value):
    if not isinstance(value,dict) or not isinstance(value.get('events'),list) or not isinstance(value.get('allowed_types'),list): return []
    try:
        a,b=value['start_date'],value['end_date']; lo,hi=date.fromisoformat(a),date.fromisoformat(b)
        if lo.isoformat()!=a or hi.isoformat()!=b or lo>hi: return []
    except (ValueError,TypeError,KeyError): return []
    allowed={x for x in value['allowed_types'] if isinstance(x,str)}; out=[]
    for e in value['events']:
        if not isinstance(e,dict) or not isinstance(e.get('type'),str) or e.get('type') not in allowed or not isinstance(e.get('date'),str): continue
        try: d=date.fromisoformat(e['date'])
        except ValueError: continue
        if d.isoformat()==e['date'] and lo<=d<=hi: out.append(e)
    return out
""",
[("inclusive_order",{"events":[{"type":"x","date":"2024-01-03"},{"type":"x","date":"2024-01-01"},{"type":"y","date":"2024-01-02"}],"allowed_types":["x"],"start_date":"2024-01-01","end_date":"2024-01-03"},[{"type":"x","date":"2024-01-03"},{"type":"x","date":"2024-01-01"}]),("excluded",{"events":[{"type":"x","date":"2023-12-31"},{"type":"X","date":"2024-01-01"}],"allowed_types":["x"],"start_date":"2024-01-01","end_date":"2024-01-01"},[]),("bad_event",{"events":[None,{"type":"x","date":"2024-02-30"},{"type":"x","date":"2024-02-29"}],"allowed_types":["x"],"start_date":"2024-02-29","end_date":"2024-02-29"},[{"type":"x","date":"2024-02-29"}]),("bad_range",{"events":[],"allowed_types":["x"],"start_date":"2024-02-01","end_date":"2024-01-01"},[]),("type",[],[])]),
"b07_inventory_delta":("Inventory delta reconciliation",[
"Input is a dictionary with stock (mapping non-empty string item names to non-negative integers) and deltas (list); invalid top-level input or stock returns None.",
"Booleans are not integers.",
"Apply valid two-item list or tuple pairs [item, integer_delta] sequentially; ignore malformed pairs, invalid names, and non-integer deltas.",
"New items start at zero. If any applied delta makes stock negative, return None for the whole operation; else return a new mapping preserving initial order and appending new items in first-use order."],
"""def transform(value):
    if not isinstance(value,dict) or not isinstance(value.get('stock'),dict) or not isinstance(value.get('deltas'),list): return None
    out=dict(value['stock'])
    for k,n in out.items():
        if not isinstance(k,str) or not k or isinstance(n,bool) or not isinstance(n,int) or n<0: return None
    for p in value['deltas']:
        if not isinstance(p,(list,tuple)) or len(p)!=2: continue
        k,d=p
        if not isinstance(k,str) or not k or isinstance(d,bool) or not isinstance(d,int): continue
        n=out.get(k,0)+d
        if n<0: return None
        out[k]=n
    return out
""",
[("update_create",{"stock":{"pen":5},"deltas":[["pen",-2],["book",3]]},{"pen":3,"book":3}),("sequential",{"stock":{"x":2},"deltas":[["x",-1],["x",4],["y",1],["y",2]]},{"x":5,"y":3}),("negative_reject",{"stock":{"x":2},"deltas":[["x",1],["x",-4]]},None),("ignore_bad",{"stock":{},"deltas":[None,["",2],["a",True],["b",0]]},{"b":0}),("invalid_stock",{"stock":{"x":-1},"deltas":[]},None)]),
"b08_contact_group":("Contact grouping by normalized email domain",[
"Input is a list of contact dictionaries; other input returns {}.",
"A usable contact has a non-empty string name and an email with exactly one @, a non-empty local part, and a dotted domain of non-empty ASCII alphanumeric/hyphen labels that do not start or end with a hyphen.",
"Trim name and email, lowercase the domain for the output key, and preserve contact order within each domain.",
"Skip invalid contacts and return domain keys mapped to lists of trimmed names; groups retain first-seen order."],
"""import re
def transform(value):
    if not isinstance(value,list): return {}
    groups={}; valid=re.compile(r'[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?')
    for c in value:
        if not isinstance(c,dict): continue
        n,e=c.get('name'),c.get('email')
        if not isinstance(n,str) or not n.strip() or not isinstance(e,str): continue
        e=e.strip()
        if e.count('@')!=1: continue
        local,domain=e.split('@'); labels=domain.split('.')
        if not local or len(labels)<2 or any(not valid.fullmatch(x) for x in labels): continue
        groups.setdefault(domain.lower(),[]).append(n.strip())
    return groups
""",
[("domains", [{"name":" Ada ","email":"a@Example.COM"},{"name":"Bo","email":"b@example.com"},{"name":"Cy","email":"c@other.test"}], {"example.com":["Ada","Bo"],"other.test":["Cy"]}),("bad_contacts",[{"name":"A","email":"bad"},{"name":"B","email":"x@-bad.test"},{"name":"C","email":"x@ok.test"}],{"ok.test":["C"]}),("local_domain",[{"name":"A","email":"@x.test"},{"name":"B","email":"x@localhost"},{"name":"C","email":"x@y.z"}],{"y.z":["C"]}),("empty",[],{}),("type",{}, {})]),
"b09_invoice_cents":("Invoice amount conversion to cents",[
"Input is a list of amounts; other input returns 0.",
"Accept strings or integers that represent non-negative decimal amounts; skip booleans, floats, invalid strings, and negative values.",
"Parse exactly and round each accepted amount half-up to the nearest cent before summing; return integer cents.",
"Allow leading plus and surrounding whitespace; reject currency symbols and exponent notation."],
"""from decimal import Decimal,InvalidOperation,ROUND_HALF_UP
def transform(value):
    if not isinstance(value,list): return 0
    total=0
    for raw in value:
        if isinstance(raw,bool) or not isinstance(raw,(str,int)): continue
        s=str(raw).strip()
        try: n=Decimal(s)
        except InvalidOperation: continue
        if not n.is_finite() or n<0 or 'e' in s.lower() or not s or s.startswith('-') or any(c not in '0123456789+.' for c in s) or s.count('.')>1 or s.count('+')>1 or ('+' in s and not s.startswith('+')): continue
        try: total+=int((n*100).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
        except InvalidOperation: continue
    return total
""",
[("sum",["1.20","2",3],620),("half_up",["0.005","1.234","2.675"],392),("skip",["-1.00","$2.00",True,1.2,"bad","0.10"],10),("plus_zero",[" +0.50 ","0","0.004"],50),("type","2.00",0)]),
"b10_log_summary":("Log level summary",[
"Input is a list; other input returns all five recognized levels with zero counts.",
"An entry is either a string whose first whitespace-delimited token is its level, or a dictionary with a string level field.",
"Recognize DEBUG, INFO, WARNING, ERROR, and CRITICAL case-insensitively after trimming; ignore unknown or malformed entries.",
"Return all five keys, including zero counts, in fixed order DEBUG, INFO, WARNING, ERROR, CRITICAL."],
"""def transform(value):
    levels=['DEBUG','INFO','WARNING','ERROR','CRITICAL']; out={x:0 for x in levels}
    if not isinstance(value,list): return out
    for e in value:
        if isinstance(e,str):
            p=e.strip().split(); level=p[0] if p else ''
        elif isinstance(e,dict) and isinstance(e.get('level'),str): level=e['level'].strip()
        else: continue
        level=level.upper()
        if level in out: out[level]+=1
    return out
""",
[("mixed",["info hi",{"level":"ERROR"},"DEBUG started"],{"DEBUG":1,"INFO":1,"WARNING":0,"ERROR":1,"CRITICAL":0}),("case",[" warning disk",{"level":" critical "},"INFO"],{"DEBUG":0,"INFO":1,"WARNING":1,"ERROR":0,"CRITICAL":1}),("unknown",["TRACE x","",{},{"level":2},None],{"DEBUG":0,"INFO":0,"WARNING":0,"ERROR":0,"CRITICAL":0}),("empty",[],{"DEBUG":0,"INFO":0,"WARNING":0,"ERROR":0,"CRITICAL":0}),("type",None,{"DEBUG":0,"INFO":0,"WARNING":0,"ERROR":0,"CRITICAL":0})]),
"b11_manifest_diff":("File manifest comparison",[
"Input is a dictionary with before and after lists; invalid top-level input returns empty added, removed, and changed lists.",
"A valid entry has a non-empty string path, non-negative integer size that is not boolean, and non-empty string sha256; ignore invalid entries.",
"For duplicate paths, the last valid entry wins.",
"Added means only after, removed means only before, and changed means present in both with size or sha256 different; return lexicographically sorted lists."],
"""def transform(value):
    empty={'added':[],'removed':[],'changed':[]}
    if not isinstance(value,dict) or not isinstance(value.get('before'),list) or not isinstance(value.get('after'),list): return empty
    def index(rows):
        out={}
        for r in rows:
            if not isinstance(r,dict): continue
            p,s,h=r.get('path'),r.get('size'),r.get('sha256')
            if not isinstance(p,str) or not p or isinstance(s,bool) or not isinstance(s,int) or s<0 or not isinstance(h,str) or not h: continue
            out[p]=(s,h)
        return out
    a,b=index(value['before']),index(value['after'])
    return {'added':sorted(b.keys()-a.keys()),'removed':sorted(a.keys()-b.keys()),'changed':sorted(p for p in a.keys()&b.keys() if a[p]!=b[p])}
""",
[("all_kinds",{"before":[{"path":"z","size":1,"sha256":"a"},{"path":"b","size":2,"sha256":"b"}],"after":[{"path":"c","size":3,"sha256":"c"},{"path":"z","size":1,"sha256":"a"},{"path":"b","size":2,"sha256":"c"}]},{"added":["c"],"removed":[],"changed":["b"]}),("removed",{"before":[{"path":"x","size":1,"sha256":"h"}],"after":[]},{"added":[],"removed":["x"],"changed":[]}),("invalid_duplicate",{"before":[{"path":"p","size":1,"sha256":"a"}],"after":[{"path":"p","size":2,"sha256":"b"},{"path":"p","size":1,"sha256":"a"},{"path":"bad","size":-1,"sha256":"x"}]},{"added":[],"removed":[],"changed":[]}),("empty",{"before":[],"after":[]},{"added":[],"removed":[],"changed":[]}),("type",[],{"added":[],"removed":[],"changed":[]})]),
"b12_bucket_assign":("Inclusive numeric bucketing",[
"Input is a dictionary with values and buckets lists; invalid top-level input returns [].",
"A bucket must have a non-empty string name and finite numeric min/max bounds that are not booleans, with min <= max; ignore invalid buckets.",
"For each finite numeric value other than a boolean, choose the first bucket whose inclusive interval contains it; return None for invalid or unmatched values.",
"Preserve input order and output length; overlapping intervals use the first supplied valid bucket."],
"""import math
def transform(value):
    if not isinstance(value,dict) or not isinstance(value.get('values'),list) or not isinstance(value.get('buckets'),list): return []
    buckets=[]
    for b in value['buckets']:
        if not isinstance(b,dict): continue
        n,lo,hi=b.get('name'),b.get('min'),b.get('max')
        if not isinstance(n,str) or not n or isinstance(lo,bool) or not isinstance(lo,(int,float)) or isinstance(hi,bool) or not isinstance(hi,(int,float)): continue
        if not math.isfinite(lo) or not math.isfinite(hi) or lo>hi: continue
        buckets.append((n,lo,hi))
    out=[]
    for x in value['values']:
        if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x): out.append(None); continue
        out.append(next((n for n,lo,hi in buckets if lo<=x<=hi),None))
    return out
""",
[("normal",{"values":[1,5,9],"buckets":[{"name":"low","min":0,"max":3},{"name":"mid","min":4,"max":6},{"name":"high","min":7,"max":10}]},["low","mid","high"]),("inclusive_overlap",{"values":[0,5,10],"buckets":[{"name":"first","min":0,"max":5},{"name":"second","min":5,"max":10}]},["first","first","second"]),("invalid_unmatched",{"values":[-1,1.5,"2",True],"buckets":[{"name":"bad","min":4,"max":2},{"name":"valid","min":0,"max":2}]},[None,"valid",None,None]),("empty",{"values":[],"buckets":[{"name":"x","min":0,"max":1}]},[]),("type",None,[])])
}

def main():
    cdir=ROOT/'verifiers'/'s8b_contracts'
    for task,(title,rules,ref,cases) in D.items():
        contract={'task_id':task,'reference_solution':ref,'task_requirements':rules,
                  'cases':[{'name':n,'input':i,'expected':e} for n,i,e in cases]}
        if task in {'b03_csv_totals','b07_inventory_delta','b08_contact_group','b10_log_summary'}:
            contract['ordered_mapping_output']=True
        (cdir/(task+'.json')).write_text(json.dumps(contract,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        p=ROOT/'tasks'/'s8b'/task/'template'/'task.md'
        p.write_text('# Repair transform\n\n## '+title+'\n\n'
                     +'Implement def transform(value) in solution.py. Its public signature must remain unchanged.\n\n'
                     +'Requirements:\n'+''.join('- '+r+'\n' for r in rules)
                     +'\nDo not modify benchmark-owned verifier files.\n',encoding='utf-8')
    print('wrote',len(D),'S8-b contracts and aligned task statements')

if __name__=='__main__': main()
