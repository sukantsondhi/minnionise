# Architecture

## Design goals

1. The public website must remain a pure static GitHub Pages app.
2. No Model mode must always work.
3. Local AI must remain local.
4. Desktop users should have an Ollama-first path with LM Studio support.
5. TTS must be independent from the LLM provider.
6. Phone pairing should avoid fragile HTTPS→HTTP LAN fetch behaviour.
7. The local bridge should use the Python standard library only.

## Components

### Browser application

`index.html`, `styles.css`, and `app.js` provide:

- mode switching;
- deterministic transformation;
- provider discovery;
- direct Ollama/LM Studio inference;
- bridge integration;
- local history and favourites;
- Web Speech fallback;
- microphone recording;
- QR rendering;
- PWA install/offline shell.

### Minnionise Bridge

`local_bridge/server.py` provides a narrow localhost API:

| Endpoint | Purpose |
|---|---|
| `GET /api/health` | health check |
| `GET /api/status` | provider + voice discovery |
| `GET /api/models` | provider/model compatibility view |
| `GET /api/pair` | LAN pairing URL; loopback-only operation |
| `POST /api/translate` | proxy Ollama/LM Studio or run no-model logic |
| `POST /api/speak` | synthesize with an available local voice |
| `GET /mobile?token=...` | token-protected phone UI in LAN mode |

The web client cannot pass arbitrary provider URLs or commands to the bridge.

## Request paths

### No Model

```text
Browser → deterministic transform → browser/system speech
```

### Direct Ollama

```text
GitHub Pages → 127.0.0.1:11434 → local model
```

### Bridge + Ollama

```text
GitHub Pages → 127.0.0.1:8765 → 127.0.0.1:11434 → local model
                                      └──────────────→ local TTS
```

### Phone Link

```text
iPhone Safari → http://desktop-LAN-IP:8765/mobile?token=...
                                   ↓
                          Minnionise Bridge
                           ↙             ↘
                    local model       local TTS
```

The phone UI is served by the desktop bridge so all subsequent API requests are same-origin HTTP on the local network.

## State

Browser settings, history and favourites are saved in `localStorage` under `minnionise:v2`.

The bridge keeps only ephemeral process state, including the random pairing token. Restarting the bridge rotates the token.
