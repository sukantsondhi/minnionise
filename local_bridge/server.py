#!/usr/bin/env python3
"""Minnionise Local Bridge v2.

Standard-library local bridge for:
- Ollama discovery + inference
- LM Studio discovery + inference
- Local voice discovery/synthesis (Piper, system voices, eSpeak)
- Secure LAN phone pairing with a random token

Run:
    python server.py          # desktop-only loopback mode
    python server.py --lan    # enable phone pairing on the local network
"""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import argparse
import json
import mimetypes
import os
import platform
import re
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

VERSION = "2.0.0"
DEFAULT_PORT = 8765
OLLAMA = "http://127.0.0.1:11434"
LMSTUDIO = "http://127.0.0.1:1234"
MAX_TEXT = 1200
TOKEN = secrets.token_urlsafe(18)
STARTED = time.time()
CONFIG = {"host": "127.0.0.1", "port": DEFAULT_PORT, "lan": False}

ALLOWED_WEB_ORIGINS = {
    "https://sukantsondhi.github.io",
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
}

LEXICON = {
    "hello":"bello","hi":"bello","goodbye":"poopaye","bye":"poopaye","friend":"amigo","friends":"amigos",
    "thank":"tank","thanks":"tank yu","you":"tu","your":"tu","yes":"si","no":"na","love":"luv","banana":"banana",
    "everyone":"tulaliloo","everybody":"tulaliloo","what":"wha","look":"luk","stop":"stupa","please":"por favor",
    "morning":"matoka","night":"noche","good":"bon","very":"bello-bello","beautiful":"bella","happy":"papoy",
    "party":"banana party","food":"papa","help":"bee-do","fire":"bee-do","boss":"big boss","work":"worka",
    "school":"skoola","today":"toda","tomorrow":"tomorra","how":"como","are":"be","is":"be","my":"mi","our":"nossa",
    "we":"wi","i":"mi","me":"mi"
}
TAILS = {
    "gentle":[" banana."," papoy."],
    "classic":[" banana!"," tulaliloo!"," papoy!"],
    "chaos":[" BANANA! BEE-DO!"," tulaliloo papoy BANANA!"," poopaye? BANANA BANANA!"],
    "teacher":[" banana."]
}


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=45, **kwargs)


def request_json(url, method="GET", payload=None, timeout=2.0):
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    try:
        ip = socket.gethostbyname(socket.gethostname())
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return None


def is_loopback(ip):
    return ip in {"127.0.0.1", "::1"} or ip.startswith("127.")


def provider_status():
    out = []
    try:
        j = request_json(f"{OLLAMA}/api/tags", timeout=1.25)
        models = []
        for m in j.get("models", []):
            details = m.get("details") or {}
            models.append({"id":m.get("name"), "name":m.get("name"), "meta":details.get("parameter_size") or details.get("family") or "Ollama"})
        out.append({"id":"ollama","name":"Ollama","connected":True,"endpoint":OLLAMA,"models":models})
    except Exception:
        out.append({"id":"ollama","name":"Ollama","connected":False,"endpoint":OLLAMA,"models":[]})
    try:
        j = request_json(f"{LMSTUDIO}/v1/models", timeout=1.25)
        models = [{"id":m.get("id"),"name":m.get("id"),"meta":"LM Studio"} for m in j.get("data",[]) if m.get("id")]
        out.append({"id":"lmstudio","name":"LM Studio","connected":True,"endpoint":LMSTUDIO,"models":models})
    except Exception:
        out.append({"id":"lmstudio","name":"LM Studio","connected":False,"endpoint":LMSTUDIO,"models":[]})
    return out


def piper_roots():
    roots = [Path.home()/"piper", Path.home()/"models", Path.home()/".local/share/piper", Path.home()/"Documents/piper"]
    if platform.system() == "Windows":
        for env in ("LOCALAPPDATA","APPDATA"):
            if os.getenv(env): roots.append(Path(os.environ[env])/"piper")
    roots += [Path(x).expanduser() for x in os.getenv("MINNIONISE_MODEL_DIRS", "").split(os.pathsep) if x]
    return roots


