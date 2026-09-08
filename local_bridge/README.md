# Minnionise Local Bridge

A zero-dependency Python companion for the GitHub Pages frontend.

## Desktop-only mode

```bash
python server.py
```

Binds to:

```text
127.0.0.1:8765
```

## Phone Link mode

```bash
python server.py --lan
```

This binds to the computer's local network and enables a random-token protected mobile UI.

## What it discovers

- Ollama at `127.0.0.1:11434`
- LM Studio at `127.0.0.1:1234`
- Piper models if the `piper` executable is on PATH
- Windows system speech
- macOS `say`
- eSpeak / eSpeak NG

## Piper discovery

Common directories include:

- `~/piper`
- `~/models`
- `~/.local/share/piper`
- `~/Documents/piper`

Additional folders can be provided with:

```bash
MINNIONISE_MODEL_DIRS="/path/one:/path/two" python server.py
```

On Windows use the platform path separator (`;`).

## Security

The bridge is intentionally not a generic local proxy. It exposes only the API operations required by Minnionise and calls fixed localhost model-provider endpoints.
