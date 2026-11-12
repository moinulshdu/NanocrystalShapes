#!/bin/bash
# Starts Nanocrystal Shapes on macOS. First time: see README (Gatekeeper).
cd "$(dirname "$0")"
for PY in "$HOME/anaconda3/bin/python3" "$HOME/opt/anaconda3/bin/python3" "/opt/anaconda3/bin/python3" \
          "$HOME/miniconda3/bin/python3" "/opt/homebrew/bin/python3" "/usr/local/bin/python3" \
          "/Library/Frameworks/Python.framework/Versions/Current/bin/python3" "$(command -v python3)"; do
  if [ -x "$PY" ] && "$PY" -c "import tkinter" >/dev/null 2>&1; then
    nohup "$PY" "Nanocrystal Shapes.pyw" "$@" >/dev/null 2>&1 &
    # close this Terminal window
    osascript -e 'tell application "Terminal" to close (every window whose name contains "Start Nanocrystal Shapes")' >/dev/null 2>&1 &
    exit 0
  fi
done
osascript -e 'display dialog "Python 3 with Tkinter was not found.\n\nPlease install Python 3 from python.org, then try again." buttons {"OK"} with icon caution'