def voices():
    out = []
    piper = shutil.which("piper")
    if piper:
        seen = set()
        for root in piper_roots():
            if not root.exists(): continue
            try:
                found = list(root.rglob("*.onnx"))[:60]
            except Exception:
                continue
            for p in found:
                sp = str(p.resolve())
                if sp in seen: continue
                seen.add(sp)
                out.append({"id":"piper::"+sp,"name":"Piper • "+p.stem,"engine":"piper","path":sp})
    system = platform.system()
    if system == "Windows":
        out.append({"id":"sapi::default","name":"Windows system voice","engine":"sapi"})
    elif system == "Darwin" and shutil.which("say"):
        try:
            r = run(["say","-v","?"])
            for line in r.stdout.splitlines()[:24]:
                name = line.split()[0] if line.split() else ""
                if name: out.append({"id":"say::"+name,"name":"macOS • "+name,"engine":"say","voice":name})
        except Exception:
            out.append({"id":"say::default","name":"macOS system voice","engine":"say","voice":None})
    else:
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        if exe:
            out.append({"id":"espeak::default","name":"eSpeak system voice","engine":"espeak","voice":"en"})
    return out


def no_model_transform(text, style="classic"):
    original = text.strip()
    def repl(match):
        w = match.group(0).lower()
        if w in LEXICON: return LEXICON[w]
        t = re.sub(r"tion$", "shun", w)
        t = re.sub(r"ing$", "in", t)
        t = re.sub(r"^th", "d", t)
        t = t.replace("th", "t")
        if style == "chaos" and len(t) > 7: t = t[: max(4, int(len(t)*.7))] + "a"
        return t
    mapped = re.sub(r"\b[a-z']+\b", repl, original.lower())
    mapped = re.sub(r"\bi am\b", "mi be", mapped)
    mapped = re.sub(r"\bdo not\b", "no-no", mapped)
    tails = TAILS.get(style, TAILS["classic"])
    tail = tails[(len(original)+len(style)) % len(tails)]
    prefix = "" if mapped.startswith("bello") else ("bello, " if style == "gentle" else "Bello! ")
    phrase = re.sub(r"\s+", " ", prefix + re.sub(r"[.!?]+$", "", mapped) + tail).strip()
    syllables = re.findall(r"[A-Za-zÀ-ÿ'-]+", phrase)[:28]
    pronunciation = " · ".join(s.lower() for s in syllables)
    return {
        "minnionese": phrase,
        "pronunciation": pronunciation,
        "syllables": syllables,
        "explanation": "Generated locally by Minnionise’s deterministic no-model phrase engine; no AI or cloud request was used.",
        "source": "no-model"
    }


def system_prompt(style):
    return (
        "You are Minnionise, a playful fan-inspired fictional-language pronunciation coach. "
        "Transform the user's English sentence into original playful banana-language inspired by comic gibberish, without quoting movie dialogue. "
        "Preserve meaning, keep it pronounceable, and avoid offensive content. "
        f"Style={style}. Return ONLY valid JSON with exactly these keys: minnionese (string), pronunciation (simple phonetic string separated with middle dots), "
        "syllables (array of max 24 short strings), explanation (one concise sentence). Do not use markdown."
    )


def parse_jsonish(raw):
    text = str(raw or "").strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        obj = json.loads(text)
    except Exception:
        a, b = text.find("{"), text.rfind("}")
        if a < 0 or b <= a: raise ValueError("Model did not return valid JSON")
        obj = json.loads(text[a:b+1])
    if not obj.get("minnionese"): raise ValueError("Model response is missing minnionese")
    if not isinstance(obj.get("syllables"), list): obj["syllables"] = re.findall(r"[A-Za-zÀ-ÿ'-]+", obj["minnionese"])[:24]
    obj.setdefault("pronunciation", " · ".join(obj["syllables"]))
    obj.setdefault("explanation", "Generated by your local model.")
    return obj


