import os,json,hmac,hashlib,base64,time,urllib.request,urllib.parse,urllib.error
from http.server import BaseHTTPRequestHandler
MAX_BODY=256*1024

def json_out(h,status,data,extra=None):
 h.send_response(status); h.send_header('Content-Type','application/json'); h.send_header('Cache-Control','no-store')
 origin=os.environ.get('ALLOWED_ORIGIN','').strip()
 request_origin=h.headers.get('Origin','')
 if origin and (origin=='*' or request_origin==origin):
  h.send_header('Access-Control-Allow-Origin', request_origin if request_origin else origin); h.send_header('Vary','Origin')
 if extra:
  for k,v in extra.items(): h.send_header(k,v)
 h.end_headers(); h.wfile.write(json.dumps(data,separators=(',',':')).encode())

def body(h):
 n=int(h.headers.get('Content-Length','0') or 0)
 if n>MAX_BODY: raise ValueError('payload')
 return json.loads(h.rfile.read(n) or b'{}')

def supabase(path,method='GET',data=None,params=None):
 base=os.environ['SUPABASE_URL'].rstrip('/')+'/rest/v1/'+path
 if params: base+='?'+urllib.parse.urlencode(params,doseq=True)
 key=os.environ.get('SUPABASE_SECRET_KEY') or os.environ['SUPABASE_SERVICE_ROLE_KEY']
 req=urllib.request.Request(base,method=method,headers={'apikey':key,'Authorization':'Bearer '+key,'Content-Type':'application/json','Prefer':'return=representation'})
 if data is not None: req.data=json.dumps(data).encode()
 try:
  with urllib.request.urlopen(req,timeout=15) as r: return r.status,json.loads(r.read() or b'null')
 except urllib.error.HTTPError as e:
  print('SUPABASE',e.code,e.read().decode(errors='ignore')); raise

def token(username):
 now=int(time.time()); p={'sub':username,'iat':now,'exp':now+43200}; raw=base64.urlsafe_b64encode(json.dumps(p,separators=(',',':')).encode()).rstrip(b'=').decode(); sig=base64.urlsafe_b64encode(hmac.new(os.environ['ADMIN_TOKEN_SECRET'].encode(),raw.encode(),hashlib.sha256).digest()).rstrip(b'=').decode(); return raw+'.'+sig

def admin(h):
 a=h.headers.get('Authorization','')
 if not a.startswith('Bearer '): return False
 try:
  raw,s=a[7:].split('.',1); expected=base64.urlsafe_b64encode(hmac.new(os.environ['ADMIN_TOKEN_SECRET'].encode(),raw.encode(),hashlib.sha256).digest()).rstrip(b'=').decode()
  if not hmac.compare_digest(s,expected): return False
  p=json.loads(base64.urlsafe_b64decode(raw+'='*((4-len(raw)%4)%4))); return p.get('sub')==os.environ['ADMIN_USERNAME'] and int(p.get('exp',0))>int(time.time())
 except Exception: return False

def mail(to,name,subject,message):
 req=urllib.request.Request(os.environ['MAIL_API_URL'].rstrip('/')+'/api/send',method='POST',headers={'Content-Type':'application/json','X-API-Key':os.environ['MAIL_API_SECRET']},data=json.dumps({'to':to,'name':name,'subject':subject,'message':message}).encode())
 with urllib.request.urlopen(req,timeout=15) as r: return r.status
