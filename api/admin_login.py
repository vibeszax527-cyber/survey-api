import os,hmac
from http.server import BaseHTTPRequestHandler
from _lib.common import body,json_out,token
class handler(BaseHTTPRequestHandler):
 def do_POST(self):
  try:
   d=body(self); u=str(d.get('username','')); p=str(d.get('password',''))
   if hmac.compare_digest(u,os.environ.get('ADMIN_USERNAME','')) and hmac.compare_digest(p,os.environ.get('ADMIN_PASSWORD','')): json_out(self,200,{'success':True,'token':token(u)}); return
   json_out(self,401,{'success':False,'error':'Invalid credentials'})
  except Exception as e: print('LOGIN',e); json_out(self,400,{'success':False,'error':'Invalid request'})
 def do_GET(self): json_out(self,405,{'success':False,'error':'Method not allowed'})
