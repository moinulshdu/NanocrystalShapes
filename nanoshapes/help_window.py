"""Help window (manual pages) and the Python Packages window."""
from __future__ import annotations

import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import bootstrap
from .manual import PAGES, as_markdown


class HelpWindow(tk.Toplevel):
    """Manual pages in a list on the left, the page on the right."""

    def __init__(self, master, page=0):
        super().__init__(master)
        self.title("Nanocrystal Shapes – Help")
        self.geometry("900x640")
        self.minsize(620, 420)

        pane = ttk.Frame(self, padding=8)
        pane.pack(fill="both", expand=True)
        pane.columnconfigure(1, weight=1)
        pane.rowconfigure(0, weight=1)

        left = ttk.Frame(pane)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        self.listbox = tk.Listbox(left, width=20, activestyle="none", exportselection=False,
                                  font=("TkDefaultFont", 11), borderwidth=1, relief="solid",
                                  highlightthickness=0, selectbackground="#1a5fb4",
                                  selectforeground="white")
        for title, _ in PAGES:
            self.listbox.insert("end", "  " + title)
        self.listbox.pack(fill="y", expand=True)
        self.listbox.bind("<<ListboxSelect>>", lambda e: self._on_select())

        body = ttk.Frame(pane)
        body.grid(row=0, column=1, sticky="nsew")
        body.rowconfigure(0, weight=1)
        body.columnconfigure(0, weight=1)
        self.text = tk.Text(body, wrap="word", padx=18, pady=14, borderwidth=1, relief="solid",
                            highlightthickness=0, cursor="arrow", spacing1=2, spacing3=2)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        self.text.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")

        base = ("TkDefaultFont", 11)
        self.text.configure(font=base)
        self.text.tag_configure("h1", font=("TkDefaultFont", 18, "bold"), spacing1=4, spacing3=10,
                                foreground="#123b72")
        self.text.tag_configure("h2", font=("TkDefaultFont", 13, "bold"), spacing1=12, spacing3=4,
                                foreground="#1a5fb4")
        self.text.tag_configure("bold", font=("TkDefaultFont", 11, "bold"))
        self.text.tag_configure("bullet", lmargin1=12, lmargin2=30)
        self.text.tag_configure("code", font=("TkFixedFont", 10), background="#f2f4f7",
                                lmargin1=12, lmargin2=12, spacing1=0, spacing3=0)
        self.text.tag_configure("para", spacing3=6)

        btns = ttk.Frame(self, padding=(8, 0, 8, 8))
        btns.pack(fill="x")
        ttk.Button(btns, text="Save Manual as File…", command=self.export).pack(side="left")
        ttk.Button(btns, text="Close", command=self.destroy).pack(side="right")
        self.bind("<Escape>", lambda e: self.destroy())
        self.show(page)

    def _on_select(self):
        sel = self.listbox.curselection()
        if sel:
            self._render(sel[0])

    def show(self, page):
        page = max(0, min(len(PAGES) - 1, page))
        self.listbox.selection_clear(0, "end")
        self.listbox.selection_set(page)
        self.listbox.see(page)
        self._render(page)
        self.lift()

    def _insert_inline(self, line, tags=()):
        parts = re.split(r"(\*\*[^*]+\*\*)", line)
        for part in parts:
            if part.startswith("**") and part.endswith("**") and len(part) > 4:
                self.text.insert("end", part[2:-2], tags + ("bold",))
            elif part:
                self.text.insert("end", part, tags)

    def _render(self, page):
        t = self.text
        t.configure(state="normal")
        t.delete("1.0", "end")
        prev_heading = False
        for line in PAGES[page][1].strip("\n").splitlines():
            if not line.strip() and prev_heading:
                continue                      # headings carry their own spacing
            prev_heading = line.startswith("#")
            if line.startswith("# "):
                t.insert("end", line[2:] + "\n", ("h1",))
            elif line.startswith("## "):
                t.insert("end", line[3:] + "\n", ("h2",))
            elif line.startswith("    "):
                t.insert("end", line[4:] + "\n", ("code",))
            elif line.startswith("- "):
                t.insert("end", "•  ", ("bullet",))
                self._insert_inline(line[2:], ("bullet",))
                t.insert("end", "\n", ("bullet",))
            elif line.strip():
                self._insert_inline(line, ("para",))
                t.insert("end", "\n", ("para",))
            else:
                t.insert("end", "\n")
        t.configure(state="disabled")
        t.yview_moveto(0)

    def export(self):
        p = filedialog.asksaveasfilename(parent=self, title="Save manual", defaultextension=".md",
                                         initialfile="Nanocrystal Shapes - User Manual.md",
                                         filetypes=[("Markdown / text", "*.md"), ("Text", "*.txt")])
        if p:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(as_markdown())


class PackagesWindow(tk.Toplevel):
    """Shows which Python packages are installed and lets the user install missing ones."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Python Packages")
        self.geometry("720x300")
        self.minsize(600, 260)
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)
        ttk.Label(frm, text="Python: %s\nVersion %s" % (sys.executable, sys.version.split()[0]),
                  foreground="#555").pack(anchor="w", pady=(0, 8))
        self.tree = ttk.Treeview(frm, columns=("status", "version", "purpose"),
                                 show="tree headings", height=4)
        self.tree.heading("#0", text="Package")
        self.tree.heading("status", text="Status")
        self.tree.heading("version", text="Version")
        self.tree.heading("purpose", text="Used for")
        self.tree.column("#0", width=110, stretch=False)
        self.tree.column("status", width=150, stretch=False)
        self.tree.column("version", width=80, stretch=False)
        self.tree.column("purpose", width=330)
        self.tree.pack(fill="both", expand=True)
        btns = ttk.Frame(frm)
        btns.pack(fill="x", pady=(10, 0))
        self.install_btn = ttk.Button(btns, text="Install Missing Packages…", command=self.install)
        self.install_btn.pack(side="left")
        ttk.Button(btns, text="Close", command=self.destroy).pack(side="right")
        self.note = ttk.Label(frm, text="", foreground="#666")
        self.note.pack(anchor="w", pady=(6, 0))
        self.bind("<Escape>", lambda e: self.destroy())
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        n_missing = 0
        for pkg, ok, version in bootstrap.status_report():
            status = ("✔ installed" if ok else "✖ missing") + ("" if pkg.required else " (optional)")
            n_missing += not ok
            self.tree.insert("", "end", text=pkg.pip_name, values=(status, version, pkg.purpose))
        import tkinter
        self.tree.insert("", "end", text="tkinter", values=("✔ built into Python", tkinter.TkVersion,
                                                           "the window, menus and buttons"))
        self.install_btn.state(["!disabled"] if n_missing else ["disabled"])
        self.note.configure(text="Missing packages can be installed here (an internet connection is needed)."
                            if n_missing else "Everything the app can use is installed.")

    def install(self):
        pkgs = bootstrap.missing()
        if not pkgs:
            return
        lines = "\n".join("  • %s – %s" % (p.pip_name, p.purpose) for p in pkgs)
        if messagebox.askyesno("Install packages", "Install these packages now?\n\n%s\n\n"
                               "They are downloaded from the official Python Package Index "
                               "(an internet connection is needed)." % lines, parent=self):
            bootstrap.install_with_progress(self, pkgs)
            self.refresh()
