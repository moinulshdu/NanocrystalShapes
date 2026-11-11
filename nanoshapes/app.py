"""Tkinter user interface for Nanocrystal Shapes."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk

from PIL import Image, ImageTk

from . import renderer as R
from . import (__ai_assistance__, __author__, __concept__, __email__, __license_note__,
               __version__, acknowledgment)

APP_NAME = "Nanocrystal Shapes"
APP_ID = "NanocrystalShapes.Desktop.App.2"     # Windows taskbar identity
VERSION = __version__
HERE = os.path.dirname(os.path.abspath(__file__))
ICON_PNG = os.path.join(HERE, "icon.png")
ICON_ICO = os.path.join(HERE, "icon.ico")


def config_dir():
    if sys.platform.startswith("win"):
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    d = os.path.join(base, "NanocrystalShapes")
    os.makedirs(d, exist_ok=True)
    return d


CONFIG = os.path.join(config_dir(), "settings.json")

SHOW_ITEMS = (("show_faces", "Faces"), ("show_edges", "Edges"),
              ("show_corners", "Corner edges (tL)"), ("show_radii", "Radii / axes"),
              ("show_arrows", "Edge arrows"), ("show_back_arrow", "Hidden arrows"),
              ("show_twins", "Twin planes"), ("lighting", "3D lighting"))

COLOR_ITEMS = (("face_color", "Faces"), ("edge_color", "Edges"),
               ("corner_color", "Corners"), ("radius_color", "Radii"),
               ("arrow_color", "Arrows"), ("twin_color", "Twins"),
               ("background", "Background"))


class App:
    PREVIEW_SS = 2

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(APP_NAME)
        self.s = self._load_settings()
        self._job = None
        self._drag = None
        self._photo = None
        self._refresh = []          # callbacks that update controls from settings
        self._prefs = self._load_prefs()

        self._build_menu()
        self._build_ui()
        self._bind_keys()
        geom = self._prefs.get("geometry")
        root.geometry(geom if geom else "1020x700")
        root.minsize(760, 520)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(50, self.redraw)

    # ------------------------------------------------------------ settings
    def _load_all(self):
        try:
            with open(CONFIG, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _load_settings(self):
        return R.Settings.from_dict(self._load_all().get("settings"))

    def _load_prefs(self):
        p = self._load_all().get("prefs") or {}
        return {"geometry": p.get("geometry"), "export_width": int(p.get("export_width", 1176)),
                "transparent": bool(p.get("transparent", False)),
                "last_dir": p.get("last_dir") or os.path.expanduser("~")}

    def save_config(self):
        self._prefs["geometry"] = self.root.geometry()
        try:
            with open(CONFIG, "w", encoding="utf-8") as f:
                json.dump({"settings": self.s.to_dict(), "prefs": self._prefs}, f, indent=2)
        except Exception:
            pass

    def on_close(self):
        self.save_config()
        self.root.destroy()

    # ------------------------------------------------------------ UI
    def _build_menu(self):
        mb = tk.Menu(self.root)
        acc = "Command" if sys.platform == "darwin" else "Ctrl"
        fm = tk.Menu(mb, tearoff=0)
        fm.add_command(label="Save Image...", accelerator=acc + "+S", command=self.save_image)
        fm.add_command(label="Save Transparent PNG...", accelerator=acc + "+Shift+S",
                       command=lambda: self.save_image(force_transparent=True))
        fm.add_separator()
        fm.add_command(label="Default View", accelerator=acc + "+R", command=self.reset_view)
        fm.add_command(label="Reset Shape Parameters", command=self.reset_params)
        fm.add_command(label="Reset Everything", command=self.reset_all)
        fm.add_separator()
        fm.add_command(label="Quit", accelerator=acc + "+Q", command=self.on_close)
        mb.add_cascade(label="File", menu=fm)
        sm = tk.Menu(mb, tearoff=0)
        for key, spec in R.SHAPES.items():
            sm.add_command(label=spec["label"], command=lambda k=key: self.change_shape(k))
        mb.add_cascade(label="Shape", menu=sm)
        tm = tk.Menu(mb, tearoff=0)
        tm.add_command(label="Create Desktop Shortcut", command=self.create_shortcut)
        tm.add_command(label="Open Settings Folder", command=self.open_settings_folder)
        mb.add_cascade(label="Tools", menu=tm)
        hm = tk.Menu(mb, tearoff=0)
        from .manual import PAGES
        for i, (title, _) in enumerate(PAGES):
            hm.add_command(label=title, accelerator="F1" if i == 0 else "",
                           command=lambda i=i: self.open_help(i))
        hm.add_separator()
        hm.add_command(label="Python Packages…", command=self.open_packages)
        hm.add_separator()
        hm.add_command(label="About Nanocrystal Shapes", command=self.show_about)
        mb.add_cascade(label="Help", menu=hm)
        self.root.config(menu=mb)

    def _bind_keys(self):
        mod = "Command" if sys.platform == "darwin" else "Control"
        self.root.bind(f"<{mod}-s>", lambda e: self.save_image())
        self.root.bind(f"<{mod}-S>", lambda e: self.save_image(force_transparent=True))
        self.root.bind(f"<{mod}-q>", lambda e: self.on_close())
        self.root.bind(f"<{mod}-r>", lambda e: self.reset_view())
        self.root.bind(f"<{mod}-t>", lambda e: self._toggle_transparent_key())
        self.root.bind("<F1>", lambda e: self.open_help(0))
        for key, d_az, d_el in (("Left", 5, 0), ("Right", -5, 0), ("Up", 0, -5), ("Down", 0, 5)):
            self.root.bind(f"<{key}>", lambda e, a=d_az, b=d_el: self._nudge(e, a, b, 1.0))
            self.root.bind(f"<Shift-{key}>", lambda e, a=d_az, b=d_el: self._nudge(e, a, b, 0.2))
        for key in ("plus", "equal", "KP_Add"):
            self.root.bind(f"<{key}>", lambda e: self._key_zoom(e, 1.08))
        for key in ("minus", "KP_Subtract"):
            self.root.bind(f"<{key}>", lambda e: self._key_zoom(e, 1 / 1.08))
        self.root.bind("<Prior>", lambda e: self._step_shape(e, -1))
        self.root.bind("<Next>", lambda e: self._step_shape(e, 1))

    def _typing(self, e):
        """True while the focus is in a text or number box (keys belong to it)."""
        w = e.widget
        return isinstance(w, (tk.Entry, ttk.Entry, ttk.Combobox, tk.Text, tk.Listbox, ttk.Scale)) or \
            w.winfo_toplevel() is not self.root

    def _nudge(self, e, d_az, d_el, f):
        if self._typing(e):
            return
        self.s.azimuth = (self.s.azimuth + d_az * f + 180) % 360 - 180
        self.s.elevation = max(-89.0, min(89.0, self.s.elevation + d_el * f))
        self._sync_view()
        self.schedule()
        return "break"

    def _key_zoom(self, e, f):
        if self._typing(e):
            return
        self._zoom_by(f)
        return "break"

    def _step_shape(self, e, d):
        if self._typing(e):
            return
        i = (self._keys.index(self.s.shape) + d) % len(self._keys)
        self.change_shape(self._keys[i])
        return "break"

    def _toggle_transparent_key(self):
        self.transparent_var.set(not self.transparent_var.get())
        self._toggle_transparent()

    def open_help(self, page=0):
        from .help_window import HelpWindow
        w = getattr(self, "_help_win", None)
        if w is not None and w.winfo_exists():
            w.show(page)
            w.deiconify()
            w.lift()
        else:
            self._help_win = HelpWindow(self.root, page)
        return self._help_win

    def open_packages(self):
        from .help_window import PackagesWindow
        w = getattr(self, "_pkg_win", None)
        if w is not None and w.winfo_exists():
            w.refresh()
            w.lift()
        else:
            self._pkg_win = PackagesWindow(self.root)
        return self._pkg_win

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=6)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(main, background="#ffffff", highlightthickness=1,
                                highlightbackground="#c8c8c8", cursor="fleur")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", lambda e: self.schedule())
        self.canvas.bind("<ButtonPress-1>", self._drag_start)
        self.canvas.bind("<B1-Motion>", self._drag_move)
        self.canvas.bind("<ButtonRelease-1>", lambda e: self._drag_end())
        self.canvas.bind("<Double-Button-1>", lambda e: self.reset_view())
        self.canvas.bind("<MouseWheel>", self._wheel)
        self.canvas.bind("<Button-4>", lambda e: self._zoom_by(1.08))
        self.canvas.bind("<Button-5>", lambda e: self._zoom_by(1 / 1.08))

        side = ttk.Frame(main, padding=(10, 0, 0, 0), width=270)
        side.grid(row=0, column=1, sticky="ns")

        nb = ttk.Notebook(side)
        nb.pack(fill="x")
        tab_shape = ttk.Frame(nb, padding=8)
        tab_disp = ttk.Frame(nb, padding=8)
        nb.add(tab_shape, text="Shape")
        nb.add(tab_disp, text="Display")

        # --- Shape tab
        ttk.Label(tab_shape, text="Shape").pack(anchor="w")
        self._labels = [spec["label"] for spec in R.SHAPES.values()]
        self._keys = list(R.SHAPES)
        self.shape_box = ttk.Combobox(tab_shape, values=self._labels, state="readonly", height=len(self._labels))
        self.shape_box.pack(fill="x", pady=(2, 8))
        self.shape_box.bind("<<ComboboxSelected>>",
                            lambda e: self.change_shape(self._keys[self.shape_box.current()]))

        self.param_frame = ttk.LabelFrame(tab_shape, text="Parameters", padding=6)
        self.param_frame.pack(fill="x")

        view = ttk.LabelFrame(tab_shape, text="View", padding=6)
        view.pack(fill="x", pady=(8, 0))
        self._slider(view, "Azimuth (deg)", -180, 180, 0.5, "{:.1f}",
                     lambda: self.s.azimuth, lambda v: setattr(self.s, "azimuth", v))
        self._slider(view, "Elevation (deg)", -89, 89, 0.5, "{:.1f}",
                     lambda: self.s.elevation, lambda v: setattr(self.s, "elevation", v))
        self._slider(view, "Zoom", 0.3, 3.0, 0.01, "{:.2f}",
                     lambda: self.s.zoom, lambda v: setattr(self.s, "zoom", v))
        ttk.Button(view, text="Default view", command=self.reset_view).pack(fill="x", pady=(4, 0))

        # --- Display tab
        show = ttk.LabelFrame(tab_disp, text="Show", padding=6)
        show.pack(fill="x")
        self.checks = {}
        for i, (key, label) in enumerate(SHOW_ITEMS):
            v = tk.BooleanVar(value=getattr(self.s, key))
            cb = ttk.Checkbutton(show, text=label, variable=v,
                                 command=lambda k=key, vv=v: self._set_attr(k, bool(vv.get())))
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 8), pady=1)
            self.checks[key] = (v, cb)

        look = ttk.LabelFrame(tab_disp, text="Opacity and thickness", padding=6)
        look.pack(fill="x", pady=(8, 0))
        self._slider(look, "Face opacity", 0.0, 1.0, 0.01, "{:.2f}",
                     lambda: self.s.face_opacity, lambda v: setattr(self.s, "face_opacity", v))
        self._slider(look, "Radii / axes thickness", 0.2, 3.0, 0.05, "{:.2f}",
                     lambda: self.s.radius_scale, lambda v: setattr(self.s, "radius_scale", v))
        self._slider(look, "Arrow thickness", 0.2, 3.0, 0.05, "{:.2f}",
                     lambda: self.s.arrow_scale, lambda v: setattr(self.s, "arrow_scale", v))
        self._slider(look, "Line width", 0.5, 6.0, 0.1, "{:.1f}",
                     lambda: self.s.edge_width, self._set_line_width)

        cols = ttk.LabelFrame(tab_disp, text="Colours", padding=6)
        cols.pack(fill="x", pady=(8, 0))
        self.swatches = {}
        for i, (key, label) in enumerate(COLOR_ITEMS):
            row = ttk.Frame(cols)
            row.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 10), pady=1)
            sw = tk.Label(row, width=3, relief="solid", borderwidth=1, cursor="hand2",
                          background=self._hex(getattr(self.s, key)))
            sw.pack(side="left")
            sw.bind("<Button-1>", lambda e, k=key: self.pick_color(k))
            ttk.Label(row, text=label).pack(side="left", padx=5)
            self.swatches[key] = sw

        self.transparent_var = tk.BooleanVar(value=self._prefs["transparent"])
        ttk.Checkbutton(side, text="Transparent background", variable=self.transparent_var,
                        command=self._toggle_transparent).pack(anchor="w", pady=(10, 0))
        ttk.Button(side, text="Save Image...", command=self.save_image).pack(fill="x", pady=(4, 0))
        self.status = ttk.Label(side, text="", foreground="#666666", wraplength=250, justify="left")
        self.status.pack(fill="x", pady=(6, 0))

        self._build_params()
        self._sync_controls()

    def _slider(self, parent, label, lo, hi, step, fmt, get, put, integer=False):
        frm = ttk.Frame(parent)
        frm.pack(fill="x", pady=2)
        top = ttk.Frame(frm)
        top.pack(fill="x")
        ttk.Label(top, text=label).pack(side="left")
        var = tk.DoubleVar(value=get())
        ent = ttk.Entry(top, width=8, justify="right")
        ent.pack(side="right")

        def show_val():
            ent.delete(0, "end")
            ent.insert(0, fmt.format(get()))

        def apply(v):
            v = max(lo, min(hi, v))
            v = int(round(v)) if integer else round(v / step) * step
            put(v)
            self.schedule()
            show_val()

        def on_scale(val):
            apply(float(val))

        def on_entry(_e=None):
            try:
                v = float(ent.get())
            except ValueError:
                show_val()
                return
            var.set(max(lo, min(hi, v)))
            apply(v)

        sc = ttk.Scale(frm, from_=lo, to=hi, variable=var, command=on_scale, length=240)
        sc.pack(fill="x")
        ent.bind("<Return>", on_entry)
        ent.bind("<FocusOut>", on_entry)
        show_val()

        def refresh():
            var.set(get())
            show_val()
        self._refresh.append((frm, refresh))
        return frm

    def _build_params(self):
        for w in self.param_frame.winfo_children():
            w.destroy()
        shape = self.s.shape
        params = self.s.shape_params()
        if not params:
            ttk.Label(self.param_frame, text="This shape has no parameters.",
                      foreground="#666666").pack(anchor="w")
            return
        order = [k for k in ("sides", "aspect", "wall", "cap", "t") if k in params]
        for key in order:
            lab, lo, hi, step, fmt = R.param_spec(shape, key)
            self._slider(self.param_frame, lab, lo, hi, step, fmt,
                         lambda k=key: self.s.shape_params()[k],
                         lambda v, k=key: self._set_param(k, v),
                         integer=(key == "sides"))

    def _set_line_width(self, v):
        self.s.edge_width = v
        self.s.corner_width = v

    def _toggle_transparent(self):
        self._prefs["transparent"] = bool(self.transparent_var.get())
        self.schedule()

    def _set_param(self, key, v):
        self.s.set_param(key, v)
        if key == "sides":
            self._update_checks()

    @staticmethod
    def _hex(c):
        return "#%02x%02x%02x" % tuple(int(x) for x in c[:3])

    def _set_attr(self, key, value):
        setattr(self.s, key, value)
        self.schedule()

    def _update_checks(self):
        sh = R.get_shape(self.s)
        poly = sh.is_polyhedron
        enabled = {
            "show_corners": poly,
            "show_arrows": poly,
            "show_back_arrow": poly,
            "show_twins": R.has_twins(self.s.shape, self.s.shape_params()),
        }
        for key, (v, cb) in self.checks.items():
            cb.configure(state="normal" if enabled.get(key, True) else "disabled")

    def _sync_controls(self):
        self.shape_box.current(self._keys.index(self.s.shape))
        self._sync_view()
        for key, (v, cb) in self.checks.items():
            v.set(getattr(self.s, key))
        for key, sw in self.swatches.items():
            sw.configure(background=self._hex(getattr(self.s, key)))
        self._update_checks()

    # ------------------------------------------------------------ mouse
    def _drag_start(self, e):
        self._drag = (e.x, e.y, self.s.azimuth, self.s.elevation)

    def _drag_move(self, e):
        if not self._drag:
            return
        x0, y0, az0, el0 = self._drag
        az = az0 - (e.x - x0) * 0.5
        self.s.azimuth = (az + 180) % 360 - 180
        self.s.elevation = max(-89.0, min(89.0, el0 + (e.y - y0) * 0.5))
        self._sync_view()
        self.schedule(fast=True)

    def _sync_view(self):
        alive = []
        for frm, fn in self._refresh:
            try:
                if frm.winfo_exists():
                    fn()
                    alive.append((frm, fn))
            except tk.TclError:
                pass
        self._refresh = alive

    def _drag_end(self):
        self._drag = None
        self.schedule()

    def _wheel(self, e):
        self._zoom_by(1.08 if e.delta > 0 else 1 / 1.08)

    def _zoom_by(self, f):
        self.s.zoom = max(0.3, min(3.0, self.s.zoom * f))
        self._sync_view()
        self.schedule()

    # ------------------------------------------------------------ drawing
    def schedule(self, fast=False):
        if self._job:
            self.root.after_cancel(self._job)
        self._job = self.root.after(15 if fast else 40, lambda: self.redraw(fast))

    def redraw(self, fast=False):
        self._job = None
        cw = max(50, self.canvas.winfo_width() - 4)
        ch = max(50, self.canvas.winfo_height() - 4)
        k = min(cw / R.REF_SIZE[0], ch / R.REF_SIZE[1])
        size = (max(10, int(R.REF_SIZE[0] * k)), max(10, int(R.REF_SIZE[1] * k)))
        try:
            img = R.render(self.s, size, 1 if fast else self.PREVIEW_SS,
                           checker=self._prefs["transparent"])
        except Exception as ex:   # never crash the UI on a bad setting
            self.status.configure(text="Render error: %s" % ex)
            return
        self._photo = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.configure(background=self._hex(self.s.background))
        self.canvas.create_image(cw // 2 + 2, ch // 2 + 2, image=self._photo)
        p = self.s.shape_params()
        bits = []
        for key in ("sides", "aspect", "wall", "cap", "t"):
            if key in p:
                lab, lo, hi, step, fmt = R.param_spec(self.s.shape, key)
                bits.append("%s %s" % (lab.split(" (")[0], fmt.format(p[key])))
        self.status.configure(text="%s\n%s\nview %.1f° / %.1f°" % (
            R.SHAPES[self.s.shape]["label"], ",  ".join(bits) if bits else "", self.s.azimuth, self.s.elevation))

    # ------------------------------------------------------------ actions
    def pick_color(self, key):
        c = colorchooser.askcolor(color=self._hex(getattr(self.s, key)), title="Choose colour", parent=self.root)
        if c and c[0]:
            setattr(self.s, key, tuple(int(round(x)) for x in c[0]))
            self.swatches[key].configure(background=self._hex(getattr(self.s, key)))
            self.schedule()

    def change_shape(self, key):
        if key not in R.SHAPES:
            return
        self.s.shape = key
        self._build_params()
        self.reset_view()

    def reset_view(self):
        az, el = R.SHAPES[self.s.shape]["view"]
        self.s.azimuth, self.s.elevation, self.s.zoom = az, el, 1.0
        self._sync_controls()
        self.schedule()

    def reset_params(self):
        self.s.params.pop(self.s.shape, None)
        self._build_params()
        self._sync_controls()
        self.schedule()

    def reset_all(self):
        if messagebox.askyesno(APP_NAME, "Restore every setting to its default?", parent=self.root):
            self.s = R.Settings()
            self._build_params()
            self._sync_controls()
            self.schedule()

    def save_image(self, force_transparent=False):
        dlg = ExportDialog(self.root, self._prefs["export_width"],
                           True if force_transparent else self._prefs["transparent"])
        self.root.wait_window(dlg.top)
        if not dlg.result:
            return
        width, transparent = dlg.result
        self._prefs["export_width"], self._prefs["transparent"] = width, transparent
        self.transparent_var.set(transparent)
        self.schedule()
        types = [("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("TIFF image", "*.tif"),
                 ("BMP image", "*.bmp"), ("PDF document", "*.pdf")]
        path = filedialog.asksaveasfilename(parent=self.root, title="Save image",
                                            initialdir=self._prefs["last_dir"],
                                            initialfile="%s.png" % self.s.shape,
                                            defaultextension=".png", filetypes=types)
        if not path:
            return
        self._prefs["last_dir"] = os.path.dirname(path)
        ext = os.path.splitext(path)[1].lower()
        height = int(round(width * R.REF_SIZE[1] / R.REF_SIZE[0]))
        if transparent and ext not in (".png", ".tif", ".tiff"):
            if not messagebox.askokcancel(
                    APP_NAME, "%s files cannot have a transparent background.\n\n"
                    "Save with the background colour instead? (Choose PNG or TIFF to keep "
                    "the background transparent.)" % ext.lstrip(".").upper(), parent=self.root):
                return
        self.status.configure(text="Saving...")
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            ss = 4 if width <= 2500 else 2
            if transparent and ext in (".png", ".tif", ".tiff"):
                img = R.render_rgba(self.s, (width, height), ss)
            else:
                img = R.render(self.s, (width, height), ss)
            if ext in (".jpg", ".jpeg"):
                img.save(path, quality=95)
            elif ext == ".pdf":
                img.save(path, resolution=300.0)
            else:
                img.save(path)
            self.status.configure(text="Saved %s (%d x %d)" % (os.path.basename(path), width, height))
        except Exception as ex:
            messagebox.showerror(APP_NAME, "Could not save the image:\n\n%s" % ex, parent=self.root)
            self.status.configure(text="")
        finally:
            self.root.config(cursor="")
        self.save_config()

    def create_shortcut(self):
        from . import shortcuts
        self.root.config(cursor="watch")
        self.root.update_idletasks()
        try:
            where = shortcuts.create_shortcut()
        except Exception as exc:
            messagebox.showerror(
                "Desktop shortcut", "The shortcut could not be created:\n\n%s\n\n"
                "See Help \u203a Troubleshooting for how to make one by hand." % exc, parent=self.root)
            return
        finally:
            self.root.config(cursor="")
        messagebox.showinfo(
            "Desktop shortcut", "Shortcut created:\n%s\n\nDouble-click it to start %s.\n\n"
            "If you move or rename the app folder later, start the app from its new place and "
            "choose Tools \u203a Create Desktop Shortcut again." % (where, APP_NAME), parent=self.root)

    def open_settings_folder(self):
        d = config_dir()
        try:
            if sys.platform.startswith("win"):
                os.startfile(d)  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                subprocess.Popen(["open", d])
            else:
                subprocess.Popen(["xdg-open", d])
        except Exception:
            messagebox.showinfo(APP_NAME, d, parent=self.root)

    def show_about(self):
        import webbrowser

        win = tk.Toplevel(self.root)
        win.title("About " + APP_NAME)
        win.transient(self.root)
        win.resizable(False, False)
        frm = ttk.Frame(win, padding=(26, 20, 26, 16))
        frm.pack(fill="both", expand=True)
        wrap = 420

        try:
            icon = Image.open(ICON_PNG).convert("RGBA").resize((96, 96), Image.LANCZOS)
            self._about_icon = ImageTk.PhotoImage(icon, master=win)
            ttk.Label(frm, image=self._about_icon).pack()
        except Exception:
            pass
        ttk.Label(frm, text=APP_NAME, font=("TkDefaultFont", 18, "bold")).pack(pady=(8, 0))
        ttk.Label(frm, text="Version %s" % __version__, foreground="#666666").pack()
        ttk.Label(frm, text="Translucent 3D figures of nanocrystal shapes\n"
                            "for slides, posters, papers and teaching.",
                  justify="center").pack(pady=(10, 12))

        ttk.Separator(frm).pack(fill="x", pady=(0, 12))
        ttk.Label(frm, text="Idea, design and direction", foreground="#666666").pack()
        ttk.Label(frm, text=__author__, font=("TkDefaultFont", 12, "bold")).pack()
        mail = tk.Label(frm, text=__email__, fg="#1a5fb4", cursor="hand2",
                        font=("TkDefaultFont", 10, "underline"))
        mail.pack(pady=(0, 10))
        mail.bind("<Button-1>", lambda e: webbrowser.open(
            "mailto:%s?subject=Nanocrystal%%20Shapes" % __email__))

        for text in (__concept__, __ai_assistance__):
            ttk.Label(frm, text=text, wraplength=wrap, justify="center").pack(pady=(0, 8))
        ttk.Label(frm, text="Privacy", foreground="#666666").pack(pady=(4, 0))
        ttk.Label(frm, text="Works completely offline. No data is collected, sent, shared or sold. "
                            "The internet is used only to install missing Python packages, and only "
                            "after you agree.", wraplength=wrap, justify="center").pack()
        priv = tk.Label(frm, text="Full details: Help \u203a Privacy & Safety", fg="#1a5fb4",
                        cursor="hand2", font=("TkDefaultFont", 10, "underline"))
        priv.pack(pady=(2, 8))
        priv.bind("<Button-1>", lambda e: (win.destroy(), self.open_help(6)))
        ttk.Label(frm, text=__license_note__, wraplength=wrap, justify="center").pack(pady=(4, 8))

        ttk.Label(frm, text="Python %s  ·  Pillow %s  ·  Tk %s\n%s %s" % (
            platform.python_version(), getattr(Image, "__version__", "?"),
            self.root.tk.call("info", "patchlevel"), platform.system(), platform.release()),
            foreground="#888888", justify="center").pack(pady=(4, 12))

        btns = ttk.Frame(frm)
        btns.pack()

        def copy_credit():
            self.root.clipboard_clear()
            self.root.clipboard_append(acknowledgment())
            self.root.update()
            copy_btn.configure(text="Copied ✔")
        copy_btn = ttk.Button(btns, text="Copy Acknowledgment Text", command=copy_credit)
        copy_btn.pack(side="left", padx=4)
        ttk.Button(btns, text="Close", command=win.destroy).pack(side="left", padx=4)
        win.bind("<Escape>", lambda e: win.destroy())

        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - win.winfo_reqwidth()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - win.winfo_reqheight()) // 3
        win.geometry("+%d+%d" % (max(x, 0), max(y, 0)))
        win.grab_set()
        return win


class ExportDialog:
    def __init__(self, parent, width, transparent):
        self.result = None
        t = self.top = tk.Toplevel(parent)
        t.title("Save Image")
        t.transient(parent)
        t.resizable(False, False)
        f = ttk.Frame(t, padding=12)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Width in pixels:").grid(row=0, column=0, sticky="w")
        self.w = tk.StringVar(value=str(width))
        sp = ttk.Spinbox(f, from_=100, to=8000, increment=98, textvariable=self.w, width=8)
        sp.grid(row=0, column=1, sticky="w", padx=6)
        self.h = ttk.Label(f, text="")
        self.h.grid(row=0, column=2, sticky="w")
        pres = ttk.Frame(f)
        pres.grid(row=1, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Label(pres, text="Presets:").pack(side="left")
        for n in (1, 2, 4, 8):
            ttk.Button(pres, text="%dx" % n, width=4,
                       command=lambda n=n: self.w.set(str(R.REF_SIZE[0] * n))).pack(side="left", padx=2)
        self.tr = tk.BooleanVar(value=transparent)
        ttk.Checkbutton(f, text="Transparent background (PNG / TIFF only)", variable=self.tr).grid(
            row=2, column=0, columnspan=3, sticky="w", pady=(8, 0))
        b = ttk.Frame(f)
        b.grid(row=3, column=0, columnspan=3, sticky="e", pady=(12, 0))
        ttk.Button(b, text="Cancel", command=t.destroy).pack(side="right")
        ttk.Button(b, text="Choose File...", command=self.ok).pack(side="right", padx=6)
        self.w.trace_add("write", lambda *a: self._upd())
        self._upd()
        t.bind("<Return>", lambda e: self.ok())
        t.bind("<Escape>", lambda e: t.destroy())
        t.grab_set()
        sp.focus_set()

    def _upd(self):
        try:
            w = int(float(self.w.get()))
            self.h.configure(text="x %d px" % round(w * R.REF_SIZE[1] / R.REF_SIZE[0]))
        except ValueError:
            self.h.configure(text="")

    def ok(self):
        try:
            w = int(float(self.w.get()))
        except ValueError:
            return
        if not 50 <= w <= 10000:
            messagebox.showwarning("Save Image", "Choose a width between 50 and 10000 pixels.", parent=self.top)
            return
        self.result = (w, bool(self.tr.get()))
        self.top.destroy()


# ---------------------------------------------------------------- identity


def set_app_identity_early():
    """Windows groups taskbar buttons by 'AppUserModelID'. Without one, every
    pythonw.exe window shares one taskbar button and icon (e.g. that of
    another Python app's pinned shortcut). Give this app its own."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass


def apply_icon(root):
    """Window, taskbar and Dock icon."""
    try:
        if sys.platform.startswith("win") and os.path.exists(ICON_ICO):
            root.iconbitmap(default=ICON_ICO)
    except Exception:
        pass
    try:
        if os.path.exists(ICON_PNG):
            big = Image.open(ICON_PNG).convert("RGBA")
            imgs = [ImageTk.PhotoImage(big.resize((n, n), Image.LANCZOS), master=root) for n in (256, 64, 32, 16)]
            root.iconphoto(True, *imgs)   # also the Dock icon on macOS
            root._icon_refs = imgs        # keep references alive
    except Exception:
        pass


def main():
    set_app_identity_early()
    root = tk.Tk(className="NanocrystalShapes")   # Linux taskbar grouping (WM_CLASS)
    apply_icon(root)
    try:
        style = ttk.Style(root)
        if sys.platform.startswith("linux") and "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    App(root)
    root.mainloop()
