"""Indicador de prestación (KPI) con gráfica de tendencia contra punto de inicio y objetivo."""
from tkinter import ttk

from toolbox_calidad.core.calc import to_float
from toolbox_calidad.ui.base import FormTool
from toolbox_calidad.ui.charts import NARANJA, VERDE, Chart, AZUL_CLARO, ROJO


class KpiTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "kpi", "title": "Indicador de prestación (KPI)", "code": "F-GO-MT-013 Rev. 0",
            "source": "019 FORMATO INDICADOR DE PRESTACIÓN.xls",
            "description": "Seguimiento semanal de un indicador frente a su punto de inicio y su objetivo. "
                           "Las barras se colorean en verde cuando alcanzan el objetivo según el sentido del KPI.",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Definición del indicador", "columns": 3, "fields": [
                    {"key": "kpi", "label": "KPI", "width": 34}, {"key": "unidad", "label": "Unidad"},
                    {"key": "sentido", "label": "Sentido", "options": ["Mayor es mejor", "Menor es mejor"],
                     "default": "Mayor es mejor"},
                    {"key": "inicio", "label": "Punto de inicio"}, {"key": "objetivo", "label": "Objetivo"},
                    {"key": "grupo", "label": "Grupo / proyecto"}]},
                {"type": "table", "key": "valores", "title": "Valores por periodo", "rows": 0,
                 "default_rows": [{"periodo": f"Semana {i}"} for i in range(1, 17)],
                 "columns": [{"key": "periodo", "label": "Periodo", "width": 14},
                             {"key": "valor", "label": "Valor KPI", "width": 12},
                             {"key": "comentario", "label": "Comentario", "width": 40}],
                 "highlight": self._hl, "summary": self._summary},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        box = ttk.LabelFrame(self.scroll.inner, text="Gráfica", padding=8, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        self.chart = Chart(box, width=900, height=340)
        self.chart.pack()
        self.on_change()

    def _params(self):
        d = self.sections["datos"]
        return to_float(d["inicio"]), to_float(d["objetivo"]), d["sentido"] != "Menor es mejor"

    def _ok(self, v):
        _, obj, mayor = self._params()
        if v is None or obj is None:
            return None
        return v >= obj if mayor else v <= obj

    def _hl(self, r):
        ok = self._ok(to_float(r.get("valor")))
        return None if ok is None else ("verde" if ok else "rojo")

    def _summary(self, rows):
        vals = [to_float(r.get("valor")) for r in rows]
        vals = [v for v in vals if v is not None]
        if not vals:
            return ""
        ok = sum(1 for v in vals if self._ok(v))
        return f"Último: {vals[-1]:g} · Promedio: {sum(vals) / len(vals):.2f} · Periodos en objetivo: {ok}/{len(vals)}"

    def on_change(self):
        if not hasattr(self, "chart"):
            return
        sec = self.sections["valores"]
        rows = sec.values()
        labels = [r["periodo"] for r in rows]
        vals = [to_float(r["valor"]) for r in rows]
        ini, obj, _ = self._params()
        colors = [None if v is None else (VERDE if self._ok(v) else (ROJO if self._ok(v) is False else AZUL_CLARO))
                  for v in vals]
        lines = []
        if ini is not None:
            lines.append(("Punto de inicio", [ini] * len(rows), NARANJA, True))
        if obj is not None:
            lines.append(("Objetivo", [obj] * len(rows), "#00B050", True))
        title = self.sections["datos"]["kpi"] or "Indicador de prestación"
        unidad = self.sections["datos"]["unidad"]
        self.chart.bars_and_lines(title, labels, vals, lines, ylabel=unidad, bar_colors=colors)
        sec.refresh()
