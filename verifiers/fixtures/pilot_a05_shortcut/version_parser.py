def parse_version(value):
 a,b,c=value.split('-',1)[0].split('.');return int(a),int(b),int(c),None
