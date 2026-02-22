#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cleanup() {
  kill "${PY_PID:-}" "${FE_PID:-}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

(
  cd "$ROOT/python_service"
  [[ -d .venv ]] || python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt >/dev/null
  exec uvicorn main:app --reload --port 8000
) &
PY_PID=$!

(
  cd "$ROOT/frontend"
  npm install >/dev/null
  exec npm run dev -- --host --port 5173
) &
FE_PID=$!

echo "Python service: http://localhost:8000"
echo "Frontend running on http://localhost:5173"
echo "Press Ctrl+C to stop all services"
wait
