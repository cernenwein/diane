#!/bin/bash
OK=true
if ! sudo apt update -qq > /dev/null; then OK=false; fi
if command -v ufw > /dev/null; then
  STATUS=$(sudo ufw status | grep -i "Status: active")
  [ -z "$STATUS" ] && OK=false
else
  OK=false
fi
if grep -q "^PermitRootLogin yes" /etc/ssh/sshd_config 2>/dev/null; then OK=false; fi
OPEN_PORTS=$(sudo ss -tuln | grep -v "127.0.0.1" | grep -v "State" | wc -l)
[ "$OPEN_PORTS" -gt 5 ] && OK=false
[ "$OK" = true ] && echo "All clear. I’m feeling secure and locked down." || echo "Some things may need attention — not fully locked down."
