#!/usr/bin/env python3
"""Minnionise bridge entrypoint with the mobile-first paired UI."""
import json
import server_core as core

core.VERSION = "2.1.0"


def mobile_page(token):
    token_js = json.dumps(token)
    page = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#090b10">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<title>Minnionise Mobile</title>
<style>
:root{--bg:#090b10;--panel:#121720;--panel2:#0d1118;--text:#faf9f1;--muted:#8d96a5;--line:#ffffff17;--yellow:#ffd72e;--green:#72efa5;--blue:#70b4ff;--red:#ff8585}
*{box-sizing:border-box;min-width:0}html,body{width:100%;max-width:100%;overflow-x:clip;-webkit-text-size-adjust:100%;text-size-adjust:100%;color-scheme:dark}body{margin:0;min-height:100svh;background:radial-gradient(circle at 95% -5%,#ffd72e22,transparent 34%),radial-gradient(circle at -15% 60%,#215faa24,transparent 36%),var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif;overscroll-behavior-x:none}.app{width:100%;max-width:640px;margin:0 auto;padding:calc(12px + env(safe-area-inset-top,0px)) max(14px,env(safe-area-inset-right,0px)) calc(42px + env(safe-area-inset-bottom,0px)) max(14px,env(safe-area-inset-left,0px))}.top{position:sticky;top:max(8px,env(safe-area-inset-top,0px));z-index:20;display:flex;align-items:center;justify-content:space-between;gap:10px;height:56px;padding:0 12px;margin-bottom:34px;border:1px solid var(--line);border-radius:18px;background:#10151ddb;backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);box-shadow:0 18px 50px #0007}.brand{font-weight:950;letter-spacing:.1em;font-size:13px;white-space:nowrap}.brand span{color:var(--yellow)}.status{display:flex;align-items:center;gap:7px;font-size:10px;color:#b7c0cb;white-space:nowrap}.dot{width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 0 5px #72efa514,0 0 18px #72efa544}.eyebrow{font-size:9px;letter-spacing:.16em;color:var(--yellow);font-weight:900}.hero h1{font-size:clamp(38px,12vw,58px);line-height:.92;letter-spacing:-.055em;margin:10px 0 14px;overflow-wrap:anywhere}.hero h1 em{display:block;color:var(--yellow);font-style:normal}.sub{font-size:14px;line-height:1.5;color:var(--muted);margin:0 0 24px}.card{width:100%;background:linear-gradient(145deg,#141a24ed,#0f131bea);border:1px solid var(--line);border-radius:22px;padding:16px;box-shadow:0 24px 70px #0007;margin-bottom:11px;overflow:hidden}.mode{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;padding:6px;border:1px solid #ffffff0c;background:#090c11;border-radius:16px}.mode button,.styles button{border:0;color:#8d96a5;background:transparent;min-height:44px;border-radius:11px;font:inherit;font-size:11px;font-weight:800;touch-action:manipulation}.mode button.on,.styles button.on{background:var(--yellow);color:#111}.section{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:17px 1px 7px}.section label{margin:0}.section span{font-size:9px;color:#667181}.label,label{display:block;font-size:9px;letter-spacing:.12em;color:#7f8998;font-weight:800}.field{width:100%;border:1px solid #ffffff16;background:#0a0e14;color:#fff;border-radius:13px;padding:12px;font:inherit;font-size:16px;outline:none}.field:focus,textarea:focus{border-color:#ffd72e66;box-shadow:0 0 0 3px #ffd72e10}select.field{min-height:48px}textarea.field{min-height:134px;max-height:40svh;resize:vertical;font-size:20px;line-height:1.35;padding:14px}.provider-grid{display:grid;grid-template-columns:1fr;gap:8px}.provider-row{display:grid;grid-template-columns:1fr;gap:7px}.styles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px}.styles button{min-height:40px;font-size:9px;border:1px solid #ffffff0c;background:#ffffff06}.go{width:100%;min-height:54px;border:0;border-radius:14px;background:linear-gradient(135deg,var(--yellow),#f4ba19);color:#111;font-size:11px;font-weight:950;letter-spacing:.08em;margin-top:14px;touch-action:manipulation;box-shadow:0 14px 32px #ffd72e18}.go:disabled{opacity:.55}.notice{display:none;margin-top:10px;border-radius:12px;padding:10px 11px;font-size:10px;line-height:1.45}.notice.show{display:block}.notice.error{background:#ff85850e;border:1px solid #ff858529;color:#ffaaaa}.notice.ok{background:#72efa50d;border:1px solid #72efa522;color:#9bf3b8}.result{display:none}.result.show{display:block}.result-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.result-actions{display:flex;gap:6px}.icon{width:42px;height:42px;border-radius:12px;border:1px solid var(--line);background:#ffffff06;color:#c7ced8;font-size:16px}.phrase{font-size:clamp(31px,10.6vw,43px);line-height:1.02;font-weight:950;letter-spacing:-.045em;margin:20px 0 10px;overflow-wrap:anywhere}.phon{color:var(--yellow);font-family:"SFMono-Regular",Menlo,monospace;font-size:11px;line-height:1.6;overflow-wrap:anywhere}.chips{display:flex;gap:7px;flex-wrap:wrap;margin:15px 0}.chips button{min-height:42px;border:1px solid var(--line);background:#ffffff07;color:#dce1e8;border-radius:999px;padding:8px 13px;font-size:11px}.voice-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.voice-row button{min-height:50px;border:1px solid var(--line);background:#ffffff07;color:#e5e8ec;border-radius:13px;font-size:11px;font-weight:800}.explain{font-size:10px;line-height:1.6;color:#788391;margin:15px 0 2px}.device{display:grid;grid-template-columns:1fr auto;gap:8px;align-items:center}.device b{font-size:11px}.device small{display:block;margin-top:4px;color:#697484;font-size:9px;line-height:1.45}.badge{padding:7px 9px;border-radius:999px;background:#72efa50d;border:1px solid #72efa522;color:#86efaa;font-size:8px;font-weight:800;white-space:nowrap}.tiny{font-size:9px;line-height:1.55;color:#687281;margin:9px 0 0}footer{text-align:center;color:#505966;font-size:8px;line-height:1.5;margin-top:22px;padding-bottom:env(safe-area-inset-bottom,0px)}button{-webkit-tap-highlight-color:transparent;cursor:pointer}button:active{transform:scale(.985)}[hidden]{display:none!important}
@media(max-width:380px){.app{padding-left:max(11px,env(safe-area-inset-left,0px));padding-right:max(11px,env(safe-area-inset-right,0px))}.hero h1{font-size:36px}.card{padding:14px}.styles{grid-template-columns:repeat(2,minmax(0,1fr))}.styles button{min-height:42px;font-size:10px}.brand{font-size:12px}.status{font-size:9px}.voice-row{grid-template-columns:1fr}.result-head{align-items:flex-start;flex-wrap:wrap}.result-actions{margin-left:auto}}
@media(hover:none){button:hover{transform:none}}
</style>
</head>
<body>
<main class="app">
  <header class="top"><div class="brand">MINNION<span>ISE</span></div><div class="status"><i class="dot"></i><span id="pairStatus">Paired locally</span></div></header>
  <section class="hero"><div class="eyebrow">DESKTOP AI • PHONE EXPERIENCE</div><h1>Your desktop AI.<em>In your pocket.</em></h1><p class="sub">Translate and practise using your computer's local models over the same Wi-Fi. Nothing needs to leave your network.</p></section>
  <section class="card">
    <div class="mode"><button class="on" id="no">No model</button><button id="my">My model</button></div>
    <div id="providerBox" hidden>
      <div class="section"><label for="provider">LOCAL PROVIDER</label><span id="providerMeta">Desktop</span></div>
      <div class="provider-grid"><div class="provider-row"><select class="field" id="provider"></select><select class="field" id="model"></select></div></div>
    </div>
    <div class="section"><label>STYLE</label><span>Tap to change</span></div>
    <div class="styles" id="styles"><button data-style="gentle">Gentle</button><button class="on" data-style="classic">Classic</button><button data-style="chaos">Chaos</button><button data-style="teacher">Teacher</button></div>
    <div class="section"><label for="input">YOUR SENTENCE</label><span id="count">0 / 500</span></div>
    <textarea class="field" id="input" maxlength="500" placeholder="Good morning everyone, how are you?"></textarea>
    <button class="go" id="go">MINNIONISE ✦</button>
    <div class="notice" id="notice"></div>
  </section>
  <section class="card result" id="result">
    <div class="result-head"><label>YOUR MINNIONESE</label><div class="result-actions"><button class="icon" id="copy" aria-label="Copy">⧉</button><button class="icon" id="share" aria-label="Share">↗</button></div></div>
    <div class="phrase" id="phrase"></div><div class="phon" id="phon"></div><div class="chips" id="chips"></div>
    <div class="voice-row"><button id="slow">🐌 Slow</button><button id="play">▶ Play</button></div><p class="explain" id="explain"></p>
  </section>
  <section class="card device"><div><b>🔒 Local pairing</b><small id="deviceMeta">This phone session is protected by a random pairing token. Stop the bridge to end it.</small></div><span class="badge">LAN ONLY</span></section>
  <footer>🍌 Fan-inspired language experiment • No affiliation with Illumination or Universal.</footer>
</main>
<script>
const TOKEN=__TOKEN__,H={'X-Minnionise-Token':TOKEN},$=s=>document.querySelector(s);let mode='no-model',style='classic',status=null,current=null;
const notice=(m,t='')=>{let n=$('#notice');n.textContent=m;n.className='notice show '+t};
async function load(){try{let r=await fetch('/api/status',{headers:H});if(!r.ok)throw Error('Pairing session is unavailable');status=await r.json();let ps=(status.providers||[]).filter(x=>x.connected&&x.models&&x.models.length);$('#provider').innerHTML=ps.map(p=>'<option value="'+p.id+'">'+p.name+'</option>').join('');fill();$('#my').disabled=!ps.length;$('#providerMeta').textContent=ps.length?ps.length+' provider'+(ps.length===1?'':'s'):'No model server';let voice=(status.voices||[])[0];$('#deviceMeta').textContent=(voice?'Voice: '+voice.name+'. ':'Browser voice fallback. ')+'This session is protected by a random pairing token.'}catch(e){$('#pairStatus').textContent='Connection issue';notice(e.message||'Could not reach the desktop bridge','error')}}
function fill(){let p=(status?.providers||[]).find(x=>x.id===$('#provider').value);$('#model').innerHTML=(p?.models||[]).map(m=>'<option value="'+m.id+'">'+m.name+'</option>').join('')}
$('#provider').onchange=fill;
$('#no').onclick=()=>{mode='no-model';$('#no').className='on';$('#my').className='';$('#providerBox').hidden=true;notice('No Model mode is ready. No AI server is required.','ok')};
$('#my').onclick=()=>{if($('#my').disabled)return;mode='model';$('#my').className='on';$('#no').className='';$('#providerBox').hidden=false;notice('Using the model running on your desktop.','ok')};
$('#styles').onclick=e=>{let b=e.target.closest('[data-style]');if(!b)return;style=b.dataset.style;document.querySelectorAll('[data-style]').forEach(x=>x.classList.toggle('on',x===b))};
$('#input').oninput=e=>$('#count').textContent=e.target.value.length+' / 500';
async function speak(t,rate=1){if(!t)return;try{let v=status?.voices?.[0];if(!v)throw Error();let r=await fetch('/api/speak',{method:'POST',headers:{...H,'Content-Type':'application/json'},body:JSON.stringify({text:t,voice_id:v.id,rate})});if(!r.ok)throw Error();let b=await r.blob(),u=URL.createObjectURL(b),a=new Audio(u);a.onended=()=>URL.revokeObjectURL(u);await a.play()}catch{if('speechSynthesis'in window){speechSynthesis.cancel();let u=new SpeechSynthesisUtterance(t);u.rate=rate;u.pitch=1.12;speechSynthesis.speak(u)}}}
$('#go').onclick=async()=>{let text=$('#input').value.trim();if(!text){notice('Type a sentence first.','error');$('#input').focus();return}let btn=$('#go'),old=btn.textContent;btn.disabled=true;btn.textContent='THINKING…';notice(mode==='model'?'Asking your desktop model…':'Transforming locally…','');try{let p=mode==='no-model'?'no-model':$('#provider').value,m=mode==='no-model'?null:$('#model').value,r=await fetch('/api/translate',{method:'POST',headers:{...H,'Content-Type':'application/json'},body:JSON.stringify({provider:p,model:m,text,style})}),j=await r.json();if(!r.ok)throw Error(j.error||'Translation failed');current=j;$('#phrase').textContent=j.minnionese;$('#phon').textContent='/ '+(j.pronunciation||'')+' /';$('#explain').textContent=j.explanation||'';$('#chips').innerHTML='';(j.syllables||[]).slice(0,28).forEach(s=>{let b=document.createElement('button');b.textContent=s;b.onclick=()=>speak(s,.75);$('#chips').append(b)});$('#result').classList.add('show');notice(mode==='model'?'Generated by your desktop model.':'Generated without an AI model.','ok');navigator.vibrate?.(12);setTimeout(()=>$('#result').scrollIntoView({behavior:'smooth',block:'nearest'}),30)}catch(e){notice(e.message||'Request failed','error')}finally{btn.disabled=false;btn.textContent=old}};
$('#play').onclick=()=>speak($('#phrase').textContent,1);$('#slow').onclick=()=>speak($('#phrase').textContent,.62);
$('#copy').onclick=async()=>{if(!current)return;let t=current.minnionese+'\n'+(current.pronunciation||'');try{await navigator.clipboard.writeText(t);notice('Copied to clipboard.','ok')}catch{notice('Copy is not available in this browser.','error')}};
$('#share').onclick=async()=>{if(!current)return;let data={title:'Minnionise',text:current.minnionese+'\n'+(current.pronunciation||'')};try{if(navigator.share)await navigator.share(data);else await navigator.clipboard.writeText(data.text)}catch{}};
load();
</script>
</body></html>'''
    return page.replace('__TOKEN__', token_js)


core.mobile_page = mobile_page

if __name__ == "__main__":
    core.main()
