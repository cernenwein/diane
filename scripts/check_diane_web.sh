#!/usr/bin/env bash
#
# check_diane_web.sh
# Verifies that the Diane web interface service is running on port 8080 and reachable.
#

set -euo pipefail

SERVICE="diane_web.service"
PORT=8080
HOST="127.0.0.1"
URL="http://${HOST}:${PORT}"

echo "=== 1. Service Status ==="
systemctl status "${SERVICE}" --no-pager || true

echo -e "\n=== 2. Recent Logs ==="
journalctl -u "${SERVICE}" -n 20 --no-pager || true

echo -e "\n=== 3. Listening Ports ==="
echo "Ports listening on ${PORT}:"
ss -ltnp | grep ":${PORT} " || echo "  (none)"

echo -e "\n=== 4. Root Path ==="
echo "GET ${URL}/"
curl -s -o /dev/null -w "%{http_code}\n" "${URL}/" || echo "  (failed)"

echo -e "\n=== 5. Query Endpoint (invalid key) ==="
echo "POST ${URL}/query with wrong key"
curl -s -o /dev/null -w "%{http_code}\n" -X POST "${URL}/query"   -H "Content-Type: application/json"   -d '{"key":"wrong_key","prompt":"test"}' || echo "  (failed)"

echo -e "\n=== 6. Query Endpoint (valid key) ==="
# Replace MY_SECRET_KEY with the actual key if set in env
VALID_KEY="${WEB_KEY:-my_secret_key}"
echo "POST ${URL}/query with valid key ($VALID_KEY)"
curl -s -o response.json -w "%{http_code}\n" -X POST "${URL}/query"   -H "Content-Type: application/json"   -d "{"key":"${VALID_KEY}","prompt":"test"}" || echo "  (failed)"
echo "Response body:"
cat response.json || true
rm -f response.json

echo -e "\n=== End of Check ==="
