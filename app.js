(() => {
  'use strict';

  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const BRIDGE = 'http://127.0.0.1:8765';
  const OLLAMA = 'http://127.0.0.1:11434';
  const LMSTUDIO = 'http://127.0.0.1:1234';
  const STORE = 'minnionise:v2';

  const state = {
    mode: 'no-model',
    style: 'classic',
    provider: 'no-model',
    model: null,
    models: [],
    bridgeToken: '',
    bridge: null,
    providers: { bridge: false, ollama: false, lmstudio: false },
    current: null,
    recording: null,
    recorder: null,
    installPrompt: null,
    historyView: 'history'
  };

  const fallbackLexicon = {
    hello: 'bello', hi: 'bello', goodbye: 'poopaye', bye: 'poopaye', friend: 'amigo', friends: 'amigos',
    thank: 'tank', thanks: 'tank yu', you: 'tu', your: 'tu', yes: 'si', no: 'na', love: 'luv',
    banana: 'banana', everyone: 'tulaliloo', everybody: 'tulaliloo', what: 'wha', look: 'luk',
    stop: 'stupa', please: 'por favor', morning: 'matoka', night: 'noche', good: 'bon', very: 'bello-bello',
    beautiful: 'bella', happy: 'papoy', party: 'banana party', food: 'papa', help: 'bee-do', fire: 'bee-do',
    boss: 'big boss', work: 'worka', school: 'skoola', today: 'toda', tomorrow: 'tomorra',
    how: 'como', are: 'be', is: 'be', my: 'mi', our: 'nossa', we: 'wi', i: 'mi', me: 'mi'
  };

  const styleTail = {
    gentle: [' banana.', ' papoy.'],
    classic: [' banana!', ' tulaliloo!', ' papoy!'],
    chaos: [' BANANA! BEE-DO!', ' tulaliloo papoy BANANA!', ' poopaye? BANANA BANANA!'],
    teacher: [' banana.']
  };

  function store() {
    try { return JSON.parse(localStorage.getItem(STORE) || '{}'); } catch { return {}; }
  }
  function saveStore(patch) {
    localStorage.setItem(STORE, JSON.stringify({ ...store(), ...patch }));
  }
  function toast(title, message = '', type = '') {
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<b>${escapeHTML(title)}</b>${message ? `<span>${escapeHTML(message)}</span>` : ''}`;
    $('#toastStack').append(el);
    setTimeout(() => el.remove(), 3600);
  }
  function escapeHTML(s = '') { return String(s).replace(/[&<>'"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c])); }
  function openModal(id) { const m = $('#' + id); if (m) { m.hidden = false; document.body.style.overflow = 'hidden'; } }
  function closeModal(id) { const m = $('#' + id); if (m) { m.hidden = true; document.body.style.overflow = ''; } }
  function copyText(text) { navigator.clipboard?.writeText(text).then(() => toast('Copied', 'Ready to paste.', 'success')).catch(() => toast('Copy failed', 'Select and copy it manually.', 'error')); }

  function splitSyllables(text) {
    const words = String(text).replace(/[^a-zA-ZÀ-ÿ'\-\s]/g, ' ').split(/\s+/).filter(Boolean);
    const out = [];
    for (const word of words) {
      if (word.length <= 5) { out.push(word); continue; }
      const chunks = word.match(/[^aeiouy]*[aeiouy]+(?:[^aeiouy](?=[^aeiouy]|$))?/gi);
      if (chunks?.length) out.push(...chunks); else out.push(word);
    }
    return out.slice(0, 28);
  }

  function localTransform(text, style) {
    const original = text.trim();
    let mapped = original.toLowerCase().replace(/\b[a-z']+\b/gi, raw => {
      const w = raw.toLowerCase();
      if (fallbackLexicon[w]) return fallbackLexicon[w];
      let t = w.replace(/tion\b/g, 'shun').replace(/ing\b/g, 'in').replace(/^th/g, 'd').replace(/th/g, 't');
      if (style === 'chaos' && t.length > 7) t = t.slice(0, Math.ceil(t.length * .7)) + 'a';
      return t;
    });
    mapped = mapped.replace(/\bi am\b/g, 'mi be').replace(/\bdo not\b/g, 'no-no').replace(/\bvery very\b/g, 'bello-bello');
    const tails = styleTail[style] || styleTail.classic;
    const deterministic = tails[(original.length + style.length) % tails.length];
    const prefix = /^bello\b/i.test(mapped) ? '' : (style === 'gentle' ? 'bello, ' : 'Bello! ');
    const phrase = (prefix + mapped.replace(/[.!?]+$/,'') + deterministic).replace(/\s+/g,' ').trim();
    const pronunciation = splitSyllables(phrase).map(s => s.toLowerCase()).join(' · ');
    const explanation = style === 'teacher'
      ? 'Built-in teacher mode swaps familiar fan-inspired vocabulary first, then applies simple sound rules so the result stays easy to imitate.'
      : 'Generated entirely in your browser with Minnionise’s deterministic no-model phrase engine. No AI server or cloud request was used.';
    return { minnionese: phrase, pronunciation, syllables: splitSyllables(phrase), explanation, source: 'No Model engine' };
  }

  function systemPrompt(style) {
    return `You are Minnionise, a playful fan-inspired fictional-language pronunciation coach. Transform the user's English sentence into original playful banana-language inspired by comic gibberish, without quoting movie dialogue. Preserve meaning, keep it pronounceable, and avoid offensive content. Style=${style}. Return ONLY valid JSON with exactly these keys: minnionese (string), pronunciation (simple phonetic string separated with middle dots), syllables (array of max 24 short strings), explanation (one concise sentence). Do not use markdown.`;
  }
  function parseModelJSON(raw) {
    const text = String(raw || '').trim().replace(/^```(?:json)?/i,'').replace(/```$/,'').trim();
    let obj;
    try { obj = JSON.parse(text); } catch {
      const start = text.indexOf('{'), end = text.lastIndexOf('}');
      if (start >= 0 && end > start) obj = JSON.parse(text.slice(start, end + 1)); else throw new Error('Model did not return valid JSON');
    }
    if (!obj.minnionese) throw new Error('Model response is missing minnionese');
    obj.pronunciation ||= splitSyllables(obj.minnionese).join(' · ');
    obj.syllables = Array.isArray(obj.syllables) && obj.syllables.length ? obj.syllables.slice(0,24) : splitSyllables(obj.minnionese);
    obj.explanation ||= 'Generated by your connected local model.';
    return obj;
  }

  async function fetchTimeout(url, options = {}, ms = 2600) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), ms);
    try {
      const req = { ...options, signal: controller.signal };
      // New Local Network Access implementations can use this hint; unsupported browsers ignore the plain fetch path below.
      try {
        if (location.protocol === 'https:' && /^http:\/\/(127\.0\.0\.1|localhost)/.test(url) && typeof Request !== 'undefined') {
          const r = new Request(url, { ...req, targetAddressSpace: 'loopback' });
          return await fetch(r);
        }
      } catch (_) {}
      return await fetch(url, req);
    } finally { clearTimeout(timer); }
  }

  async function scanBridge() {
    try {
      const r = await fetchTimeout(`${BRIDGE}/api/status`, { headers: state.bridgeToken ? {'X-Minnionise-Token': state.bridgeToken} : {} }, 1800);
      if (!r.ok) throw new Error('Bridge unavailable');
      const data = await r.json();
      state.providers.bridge = true; state.bridge = data;
      state.bridgeToken = data.token || state.bridgeToken;
      return data;
    } catch { state.providers.bridge = false; state.bridge = null; return null; }
  }
  async function scanOllama() {
    try {
      const r = await fetchTimeout(`${OLLAMA}/api/tags`, {}, 1600); if (!r.ok) throw 0;
      const j = await r.json(); state.providers.ollama = true; return (j.models || []).map(x => ({ id: x.name, name: x.name, meta: x.details?.parameter_size || x.details?.family || 'Ollama' }));
    } catch { state.providers.ollama = false; return []; }
  }
  async function scanLMStudio() {
    try {
      const r = await fetchTimeout(`${LMSTUDIO}/v1/models`, {}, 1600); if (!r.ok) throw 0;
      const j = await r.json(); state.providers.lmstudio = true; return (j.data || []).map(x => ({ id: x.id, name: x.id, meta: 'LM Studio' }));
    } catch { state.providers.lmstudio = false; return []; }
  }
  async function scanConnections(showToast = false) {
    $('#bridgeDiag').textContent = $('#ollamaDiag').textContent = $('#lmDiag').textContent = 'Scanning…';
    ['bridge','ollama','lm'].forEach(x => $('#' + x + 'Light').className = 'diag-light');
    const [bridge, ollama, lm] = await Promise.all([scanBridge(), scanOllama(), scanLMStudio()]);
    const bridgeModels = bridge?.providers?.flatMap(p => (p.models || []).map(m => ({ id:m.id || m.name, name:m.name || m.id, meta:p.name, provider:p.id }))) || [];
    const status = [
      ['bridge', !!bridge, bridge ? `${bridgeModels.length} models` : 'Not running'],
      ['ollama', !!ollama.length, ollama.length ? `${ollama.length} models` : 'Not reachable'],
      ['lm', !!lm.length, lm.length ? `${lm.length} models` : 'Not reachable']
    ];
    status.forEach(([id, live, label]) => { $('#' + id + 'Light').classList.add(live ? 'live' : 'fail'); $('#' + id + 'Diag').textContent = label; });
    $('#bridgeOptionState').textContent = bridge ? 'Connected' : 'Start'; $('#bridgeOptionState').classList.toggle('live', !!bridge);
    $('#ollamaOptionState').textContent = ollama.length ? `${ollama.length} models` : 'Setup'; $('#ollamaOptionState').classList.toggle('live', !!ollama.length);
    $('#lmOptionState').textContent = lm.length ? `${lm.length} models` : 'Setup'; $('#lmOptionState').classList.toggle('live', !!lm.length);
    if (showToast) toast('Connection scan complete', bridge ? 'Bridge detected.' : (ollama.length || lm.length ? 'Local model server detected.' : 'No local AI server detected.'), bridge || ollama.length || lm.length ? 'success' : '');
    return { bridge, ollama, lm, bridgeModels };
  }

  async function chooseProvider(provider) {
    if (provider === 'no-model') { setMode('no-model'); closeModal('connectModal'); return; }
    const scan = await scanConnections();
    let models = [];
    if (provider === 'bridge') models = scan.bridgeModels;
    if (provider === 'ollama') models = scan.ollama.map(x => ({...x, provider:'ollama'}));
    if (provider === 'lmstudio') models = scan.lm.map(x => ({...x, provider:'lmstudio'}));
    if (!models.length) {
      toast(`${provider === 'lmstudio' ? 'LM Studio' : provider[0].toUpperCase()+provider.slice(1)} is not ready`, 'Use the setup instructions below, then scan again.', 'error');
      return;
    }
    state.provider = provider; state.models = models; setMode('my-model'); showModelPicker();
  }

  function showModelPicker() {
    $('#modelProviderLabel').textContent = state.provider === 'bridge' ? 'Minnionise Bridge' : state.provider === 'ollama' ? 'Ollama' : 'LM Studio';
    const list = $('#modelList'); list.innerHTML = '';
    state.models.forEach(m => {
      const b = document.createElement('button'); b.className = `model-item ${state.model?.id === m.id ? 'active':''}`;
      b.innerHTML = `<span class="radio"></span><div><b>${escapeHTML(m.name)}</b><small>${escapeHTML(m.meta || m.provider || '')}</small></div>`;
      b.onclick = () => { state.model = m; state.provider = state.provider || m.provider; saveStore({ provider: state.provider, model: m }); updateModeUI(); closeModal('modelModal'); closeModal('connectModal'); toast('Local model connected', m.name, 'success'); };
      list.append(b);
    });
    openModal('modelModal');
  }

  async function runModel(text) {
    if (!state.model) throw new Error('Select a local model first');
    const messages = [{ role:'system', content: systemPrompt(state.style) }, { role:'user', content:text }];
    if (state.provider === 'bridge') {
      const r = await fetchTimeout(`${BRIDGE}/api/translate`, { method:'POST', headers:{'Content-Type':'application/json', ...(state.bridgeToken ? {'X-Minnionise-Token':state.bridgeToken}:{})}, body:JSON.stringify({ provider:state.model.provider, model:state.model.id, text, style:state.style }) }, 65000);
      const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Bridge translation failed'); return j;
    }
    if (state.provider === 'ollama') {
      const r = await fetchTimeout(`${OLLAMA}/api/chat`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ model:state.model.id, messages, stream:false, format:'json', options:{temperature:.35} }) }, 65000);
      const j = await r.json(); if (!r.ok) throw new Error(j.error || 'Ollama request failed'); return parseModelJSON(j.message?.content);
    }
    if (state.provider === 'lmstudio') {
      const r = await fetchTimeout(`${LMSTUDIO}/v1/chat/completions`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ model:state.model.id, messages, temperature:.35, max_tokens:550 }) }, 65000);
      const j = await r.json(); if (!r.ok) throw new Error(j.error?.message || 'LM Studio request failed'); return parseModelJSON(j.choices?.[0]?.message?.content);
    }
    throw new Error('Unsupported model provider');
  }

  function renderResult(result, input) {
    state.current = { ...result, input, timestamp: Date.now(), provider: state.mode === 'no-model' ? 'no-model' : state.provider, model: state.model?.name || 'Built-in engine' };
    $('#resultPhrase').textContent = result.minnionese;
    $('#pronunciation').textContent = `/ ${result.pronunciation || splitSyllables(result.minnionese).join(' · ')} /`;
    $('#explanation').textContent = result.explanation || '';
    const chips = $('#syllables'); chips.innerHTML = '';
    (result.syllables || splitSyllables(result.minnionese)).slice(0,28).forEach(s => {
      const b = document.createElement('button'); b.textContent = s; b.onclick = () => speak(s, +$('#speedRange').value * .8); chips.append(b);
    });
    $('#resultZone').hidden = false;
    addHistory(state.current);
    setTimeout(() => $('#resultZone').scrollIntoView({behavior:'smooth',block:'nearest'}), 30);
  }

  async function translate() {
    const text = $('#sentenceInput').value.trim();
    if (!text) { $('#sentenceInput').focus(); toast('Add a sentence first'); return; }
    const btn = $('#translateBtn'); btn.disabled = true; const old = btn.innerHTML; btn.innerHTML = '<span>THINKING…</span><i>◌</i>';
    try {
      let result;
      if (state.mode === 'no-model') result = localTransform(text, state.style);
      else result = await runModel(text);
      renderResult(result, text);
    } catch (e) {
      toast('Local model request failed', e.message || 'Switching is always available in No Model mode.', 'error');
    } finally { btn.disabled = false; btn.innerHTML = old; }
  }

  function browserSpeak(text, rate = .9) {
    if (!('speechSynthesis' in window)) return toast('Voice unavailable', 'This browser does not expose speech synthesis.', 'error');
    speechSynthesis.cancel(); const u = new SpeechSynthesisUtterance(text); u.rate = rate; u.pitch = 1.14; speechSynthesis.speak(u);
  }
  async function speak(text, rate = .9) {
    if (!text) return;
    if (state.providers.bridge && state.bridge?.voices?.length) {
      try {
        const voice = state.bridge.voices[0];
        const r = await fetchTimeout(`${BRIDGE}/api/speak`, { method:'POST', headers:{'Content-Type':'application/json', ...(state.bridgeToken ? {'X-Minnionise-Token':state.bridgeToken}:{})}, body:JSON.stringify({text, voice_id:voice.id, rate}) }, 50000);
        if (!r.ok) throw 0; const blob = await r.blob(); const url = URL.createObjectURL(blob); const a = new Audio(url); a.onended=()=>URL.revokeObjectURL(url); await a.play(); return;
      } catch (_) {}
    }
    browserSpeak(text, rate);
  }

  function addHistory(entry) {
    const db = store(); const hist = db.history || [];
    const clean = hist.filter(x => x.minnionese !== entry.minnionese); clean.unshift(entry); saveStore({history:clean.slice(0,40)}); renderHistory();
  }
  function renderHistory() {
    const db = store(); const items = state.historyView === 'favorites' ? (db.favorites || []) : (db.history || []); const list = $('#historyList'); list.innerHTML='';
    if (!items.length) { list.innerHTML = `<div class="empty-state">${state.historyView === 'favorites' ? 'No favourites yet. Tap ☆ on a result.' : 'Your local history is empty.'}</div>`; return; }
    items.forEach(item => {
      const el = document.createElement('button'); el.className='history-entry'; const date = new Date(item.timestamp || Date.now());
      el.innerHTML=`<div><b>${escapeHTML(item.minnionese)}</b><span>${escapeHTML(item.input || '')}</span></div><time>${date.toLocaleDateString()}</time>`;
      el.onclick=()=>{renderResult(item,item.input||'');closeModal('historyModal')}; list.append(el);
    });
  }
  function toggleFavorite() {
    if (!state.current) return; const db=store(), fav=db.favorites||[]; const exists=fav.some(x=>x.minnionese===state.current.minnionese);
    const next=exists?fav.filter(x=>x.minnionese!==state.current.minnionese):[state.current,...fav].slice(0,40); saveStore({favorites:next}); $('#favoriteBtn').textContent=exists?'☆':'★'; toast(exists?'Removed from favourites':'Saved to favourites','Stored only in this browser.','success'); renderHistory();
  }

  function setMode(mode) {
    state.mode = mode;
    if (mode === 'no-model') { state.provider='no-model'; state.model=null; }
    saveStore({mode, provider:state.provider, model:state.model}); updateModeUI();
  }
  function updateModeUI() {
    $$('[data-app-mode]').forEach(b => { const active=b.dataset.appMode===state.mode; b.classList.toggle('active',active); b.setAttribute('aria-selected',String(active)); });
    const modelMode = state.mode === 'my-model'; $('#providerRibbon').hidden = !modelMode;
    if (modelMode) {
      $('#activeModelLabel').textContent = state.model?.name || 'Select a local model';
      $('#brainStatus').textContent = state.model?.name || 'My Model mode';
      $('#brainMeta').textContent = state.provider === 'bridge' ? 'via Minnionise Bridge' : state.provider === 'ollama' ? 'Ollama' : state.provider === 'lmstudio' ? 'LM Studio' : 'Connect a provider';
      $('#connectionLabel').textContent = state.model ? state.model.name : 'My model'; $('#connectionDot').classList.toggle('live', !!state.model);
    } else {
      $('#brainStatus').textContent='Built-in engine'; $('#brainMeta').textContent='Zero setup'; $('#connectionLabel').textContent='No model'; $('#connectionDot').classList.remove('live');
    }
    if (state.providers.bridge && state.bridge?.voices?.length) { $('#voiceStatus').textContent=state.bridge.voices[0].name; $('#voiceMeta').textContent='Minnionise Bridge'; }
    else { $('#voiceStatus').textContent='Browser voice'; $('#voiceMeta').textContent='On this device'; }
  }

  async function generatePairing() {
    const qr = $('#qrCode'); qr.innerHTML = '<div class="qr-placeholder">⌁<small>Checking your local bridge…</small></div>';
    const bridge = await scanBridge(); updateModeUI();
    if (!bridge) { qr.innerHTML='<div class="qr-placeholder">⌁<small>Bridge not detected. Start it with <b>--lan</b> on your computer.</small></div>'; $('#pairUrlBox').hidden=true; return; }
    try {
      const r=await fetchTimeout(`${BRIDGE}/api/pair`,{headers:state.bridgeToken?{'X-Minnionise-Token':state.bridgeToken}:{}}); const data=await r.json();
      if (!r.ok || !data.url) throw new Error(data.error||'LAN mode is not enabled');
      $('#pairUrl').textContent=data.url; $('#pairUrlBox').hidden=false; qr.innerHTML='';
      if (window.QRCode) new QRCode(qr,{text:data.url,width:220,height:220,colorDark:'#101214',colorLight:'#f7f5e9',correctLevel:QRCode.CorrectLevel.M});
      else qr.innerHTML=`<div class="qr-placeholder">⌁<small>QR library could not load. Copy the pairing URL instead.</small></div>`;
    } catch(e){ qr.innerHTML=`<div class="qr-placeholder">⌁<small>${escapeHTML(e.message)}. Restart with <b>python local_bridge/server.py --lan</b>.</small></div>`; $('#pairUrlBox').hidden=true; }
  }

  async function startRecording() {
    if (state.recorder?.state === 'recording') { state.recorder.stop(); return; }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({audio:true}); const chunks=[]; const rec=new MediaRecorder(stream); state.recorder=rec;
      rec.ondataavailable=e=>chunks.push(e.data); rec.onstop=()=>{ stream.getTracks().forEach(t=>t.stop()); const blob=new Blob(chunks,{type:rec.mimeType}); if(state.recording)URL.revokeObjectURL(state.recording); state.recording=URL.createObjectURL(blob); const a=$('#recordingPlayback');a.src=state.recording;a.hidden=false; $('#recordBtn').classList.remove('recording'); $('#recordBtn b').textContent='Record again'; };
      rec.start(); $('#recordBtn').classList.add('recording'); $('#recordBtn b').textContent='Stop recording'; toast('Recording locally','Nothing is uploaded.','success');
    } catch(e){ toast('Microphone unavailable', e.message || 'Allow microphone access in your browser.', 'error'); }
  }

  function bind() {
    $$('[data-close-modal]').forEach(b=>b.onclick=()=>closeModal(b.dataset.closeModal));
    $$('.modal-backdrop').forEach(m=>m.addEventListener('click',e=>{if(e.target===m)closeModal(m.id)}));
    $$('[data-app-mode]').forEach(b=>b.onclick=()=>{ if(b.dataset.appMode==='my-model'){setMode('my-model');openModal('connectModal');scanConnections();}else setMode('no-model'); });
    $$('.style-picker button').forEach(b=>b.onclick=()=>{$$('.style-picker button').forEach(x=>x.classList.remove('active'));b.classList.add('active');state.style=b.dataset.style;saveStore({style:state.style})});
    $('#sentenceInput').addEventListener('input',e=>$('#charCount').textContent=`${e.target.value.length} / 500`);
    $('#sentenceInput').addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter')translate()});
    $('#translateBtn').onclick=translate; $('#openConnectBtn').onclick=()=>{openModal('connectModal');scanConnections()}; $('#changeModelBtn').onclick=()=>{openModal('connectModal');scanConnections()};
    $$('.provider-option').forEach(b=>b.onclick=()=>chooseProvider(b.dataset.provider));
    $('#refreshModelsBtn').onclick=async()=>{await chooseProvider(state.provider)};
    $$('.help-tabs button').forEach(b=>b.onclick=()=>{$$('.help-tabs button').forEach(x=>x.classList.toggle('active',x===b));$$('[data-help-panel]').forEach(p=>p.hidden=p.dataset.helpPanel!==b.dataset.help)});
    $$('[data-copy-command]').forEach(b=>b.onclick=()=>copyText($('code',b.parentElement).textContent));
    $('#quickPairBtn').onclick=()=>{openModal('pairModal');generatePairing()}; $('#refreshPairBtn').onclick=generatePairing; $('#copyPairUrl').onclick=()=>copyText($('#pairUrl').textContent);
    $('#playBtn').onclick=()=>speak(state.current?.minnionese,+$('#speedRange').value); $('#slowBtn').onclick=()=>speak(state.current?.minnionese,.62);
    $('#repeatBtn').onclick=async()=>{for(let i=0;i<3;i++){speak(state.current?.minnionese,+$('#speedRange').value);await new Promise(r=>setTimeout(r,Math.max(1300,(state.current?.minnionese?.length||20)*55)))}};
    $('#speedRange').oninput=e=>$('#speedValue').textContent=(+e.target.value).toFixed(2)+'×'; $('#recordBtn').onclick=startRecording;
    $('#copyBtn').onclick=()=>copyText(`${state.current?.minnionese || ''}\n${state.current?.pronunciation ? '/ '+state.current.pronunciation+' /':''}`); $('#favoriteBtn').onclick=toggleFavorite;
    $('#shareBtn').onclick=async()=>{if(!state.current)return;const data={title:'Minnionise',text:`${state.current.minnionese}\n${state.current.pronunciation||''}`,url:location.href};try{if(navigator.share)await navigator.share(data);else copyText(data.text)}catch{}};
    $('#openHistoryBtn').onclick=()=>{renderHistory();openModal('historyModal')}; $$('.history-tabs [data-history]').forEach(b=>b.onclick=()=>{state.historyView=b.dataset.history;$$('.history-tabs [data-history]').forEach(x=>x.classList.toggle('active',x===b));renderHistory()});
    $('#clearHistoryBtn').onclick=()=>{const db=store();saveStore({...db,history:[],favorites:[]});renderHistory();toast('Local library cleared')};
    window.addEventListener('beforeinstallprompt',e=>{e.preventDefault();state.installPrompt=e;$('#installBtn').hidden=false}); $('#installBtn').onclick=async()=>{if(state.installPrompt){state.installPrompt.prompt();await state.installPrompt.userChoice;state.installPrompt=null;$('#installBtn').hidden=true}};
    document.addEventListener('keydown',e=>{if(e.key==='Escape')$$('.modal-backdrop:not([hidden])').forEach(m=>closeModal(m.id))});
  }

  async function init() {
    const db=store(); state.mode=db.mode||'no-model'; state.style=db.style||'classic'; state.provider=db.provider||'no-model'; state.model=db.model||null;
    $$('.style-picker button').forEach(b=>b.classList.toggle('active',b.dataset.style===state.style)); bind(); renderHistory(); updateModeUI();
    if ('serviceWorker' in navigator) navigator.serviceWorker.register('./sw.js').catch(()=>{});
    const bridge=await scanBridge(); if(bridge){state.providers.bridge=true;updateModeUI()}
    // If a stored model was connected through a direct provider, don't make a surprise request on startup; verify only when My Model mode is used.
    if(state.mode==='my-model'&&state.model) updateModeUI();
  }
  init();
})();
