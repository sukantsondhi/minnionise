# Security Model

Minnionise connects a public static website to software on the user's own machine, so the local boundary is treated as a security boundary.

## Browser app

- No API keys are required.
- No Model mode performs no AI network request.
- Result history/favourites use localStorage.
- microphone recordings are kept as in-memory blob URLs in the active tab.
- no analytics or tracking code is included.

## Bridge binding

Default:

```text
127.0.0.1:8765
```

This is not reachable from another device.

Only `--lan` switches the bind address to `0.0.0.0`.

## Origin checks

Loopback browser API requests are accepted only from the explicit Minnionise GitHub Pages origin and known localhost development origins.

The bridge does not use a wildcard CORS policy.

## LAN authorization

Remote devices must provide the random bridge token. `/api/pair` itself can only be requested from the loopback computer.

## Provider allowlist

The browser cannot tell the bridge to call an arbitrary URL. Provider choices are fixed to:

- Ollama on `127.0.0.1:11434`
- LM Studio on `127.0.0.1:1234`
- the built-in no-model engine

## What Minnionise does not do

- execute arbitrary shell commands from browser input;
- expose a general proxy endpoint;
- upload prompts to a Minnionise cloud service;
- save phone pairing tokens to disk;
- bind to LAN unless explicitly requested.

## User responsibility

When exposing Ollama, LM Studio or the Minnionise Bridge beyond loopback, follow the local server vendor's authentication/network guidance and restrict access to trusted private networks.
