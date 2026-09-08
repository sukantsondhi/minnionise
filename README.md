![Minnionise](docs/banner.svg)

<div align="center">

# 🍌 MINNIONISE

### Local-first Minnionese learning with No-Model mode, Ollama, LM Studio, local voices, and secure phone pairing.

[![Live App](https://img.shields.io/badge/OPEN-LIVE_APP-FFD72E?style=for-the-badge&labelColor=10141b)](https://sukantsondhi.github.io/minnionise/)
[![Pages](https://img.shields.io/github/actions/workflow/status/sukantsondhi/minnionise/pages.yml?style=for-the-badge&label=PAGES&logo=github)](https://github.com/sukantsondhi/minnionise/actions)
[![Local First](https://img.shields.io/badge/AI-LOCAL_FIRST-69F0A3?style=for-the-badge&labelColor=10141b)](#privacy--security)
[![Python](https://img.shields.io/badge/BRIDGE-PYTHON-5DA8FF?style=for-the-badge&labelColor=10141b&logo=python&logoColor=white)](local_bridge/README.md)

**No cloud required • No account required • No API key required**

</div>

---

## ✨ What is Minnionise?

Minnionise is a playful, fan-inspired language and pronunciation lab. Type a sentence, transform it into original Minnionese-style gibberish, break it into pronunciation chunks, hear it spoken, practise it, and optionally power the transformation with an LLM already running on your own computer.

The app is intentionally **progressive**:

| Power level | What you need | What happens |
| --- | --- | --- |
| ◌ **No Model** | Nothing | Deterministic local transformation in your browser |
| ✦ **My Model** | Ollama or LM Studio | Your local LLM generates richer translations and explanations |
| 🔊 **Local Voice** | Minnionise Bridge | Piper/system voices can speak the result locally |
| 📱 **Phone Link** | Bridge in `--lan` mode | Scan a QR code and use the desktop model from iPhone/iPad |

---

## 🚀 Live app

**https://sukantsondhi.github.io/minnionise/**

The public app is a static site and is deployed free through GitHub Pages.

---

## 🍌 Highlights

- **No-Model Mode** — usable immediately without an LLM, Python server, API, or cloud service.
- **My-Model Mode** — connect Ollama, LM Studio, or the Minnionise Bridge.
- **Auto discovery** — scan local providers and list their installed models.
- **Independent brain + voice** — use one local model for language and a different local engine for speech.
- **Voice Coach** — normal playback, slow playback, repeat ×3, speed control, and tappable pronunciation chunks.
- **Local recording** — record your own attempt without uploading the audio.
- **History + favourites** — stored in browser local storage.
- **Copy + native share** — share generated Minnionese from supported devices.
- **Secure QR phone pairing** — use desktop AI from iPhone/iPad over your local network.
- **Responsive mobile UX** — safe-area support, thumb-sized controls, bottom-sheet modals, long-text hardening, small-screen layouts, and iOS-friendly form sizing.
- **PWA-ready** — manifest + service worker caching.
- **Responsive UI** — designed for desktop, laptop, iPad, and phone.
- **Local-first security** — loopback binding by default, explicit LAN mode, origin checks, and a random phone token.

---

## 🧠 Architecture

```text
                         MINNIONISE WEB APP
                   GitHub Pages / static frontend
                              │
             ┌────────────────┼────────────────┐
             │                │                │
             ▼                ▼                ▼
        NO MODEL         DIRECT LOCAL      MINNIONISE
        Browser logic       MODEL             BRIDGE
                            │                 :8765
                       ┌────┴─────┐        ┌───┴────┐
                       │          │        │        │
                    Ollama    LM Studio  Ollama   LM Studio
                    :11434      :1234
                                           │
                                           ├── Piper
                                           ├── Windows SAPI
                                           ├── macOS `say`
                                           └── eSpeak
                                                │
                                                ▼
                                         PHONE LINK
                                    QR + LAN pairing token
```

More detail: [Architecture docs](docs/ARCHITECTURE.md)

---

## ⚡ Quick start

### Option A — zero setup

Open the live app and leave **No Model** selected.

That's it.

The transformation is performed by a deterministic browser-side engine and browser speech synthesis is used when no local voice bridge is connected.

### Option B — Ollama

Install/start Ollama and make sure you have at least one model:

```bash
ollama pull qwen3:8b
ollama serve
```

Then open Minnionise → **My Model** → **Connect** → **Ollama**.

For the most reliable browser connection, use the bridge below. It removes the need to tune each model server's CORS configuration.

### Option C — LM Studio

Load a model in LM Studio and start its server.

CLI example:

```bash
lms server start --cors
```

Then choose **LM Studio** from the Minnionise Connection Center.

### Option D — recommended: Minnionise Bridge

Clone the repository:

```bash
git clone https://github.com/sukantsondhi/minnionise.git
cd minnionise
```

Start the bridge:

**Windows**

```bat
local_bridge\start_windows.bat
```

or:

```bash
python local_bridge/server.py
```

**macOS / Linux**

```bash
./local_bridge/start_macos_linux.sh
```

or:

```bash
python3 local_bridge/server.py
```

The bridge listens on:

```text
http://127.0.0.1:8765
```

Then click **Connect** in Minnionise. The web app will discover the bridge, installed local models, and available local voices.

Full setup guide: [docs/SETUP.md](docs/SETUP.md)

---

## 📱 iPhone / iPad QR pairing

The phone architecture deliberately differs from desktop browser → localhost access.

Start the bridge with LAN mode:

```bash
python local_bridge/server.py --lan
```

Then:

1. Open Minnionise on the computer.
2. Select **Pair by QR**.
3. Generate the QR code.
4. Make sure the iPhone/iPad and computer are on the same Wi-Fi.
5. Scan it using the Camera app.
6. Minnionise Mobile opens directly from the computer.

The QR URL looks conceptually like:

```text
http://192.168.x.x:8765/mobile?token=<random-pairing-token>
```

This approach means the phone UI and API share the same local HTTP origin. It avoids an HTTPS GitHub Pages page having to make mixed-content HTTP requests to your LAN computer.

The paired mobile UI is specifically optimized for phone screens: safe areas, no horizontal overflow, ≥44px touch targets, 16px form controls to avoid iOS zoom, responsive result text, and compact No-Model/My-Model controls.

See: [docs/PHONE_PAIRING.md](docs/PHONE_PAIRING.md)

> LAN mode exposes the bridge to your local network. Remote API requests require the cryptographically random pairing token. Stop the bridge when you are finished if you do not want it listening on your LAN.

---

## 🔌 Supported local providers

### Ollama

Minnionise uses:

```text
GET  /api/tags
POST /api/chat
```

Default endpoint:

```text
http://127.0.0.1:11434
```

### LM Studio

Minnionise uses the local OpenAI-compatible endpoints:

```text
GET  /v1/models
POST /v1/chat/completions
```

Default endpoint:

```text
http://127.0.0.1:1234
```

### Minnionise Bridge

```text
GET  /api/health
GET  /api/status
GET  /api/models
GET  /api/pair
POST /api/translate
POST /api/speak
```

Details: [docs/PROVIDERS.md](docs/PROVIDERS.md)

---

## 🔊 Local voices

The bridge scans for supported local speech engines.

### Piper

If the `piper` executable is available, the bridge searches common model locations plus directories provided through:

```bash
MINNIONISE_MODEL_DIRS
```

Example:

```bash
export MINNIONISE_MODEL_DIRS="$HOME/voices:$HOME/Downloads/piper"
python local_bridge/server.py
```

Windows PowerShell example:

```powershell
$env:MINNIONISE_MODEL_DIRS="$HOME\Documents\piper"
python local_bridge\server.py
```

### System speech

Fallback local engines include:

- Windows: `System.Speech` / SAPI
- macOS: `say`
- Linux: `espeak-ng` or `espeak`

If none are available, the public web app still falls back to browser `SpeechSynthesis`.

---

## 🧪 No-Model engine

No Model mode is not pretending to be an LLM.

It is a deterministic local transformation engine consisting of:

1. a small original playful vocabulary map,
2. pronunciation-friendly sound substitutions,
3. style rules,
4. deterministic endings,
5. automatic pronunciation chunk generation.

Available styles:

- **Gentle**
- **Classic**
- **Chaos**
- **Teacher**

This guarantees that Minnionise remains useful even if no AI runtime exists on the device.

---

## 🎛 User experience

The interface includes:

```text
No Model  ↔  My Model
      │
      ▼
Sentence Composer
      │
      ▼
Minnionese Result
      │
      ├── pronunciation guide
      ├── tappable practice chunks
      ├── voice playback
      ├── slow playback
      ├── repeat ×3
      ├── recording
      ├── copy/share
      └── favourites/history
```

On phones the UI changes rather than merely shrinking: status cards collapse, style controls reflow, connection modals become bottom sheets, provider cards become stacked touch targets, long model names/URLs wrap safely, and iPhone safe-area insets are respected.

---

## 🔐 Privacy & security

Minnionise is intentionally local-first.

### Desktop default

```bash
python local_bridge/server.py
```

binds to:

```text
127.0.0.1
```

It therefore does **not** listen on the LAN.

### LAN / phone mode

```bash
python local_bridge/server.py --lan
```

binds to the local network so another device can connect.

Protections include:

- random high-entropy pairing token on every bridge launch,
- token requirement for non-loopback clients,
- explicit allowed browser origins,
- loopback/LAN binding rather than public hosting,
- no arbitrary provider proxy URL,
- maximum request sizes,
- no cloud analytics in the project,
- no account or authentication database.

Read the security model before exposing LAN mode: [docs/SECURITY.md](docs/SECURITY.md)

---

## 📁 Project structure

```text
minnionise/
├── index.html
├── styles.css              # responsive override layer
├── styles-base.css         # core visual system
├── app.js
├── favicon.svg
├── manifest.webmanifest
├── sw.js
├── 404.html
├── .nojekyll
├── README.md
├── LICENSE
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SETUP.md
│   ├── PROVIDERS.md
│   ├── PHONE_PAIRING.md
│   └── SECURITY.md
├── local_bridge/
│   ├── server.py            # mobile-first entrypoint
│   ├── server_core.py       # bridge implementation
│   ├── start_windows.bat
│   ├── start_macos_linux.sh
│   ├── models.example.json
│   └── README.md
└── .github/
    └── workflows/
        └── pages.yml
```

---

## 🌐 GitHub Pages deployment

The application frontend requires **no build step**.

Every push to `main` runs:

```text
.github/workflows/pages.yml
```

which packages the static application and deploys it using the official GitHub Pages actions.

The workflow includes both the base visual system and the mobile override stylesheet, so the exact production UI is what gets deployed.

---

## 🛠 Development

Run the frontend locally:

```bash
python -m http.server 8000
```

Then visit:

```text
http://127.0.0.1:8000
```

In another terminal:

```bash
python local_bridge/server.py
```

For phone testing:

```bash
python local_bridge/server.py --lan
```

---

## 🗺 Roadmap

Potential future additions:

- local Whisper pronunciation scoring,
- browser-native WebGPU model mode,
- packaged Windows/macOS bridge installers,
- custom local voice selection,
- downloadable language packs,
- richer lesson mode,
- pronunciation streaks and training sessions,
- optional Ollama model recommendations based on device RAM/VRAM.

---

## ⚠️ Fan project notice

Minnionise is an independent fan-inspired experimental project. It is not affiliated with, endorsed by, or sponsored by Illumination, Universal Pictures, or the owners of the Minions intellectual property.

The project intentionally uses original UI artwork and original playful language rules rather than distributing copyrighted character artwork, film audio, or dialogue.

---

<div align="center">

### 🍌 Bello. Build local. Keep it private.

Made by [Sukant Sondhi](https://github.com/sukantsondhi)

</div>
