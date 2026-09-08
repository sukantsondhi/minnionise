#!/usr/bin/env sh
cd "$(dirname "$0")" || exit 1
printf '\n🍌 MINNIONISE LOCAL BRIDGE\n\n1. Desktop only\n2. Desktop + iPhone/iPad QR pairing\n\nChoose 1 or 2: '
read choice
if [ "$choice" = "2" ]; then python3 server.py --lan; else python3 server.py; fi
