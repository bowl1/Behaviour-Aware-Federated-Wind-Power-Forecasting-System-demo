#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY_DIR="$ROOT/python_service"
API_DIR="$ROOT/src"
FE_DIR="$ROOT/frontend"

cleanup() {
  set +e
  [[ -n "${PY_PID:-}" ]] && kill "$PY_PID" 2>/dev/null || true
  [[ -n "${API_PID:-}" ]] && kill "$API_PID" 2>/dev/null || true
  [[ -n "${FE_PID:-}" ]] && kill "$FE_PID" 2>/dev/null || true
}
trap cleanup EXIT

pushd "$PY_DIR" >/dev/null
if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip >/dev/null
pip install -r requirements.txt >/dev/null
uvicorn main:app --reload --port 8000 &
PY_PID=$!
deactivate
popd >/dev/null

echo "Python service running on http://localhost:8000"

pushd "$API_DIR" >/dev/null
dotnet restore >/dev/null
dotnet run --urls http://localhost:5000 &
API_PID=$!
popd >/dev/null

echo "C# API running on http://localhost:5000"

echo "Starting React dev server..."
pushd "$FE_DIR" >/dev/null
npm install >/dev/null
npm run dev -- --host --port 5173 &
FE_PID=$!
popd >/dev/null

echo "Frontend running on http://localhost:5173"

echo "Press Ctrl+C to stop all services"
wait
