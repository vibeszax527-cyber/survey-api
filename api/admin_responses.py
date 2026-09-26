from http.server import BaseHTTPRequestHandler
from _lib.common import body,json_out,supabase,admin
class handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   qs=self.path.split('?',1)[1] if '?' in self.path else ''; p=dict(x.split('=',1) for x in qs.split('&') if '=' in x); sid=p.get('survey_id'); filt={'select':'id,survey_id,name,email,phone,answers,submitted_at,expires_at','survey_id':'eq.'+sid,'order':'submitted_at.desc'}
   if p.get('search'): s=p['search'].replace(',',''); filt['or']=f'name.ilike.*{s}*,email.ilike.*{s}*,phone.ilike.*{s}*'
   if p.get('from'): filt['submitted_at']='gte.'+p['from']
   if p.get('to'): filt['submitted_at']='lte.'+p['to']+'T23:59:59Z'
   _,data=supabase('survey_responses',params=filt); json_out(self,200,{'success':True,'responses':data})
  except Exception as e: print('RESPONSES GET',e); json_out(self,400,{'success':False,'error':'Could not load responses'})
 def do_DELETE(self):
  if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   sid=self.path.split('?',1)[1].split('id=',1)[1].split('&')[0]; supabase('survey_responses','DELETE',params={'id':'eq.'+sid}); json_out(self,200,{'success':True})
  except Exception as e: print('RESPONSES DELETE',e); json_out(self,400,{'success':False,'error':'Could not delete response'})
