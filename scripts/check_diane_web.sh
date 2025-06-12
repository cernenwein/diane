#!/usr/bin/env bash
#
# check_diane_web.sh
# Verifies that the Diane web interface service (diane_web.service) is running and reachable.
#

set -e

echo "=== 1. Service Status ==="
sudo systemctl status diane_web.service --no-pager || true

echo ""
echo "=== 2. Recent Logs ==="
sudo journalctl -u diane_web.service -n 20 --no-pager || true

echo ""
echo "=== 3. Listening Ports ==="
echo "Ports listening on 5000:"
ss -ltnp | grep ':5000 ' || echo "  (none)"

echo ""
echo "=== 4. Local Connectivity ==="
echo "Curl localhost:5000 root path:"
curl -I http://127.0.0.1:5000/ || echo "  (failed)"

echo ""
echo "=== 5. Query Endpoint ==="
echo "Sample POST:"
curl -X POST http://127.0.0.1:5000/query -H "Content-Type: application/json" \
  -d '{"key":"my_secret_key","prompt":"test"}' || echo "  (failed)"
