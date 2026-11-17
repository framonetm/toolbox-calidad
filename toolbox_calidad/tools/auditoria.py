"""Auditoría del grupo de mejora: 36 preguntas, 100 puntos, seguimiento de 12 semanas."""
import tkinter as tk
from tkinter import ttk

from toolbox_calidad.core.calc import to_float
from toolbox_calidad.core.storage import load_json
from toolbox_calidad.ui.base import ToolBase
from toolbox_calidad.ui.widgets import FieldsSection, ScrollFrame, TableSection

SEMANAS = 12
OBJETIVO_DEFECTO = [12, 15, 24, 33, 56, 58, 77, 79, 79, 85, 100, 100]


class AuditoriaTool(ToolBase):
    tool_id = "auditoria_grupo"
    title = "Auditoría del grupo de mejora"
    code = "F-GO-MT-026"
    source = "026 AUDITORIA DEL GRUPO DE MEJORA.xls"
    description = ("Evalúa semanalmente al grupo de mejora en planificación, implementación, control de resultados, "
                   "estabilización e involucración (100 puntos). Marca cada pregunta lograda en la semana; el total "
                   "se compara con la curva objetivo. Las preguntas con cero puntos alimentan el registro de acciones.")

    def build_body(self, parent):
        self.preguntas = load_json("auditoria_grupo_mejora.json")
        sf = ScrollFrame(parent)
        sf.pack(fill="both", expand=True)
        inner = sf.inner
        self.datos = FieldsSection(inner, {"key": "datos", "title": "Datos del grupo", "columns": 3, "fields": [
            {"key": "grupo", "label": "Grupo"}, {"key": "inicio", "label": "Fecha inicio"},
            {"key": "auditoria", "label": "Fecha auditoría", "kind": "date", "default": "hoy"},
            {"key": "perdida", "label": "Pérdida relacionada"}, {"key": "costo", "label": "Costo del proyecto ($)"},
            {"key": "ahorro", "label": "Ahorros anuales ($/año)"}, {"key": "pasos_plan", "label": "Pasos planificados"},
            {"key": "pasos_real", "label": "Pasos reales"}, {"key": "criticos", "label": "Puntos críticos al Comité", "width": 40}]},
            self.mark_dirty)
        self.datos.frame.pack(fill="x", pady=6)

        box = ttk.LabelFrame(inner, text="Cuestionario (marca ✓ si se logra en la semana)", padding=8, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        g = ttk.Frame(box)
        g.pack(fill="x")
        heads = ["Categoría", "No.", "Pregunta", "Pts"] + [f"S{i}" for i in range(1, SEMANAS + 1)]
        for c, h in enumerate(heads):
            ttk.Label(g, text=h, style="TH.TLabel", anchor="center").grid(row=0, column=c, sticky="nsew", padx=1, pady=1)
        self.vars = {}
        self.cat_rows = {}
        r = 1
        cats = []
        for q in self.preguntas:
            if q["categoria"] not in cats:
                cats.append(q["categoria"])
        for cat in cats:
            qs = [q for q in self.preguntas if q["categoria"] == cat]
            ttk.Label(g, text=cat, style="Group.TLabel", wraplength=110).grid(row=r, column=0, rowspan=len(qs), sticky="nw", padx=4)
            for q in qs:
                ttk.Label(g, text=str(q["n"])).grid(row=r, column=1, sticky="n")
                sub = f"[{q['subcategoria']}] " if q.get("subcategoria") and q["subcategoria"] != cat else ""
                ttk.Label(g, text=sub + q["pregunta"], wraplength=430, justify="left").grid(row=r, column=2, sticky="w", padx=4, pady=1)
                ttk.Label(g, text=str(q["puntos"]), anchor="center").grid(row=r, column=3)
                for w in range(SEMANAS):
                    v = tk.BooleanVar(value=False)
                    ttk.Checkbutton(g, variable=v, command=self._recalc).grid(row=r, column=4 + w)
                    self.vars[(q["n"], w)] = v
                r += 1
            lbls = []
            ttk.Label(g, text=f"Subtotal {cat}", style="Help.TLabel").grid(row=r, column=2, sticky="e", padx=4)
            ttk.Label(g, text=str(sum(q["puntos"] for q in qs)), style="Help.TLabel").grid(row=r, column=3)
            for w in range(SEMANAS):
                lb = ttk.Label(g, text="0", style="Help.TLabel", anchor="center")
                lb.grid(row=r, column=4 + w)
                lbls.append(lb)
            self.cat_rows[cat] = (qs, lbls)
            ttk.Separator(g).grid(row=r + 1, column=0, columnspan=len(heads), sticky="ew", pady=3)
            r += 2
        ttk.Label(g, text="TOTAL", font=("Segoe UI", 10, "bold")).grid(row=r, column=2, sticky="e", padx=4)
        ttk.Label(g, text="100", font=("Segoe UI", 10, "bold")).grid(row=r, column=3)
        self.total_lbls = []
        for w in range(SEMANAS):
            lb = tk.Label(g, text="0", font=("Segoe UI", 10, "bold"), width=4, relief="solid", borderwidth=1)
            lb.grid(row=r, column=4 + w, padx=1)
            self.total_lbls.append(lb)
        r += 1
        ttk.Label(g, text="Objetivo (editable)").grid(row=r, column=2, sticky="e", padx=4)
        self.obj_vars = []
        for w in range(SEMANAS):
            v = tk.StringVar(value=str(OBJETIVO_DEFECTO[w]))
            ttk.Entry(g, textvariable=v, width=4, justify="center").grid(row=r, column=4 + w, padx=1)
            v.trace_add("write", lambda *a: self._recalc())
            self.obj_vars.append(v)
        g.columnconfigure(2, weight=1)

        self.acciones = TableSection(inner, {"key": "acciones", "title": "Registro de acciones de la auditoría", "rows": 3,
                                             "columns": [{"key": "elemento", "label": "Elemento de la auditoría (cero puntos)", "width": 50},
                                                         {"key": "sugeridas", "label": "Acciones sugeridas", "width": 30},
                                                         {"key": "plan", "label": "Plan de acción (resp./fecha)", "width": 24}]},
                                     self.mark_dirty)
        self.acciones.frame.pack(fill="x", pady=6)
        sem = ttk.Frame(self.acciones.extra_bar)
        sem.pack(side="left", padx=12)
        ttk.Label(sem, text="Generar desde la semana:").pack(side="left")
        self.sem_var = tk.StringVar(value="1")
        ttk.Combobox(sem, textvariable=self.sem_var, values=[str(i) for i in range(1, SEMANAS + 1)], width=4,
                     state="readonly").pack(side="left", padx=4)
        ttk.Button(sem, text="Agregar preguntas con cero puntos", command=self.generar_acciones).pack(side="left")
        self._recalc()

    # ---------------------------------------------------------------------
    def week_total(self, w):
        return sum(q["puntos"] for q in self.preguntas if self.vars[(q["n"], w)].get())

    def _recalc(self):
        for cat, (qs, lbls) in self.cat_rows.items():
            for w, lb in enumerate(lbls):
                lb.configure(text=str(sum(q["puntos"] for q in qs if self.vars[(q["n"], w)].get())))
        for w, lb in enumerate(self.total_lbls):
            t = self.week_total(w)
            obj = to_float(self.obj_vars[w].get())
            used = any(self.vars[(q["n"], w)].get() for q in self.preguntas)
            color = "white" if not used or obj is None else ("#C6EFCE" if t >= obj else "#F8CBAD")
            lb.configure(text=str(t), background=color)
        self.mark_dirty()

    def generar_acciones(self):
        w = int(self.sem_var.get()) - 1
        existentes = {r["elemento"] for r in self.acciones.values()}
        rows = self.acciones.nonempty_values()
        for q in self.preguntas:
            if not self.vars[(q["n"], w)].get():
                el = f"{q['n']}. {q['pregunta']} ({q['puntos']} pts)"
                if el not in existentes:
                    rows.append({"elemento": el, "sugeridas": "", "plan": ""})
        self.acciones.set(rows)
        self.mark_dirty()

    # ---------------------------------------------------------------------
    def get_state(self):
        return {"datos": self.datos.get(),
                "marcas": [f"{n}-{w}" for (n, w), v in self.vars.items() if v.get()],
                "objetivo": [v.get() for v in self.obj_vars],
                "acciones": self.acciones.get()}

    def set_state(self, state):
        state = state or {}
        self.datos.set(state.get("datos"))
        marcas = set(state.get("marcas", []))
        for (n, w), v in self.vars.items():
            v.set(f"{n}-{w}" in marcas)
        obj = state.get("objetivo") or [str(x) for x in OBJETIVO_DEFECTO]
        for v, o in zip(self.obj_vars, obj):
            v.set(o)
        self.acciones.set(state.get("acciones"))
        self._recalc()

    def blocks(self):
        out = self.datos.blocks()
        rows = []
        for q in self.preguntas:
            rows.append([q["categoria"], q["n"], q["pregunta"], q["puntos"]] +
                        ["X" if self.vars[(q["n"], w)].get() else "" for w in range(SEMANAS)])
        rows.append(["", "", "TOTAL", 100] + [self.week_total(w) for w in range(SEMANAS)])
        rows.append(["", "", "Objetivo", ""] + [v.get() for v in self.obj_vars])
        hl = {}
        out.append({"type": "table", "title": "Cuestionario de auditoría",
                    "headers": ["Categoría", "No.", "Pregunta", "Pts"] + [f"S{i}" for i in range(1, SEMANAS + 1)],
                    "rows": rows, "highlight": hl})
        out.extend(self.acciones.blocks())
        return out
