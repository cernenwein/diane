#!/bin/bash
echo "[✓] Enabling Bluetooth auto-connect..."

cp bluetooth/bluetooth-auto-connect.service /etc/systemd/system/
chmod +x bluetooth/auto_connect.sh

systemctl daemon-reexec
systemctl daemon-reload
systemctl enable bluetooth-auto-connect
systemctl start bluetooth-auto-connect

echo "[✓] Bluetooth auto-connect service enabled and running."
