"""Widgets reutilizables: marco con scroll y secciones de formato declarativas.

Cada sección se construye a partir de un diccionario (``spec``) y expone:

* ``get()``   → valor serializable a JSON
* ``set(v)``  → restaura el valor
* ``blocks()``→ bloques para exportar (ver ``core.export``)
"""
from __future__ import annotations

import datetime as _dt
import tkinter as tk
from tkinter import ttk

from toolbox_calidad.core.calc import resumen_checklist, promedio_calificaciones

FONT = ("Segoe UI", 10)
FONT_B = ("Segoe UI", 10, "bold")
FONT_S = ("Segoe UI", 9)
COLOR_HL = {"rojo": "#F8CBAD", "ambar": "#FFE699", "verde": "#C6EFCE", "gris": "#E7E6E6", None: "white"}


# ---------------------------------------------------------------------------
class ScrollFrame(ttk.Frame):
    """Marco con barras de desplazamiento; el contenido va en ``.inner``.

    La rueda del ratón se enlaza una sola vez a nivel global y desplaza el
    ``ScrollFrame`` que está bajo el puntero (funciona igual en Windows, macOS y Linux).
    """

    _wheel_bound = False

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background="#F5F7FA")
        self.canvas._scrollframe = self
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)
        self.inner = ttk.Frame(self.canvas, style="Body.TFrame", padding=10)
        self._win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", self._on_inner)
        self.canvas.bind("<Configure>", self._on_canvas)
        if not ScrollFrame._wheel_bound:
            ScrollFrame._wheel_bound = True
            self.bind_all("<MouseWheel>", ScrollFrame._wheel, add="+")
            self.bind_all("<Button-4>", lambda e: ScrollFrame._wheel(e, -120), add="+")
            self.bind_all("<Button-5>", lambda e: ScrollFrame._wheel(e, 120), add="+")

    def _on_inner(self, _e=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas(self, e):
        req = self.inner.winfo_reqwidth()
        self.canvas.itemconfigure(self._win, width=max(e.width, req))

    @staticmethod
    def _wheel(e, delta=None):
        try:
            w = e.widget.winfo_containing(e.x_root, e.y_root)
        except Exception:
            return
        # Los cuadros de texto y listas se desplazan solos
        if w is None or isinstance(w, (tk.Text, tk.Listbox, ttk.Treeview)):
            return
        while w is not None and not hasattr(w, "_scrollframe"):
            w = getattr(w, "master", None)
        if w is None:
            return
        d = delta if delta is not None else -e.delta
        step = int(d / 120) if abs(d) >= 120 else (1 if d > 0 else -1)
        w.yview_scroll(step * 3, "units")


# ---------------------------------------------------------------------------
class Section:
    """Clase base de las secciones."""

    def __init__(self, master, spec: dict, on_change=None):
        self.spec = spec
        self.key = spec["key"]
        self.on_change = on_change or (lambda: None)
        self.frame = ttk.LabelFrame(master, text=spec.get("title", ""), padding=8, style="Sec.TLabelframe")
        if spec.get("help"):
            ttk.Label(self.frame, text=spec["help"], style="Help.TLabel",
                      wraplength=900, justify="left").pack(anchor="w", pady=(0, 6))
        self.body = ttk.Frame(self.frame)
        self.body.pack(fill="both", expand=True)
        self.build()

    def build(self):  # pragma: no cover - abstracto
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def set(self, value):
        raise NotImplementedError

    def blocks(self):
        return []

    def changed(self, *_):
        self.on_change()


# ---------------------------------------------------------------------------
class FieldsSection(Section):
    """Campos etiqueta/valor en una rejilla de N columnas.

    Cada campo: ``{"key", "label", "options"?, "kind": "text|date|number", "width"?,
    "readonly"?, "default"?}``
    """

    def build(self):
        self.vars = {}
        self.widgets = {}
        cols = self.spec.get("columns", 2)
        for i, f in enumerate(self.spec["fields"]):
            r, c = divmod(i, cols)
            ttk.Label(self.body, text=f["label"] + ":", font=FONT_B if f.get("bold") else FONT
                      ).grid(row=r, column=2 * c, sticky="w", padx=(0, 6), pady=3)
            var = tk.StringVar(value=self._default(f))
            if f.get("options"):
                w = ttk.Combobox(self.body, textvariable=var, values=f["options"],
                                 width=f.get("width", 28))
                w.bind("<<ComboboxSelected>>", self.changed)
            else:
                w = ttk.Entry(self.body, textvariable=var, width=f.get("width", 30))
            if f.get("readonly"):
                w.state(["readonly"])
            w.grid(row=r, column=2 * c + 1, sticky="we", padx=(0, 18), pady=3)
            var.trace_add("write", self.changed)
            self.vars[f["key"]] = var
            self.widgets[f["key"]] = w
        for c in range(cols):
            self.body.columnconfigure(2 * c + 1, weight=1)

    @staticmethod
    def _default(f):
        if f.get("kind") == "date" and f.get("default") == "hoy":
            return _dt.date.today().strftime("%d/%m/%Y")
        return str(f.get("default", ""))

    def get(self):
        return {k: v.get() for k, v in self.vars.items()}

    def set(self, value):
        for f in self.spec["fields"]:
            self.vars[f["key"]].set((value or {}).get(f["key"], self._default(f)))

    def __getitem__(self, key):
        return self.vars[key].get()

    def put(self, key, value):
        self.vars[key].set(value)

    def blocks(self):
        return [{"type": "kv", "title": self.spec.get("title", ""),
                 "pairs": [(f["label"], self.vars[f["key"]].get()) for f in self.spec["fields"]]}]


# ---------------------------------------------------------------------------
class ChoicesSection(Section):
    """Opciones marcables (casillas o radio). ``{"options": [...], "multi": bool}``"""

    def build(self):
        self.multi = self.spec.get("multi", True)
        if self.multi:
            self.vars = {o: tk.BooleanVar(value=False) for o in self.spec["options"]}
            for i, o in enumerate(self.spec["options"]):
                ttk.Checkbutton(self.body, text=o, variable=self.vars[o], command=self.changed
                                ).grid(row=i // 6, column=i % 6, sticky="w", padx=6, pady=2)
        else:
            self.var = tk.StringVar()
            for i, o in enumerate(self.spec["options"]):
                ttk.Radiobutton(self.body, text=o, value=o, variable=self.var, command=self.changed
                                ).grid(row=i // 6, column=i % 6, sticky="w", padx=6, pady=2)

    def get(self):
        if self.multi:
            return [o for o, v in self.vars.items() if v.get()]
        return self.var.get()

    def set(self, value):
        if self.multi:
            value = value or []
            for o, v in self.vars.items():
                v.set(o in value)
        else:
            self.var.set(value or "")

    def blocks(self):
        sel = self.get()
        txt = ", ".join(sel) if isinstance(sel, list) else sel
        return [{"type": "kv", "title": self.spec.get("title", ""),
                 "pairs": [("Selección", txt or "—")]}]


# ---------------------------------------------------------------------------
class TextSection(Section):
    """Texto libre multilínea. ``{"height": 4}``"""

    def build(self):
        wrap = ttk.Frame(self.body)
        wrap.pack(fill="both", expand=True)
        self.text = tk.Text(wrap, height=self.spec.get("height", 4), wrap="word", font=FONT,
                            relief="solid", borderwidth=1, undo=True)
        sb = ttk.Scrollbar(wrap, command=self.text.yview)
        self.text.configure(yscrollcommand=sb.set)
        self.text.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        if self.spec.get("placeholder"):
            self.text.insert("1.0", "")
        self.text.bind("<<Modified>>", self._mod)

    def _mod(self, _e=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.changed()

    def get(self):
        return self.text.get("1.0", "end-1c")

    def set(self, value):
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value or "")

    def blocks(self):
        return [{"type": "text", "title": self.spec.get("title", ""), "text": self.get()}]


# ---------------------------------------------------------------------------
class TableSection(Section):
    """Tabla editable.

    ``columns``: lista de ``{"key", "label", "width"?, "options"?, "compute"?(fila)->valor,
    "readonly"?}``. ``rows``: filas iniciales. ``default_rows``: lista de dicts precargados.
    ``highlight``: función opcional ``fila -> 'rojo'|'ambar'|'verde'|None``.
    """

    def build(self):
        self.columns = self.spec["columns"]
        self.rows: list[dict] = []
        self.grid = ttk.Frame(self.body)
        self.grid.pack(fill="x", anchor="w")
        if not self.spec.get("numbered") is False:
            ttk.Label(self.grid, text="#", style="TH.TLabel", anchor="center", width=3
                      ).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        for ci, col in enumerate(self.columns, start=1):
            ttk.Label(self.grid, text=col["label"], style="TH.TLabel", anchor="center",
                      wraplength=max(60, col.get("width", 14) * 7), justify="center"
                      ).grid(row=0, column=ci, sticky="nsew", padx=1, pady=1)
        bar = ttk.Frame(self.body)
        bar.pack(fill="x", pady=(6, 0))
        if not self.spec.get("fixed"):
            ttk.Button(bar, text="+ Agregar fila", command=self.add_row).pack(side="left")
            ttk.Button(bar, text="− Quitar última", command=self.remove_row).pack(side="left", padx=6)
        self.extra_bar = bar
        self.summary = ttk.Label(bar, text="", style="Help.TLabel")
        self.summary.pack(side="right")
        self._loading = False
        self.reset()

    # -- filas -------------------------------------------------------------
    def reset(self):
        self._loading = True
        try:
            for r in list(self.rows):
                self._destroy_row(r)
            self.rows.clear()
            default = self.spec.get("default_rows")
            if callable(default):
                default = default()
            for d in default or []:
                self.add_row(d)
            for _ in range(max(0, self.spec.get("rows", 5) - len(default or []))):
                self.add_row()
        finally:
            self._loading = False
        self.refresh()

    def _destroy_row(self, row):
        for w in row["_widgets"]:
            w.destroy()

    def add_row(self, values: dict | None = None):
        values = values or {}
        idx = len(self.rows) + 1
        row = {"_vars": {}, "_widgets": []}
        lbl = ttk.Label(self.grid, text=str(idx), anchor="center", width=3)
        lbl.grid(row=idx, column=0, sticky="nsew", padx=1)
        row["_widgets"].append(lbl)
        for ci, col in enumerate(self.columns, start=1):
            var = tk.StringVar(value=str(values.get(col["key"], col.get("default", ""))))
            if col.get("options"):
                w = ttk.Combobox(self.grid, textvariable=var, values=col["options"],
                                 width=col.get("width", 14))
                w.bind("<<ComboboxSelected>>", lambda e: self._cell_changed())
            else:
                w = tk.Entry(self.grid, textvariable=var, width=col.get("width", 14), font=FONT,
                             relief="solid", borderwidth=1, justify=col.get("justify", "left"))
                if col.get("compute") or col.get("readonly"):
                    w.configure(state="readonly", readonlybackground="#EEF3F8")
            w.grid(row=idx, column=ci, sticky="nsew", padx=1, pady=1)
            var.trace_add("write", lambda *a: self._cell_changed())
            row["_vars"][col["key"]] = var
            row["_widgets"].append(w)
        self.rows.append(row)
        if not self._loading:
            self.refresh()
            self.changed()
        return row

    def remove_row(self):
        if self.rows:
            self._destroy_row(self.rows.pop())
            self.refresh()
            self.changed()

    def _cell_changed(self):
        if self._loading:
            return
        self.refresh()
        self.changed()

    # -- cálculo -----------------------------------------------------------
    def row_values(self, row) -> dict:
        return {k: v.get() for k, v in row["_vars"].items()}

    def refresh(self):
        """Recalcula columnas calculadas y colores."""
        self._loading = True
        try:
            for row in self.rows:
                vals = self.row_values(row)
                for col in self.columns:
                    if col.get("compute"):
                        try:
                            res = col["compute"](vals)
                        except Exception:
                            res = "¡error!"
                        res = "" if res is None else (f"{res:.2f}".rstrip("0").rstrip(".")
                                                       if isinstance(res, float) else str(res))
                        if row["_vars"][col["key"]].get() != res:
                            row["_vars"][col["key"]].set(res)
                        vals[col["key"]] = res
                color = None
                if self.spec.get("highlight"):
                    try:
                        color = self.spec["highlight"](vals)
                    except Exception:
                        color = None
                for w in row["_widgets"][1:]:
                    if isinstance(w, tk.Entry):
                        bg = COLOR_HL.get(color, "white")
                        w.configure(background=bg)
                        if str(w.cget("state")) == "readonly":
                            w.configure(readonlybackground=bg if color else "#EEF3F8")
            if self.spec.get("summary"):
                try:
                    self.summary.configure(text=self.spec["summary"](self.values()))
                except Exception:
                    self.summary.configure(text="")
        finally:
            self._loading = False

    # -- API ---------------------------------------------------------------
    def values(self) -> list[dict]:
        return [self.row_values(r) for r in self.rows]

    def nonempty_values(self) -> list[dict]:
        keys = [c["key"] for c in self.columns if not c.get("compute")]
        return [v for v in self.values() if any(str(v.get(k, "")).strip() for k in keys)]

    def get(self):
        return self.values()

    def set(self, value):
        self._loading = True
        try:
            for r in list(self.rows):
                self._destroy_row(r)
            self.rows.clear()
            for v in value or []:
                self.add_row(v)
        finally:
            self._loading = False
        if not value:
            self.reset()
        self.refresh()

    def blocks(self):
        rows = self.nonempty_values()
        hl = {}
        if self.spec.get("highlight"):
            for i, v in enumerate(rows):
                try:
                    c = self.spec["highlight"](v)
                except Exception:
                    c = None
                if c:
                    hl[i] = c
        b = [{"type": "table", "title": self.spec.get("title", ""),
              "headers": ["#"] + [c["label"] for c in self.columns],
              "rows": [[i + 1] + [v.get(c["key"], "") for c in self.columns] for i, v in enumerate(rows)],
              "highlight": hl}]
        if self.spec.get("summary"):
            try:
                b.append({"type": "note", "text": self.spec["summary"](self.values())})
            except Exception:
                pass
        return b


# ---------------------------------------------------------------------------
class ChecklistSection(Section):
    """Lista de verificación agrupada.

    ``groups``: ``[{"name", "items": [{"code", "text"}]}]``; ``options``: respuestas;
    ``score``: si es True agrega calificación 0-5 por apartado.
    """

    def build(self):
        self.options = self.spec.get("options", ["Sí", "No", "N/A"])
        self.positive = self.spec.get("positive", (self.options[0],))
        self.negative = self.spec.get("negative", (self.options[1],) if len(self.options) > 1 else ())
        self.score = self.spec.get("score", False)
        self.items = []  # (id, group, code, text, resp_var, obs_var, score_var)
        self.group_labels = {}
        self.top = ttk.Label(self.body, text="", style="Sum.TLabel")
        self.top.pack(anchor="w", pady=(0, 6))
        tools = ttk.Frame(self.body)
        tools.pack(anchor="w", pady=(0, 6))
        ttk.Label(tools, text="Marcar sin respuesta como:").pack(side="left")
        for o in self.options:
            ttk.Button(tools, text=o, width=max(4, len(o) + 1),
                       command=lambda o=o: self.fill_empty(o)).pack(side="left", padx=2)
        for gi, g in enumerate(self.spec["groups"]):
            gf = ttk.Frame(self.body)
            gf.pack(fill="x", pady=(8, 2))
            ttk.Label(gf, text=g["name"], style="Group.TLabel").pack(side="left")
            gl = ttk.Label(gf, text="", style="Help.TLabel")
            gl.pack(side="right")
            self.group_labels[gi] = gl
            grid = ttk.Frame(self.body)
            grid.pack(fill="x")
            heads = ["Clave", "Aspecto a verificar", "Respuesta", "Observaciones"] + (["Calif. 0-5"] if self.score else [])
            for ci, h in enumerate(heads):
                ttk.Label(grid, text=h, style="TH.TLabel", anchor="center").grid(row=0, column=ci, sticky="nsew", padx=1)
            grid.columnconfigure(1, weight=1)
            grid.columnconfigure(3, weight=1)
            for ii, it in enumerate(g["items"], start=1):
                iid = f"{gi}-{ii - 1}"
                ttk.Label(grid, text=it.get("code", ""), width=8).grid(row=ii, column=0, sticky="nw", pady=1)
                ttk.Label(grid, text=it["text"], wraplength=520, justify="left").grid(
                    row=ii, column=1, sticky="w", pady=1, padx=4)
                rv = tk.StringVar()
                cb = ttk.Combobox(grid, textvariable=rv, values=[""] + self.options, width=11, state="readonly")
                cb.grid(row=ii, column=2, sticky="n", padx=2, pady=1)
                rv.trace_add("write", lambda *a: self._upd())
                ov = tk.StringVar()
                ttk.Entry(grid, textvariable=ov, width=34).grid(row=ii, column=3, sticky="new", padx=2, pady=1)
                ov.trace_add("write", self.changed)
                sv = tk.StringVar()
                if self.score:
                    ttk.Combobox(grid, textvariable=sv, values=["", "0", "1", "2", "3", "4", "5"], width=5,
                                 state="readonly").grid(row=ii, column=4, sticky="n", padx=2, pady=1)
                    sv.trace_add("write", lambda *a: self._upd())
                self.items.append((iid, gi, it.get("code", ""), it["text"], rv, ov, sv))
        self._upd()

    def fill_empty(self, option):
        for it in self.items:
            if not it[4].get():
                it[4].set(option)

    def stats(self, group=None):
        sel = [it for it in self.items if group is None or it[1] == group]
        res = resumen_checklist([it[4].get() for it in sel], self.positive, self.negative)
        res["promedio"] = promedio_calificaciones(it[6].get() for it in sel) if self.score else None
        return res

    @staticmethod
    def _fmt(st):
        pct = "—" if st["porcentaje"] is None else f"{st['porcentaje']:.0f} %"
        s = (f"Cumple: {st['cumple']}   No cumple: {st['no_cumple']}   N/A: {st['na']}   "
             f"Pendientes: {st['sin_respuesta']}   Cumplimiento: {pct}")
        if st.get("promedio") is not None:
            s += f"   Calificación promedio: {st['promedio']:.2f}/5"
        return s

    def _upd(self):
        self.top.configure(text="Resumen general →  " + self._fmt(self.stats()))
        for gi, lbl in self.group_labels.items():
            st = self.stats(gi)
            pct = "—" if st["porcentaje"] is None else f"{st['porcentaje']:.0f} %"
            extra = f" · {st['promedio']:.1f}/5" if st.get("promedio") is not None else ""
            lbl.configure(text=f"{pct} cumplimiento · {st['sin_respuesta']} pendientes{extra}")
        self.changed()

    def get(self):
        return {iid: {"r": rv.get(), "obs": ov.get(), "cal": sv.get()}
                for iid, _g, _c, _t, rv, ov, sv in self.items
                if rv.get() or ov.get() or sv.get()}

    def set(self, value):
        value = value or {}
        for iid, _g, _c, _t, rv, ov, sv in self.items:
            d = value.get(iid, {})
            rv.set(d.get("r", ""))
            ov.set(d.get("obs", ""))
            sv.set(d.get("cal", ""))

    def blocks(self):
        out = [{"type": "kv", "title": self.spec.get("title", "") + " — Resumen",
                "pairs": [("General", self._fmt(self.stats()))] +
                         [(g["name"], self._fmt(self.stats(gi))) for gi, g in enumerate(self.spec["groups"])]}]
        for gi, g in enumerate(self.spec["groups"]):
            rows, hl = [], {}
            for it in [x for x in self.items if x[1] == gi]:
                r = it[4].get()
                if r in self.negative:
                    hl[len(rows)] = "rojo"
                elif r in self.positive:
                    hl[len(rows)] = "verde"
                rows.append([it[2], it[3], r, it[5].get()] + ([it[6].get()] if self.score else []))
            out.append({"type": "table", "title": g["name"],
                        "headers": ["Clave", "Aspecto", "Respuesta", "Observaciones"] + (["Calif."] if self.score else []),
                        "rows": rows, "highlight": hl})
        return out


# ---------------------------------------------------------------------------
class SignaturesSection(Section):
    """Bloque de firmas: rol / nombre / fecha."""

    def build(self):
        self.vars = {}
        for ci, h in enumerate(["Rol", "Nombre (Apellido paterno, materno, nombre)", "Fecha"]):
            ttk.Label(self.body, text=h, style="TH.TLabel").grid(row=0, column=ci, sticky="nsew", padx=1)
        for i, role in enumerate(self.spec["roles"], start=1):
            ttk.Label(self.body, text=role).grid(row=i, column=0, sticky="w", padx=4, pady=2)
            nv, fv = tk.StringVar(), tk.StringVar()
            ttk.Entry(self.body, textvariable=nv, width=45).grid(row=i, column=1, sticky="we", padx=2)
            ttk.Entry(self.body, textvariable=fv, width=14).grid(row=i, column=2, padx=2)
            nv.trace_add("write", self.changed)
            fv.trace_add("write", self.changed)
            self.vars[role] = (nv, fv)
        self.body.columnconfigure(1, weight=1)

    def get(self):
        return {r: {"nombre": n.get(), "fecha": f.get()} for r, (n, f) in self.vars.items()}

    def set(self, value):
        value = value or {}
        for r, (n, f) in self.vars.items():
            n.set(value.get(r, {}).get("nombre", ""))
            f.set(value.get(r, {}).get("fecha", ""))

    def blocks(self):
        return [{"type": "table", "title": self.spec.get("title", "Firmas"),
                 "headers": ["Rol", "Nombre", "Fecha", "Firma"],
                 "rows": [[r, n.get(), f.get(), ""] for r, (n, f) in self.vars.items()]}]


SECTION_TYPES = {
    "fields": FieldsSection,
    "choices": ChoicesSection,
    "text": TextSection,
    "table": TableSection,
    "checklist": ChecklistSection,
    "signatures": SignaturesSection,
}


def build_section(master, spec, on_change=None) -> Section:
    return SECTION_TYPES[spec["type"]](master, spec, on_change)


# ---------------------------------------------------------------------------
def setup_styles(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    root.option_add("*Font", FONT)
    # Evita que la rueda del ratón cambie el valor de los combos al desplazar el formulario
    for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
        root.unbind_class("TCombobox", seq)
    style.configure(".", font=FONT)
    style.configure("Body.TFrame", background="#F5F7FA")
    style.configure("Sec.TLabelframe", background="#F5F7FA")
    style.configure("Sec.TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground="#1F4E79",
                    background="#F5F7FA")
    style.configure("TH.TLabel", background="#1F4E79", foreground="white", font=FONT_B, padding=3)
    style.configure("Group.TLabel", font=("Segoe UI", 10, "bold"), foreground="#1F4E79")
    style.configure("Help.TLabel", foreground="#595959", font=FONT_S)
    style.configure("Sum.TLabel", foreground="#1F4E79", font=FONT_B)
    style.configure("Title.TLabel", font=("Segoe UI", 15, "bold"), foreground="#1F4E79")
    style.configure("Big.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1F4E79")
    style.configure("Toolbar.TFrame", background="#DDEBF7")
    style.configure("Accent.TButton", font=FONT_B)
    style.configure("Treeview", rowheight=24)
    style.configure("Treeview.Heading", font=FONT_B)
