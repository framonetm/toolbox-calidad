"""Clase base de herramientas y herramienta genérica basada en esquemas."""
from __future__ import annotations

import os
import subprocess
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from toolbox_calidad.core import export, storage
from toolbox_calidad.ui.widgets import ScrollFrame, build_section


def open_file(path):
    """Abre un archivo con la aplicación predeterminada del sistema."""
    path = str(path)
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        webbrowser.open(Path(path).as_uri())


def safe_name(text):
    keep = "".join(ch if ch.isalnum() or ch in " -_" else "_" for ch in text)
    return "_".join(keep.split())[:60] or "documento"


class ToolBase(ttk.Frame):
    """Herramienta con barra: Nuevo · Abrir · Guardar · Exportar Excel · Exportar PDF/HTML · Info.

    Las subclases implementan ``build_body(parent)``, ``get_state()``, ``set_state(d)``
    y ``blocks()``.
    """

    tool_id = "herramienta"
    title = "Herramienta"
    code = ""
    description = ""
    source = ""
    savable = True

    def __init__(self, master, meta: dict | None = None):
        super().__init__(master)
        if meta:
            self.tool_id = meta.get("id", self.tool_id)
            self.title = meta.get("title", self.title)
            self.code = meta.get("code", self.code)
            self.description = meta.get("description", self.description)
            self.source = meta.get("source", self.source)
        self.path: Path | None = None
        self.dirty = False
        self._build_toolbar()
        self.build_body(self)
        self.dirty = False

    # -- barra -------------------------------------------------------------
    def _build_toolbar(self):
        bar = ttk.Frame(self, style="Toolbar.TFrame", padding=(8, 6))
        bar.pack(fill="x")
        ttk.Label(bar, text=self.title, style="Title.TLabel", background="#DDEBF7").pack(side="left", padx=(0, 16))
        if self.code:
            ttk.Label(bar, text=self.code, background="#DDEBF7", foreground="#595959").pack(side="left")
        right = ttk.Frame(bar, style="Toolbar.TFrame")
        right.pack(side="right")
        buttons = []
        if self.savable:
            buttons += [("Nuevo", self.cmd_new), ("Abrir…", self.cmd_open), ("Guardar", self.cmd_save),
                        ("Guardar como…", self.cmd_save_as)]
        buttons += [("Exportar Excel", self.cmd_xlsx), ("Imprimir / PDF", self.cmd_html), ("ⓘ Info", self.cmd_info)]
        for text, cmd in buttons:
            ttk.Button(right, text=text, command=cmd).pack(side="left", padx=2)
        self.status = ttk.Label(self, text="", foreground="#595959", padding=(10, 2))
        self.status.pack(side="bottom", fill="x")

    def set_status(self, text):
        self.status.configure(text=text)

    def mark_dirty(self):
        self.dirty = True

    # -- a implementar -----------------------------------------------------
    def build_body(self, parent):  # pragma: no cover
        raise NotImplementedError

    def get_state(self) -> dict:
        return {}

    def set_state(self, state: dict):
        pass

    def blocks(self) -> list[dict]:
        return []

    def reset(self):
        self.set_state({})

    # -- comandos ----------------------------------------------------------
    def confirm_discard(self):
        if not self.dirty:
            return True
        return messagebox.askyesno(self.title, "Hay cambios sin guardar. ¿Descartarlos?", parent=self)

    def cmd_new(self):
        if self.confirm_discard():
            self.reset()
            self.path = None
            self.dirty = False
            self.set_status("Documento nuevo")

    def cmd_open(self):
        if not self.confirm_discard():
            return
        p = filedialog.askopenfilename(parent=self, title="Abrir documento",
                                       filetypes=[("Documento toolbox", "*.qtb.json"), ("JSON", "*.json")])
        if not p:
            return
        try:
            doc = storage.load_document(p, self.tool_id)
            self.set_state(doc.get("secciones", {}))
        except Exception as exc:
            messagebox.showerror(self.title, f"No se pudo abrir el archivo:\n{exc}", parent=self)
            return
        self.path = Path(p)
        self.dirty = False
        self.set_status(f"Abierto: {p}")

    def cmd_save(self):
        if self.path is None:
            return self.cmd_save_as()
        doc = storage.new_document(self.tool_id, self.title)
        doc["secciones"] = self.get_state()
        storage.save_document(self.path, doc)
        self.dirty = False
        self.set_status(f"Guardado: {self.path}")

    def cmd_save_as(self):
        p = filedialog.asksaveasfilename(parent=self, title="Guardar documento",
                                         defaultextension=".qtb.json",
                                         initialfile=safe_name(self.title) + storage.EXTENSION,
                                         filetypes=[("Documento toolbox", "*.qtb.json")])
        if p:
            self.path = Path(p)
            self.cmd_save()

    def _export(self, kind):
        ext = ".xlsx" if kind == "xlsx" else ".html"
        p = filedialog.asksaveasfilename(parent=self, title="Exportar", defaultextension=ext,
                                         initialfile=safe_name(self.title) + ext,
                                         filetypes=[("Excel", "*.xlsx")] if kind == "xlsx" else [("HTML", "*.html")])
        if not p:
            return
        try:
            blocks = self.blocks()
            fn = export.to_xlsx if kind == "xlsx" else export.to_html
            out = fn(p, self.title, blocks, self.code)
        except Exception as exc:
            messagebox.showerror(self.title, f"No se pudo exportar:\n{exc}", parent=self)
            return
        self.set_status(f"Exportado: {out}")
        open_file(out)

    def cmd_xlsx(self):
        self._export("xlsx")

    def cmd_html(self):
        self._export("html")
        self.set_status(self.status.cget("text") + "  —  usa Ctrl+P en el navegador para imprimir o guardar como PDF")

    def cmd_info(self):
        msg = self.description or self.title
        if self.source:
            msg += f"\n\nBasado en el formato original: {self.source}"
        messagebox.showinfo(self.title, msg, parent=self)


class FormTool(ToolBase):
    """Herramienta construida a partir de un esquema declarativo (ver ``forms``)."""

    def __init__(self, master, schema: dict):
        self.schema = schema
        super().__init__(master, schema)

    def build_body(self, parent):
        self.scroll = ScrollFrame(parent)
        self.scroll.pack(fill="both", expand=True)
        inner = self.scroll.inner
        if self.schema.get("intro"):
            ttk.Label(inner, text=self.schema["intro"], style="Help.TLabel", wraplength=1000,
                      justify="left", background="#F5F7FA").pack(anchor="w", pady=(0, 8))
        self.sections = {}
        for spec in self.schema["sections"]:
            sec = build_section(inner, spec, self._on_change)
            sec.frame.pack(fill="x", expand=True, pady=6)
            self.sections[spec["key"]] = sec
        self.after_build()

    def after_build(self):
        """Gancho para subclases."""

    def _on_change(self):
        self.mark_dirty()
        self.on_change()

    def on_change(self):
        """Gancho para subclases (recalcular resultados)."""

    def get_state(self):
        return {k: s.get() for k, s in self.sections.items()}

    def set_state(self, state):
        for k, s in self.sections.items():
            s.set((state or {}).get(k))
        self.on_change()

    def blocks(self):
        out = []
        if self.schema.get("intro"):
            out.append({"type": "note", "text": self.schema["intro"]})
        for s in self.sections.values():
            out.extend(s.blocks())
        out.extend(self.extra_blocks())
        return out

    def extra_blocks(self):
        return []
