# Local Model Providers

## Ollama

Default API base:

```text
http://127.0.0.1:11434
```

Minnionise uses:

- `GET /api/tags`
- `POST /api/chat`

The model is asked to return structured JSON for the Minnionese result, pronunciation, practice chunks and a short explanation.

## LM Studio

Default/common API base:

```text
http://127.0.0.1:1234
```

Minnionise uses its OpenAI-compatible endpoints:

- `GET /v1/models`
- `POST /v1/chat/completions`

For direct browser use, start with CORS enabled:

```bash
lms server start --cors
```

## Minnionise Bridge

The bridge is a provider aggregator rather than another LLM runtime. It discovers Ollama and LM Studio on localhost, then exposes a deliberately narrow API to the web app.

This is the recommended mode because it also provides local voice discovery and phone pairing.

## Voice providers

The bridge can discover/use:

- Piper `.onnx` models when the `piper` binary is available;
- Windows System.Speech;
- macOS `say` voices;
- eSpeak / eSpeak NG on Linux.

If the bridge has no voice engine, the GitHub Pages web app falls back to `SpeechSynthesis` in the browser.
