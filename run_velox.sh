#!/usr/bin/env bash
# ──────────────────────────────────────────────────
#  VeloX Race Master — Launcher
# ──────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN="$SCRIPT_DIR/velox.py"

echo ""
echo "  ⚡ Memulai VeloX Race Master..."
echo "  Pastikan library: rich & requests sudah terinstall."
echo ""

# Prefer venv if it exists
if [ -f "$SCRIPT_DIR/.venv/bin/python" ]; then
    exec "$SCRIPT_DIR/.venv/bin/python" "$MAIN" "$@"
else
    exec python3 "$MAIN" "$@"
fi
