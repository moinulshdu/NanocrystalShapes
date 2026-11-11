"""
Finds missing Python packages and installs them, only with the user's permission.

This module must not import Pillow or NumPy at the top, because it runs before
they are known to be installed.
"""
from __future__ import annotations

import importlib
import importlib.util
import subprocess
import sys
import threading


class Package:
    def __init__(self, pip_name, import_name, required, purpose, check=None):
        self.pip_name = pip_name
        self.import_name = import_name
        self.required = required
        self.purpose = purpose
        self.check = check or import_name     # module that must import successfully


PACKAGES = [
    Package("Pillow", "PIL", True, "drawing, showing and saving the figures", check="PIL.ImageTk"),
    Package("numpy", "numpy", False, "faster saving with a transparent background"),
]


def _forget_failed(name):
    root = name.split(".")[0]
    for mod in list(sys.modules):
        if (mod == root or mod.startswith(root + ".")) and sys.modules[mod] is None:
            del sys.modules[mod]


def is_installed(pkg: Package) -> bool:
    _forget_failed(pkg.check)
    try:
        importlib.import_module(pkg.check)
        return True
    except Exception:
        return False


def version_of(pkg: Package) -> str:
    try:
        from importlib import metadata
        return metadata.version(pkg.pip_name)
    except Exception:
        pass
    try:
        return str(getattr(importlib.import_module(pkg.import_name), "__version__", "?"))
    except Exception:
        return "-"


def status_report():
    """[(package, installed, version)] for every package the app can use."""
    out = []
    for p in PACKAGES:
        ok = is_installed(p)
        out.append((p, ok, version_of(p) if ok else "-"))
    return out


def missing(required=None):
    """Missing packages; required=True/False limits to required or optional ones."""
    return [p for p in PACKAGES if (required is None or p.required == required) and not is_installed(p)]


def pip_install(names):
    """Install with pip. Retries as a personal (--user) install when the normal
    install is not allowed. Returns (success, last output)."""
    base = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    flags = 0x08000000 if sys.platform.startswith("win") else 0   # no console window
    last = ""
    for extra in ([], ["--user"], ["--user", "--break-system-packages"]):
        try:
            r = subprocess.run(base + extra + list(names), capture_output=True, text=True,
                               creationflags=flags)
        except Exception as ex:
            return False, str(ex)
        if r.returncode == 0:
            try:                     # a brand-new --user folder is not on sys.path yet
                import site
                site.addsitedir(site.getusersitepackages())
            except Exception:
                pass
            importlib.invalidate_caches()
            return True, r.stdout[-1500:]
        last = (r.stderr or r.stdout)[-1500:]
    return False, last


def install_with_progress(parent, pkgs, title="Installing packages"):
    """Runs pip in the background with a small progress window. Returns True on success."""
    import tkinter as tk
    from tkinter import ttk

    names = [p.pip_name for p in pkgs]
    win = tk.Toplevel(parent)
    win.title(title)
    win.resizable(False, False)
    try:
        win.transient(parent)
    except tk.TclError:
        pass
    frm = ttk.Frame(win, padding=16)
    frm.pack(fill="both", expand=True)
    ttk.Label(frm, text="Installing %s ...\nThis can take a minute. Please wait." % ", ".join(names)).pack(anchor="w")
    bar = ttk.Progressbar(frm, mode="indeterminate", length=320)
    bar.pack(fill="x", pady=(10, 0))
    bar.start(12)
    win.protocol("WM_DELETE_WINDOW", lambda: None)     # cannot be closed while pip runs
    result = {}

    def work():
        result["ok"], result["log"] = pip_install(names)

    th = threading.Thread(target=work, daemon=True)
    th.start()

    def poll():
        if th.is_alive():
            win.after(150, poll)
        else:
            win.destroy()
    win.after(150, poll)
    win.wait_window()
    ok = result.get("ok", False) and all(is_installed(p) for p in pkgs)
    from tkinter import messagebox
    if ok:
        messagebox.showinfo(title, "Installed: %s." % ", ".join(names), parent=parent)
    else:
        messagebox.showerror(
            title, "The installation did not succeed.\n\nYou can install it yourself with:\n"
            "  %s -m pip install %s\n\n%s" % (sys.executable, " ".join(names), result.get("log", "")[-600:]),
            parent=parent)
    return ok


def ensure_required(root) -> bool:
    """Called before the window opens. Offers to install missing required
    packages. Returns False if the app cannot start."""
    from tkinter import messagebox
    req = missing(required=True)
    if not req:
        return True
    lines = "\n".join("  \u2022 %s \u2013 %s" % (p.pip_name, p.purpose) for p in req)
    ok = messagebox.askyesno(
        "Nanocrystal Shapes \u2013 packages needed",
        "Nanocrystal Shapes needs these Python packages, which are not installed for\n%s:\n\n%s\n\n"
        "Install them now? (An internet connection is needed.)" % (sys.executable, lines), parent=root)
    if not ok:
        messagebox.showinfo("Nanocrystal Shapes", "Nanocrystal Shapes cannot run without these packages.\n"
                            "Start it again whenever you are ready to install them.", parent=root)
        return False
    return install_with_progress(root, req, "Nanocrystal Shapes \u2013 installing")
