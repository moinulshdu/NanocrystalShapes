"""Tools › Create Desktop Shortcut, for Windows, macOS and Linux.

Windows: a shortcut on the desktop and in the Start menu. Both carry the app's
         own taskbar identity (AppUserModelID), so a running window groups with
         them and "Pin to taskbar" pins a shortcut that starts the app.
macOS:   a small "Nanocrystal Shapes.app" on the desktop. It is made on your own
         Mac, so Gatekeeper does not block it.
Linux:   a .desktop entry on the desktop and in the applications menu.

The shortcut points at this folder. If the folder is moved or renamed, start
the app once from its new place and create the shortcut again.
"""
from __future__ import annotations

import base64
import os
import stat
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
LAUNCHER = APP_DIR / "Nanocrystal Shapes.pyw"
ICONS = Path(__file__).resolve().parent
APP_NAME = "Nanocrystal Shapes"
DESCRIPTION = "Translucent 3D figures of nanocrystal shapes"


def gui_python() -> str:
    """The Python that starts the app without a console window."""
    exe = Path(sys.executable)
    if sys.platform.startswith("win") and exe.name.lower() == "python.exe":
        w = exe.with_name("pythonw.exe")
        if w.exists():
            return str(w)
    return str(exe)


def create_shortcut() -> str:
    """Creates the shortcut(s); returns a description of where. Raises on failure."""
    if sys.platform.startswith("win"):
        return _windows()
    if sys.platform == "darwin":
        return _macos()
    return _linux()


# ------------------------------------------------------------------ Windows
def _ps_quote(s) -> str:
    return "'" + str(s).replace("'", "''") + "'"


# Sets System.AppUserModel.ID on a .lnk file (the taskbar identity).
_AUMID_CS = r'''
using System;
using System.Runtime.InteropServices;
public static class NsAumid {
  [StructLayout(LayoutKind.Sequential, Pack = 4)]
  public struct PropertyKey { public Guid fmtid; public uint pid; }
  [StructLayout(LayoutKind.Explicit, Size = 24)]
  public struct PropVariant { [FieldOffset(0)] public ushort vt; [FieldOffset(8)] public IntPtr p; }
  [ComImport, Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
  public interface IPropertyStore {
    void GetCount(out uint c);
    void GetAt(uint i, out PropertyKey k);
    void GetValue(ref PropertyKey k, out PropVariant v);
    void SetValue(ref PropertyKey k, ref PropVariant v);
    void Commit();
  }
  [DllImport("shell32.dll", CharSet = CharSet.Unicode, PreserveSig = false)]
  static extern void SHGetPropertyStoreFromParsingName(string path, IntPtr pbc, int flags,
      ref Guid riid, [MarshalAs(UnmanagedType.Interface)] out IPropertyStore store);
  public static void Set(string lnk, string id) {
    Guid iid = new Guid("886D8EEB-8CF2-4446-8D02-CDBA1DBDCF99");
    IPropertyStore store;
    SHGetPropertyStoreFromParsingName(lnk, IntPtr.Zero, 2, ref iid, out store);
    PropertyKey key = new PropertyKey();
    key.fmtid = new Guid("9F4C2855-9F79-4B39-A8D0-E1D42DE1D5F3");
    key.pid = 5;
    PropVariant v = new PropVariant();
    v.vt = 31;
    v.p = Marshal.StringToCoTaskMemUni(id);
    store.SetValue(ref key, ref v);
    store.Commit();
    Marshal.FreeCoTaskMem(v.p);
    Marshal.ReleaseComObject(store);
  }
}
'''