def translate_with(provider, model, text, style):
    if provider == "no-model": return no_model_transform(text, style)
    messages = [{"role":"system","content":system_prompt(style)},{"role":"user","content":text}]
    if provider == "ollama":
        j = request_json(f"{OLLAMA}/api/chat", "POST", {"model":model,"messages":messages,"stream":False,"format":"json","options":{"temperature":0.35}}, timeout=70)
        return parse_jsonish((j.get("message") or {}).get("content"))
    if provider == "lmstudio":
        j = request_json(f"{LMSTUDIO}/v1/chat/completions", "POST", {"model":model,"messages":messages,"temperature":0.35,"max_tokens":550}, timeout=70)
        choices = j.get("choices") or []
        if not choices: raise ValueError("LM Studio returned no choices")
        return parse_jsonish((choices[0].get("message") or {}).get("content"))
    raise ValueError("Unsupported provider")


def synth(text, voice, rate, directory):
    engine = voice.get("engine")
    out = Path(directory)/"voice.wav"
    if engine == "piper":
        cmd = [shutil.which("piper") or "piper", "--model", voice["path"], "--length_scale", str(1/max(rate,.1)), "--output_file", str(out)]
        r = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=60)
    elif engine == "espeak":
        exe = shutil.which("espeak-ng") or shutil.which("espeak")
        r = run([exe,"-v",voice.get("voice") or "en","-s",str(int(170*rate)),"-w",str(out),text])
    elif engine == "say":
        out = Path(directory)/"voice.aiff"
        cmd = ["say"]
        if voice.get("voice"): cmd += ["-v",voice["voice"]]
        cmd += ["-r",str(int(190*rate)),"-o",str(out),text]
        r = run(cmd)
    elif engine == "sapi":
        safe_text = text.replace("'","''")
        safe_path = str(out).replace("'","''")
        ps = f"Add-Type -AssemblyName System.Speech;$s=New-Object System.Speech.Synthesis.SpeechSynthesizer;$s.Rate=0;$s.SetOutputToWaveFile('{safe_path}');$s.Speak('{safe_text}');$s.Dispose()"
        r = run(["powershell","-NoProfile","-Command",ps])
    else:
        raise RuntimeError("Unsupported voice engine")
    if r.returncode != 0: raise RuntimeError((r.stderr or r.stdout or "Synthesis failed").strip())
    if not out.exists(): raise RuntimeError("Voice engine did not create an audio file")
    return out


