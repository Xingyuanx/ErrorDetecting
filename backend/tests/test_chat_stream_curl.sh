#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
USERNAME="${USERNAME:-admin}"
PASSWORD="${PASSWORD:-admin123}"
SESSION_ID="${SESSION_ID:-curl-sse-$(date +%s)}"
MESSAGE="${MESSAGE:-杀戮尖塔的观者怎么玩}"

TOKEN="$(
  curl -sS "${BASE_URL}/api/v1/user/login" \
    -H 'Content-Type: application/json' \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["token"])'
)"

TMP_OUT="$(mktemp)"
cleanup() { rm -f "${TMP_OUT}"; }
trap cleanup EXIT

curl -N -sS "${BASE_URL}/api/v1/ai/chat" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d "$(python3 - <<'PY'
import json, os
payload = {
  "sessionId": os.environ["SESSION_ID"],
  "message": os.environ["MESSAGE"],
  "stream": True,
  "context": {
    "webSearch": True,
    "agent": "Hadoop助手. You MUST use the web_search tool before answering."
  }
}
print(json.dumps(payload, ensure_ascii=False))
PY
)" | tee "${TMP_OUT}"

python3 - <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
s = p.read_text(encoding="utf-8", errors="ignore")
n = len(re.findall(r"^data: ", s, flags=re.M))
if n <= 0:
  raise SystemExit("未收到任何 SSE data 行，测试失败")
print(f"OK: 收到 {n} 条 SSE data 行")
PY "${TMP_OUT}"

