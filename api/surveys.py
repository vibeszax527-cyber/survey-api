import json,uuid
from http.server import BaseHTTPRequestHandler
from _lib.common import body,json_out,supabase,admin
class handler(BaseHTTPRequestHandler):
 def do_GET(self):
  try:
   q=self.path.split('?',1)[1] if '?' in self.path else ''; params=dict(x.split('=',1) for x in q.split('&') if '=' in x); sid=params.get('id')
   if sid:
    code,data=supabase('surveys',params={'select':'id,title,description,questions,is_active,created_at','id':'eq.'+sid,'limit':'1'})
    if not data or not data[0].get('is_active'): json_out(self,404,{'success':False,'error':'Survey unavailable'}); return
    json_out(self,200,{'success':True,'survey':data[0]}); return
   if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
   code,data=supabase('surveys',params={'select':'id,title,description,is_active,created_at,survey_responses(count)','order':'created_at.desc'})
   json_out(self,200,{'success':True,'surveys':data})
  except Exception as e: print('SURVEYS GET',e); json_out(self,500,{'success':False,'error':'Server error'})
 def do_POST(self):
  if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   d=body(self); title=str(d.get('title','')).strip(); qs=d.get('questions',[])
   if not title or not isinstance(qs,list): raise ValueError()
   code,data=supabase('surveys','POST',{'title':title,'description':d.get('description'),'questions':qs,'is_active':True})
   json_out(self,201,{'success':True,'survey':data[0]})
  except Exception as e: print('SURVEYS POST',e); json_out(self,400,{'success':False,'error':'Could not create survey'})
 def do_PATCH(self):
  if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   sid=self.path.split('?',1)[1].split('id=',1)[1].split('&')[0]; d=body(self); allowed={k:d[k] for k in ('title','description','questions','is_active') if k in d};
   code,data=supabase('surveys','PATCH',allowed,{'id':'eq.'+sid}); json_out(self,200,{'success':True,'survey':data[0] if data else None})
  except Exception as e: print('SURVEYS PATCH',e); json_out(self,400,{'success':False,'error':'Could not update survey'})
 def do_DELETE(self):
  if not admin(self): json_out(self,401,{'success':False,'error':'Unauthorized'}); return
  try:
   sid=self.path.split('?',1)[1].split('id=',1)[1].split('&')[0]; supabase('surveys','DELETE',params={'id':'eq.'+sid}); json_out(self,200,{'success':True})
  except Exception as e: print('SURVEYS DELETE',e); json_out(self,400,{'success':False,'error':'Could not delete survey'})
