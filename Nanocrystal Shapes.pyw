#!/usr/bin/env python3
"""Nanocrystal Shapes - start file.

Checks that the required Python packages are installed (and asks before
installing anything), then opens the window. Double-click the launcher for
your system instead of this file:
  Windows: Start Nanocrystal Shapes (Windows).bat
  macOS:   Start Nanocrystal Shapes (macOS).command
  Linux:   start_nanocrystal_shapes.sh
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import tkinter as tk
except ImportError:
    print("This app needs Python with Tkinter (on Linux: sudo apt install python3-tk).")
    sys.exit(1)

from nanoshapes import bootstrap  # noqa: E402  (imports no third-party packages)


def check_packages():
    root = tk.Tk()
    root.withdraw()
    try:
        return bootstrap.ensure_required(root)
    finally:
        root.destroy()


if __name__ == "__main__":
    if check_packages():
        from nanoshapes.app import main
        main()
