import uuid,datetime
from http.server import BaseHTTPRequestHandler
from _lib.common import body,json_out,supabase,mail
class handler(BaseHTTPRequestHandler):
 def do_POST(self):
  try:
   d=body(self); sid=str(uuid.UUID(str(d.get('survey_id')))); name=str(d.get('name','')).strip(); email=str(d.get('email','')).strip(); phone=str(d.get('phone','')).strip(); answers=d.get('answers',{})
   if not name or '@' not in email or not isinstance(answers,dict): raise ValueError()
   _,ss=supabase('surveys',params={'select':'id,title,questions,is_active','id':'eq.'+sid,'limit':'1'})
   if not ss or not ss[0]['is_active']: json_out(self,404,{'success':False,'error':'Survey unavailable'}); return
   qs=ss[0]['questions']; allowed={str(q.get('id')):q for q in qs}
   for q in qs:
    v=answers.get(q.get('id'))
    if q.get('required') and (v is None or v=='' or v==[]): raise ValueError()
    if v is not None and q.get('type')=='checkbox' and not isinstance(v,list): raise ValueError()
    if v is not None and q.get('type')!='checkbox' and not isinstance(v,str): raise ValueError()
   clean={k:v for k,v in answers.items() if k in allowed}
   _,rows=supabase('survey_responses','POST',{'survey_id':sid,'name':name,'email':email,'phone':phone or None,'answers':clean})
   try: mail(email,name,'Survey response received','Thank you, '+name+'. Your response to “'+ss[0]['title']+'” has been received successfully.')
   except Exception as e: print('MAIL',e)
   json_out(self,201,{'success':True,'response_id':rows[0]['id']})
  except Exception as e: print('SUBMIT',e); json_out(self,400,{'success':False,'error':'Could not submit response'})
