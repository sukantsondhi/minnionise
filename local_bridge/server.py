#!/usr/bin/env python3
"""Minnionise local-only voice bridge. Python standard library only."""
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import json,os,platform,re,shutil,subprocess,tempfile,urllib.request
HOST='127.0.0.1';PORT=8765

def run(cmd,**kw): return subprocess.run(cmd,capture_output=True,text=True,timeout=30,**kw)
def models():
 out=[]
 piper=shutil.which('piper')
 if piper:
  roots=[Path.home()/'piper',Path.home()/'models',Path.home()/'.local/share/piper']
  roots += [Path(x).expanduser() for x in os.getenv('MINNIONISE_MODEL_DIRS','').split(os.pathsep) if x]
  for root in roots:
   if root.exists():
    for p in list(root.rglob('*.onnx'))[:50]: out.append({'id':'piper::'+str(p),'name':p.stem,'engine':'piper','path':str(p)})
 if platform.system()=='Darwin' and shutil.which('say'):
  r=run(['say','-v','?']);
  for line in r.stdout.splitlines()[:40]:
   name=line.split()[0];out.append({'id':'say::'+name,'name':name,'engine':'say'})
 e=shutil.which('espeak-ng') or shutil.which('espeak')
 if e:
  r=run([e,'--voices=en'])
  for line in r.stdout.splitlines()[1:16]:
   bits=line.split()
   if len(bits)>3: out.append({'id':'espeak::'+bits[3],'name':'eSpeak '+bits[3],'engine':'espeak'})
 if platform.system()=='Windows':
  out.append({'id':'sapi::default','name':'Windows system voice','engine':'sapi'})
 return out

def synth(text,m,rate,path):
 if m['engine']=='piper':
  r=subprocess.run(['piper','--model',m['path'],'--length_scale',str(1/max(rate,.1)),'--output_file',str(path)],input=text,text=True,capture_output=True,timeout=45)
 elif m['engine']=='espeak': r=run([shutil.which('espeak-ng') or shutil.which('espeak'),'-v',m['id'].split('::',1)[1],'-s',str(int(170*rate)),'-w',str(path),text])
 elif m['engine']=='say':
  a=path.with_suffix('.aiff');r=run(['say','-v',m['name'],'-r',str(int(190*rate)),'-o',str(a),text]);return a
 elif m['engine']=='sapi':
  safe=text.replace("'","''");ps=f"$v=New-Object -ComObject SAPI.SpVoice;$s=New-Object -ComObject SAPI.SpFileStream;$s.Open('{path}',3,$false);$v.AudioOutputStream=$s;$v.Speak('{safe}');$s.Close()";r=run(['powershell','-NoProfile','-Command',ps])
 else: raise RuntimeError('Unsupported engine')
 if r.returncode: raise RuntimeError(r.stderr or 'Synthesis failed')
 return path
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def headers(self,ctype='application/json'):
  self.send_header('Content-Type',ctype);self.send_header('Access-Control-Allow-Origin','*');self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS');self.send_header('Access-Control-Allow-Headers','Content-Type');self.send_header('Access-Control-Allow-Private-Network','true');self.send_header('Cache-Control','no-store')
 def sendj(self,x,status=200):
  b=json.dumps(x).encode();self.send_response(status);self.headers();self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
 def do_OPTIONS(self): self.send_response(204);self.headers();self.end_headers()
 def do_GET(self):
  if self.path=='/api/health': return self.sendj({'ok':True,'platform':platform.system()})
  if self.path=='/api/models':
   ms=models();return self.sendj({'models':ms,'count':len(ms)})
  self.sendj({'error':'Not found'},404)
 def do_POST(self):
  try:
   n=min(int(self.headers.get('Content-Length','0')),64000);d=json.loads(self.rfile.read(n) or b'{}')
   if self.path!='/api/speak': return self.sendj({'error':'Not found'},404)
   text=str(d.get('text','')).strip()[:500];mid=str(d.get('model_id',''));rate=max(.5,min(1.5,float(d.get('rate',1))))
   m=next((x for x in models() if x['id']==mid),None)
   if not text or not m:return self.sendj({'error':'Invalid text or unavailable model'},400)
   with tempfile.TemporaryDirectory(prefix='minnionise-') as td:
    p=synth(text,m,rate,Path(td)/'voice.wav');b=p.read_bytes();self.send_response(200);self.headers('audio/aiff' if p.suffix=='.aiff' else 'audio/wav');self.send_header('Content-Length',str(len(b)));self.end_headers();self.wfile.write(b)
  except Exception as e:self.sendj({'error':str(e)},500)
if __name__=='__main__':
 print(f'🍌 Minnionise local bridge running at http://{HOST}:{PORT}');print('Models:',len(models()));ThreadingHTTPServer((HOST,PORT),H).serve_forever()
