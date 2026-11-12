#!/usr/bin/env bash
# Starts Nanocrystal Shapes on Linux.
cd "$(dirname "$(readlink -f "$0")")"
for PY in python3 python; do
  if command -v "$PY" >/dev/null 2>&1 && "$PY" -c "import tkinter" >/dev/null 2>&1; then
    exec "$PY" "Nanocrystal Shapes.pyw" "$@"
  fi
done
MSG="Python 3 with Tkinter was not found. Install it, e.g.: sudo apt install python3 python3-tk"
command -v zenity >/dev/null && zenity --error --text="$MSG" || echo "$MSG"
exit 1
