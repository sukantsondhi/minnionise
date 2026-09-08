# iPhone / iPad Phone Link

## Why the phone UI is served by the bridge

A GitHub Pages tab is HTTPS. Desktop local-model servers commonly expose HTTP on `localhost` or a private LAN IP. Browser Local Network Access rules and mixed-content handling vary by browser/platform.

Minnionise avoids depending on that behaviour for the primary phone path.

When you scan the QR code, iPhone/iPad opens a mobile page directly from the computer:

```text
http://<desktop-lan-ip>:8765/mobile?token=<random-token>
```

The mobile UI and its API therefore share the same local origin.

## Enable pairing

```bash
python local_bridge/server.py --lan
```

Then:

1. Put the phone and computer on the same Wi-Fi.
2. Open Minnionise on the computer.
3. Select **Pair by QR**.
4. Scan with the iPhone/iPad Camera app.
5. Open the displayed local page.

## Security properties

- LAN mode is off by default.
- A new cryptographically random token is created every bridge process start.
- Non-loopback clients must provide that token.
- The token is included in the QR URL.
- Stopping/restarting the bridge invalidates the previous session.
- The bridge does not expose arbitrary file-system or shell-command APIs.

## Firewalls

The operating system may ask whether Python may accept connections on a private network. For phone pairing, allow it on **Private** networks only.

Do not expose port 8765 through your router or to the public internet.
