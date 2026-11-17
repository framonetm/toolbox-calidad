"""Calculadoras: ventilación (cambios de aire), Pareto y capacidad de proceso."""
import tkinter as tk
from tkinter import ttk

from toolbox_calidad.core import calc
from toolbox_calidad.core.calc import to_float
from toolbox_calidad.ui.base import FormTool
from toolbox_calidad.ui.charts import Chart


def _f(v, nd=2):
    return "—" if v is None else f"{v:,.{nd}f}"


# ---------------------------------------------------------------------------
class VentilacionTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "ventilacion_calc", "title": "Ventilación — cálculo de cambios de aire por hora", "code": "N = Q·60 / Vol",
            "source": "VENTILACIÓN - Cálculo del Número de Recambios Por Hora.xls",
            "description": "Calcula los cambios de aire por hora de un cuarto (N = Q × 60 / Vol, con Q en ft³/min y Vol "
                           "en ft³) y el caudal necesario para lograr un número de cambios objetivo. Referencia: el "
                           "almacén cerrado de residuos peligrosos con ventilación forzada requiere ≥ 6 cambios/h "
                           "(RLGPGIR Art. 82 fr. II c).",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Datos del espacio", "columns": 3, "fields": [
                    {"key": "espacio", "label": "Espacio / cuarto", "width": 30},
                    {"key": "l1", "label": "Largo L1 (m)"}, {"key": "l2", "label": "Ancho L2 (m)"}, {"key": "l3", "label": "Alto L3 (m)"},
                    {"key": "vol_m3", "label": "o volumen directo (m³)"},
                    {"key": "q", "label": "Caudal Q del extractor"},
                    {"key": "q_unidad", "label": "Unidad de Q", "options": ["ft³/min (CFM)", "m³/h"], "default": "ft³/min (CFM)"},
                    {"key": "n_obj", "label": "Cambios/h objetivo", "default": "6"}]},
                {"type": "table", "key": "equipos", "title": "Varios extractores (opcional: se suman a Q)", "rows": 2, "columns": [
                    {"key": "equipo", "label": "Equipo", "width": 24}, {"key": "cfm", "label": "Caudal (ft³/min)", "width": 12}]},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        box = ttk.LabelFrame(self.scroll.inner, text="Resultado", padding=10, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        self.res = ttk.Label(box, text="", font=("Segoe UI", 12), justify="left")
        self.res.pack(anchor="w")
        self.on_change()

    def calcular(self):
        d = self.sections["datos"]
        vol_m3 = to_float(d["vol_m3"])
        if vol_m3 is None:
            dims = [to_float(d[k]) for k in ("l1", "l2", "l3")]
            vol_m3 = dims[0] * dims[1] * dims[2] if all(x is not None for x in dims) else None
        vol_ft3 = vol_m3 * calc.M3_A_FT3 if vol_m3 is not None else None
        q = to_float(d["q"], 0.0)
        q_cfm = calc.m3h_a_cfm(q) if d["q_unidad"].startswith("m³") else q
        q_cfm += sum(to_float(r.get("cfm"), 0) for r in self.sections["equipos"].values())
        n = calc.cambios_aire_por_hora(q_cfm, vol_ft3) if q_cfm else None
        req = calc.caudal_requerido_cfm(d["n_obj"], vol_ft3) if vol_ft3 else None
        return {"vol_m3": vol_m3, "vol_ft3": vol_ft3, "q_cfm": q_cfm, "n": n, "req_cfm": req,
                "req_m3h": req * 60 / calc.M3_A_FT3 if req else None, "n_obj": to_float(d["n_obj"])}

    def on_change(self):
        if not hasattr(self, "res"):
            return
        r = self.calcular()
        txt = (f"Volumen: {_f(r['vol_m3'])} m³  =  {_f(r['vol_ft3'])} ft³\n"
               f"Caudal total: {_f(r['q_cfm'])} ft³/min\n"
               f"Cambios de aire por hora  N = {_f(r['n'])}\n"
               f"Caudal requerido para {_f(r['n_obj'], 0)} cambios/h: {_f(r['req_cfm'])} ft³/min  ({_f(r['req_m3h'])} m³/h)")
        if r["n"] is not None and r["n_obj"]:
            txt += "\n" + ("✔ Cumple el objetivo" if r["n"] >= r["n_obj"] else "✘ No alcanza el objetivo")
        self.res.configure(text=txt)

    def extra_blocks(self):
        r = self.calcular()
        return [{"type": "kv", "title": "Resultado", "pairs": [
            ("Volumen (m³)", _f(r["vol_m3"])), ("Volumen (ft³)", _f(r["vol_ft3"])), ("Caudal total (ft³/min)", _f(r["q_cfm"])),
            ("Cambios de aire por hora N", _f(r["n"])), ("Cambios/h objetivo", _f(r["n_obj"], 0)),
            ("Caudal requerido (ft³/min)", _f(r["req_cfm"])), ("Caudal requerido (m³/h)", _f(r["req_m3h"]))]},
            {"type": "note", "text": "Fórmula: N = Q × 60 / Vol (Q en ft³/min, Vol en ft³)."}]


# ---------------------------------------------------------------------------
class ParetoTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "pareto", "title": "Diagrama de Pareto", "code": "Pareto 80/20",
            "source": "Herramienta adicional (complementa la ficha de análisis de pérdida y el reporte de averías)",
            "description": "Ordena las categorías (pérdidas, averías, defectos, causas 4M) de mayor a menor y muestra el % "
                           "acumulado. Las barras oscuras son los «pocos vitales» que explican ~80 % del total.",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Datos", "columns": 2, "fields": [
                    {"key": "titulo", "label": "Título", "width": 40, "default": "Pareto de pérdidas"},
                    {"key": "unidad", "label": "Unidad (eventos, min, $…)", "default": "eventos"}]},
                {"type": "table", "key": "datos_tabla", "title": "Categorías", "rows": 8, "columns": [
                    {"key": "cat", "label": "Categoría", "width": 34}, {"key": "valor", "label": "Valor", "width": 12}]},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        box = ttk.LabelFrame(self.scroll.inner, text="Gráfica de Pareto", padding=8, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        self.chart = Chart(box, width=900, height=360)
        self.chart.pack()
        self.tabla = ttk.Label(box, text="", font=("Consolas", 9), justify="left")
        self.tabla.pack(anchor="w", pady=6)
        self.on_change()

    def resultado(self):
        return calc.pareto([(r["cat"], r["valor"]) for r in self.sections["datos_tabla"].values()
                            if r["cat"].strip() and to_float(r["valor"]) is not None])

    def on_change(self):
        if not hasattr(self, "chart"):
            return
        res = self.resultado()
        self.chart.pareto(self.sections["datos"]["titulo"], [r["categoria"] for r in res],
                          [r["valor"] for r in res], [r["acumulado"] for r in res])
        self.tabla.configure(text="\n".join(f"{r['categoria'][:30]:<30} {r['valor']:>10g} {r['pct']:>7.1f}% {r['acumulado']:>7.1f}%"
                                            for r in res))

    def extra_blocks(self):
        res = self.resultado()
        return [{"type": "table", "title": "Pareto ordenado", "headers": ["Categoría", "Valor", "%", "% acumulado"],
                 "rows": [[r["categoria"], r["valor"], round(r["pct"], 1), round(r["acumulado"], 1)] for r in res],
                 "highlight": {i: "ambar" for i, r in enumerate(res) if r["acumulado"] - r["pct"] < 80}}]


# ---------------------------------------------------------------------------
class CapacidadTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "capacidad", "title": "Capacidad de proceso (Cp, Cpk) y carta I-MR", "code": "SPC",
            "source": "Herramienta adicional de control estadístico",
            "description": "Pega los datos (uno por línea o separados por espacios/;) y los límites de especificación. "
                           "Calcula Cp/Cpk con σ dentro (rango móvil/1.128), Pp/Ppk con σ global, la carta de "
                           "individuales con límites ±3σ y el histograma frente a LIE/LSE.",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Característica", "columns": 3, "fields": [
                    {"key": "caract", "label": "Característica", "width": 30}, {"key": "unidad", "label": "Unidad"},
                    {"key": "lie", "label": "LIE"}, {"key": "nominal", "label": "Nominal"}, {"key": "lse", "label": "LSE"}]},
                {"type": "text", "key": "valores", "title": "Datos medidos (en orden de producción)", "height": 6},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        box = ttk.LabelFrame(self.scroll.inner, text="Resultados", padding=8, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        self.res = ttk.Label(box, text="", font=("Consolas", 10), justify="left")
        self.res.pack(anchor="w")
        charts = ttk.Frame(box)
        charts.pack(fill="x", pady=6)
        self.hist = Chart(charts, width=560, height=300)
        self.hist.pack(side="left", padx=(0, 8))
        self.ctrl = Chart(charts, width=560, height=300)
        self.ctrl.pack(side="left")
        self.on_change()

    def datos(self):
        txt = self.sections["valores"].get().replace(";", " ").replace("\t", " ")
        out = []
        for tok in txt.split():
            v = to_float(tok)
            if v is not None:
                out.append(v)
        return out

    def calcular(self):
        x = self.datos()
        d = self.sections["datos"]
        if len(x) < 2:
            return None, x
        try:
            return calc.capacidad(x, d["lie"], d["lse"]), x
        except ValueError:
            return None, x

    def on_change(self):
        if not hasattr(self, "res"):
            return
        r, x = self.calcular()
        d = self.sections["datos"]
        if not r:
            self.res.configure(text="Captura al menos 2 datos.")
            self.hist._empty("Histograma")
            self.ctrl._empty("Carta de individuales")
            return
        def g(v):
            return "—" if v is None else f"{v:.3f}"
        verdict = ""
        if r["Cpk"] is not None:
            verdict = ("capaz (Cpk ≥ 1.33)" if r["Cpk"] >= 1.33 else
                       "marginal (1.00 ≤ Cpk < 1.33)" if r["Cpk"] >= 1 else "no capaz (Cpk < 1.00)")
        self.res.configure(text=(
            f"n = {r['n']}   media = {g(r['media'])}   mín = {g(r['min'])}   máx = {g(r['max'])}\n"
            f"σ dentro = {g(r['sigma_dentro'])}   σ global = {g(r['sigma_global'])}\n"
            f"Cp = {g(r['Cp'])}   Cpk = {g(r['Cpk'])}   Pp = {g(r['Pp'])}   Ppk = {g(r['Ppk'])}   → {verdict}\n"
            f"Fuera de especificación: {r['fuera_especificacion']}   "
            f"Puntos fuera de control: {', '.join(map(str, r['fuera_control'])) or 'ninguno'}"))
        self.hist.histogram("Histograma", x, to_float(d["lie"]), to_float(d["lse"]))
        self.ctrl.control("Carta de individuales (I)", x, r["media"], r["LCS"], r["LCI"])

    def extra_blocks(self):
        r, x = self.calcular()
        if not r:
            return []
        return [{"type": "kv", "title": "Resultados", "pairs": [
            (k, round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "fuera_control"] +
            [("Puntos fuera de control", ", ".join(map(str, r["fuera_control"])) or "ninguno")]}]