def mobile_page(token):
    token_js = json.dumps(token)
    return f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#090b10"><title>Minnionise Mobile</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(circle at 90% 0,#594c0d55,transparent 32%),#090b10;color:#faf9f1;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}.app{{max-width:650px;margin:auto;padding:18px 16px 50px}}header{{display:flex;justify-content:space-between;align-items:center;padding:8px 0 35px}}.brand{{font-weight:950;letter-spacing:.12em}}.brand span{{color:#ffd72e}}.status{{font-size:10px;background:#162018;border:1px solid #365b3d;color:#87e99d;padding:8px 10px;border-radius:99px}}h1{{font-size:clamp(43px,14vw,68px);line-height:.92;letter-spacing:-.065em;margin:0 0 13px}}h1 em{{color:#ffd72e;font-style:normal}}.sub{{color:#8993a2;font-size:14px;line-height:1.5;margin-bottom:25px}}.card{{background:#121720e8;border:1px solid #ffffff17;border-radius:24px;padding:18px;box-shadow:0 25px 70px #0007;margin-bottom:12px}}.mode{{display:grid;grid-template-columns:1fr 1fr;gap:7px;background:#090c11;padding:6px;border-radius:16px}}button,select,textarea{{font:inherit}}.mode button{{border:0;border-radius:12px;padding:11px;background:transparent;color:#7e8897;font-weight:700}}.mode .on{{background:#ffd72e;color:#111}}label{{display:block;font-size:9px;letter-spacing:.12em;color:#7a8492;margin:14px 0 7px}}select,textarea{{width:100%;border:1px solid #ffffff14;background:#0b0e14;color:#fff;border-radius:13px;padding:12px;outline:none}}textarea{{min-height:130px;resize:vertical;font-size:20px;line-height:1.35}}.go,.play{{width:100%;border:0;border-radius:14px;background:#ffd72e;color:#121212;font-weight:900;padding:15px;margin-top:12px}}.result{{display:none}}.result.show{{display:block}}.phrase{{font-size:37px;line-height:1.03;font-weight:950;letter-spacing:-.04em;margin:10px 0}}.phon{{color:#ffd72e;font-family:monospace;font-size:11px;line-height:1.6}}.chips{{display:flex;gap:6px;flex-wrap:wrap;margin:14px 0}}.chips button{{border:1px solid #ffffff17;background:#ffffff08;color:#ddd;border-radius:99px;padding:7px 10px}}.row{{display:grid;grid-template-columns:1fr 1fr;gap:7px}}.row button{{border:1px solid #ffffff17;background:#ffffff07;color:#ddd;border-radius:12px;padding:12px}}.tiny{{font-size:9px;line-height:1.55;color:#687281}}code{{color:#b9c2d0}}footer{{color:#505966;font-size:8px;text-align:center;margin-top:24px}}
