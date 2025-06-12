#!/usr/bin/env bash
#
# list_diane_services.sh
# Lists Diane-related systemd services: active, enabled, and unit file paths.
#

echo "=== Active Diane Services ==="
systemctl list-units --type=service --state=running | grep -i diane || echo "  (none running)"

echo ""
echo "=== Enabled Diane Services ==="
systemctl list-unit-files --state=enabled | grep -i diane || echo "  (none enabled)"

echo ""
echo "=== Diane Service File Locations & Status ==="
systemctl list-unit-files | grep -i diane | awk '{print $1}' | sort -u | while read svc; do
  echo "Service: $svc"
  path=$(systemctl show -p FragmentPath "$svc" | cut -d= -f2)
  echo "  Unit file: ${path:-(not found)}"
  enabled=$(systemctl is-enabled "$svc" 2>/dev/null || echo disabled)
  active=$(systemctl is-active "$svc" 2>/dev/null || echo inactive)
  echo "  Enabled: $enabled"
  echo "  Active:  $active"
  echo ""
done
