import base64,os,re,uuid,urllib.request
from http.server import BaseHTTPRequestHandler
from _lib.common import body,json_out,supabase

MAX_FILE=3*1024*1024
ALLOWED={"image/jpeg","image/png","image/webp","image/gif"}

class handler(BaseHTTPRequestHandler):
 def do_POST(self):
  try:
   d=body(self)
   sid=str(uuid.UUID(str(d.get("survey_id"))))
   name=str(d.get("name","photo")).strip()[:80]
   mime=str(d.get("type","")).lower()
   raw=str(d.get("data",""))
   if mime not in ALLOWED or not raw.startswith("data:"): raise ValueError()
   if "," not in raw: raise ValueError()
   encoded=raw.split(",",1)[1]
   data=base64.b64decode(encoded,validate=True)
   if not data or len(data)>MAX_FILE: raise ValueError()
   _,rows=supabase("surveys",params={"select":"id,is_active","id":"eq."+sid,"limit":"1"})
   if not rows or not rows[0].get("is_active"):
    json_out(self,404,{"success":False,"error":"Survey unavailable"}); return
   ext={"image/jpeg":"jpg","image/png":"png","image/webp":"webp","image/gif":"gif"}[mime]
   safe=re.sub(r"[^a-zA-Z0-9_-]+","-",name.rsplit(".",1)[0])[:40] or "photo"
   path=f"{sid}/{uuid.uuid4().hex}-{safe}.{ext}"
   url=os.environ["SUPABASE_URL"].rstrip("/")+"/storage/v1/object/survey-assets/"+path
   req=urllib.request.Request(url,method="POST",headers={"apikey":os.environ["SUPABASE_SERVICE_ROLE_KEY"],"Authorization":"Bearer "+os.environ["SUPABASE_SERVICE_ROLE_KEY"],"Content-Type":mime,"x-upsert":"false"},data=data)
   with urllib.request.urlopen(req,timeout=20) as r:
    if r.status>=300: raise ValueError()
   public=os.environ["SUPABASE_URL"].rstrip("/")+"/storage/v1/object/public/survey-assets/"+path
   json_out(self,201,{"success":True,"url":public,"path":path})
  except Exception as e:
   print("UPLOAD",e); json_out(self,400,{"success":False,"error":"Could not upload image"})
