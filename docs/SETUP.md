# Setup Guide

Minnionise is deliberately progressive: the website works before you install anything, then unlocks more capability as local components become available.

## 1. No Model mode

Open the GitHub Pages site and keep **No Model** selected.

This mode uses deterministic JavaScript rules stored in `app.js`. It does not call a model endpoint.

## 2. Ollama

Ollama's normal local API is expected at:

```text
http://127.0.0.1:11434
```

Start Ollama and ensure at least one model is installed, for example:

```bash
ollama run qwen3:8b
```

Then use **Connect → Ollama**.

### Direct-browser CORS note

Because the public Minnionise site is served from `https://sukantsondhi.github.io`, direct browser requests may require Ollama to allow that origin. Ollama exposes `OLLAMA_ORIGINS` for additional web origins.

The easiest alternative is the Minnionise Bridge, which talks to Ollama from Python on the same computer and exposes only the narrow API Minnionise needs.

## 3. LM Studio

Start LM Studio's server from its Developer UI or CLI. For direct browser access:

```bash
lms server start --cors
```

The expected endpoint is typically:

```text
http://127.0.0.1:1234
```

Then choose **Connect → LM Studio**.

## 4. Minnionise Bridge

Requirements:

- Python 3.9+
- no third-party Python packages required

Run:

```bash
python local_bridge/server.py
```

Expected URL:

```text
http://127.0.0.1:8765
```

The bridge automatically scans Ollama, LM Studio and supported local voice engines.

### Windows launcher

Double-click:

```text
local_bridge/start_windows.bat
```

### macOS / Linux launcher

```bash
chmod +x local_bridge/start_macos_linux.sh
./local_bridge/start_macos_linux.sh
```

## 5. Phone pairing

Run:

```bash
python local_bridge/server.py --lan
```

Open Minnionise on the computer and choose **Pair by QR**.

See `PHONE_PAIRING.md` for network and security details.

## 6. GitHub Pages

Repository settings:

```text
Settings → Pages → Build and deployment → Source → GitHub Actions
```

Push to `main`; `.github/workflows/pages.yml` deploys the static site.