</style></head><body><div class="app"><header><div class="brand">MINNION<span>ISE</span></div><div class="status" id="status">● Paired</div></header><h1>Your desktop AI.<br><em>In your pocket.</em></h1><p class="sub">This page is being served directly by your computer. Prompts stay on your local network.</p><div class="card"><div class="mode"><button class="on" id="no">No model</button><button id="my">My model</button></div><div id="providerBox" hidden><label>LOCAL PROVIDER</label><select id="provider"></select><label>MODEL</label><select id="model"></select></div><label>YOUR SENTENCE</label><textarea id="input" placeholder="Good morning everyone, how are you?"></textarea><button class="go" id="go">MINNIONISE ✦</button></div><div class="card result" id="result"><label>YOUR MINNIONESE</label><div class="phrase" id="phrase"></div><div class="phon" id="phon"></div><div class="chips" id="chips"></div><div class="row"><button id="slow">🐌 Slow</button><button id="play">▶ Play</button></div><p class="tiny" id="explain"></p></div><div class="card"><b style="font-size:11px">🔒 Local pairing</b><p class="tiny">The random pairing token is required for requests from devices other than this computer. Stop the bridge to end this phone session.</p></div><footer>🍌 Fan-inspired experiment • No affiliation with Illumination or Universal.</footer></div><script>
const TOKEN={token_js},H={{'X-Minnionise-Token':TOKEN}},$=s=>document.querySelector(s);let mode='no-model',status=null;async function load(){{let r=await fetch('/api/status',{{headers:H}});status=await r.json();let ps=(status.providers||[]).filter(x=>x.connected&&x.models.length);$('#provider').innerHTML=ps.map(p=>`<option value="${{p.id}}">${{p.name}}</option>`).join('');fill();if(!ps.length)$('#my').disabled=true}}function fill(){{let p=(status?.providers||[]).find(x=>x.id===$('#provider').value);$('#model').innerHTML=(p?.models||[]).map(m=>`<option value="${{m.id}}">${{m.name}}</option>`).join('')}}$('#provider').onchange=fill;$('#no').onclick=()=>{{mode='no-model';$('#no').className='on';$('#my').className='';$('#providerBox').hidden=true}};$('#my').onclick=()=>{{mode='model';$('#my').className='on';$('#no').className='';$('#providerBox').hidden=false}};async function speak(t,rate=1){{try{{let v=status?.voices?.[0];if(!v)throw 0;let r=await fetch('/api/speak',{{method:'POST',headers:{{...H,'Content-Type':'application/json'}},body:JSON.stringify({{text:t,voice_id:v.id,rate}})}});if(!r.ok)throw 0;let b=await r.blob(),u=URL.createObjectURL(b),a=new Audio(u);a.onended=()=>URL.revokeObjectURL(u);a.play()}}catch{{let u=new SpeechSynthesisUtterance(t);u.rate=rate;speechSynthesis.speak(u)}}}}$('#go').onclick=async()=>{{let text=$('#input').value.trim();if(!text)return;$('#go').textContent='THINKING…';try{{let p=mode==='no-model'?'no-model':$('#provider').value,m=mode==='no-model'?null:$('#model').value,r=await fetch('/api/translate',{{method:'POST',headers:{{...H,'Content-Type':'application/json'}},body:JSON.stringify({{provider:p,model:m,text,style:'classic'}})}}),j=await r.json();if(!r.ok)throw Error(j.error||'Failed');$('#phrase').textContent=j.minnionese;$('#phon').textContent='/ '+j.pronunciation+' /';$('#explain').textContent=j.explanation||'';$('#chips').innerHTML='';(j.syllables||[]).forEach(s=>{{let b=document.createElement('button');b.textContent=s;b.onclick=()=>speak(s,.75);$('#chips').append(b)}});$('#result').classList.add('show')}}catch(e){{alert(e.message)}}finally{{$('#go').textContent='MINNIONISE ✦'}}}};$('#play').onclick=()=>speak($('#phrase').textContent,1);$('#slow').onclick=()=>speak($('#phrase').textContent,.62);load();
</script></body></html>'''


class Handler(BaseHTTPRequestHandler):
    server_version = "MinnioniseBridge/2"

    def log_message(self, fmt, *args):
        print(f"[{self.client_address[0]}] " + (fmt % args))

    def _origin_allowed(self):
        origin = self.headers.get("Origin")
        if not origin: return True
        if origin in ALLOWED_WEB_ORIGINS: return True
        # Same-origin mobile UI served by the bridge.
        try:
            u = urlparse(origin)
            if u.port == CONFIG["port"] and (u.hostname in {"127.0.0.1","localhost",local_ip()}): return True
        except Exception:
            pass
        return False

    def _token(self):
        header = self.headers.get("X-Minnionise-Token", "")
        if header: return header
        return parse_qs(urlparse(self.path).query).get("token", [""])[0]

    def _authorized(self, api=True):
        ip = self.client_address[0]
        if is_loopback(ip):
            return self._origin_allowed()
        return CONFIG["lan"] and secrets.compare_digest(self._token(), TOKEN)

    def _cors(self):
        origin = self.headers.get("Origin")
        if origin and self._origin_allowed(): self.send_header("Access-Control-Allow-Origin", origin)
        self.send_header("Vary", "Origin")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Minnionise-Token")
        self.send_header("Access-Control-Allow-Private-Network", "true")
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")

    def json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status); self._cors(); self.send_header("Content-Type","application/json; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

    def html(self, text, status=200):
        body = text.encode("utf-8")
        self.send_response(status); self._cors(); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_OPTIONS(self):
        if not self._origin_allowed(): return self.json({"error":"Origin not allowed"},403)
        self.send_response(204); self._cors(); self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path in {"/mobile","/"} and not is_loopback(self.client_address[0]):
            if not self._authorized(False): return self.html("<h1>Pairing token invalid</h1>",403)
            return self.html(mobile_page(self._token()))
        if path == "/api/health":
            if not self._authorized(): return self.json({"error":"Unauthorized"},403)
            return self.json({"ok":True,"version":VERSION})
        if path == "/api/status":
            if not self._authorized(): return self.json({"error":"Unauthorized"},403)
            result = {"ok":True,"name":"Minnionise Local Bridge","version":VERSION,"platform":platform.system(),"uptime":int(time.time()-STARTED),"lan_enabled":CONFIG["lan"],"providers":provider_status(),"voices":voices()}
            if is_loopback(self.client_address[0]): result["token"] = TOKEN
            return self.json(result)
        if path == "/api/models":
            if not self._authorized(): return self.json({"error":"Unauthorized"},403)
            return self.json({"providers":provider_status(),"voices":voices()})
        if path == "/api/pair":
            if not is_loopback(self.client_address[0]) or not self._authorized(): return self.json({"error":"Pairing can only be created from this computer"},403)
            if not CONFIG["lan"]: return self.json({"error":"LAN mode is disabled. Restart with --lan."},409)
            ip = local_ip()
            if not ip: return self.json({"error":"Could not determine a LAN IP address"},500)
            return self.json({"url":f"http://{ip}:{CONFIG['port']}/mobile?token={TOKEN}","ip":ip,"port":CONFIG["port"],"token":TOKEN})
        return self.json({"error":"Not found"},404)

    def do_POST(self):
        if not self._authorized(): return self.json({"error":"Unauthorized"},403)
        path = urlparse(self.path).path
        try:
            length = min(int(self.headers.get("Content-Length","0") or 0), 128_000)
            data = json.loads(self.rfile.read(length) or b"{}")
            if path == "/api/translate":
                text = str(data.get("text","")).strip()[:MAX_TEXT]
                provider = str(data.get("provider","no-model"))
                model = data.get("model")
                style = str(data.get("style","classic"))
                if not text: return self.json({"error":"Text is required"},400)
                if provider not in {"no-model","ollama","lmstudio"}: return self.json({"error":"Unsupported provider"},400)
                result = translate_with(provider, model, text, style)
                result["provider"] = provider; result["model"] = model
                return self.json(result)
            if path == "/api/speak":
                text = str(data.get("text","")).strip()[:MAX_TEXT]
                rate = max(.5,min(1.5,float(data.get("rate",1))))
                available = voices(); vid = str(data.get("voice_id", "")); voice = next((v for v in available if v["id"] == vid), available[0] if available else None)
                if not text or not voice: return self.json({"error":"No local voice is available"},400)
                with tempfile.TemporaryDirectory(prefix="minnionise-") as td:
                    p = synth(text, voice, rate, td); body = p.read_bytes(); ctype = "audio/aiff" if p.suffix.lower()==".aiff" else "audio/wav"
                    self.send_response(200); self._cors(); self.send_header("Content-Type",ctype); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
                    return
            return self.json({"error":"Not found"},404)
        except urllib.error.HTTPError as e:
            try: msg = e.read().decode("utf-8")[:1000]
            except Exception: msg = str(e)
            return self.json({"error":f"Local provider returned HTTP {e.code}: {msg}"},502)
        except Exception as e:
            return self.json({"error":str(e)},500)


def main():
    ap = argparse.ArgumentParser(description="Minnionise local AI + voice bridge")
    ap.add_argument("--lan", action="store_true", help="Bind to the local network and enable QR phone pairing")
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    args = ap.parse_args()
    CONFIG["lan"] = bool(args.lan); CONFIG["port"] = args.port; CONFIG["host"] = "0.0.0.0" if args.lan else "127.0.0.1"
    print("\n🍌 MINNIONISE LOCAL BRIDGE v" + VERSION)
    print("   Desktop: http://127.0.0.1:%d" % args.port)
    if args.lan:
        ip = local_ip()
        print("   LAN mode: ENABLED")
        print("   Pairing:  http://%s:%d/mobile?token=%s" % (ip or "<your-ip>", args.port, TOKEN))
        print("   Security: remote devices require the random pairing token")
    else:
        print("   LAN mode: off (use --lan to enable phone pairing)")
    ps = provider_status(); print("   Models:   " + ", ".join(f"{p['name']}={len(p['models']) if p['connected'] else 'offline'}" for p in ps))
    print("   Voices:   %d local voice(s)\n" % len(voices()))
    ThreadingHTTPServer((CONFIG["host"], args.port), Handler).serve_forever()

if __name__ == "__main__": main()
