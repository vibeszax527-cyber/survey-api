import os
from http.server import BaseHTTPRequestHandler
from _lib.common import json_out,supabase
class handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.headers.get('Authorization')!='Bearer '+os.environ.get('CRON_SECRET',''): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   supabase('survey_responses','DELETE',params={'expires_at':'lte.now()'}); json_out(self,200,{'success':True})
  except Exception as e: print('CLEANUP',e); json_out(self,500,{'success':False,'error':'Cleanup failed'})