def _windows() -> str:
    from .app import APP_ID
    ico = ICONS / "icon.ico"
    script = f"""
$ErrorActionPreference = 'Stop'
$ws = New-Object -ComObject WScript.Shell
$made = @()
foreach ($dir in @([Environment]::GetFolderPath('Desktop'), [Environment]::GetFolderPath('Programs'))) {{
  if ($dir) {{
    $p = Join-Path $dir {_ps_quote(APP_NAME + '.lnk')}
    $s = $ws.CreateShortcut($p)
    $s.TargetPath = {_ps_quote(gui_python())}
    $s.Arguments = {_ps_quote('"' + str(LAUNCHER) + '"')}
    $s.WorkingDirectory = {_ps_quote(APP_DIR)}
    $s.Description = {_ps_quote(DESCRIPTION)}
    {"$s.IconLocation = " + _ps_quote(str(ico) + ',0') if ico.exists() else ''}
    $s.Save()
    $made += $p
  }}
}}
try {{
  Add-Type -TypeDefinition @'
{_AUMID_CS}
'@
  foreach ($p in $made) {{ [NsAumid]::Set($p, {_ps_quote(APP_ID)}) }}
}} catch {{ }}
$made -join "`n"
"""
    enc = base64.b64encode(script.encode("utf-16-le")).decode()
    proc = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                           "-EncodedCommand", enc], capture_output=True, text=True,
                          creationflags=0x08000000, timeout=120)
    paths = [ln for ln in proc.stdout.strip().splitlines() if ln.strip()]
    if proc.returncode != 0 or not paths:
        raise RuntimeError(proc.stderr.strip() or "PowerShell could not create the shortcut.")
    return "Desktop: " + paths[0] + ("\nStart menu: " + paths[1] if len(paths) > 1 else "")


# ------------------------------------------------------------------ macOS
def _macos() -> str:
    app = Path.home() / "Desktop" / (APP_NAME + ".app")
    contents = app / "Contents"
    macos = contents / "MacOS"
    res = contents / "Resources"
    macos.mkdir(parents=True, exist_ok=True)
    res.mkdir(parents=True, exist_ok=True)
    runner = macos / "NanocrystalShapes"
    runner.write_text('#!/bin/bash\ncd "%s"\nexec "%s" "%s" "$@"\n' % (APP_DIR, sys.executable, LAUNCHER),
                      encoding="utf-8")
    runner.chmod(runner.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    icon_key = ""
    icns = ICONS / "icon.icns"
    if icns.exists():
        (res / "icon.icns").write_bytes(icns.read_bytes())
        icon_key = "<key>CFBundleIconFile</key><string>icon</string>"
    from . import __version__
    (contents / "Info.plist").write_text(f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>{APP_NAME}</string>
<key>CFBundleDisplayName</key><string>{APP_NAME}</string>
<key>CFBundleIdentifier</key><string>local.nanocrystalshapes.app</string>
<key>CFBundleExecutable</key><string>NanocrystalShapes</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>{__version__}</string>
<key>CFBundleShortVersionString</key><string>{__version__}</string>
<key>NSHighResolutionCapable</key><true/>
{icon_key}
</dict></plist>
""", encoding="utf-8")
    try:                                                   # make Finder pick up the icon
        subprocess.run(["touch", str(app)], check=False, timeout=5)
    except (OSError, subprocess.SubprocessError):
        pass
    return str(app)


# ------------------------------------------------------------------ Linux
def _linux() -> str:
    entry = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment={DESCRIPTION}
Exec="{sys.executable}" "{LAUNCHER}"
Path={APP_DIR}
Icon={ICONS / 'icon.png'}
Terminal=false
Categories=Graphics;Science;Education;
StartupWMClass=Nanocrystalshapes
"""
    made = []
    apps = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "applications"
    desktop = Path.home() / "Desktop"
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True,
                             timeout=5).stdout.strip()
        if out:
            desktop = Path(out)
    except (OSError, subprocess.SubprocessError):
        pass
    for folder in (desktop, apps):
        try:
            folder.mkdir(parents=True, exist_ok=True)
            p = folder / "nanocrystal-shapes.desktop"
            p.write_text(entry, encoding="utf-8")
            p.chmod(0o755)
            made.append(str(p))
            try:   # GNOME: allow launching from the desktop without a warning
                subprocess.run(["gio", "set", str(p), "metadata::trusted", "true"],
                               capture_output=True, check=False, timeout=5)
            except (OSError, subprocess.SubprocessError):
                pass
        except OSError:
            continue
    if not made:
        raise RuntimeError("Could not write a .desktop file.")
    return "Desktop: " + made[0] + ("\nApplications menu: " + made[1] if len(made) > 1 else "")
