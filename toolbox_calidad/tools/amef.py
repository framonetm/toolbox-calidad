"""AMEF / FMEA con cálculo automático de RPN, umbral de acción y escalas de referencia."""
import tkinter as tk
from tkinter import ttk

from toolbox_calidad.core.calc import rpn, to_float
from toolbox_calidad.ui.base import FormTool

SEVERIDAD = [
    (10, "Peligroso sin alerta", "El modo de falla afecta la operación del sistema sin aviso"),
    (9, "Peligroso con alerta", "El modo de falla afecta la operación del sistema con aviso"),
    (8, "Muy alto", "Sistema inoperable con daños destructivos"),
    (7, "Alto", "Sistema inoperable con equipo dañado"),
    (6, "Moderado", "Sistema inoperable con daños menores"),
    (5, "Bajo", "Sistema inoperable sin daños"),
    (4, "Muy bajo", "Sistema operable con degradación significativa del rendimiento"),
    (3, "Menor", "Sistema operable con alguna degradación del rendimiento"),
    (2, "Muy menor", "Sistema operable con mínima interferencia"),
    (1, "Ninguno", "Sin efecto"),
]
OCURRENCIA = [
    (10, "Muy alta: fallas casi inevitables", "> 1 en 2"), (9, "Muy alta", "1 en 3"),
    (8, "Alta: fallas repetitivas", "1 en 8"), (7, "Alta", "1 en 20"),
    (6, "Moderada: fallas ocasionales", "1 en 80"), (5, "Moderada", "1 en 400"), (4, "Moderada", "1 en 2 000"),
    (3, "Baja: relativamente pocas fallas", "1 en 15 000"), (2, "Baja", "1 en 150 000"),
    (1, "Remota: falla improbable", "< 1 en 1 500 000"),
]
DETECCION = [
    (10, "Incertidumbre absoluta", "El control no puede detectar la causa/modo de falla"),
    (9, "Muy remota", "Probabilidad muy remota de detección"), (8, "Remota", "Probabilidad remota de detección"),
    (7, "Muy baja", "Probabilidad muy baja de detección"), (6, "Baja", "Probabilidad baja de detección"),
    (5, "Moderada", "Probabilidad moderada de detección"), (4, "Moderadamente alta", "Probabilidad moderadamente alta"),
    (3, "Alta", "Probabilidad alta de detección"), (2, "Muy alta", "Probabilidad muy alta de detección"),
    (1, "Casi segura", "El control detectará casi con certeza la causa/modo de falla"),
]
ESCALA = [str(i) for i in range(1, 11)]


def _rpn(s, o, d):
    try:
        return rpn(s, o, d)
    except ValueError:
        return "fuera de 1-10"


class AmefTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "amef", "title": "AMEF / FMEA — Análisis de modo y efecto de falla", "code": "AMEF",
            "source": "009 AMEF-FORMATO Y CONTROL DE AYUDA.xls",
            "description": "Identifica modos de falla potenciales y su impacto, prioriza con el RPN = Severidad × "
                           "Ocurrencia × Detección y da seguimiento a las acciones (nuevo RPN). Las filas cuyo RPN "
                           "supera el umbral o cuya severidad es ≥ 9 se resaltan. Actualiza el AMEF periódicamente.",
            "intro": "Ejemplo del formato original: Contención de líquido refrigerante / conexión de manguera → modo: "
                     "rotura o grieta → efecto: goteo (S=8) → causa: sobrepresión (O=8) → control: validación del ciclo "
                     "de presión (D=1) → RPN 64.",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Encabezado", "columns": 3, "fields": [
                    {"key": "tipo", "label": "Tipo de AMEF", "options": ["Proceso", "Diseño", "Sistema", "Servicio"]},
                    {"key": "numero", "label": "AMEF número"}, {"key": "sistema", "label": "Sistema"},
                    {"key": "subsistema", "label": "Subsistema"}, {"key": "componente", "label": "Componente / proceso"},
                    {"key": "elaboro", "label": "Elaborado por"}, {"key": "disenador", "label": "Responsable de diseño/proceso"},
                    {"key": "fecha", "label": "Fecha AMEF", "kind": "date", "default": "hoy"},
                    {"key": "revision", "label": "Fecha de revisión"}, {"key": "equipo", "label": "Equipo de análisis", "width": 34},
                    {"key": "umbral", "label": "Umbral de acción RPN", "default": "100"}]},
                {"type": "table", "key": "amef", "title": "Análisis", "rows": 6,
                 "columns": [
                     {"key": "funcion", "label": "Parte / función", "width": 18},
                     {"key": "modo", "label": "Modo(s) potencial(es) de falla", "width": 18},
                     {"key": "efecto", "label": "Efecto(s) potencial(es)", "width": 16},
                     {"key": "s", "label": "Sev", "width": 4, "options": ESCALA},
                     {"key": "causa", "label": "Causa(s) potencial(es)", "width": 16},
                     {"key": "o", "label": "Ocu", "width": 4, "options": ESCALA},
                     {"key": "control", "label": "Controles actuales", "width": 16},
                     {"key": "d", "label": "Det", "width": 4, "options": ESCALA},
                     {"key": "rpn", "label": "RPN", "width": 6, "compute": lambda r: _rpn(r["s"], r["o"], r["d"])},
                     {"key": "accion", "label": "Acción(es) recomendada(s)", "width": 18},
                     {"key": "resp", "label": "Responsable y fecha", "width": 13},
                     {"key": "tomada", "label": "Acción(es) tomada(s)", "width": 16},
                     {"key": "s2", "label": "N. Sev", "width": 4, "options": ESCALA},
                     {"key": "o2", "label": "N. Ocu", "width": 4, "options": ESCALA},
                     {"key": "d2", "label": "N. Det", "width": 4, "options": ESCALA},
                     {"key": "rpn2", "label": "Nuevo RPN", "width": 6, "compute": lambda r: _rpn(r["s2"], r["o2"], r["d2"])}],
                 "highlight": self._highlight, "summary": self._summary},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        bar = self.sections["amef"].extra_bar
        ttk.Button(bar, text="Ordenar por RPN ↓", command=self.sort_rpn).pack(side="left", padx=6)
        ttk.Button(bar, text="Ver escalas S / O / D", command=self.show_scales).pack(side="left")

    def _umbral(self):
        try:
            return to_float(self.sections["datos"]["umbral"], 100) or 100
        except Exception:
            return 100

    def _highlight(self, r):
        val = to_float(r.get("rpn"))
        new = to_float(r.get("rpn2"))
        if val is None:
            return None
        if new is not None and new < self._umbral():
            return "verde"
        if val >= self._umbral() or (to_float(r.get("s"), 0) >= 9):
            return "rojo"
        if val >= self._umbral() / 2:
            return "ambar"
        return None

    def _summary(self, rows):
        vals = [to_float(r.get("rpn")) for r in rows]
        vals = [v for v in vals if v is not None]
        if not vals:
            return "Captura S, O y D para calcular el RPN"
        criticos = sum(1 for v in vals if v >= self._umbral())
        return f"Modos evaluados: {len(vals)} · RPN máx: {max(vals):.0f} · Sobre el umbral: {criticos}"

    def on_change(self):
        if "amef" in getattr(self, "sections", {}):
            self.sections["amef"].refresh()

    def sort_rpn(self):
        sec = self.sections["amef"]
        rows = sec.values()
        rows.sort(key=lambda r: to_float(r.get("rpn"), -1), reverse=True)
        sec.set(rows)
        self.mark_dirty()

    def show_scales(self):
        win = tk.Toplevel(self)
        win.title("Escalas de severidad, ocurrencia y detección")
        win.geometry("820x520")
        nb = ttk.Notebook(win)
        nb.pack(fill="both", expand=True, padx=8, pady=8)
        for name, data, cols in (("Severidad", SEVERIDAD, ("Valor", "Efecto", "Criterio")),
                                 ("Ocurrencia", OCURRENCIA, ("Valor", "Probabilidad de falla", "Tasa")),
                                 ("Detección", DETECCION, ("Valor", "Detección", "Criterio"))):
            fr = ttk.Frame(nb)
            nb.add(fr, text=name)
            tv = ttk.Treeview(fr, columns=("c0", "c1", "c2"), show="headings", height=11)
            for i, (c, w) in enumerate(zip(cols, (60, 240, 460))):
                tv.heading(f"c{i}", text=c)
                tv.column(f"c{i}", width=w, anchor="center" if i == 0 else "w")
            for row in data:
                tv.insert("", "end", values=row)
            tv.pack(fill="both", expand=True)

    def extra_blocks(self):
        return [{"type": "table", "title": "Escala de severidad", "headers": ["Valor", "Efecto", "Criterio"],
                 "rows": [list(r) for r in SEVERIDAD]},
                {"type": "table", "title": "Escala de ocurrencia", "headers": ["Valor", "Probabilidad", "Tasa"],
                 "rows": [list(r) for r in OCURRENCIA]},
                {"type": "table", "title": "Escala de detección", "headers": ["Valor", "Detección", "Criterio"],
                 "rows": [list(r) for r in DETECCION]}]
