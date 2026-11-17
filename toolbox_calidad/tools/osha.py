"""Registro de accidentes OSHA 300, resumen 300A e índices de accidentabilidad."""
from tkinter import ttk

from toolbox_calidad.core.calc import indices_osha, to_float
from toolbox_calidad.ui.base import FormTool

CLASES = ["Muerte (G)", "Días fuera del trabajo (H)", "Trabajo transferido o restringido (I)", "Otro caso registrable (J)"]
TIPOS = ["Lesión", "Desorden de la piel", "Condición respiratoria", "Envenenamiento", "Pérdida de la audición", "Otras enfermedades"]


def _fmt(v):
    return "—" if v is None else f"{v:.2f}"


class OshaTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "osha", "title": "Registro de accidentes OSHA 300 / 300A e índices", "code": "OSHA 300 · 300A",
            "source": "Registro Accidentes OSHA.xls · Registro Accidentes OSHA_Parte 1.xls",
            "description": "Registro de lesiones y enfermedades de trabajo (formulario OSHA 300), resumen anual (300A) "
                           "calculado automáticamente e índices por 200 000 horas: TRIR, DART, LWIR, LWSR y OSHA SR.",
            "intro": "Nota: TRIR se calcula con todos los casos registrables (G+H+I+J), como lo define OSHA. "
                     "La hoja original sumaba sólo H + J.",
            "sections": [
                {"type": "fields", "key": "datos", "title": "Establecimiento", "columns": 3, "fields": [
                    {"key": "nombre", "label": "Nombre del establecimiento", "width": 30}, {"key": "anio", "label": "Año"},
                    {"key": "direccion", "label": "Dirección"}, {"key": "ciudad", "label": "Ciudad"}, {"key": "estado", "label": "Estado"},
                    {"key": "fuerza", "label": "Fuerza de trabajo (promedio)"},
                    {"key": "horas", "label": "Horas trabajadas en el año", "bold": True}]},
                {"type": "table", "key": "casos", "title": "Formulario OSHA 300 — registro de casos", "rows": 5, "columns": [
                    {"key": "caso", "label": "(A) No. caso", "width": 6}, {"key": "nombre", "label": "(B) Empleado", "width": 16},
                    {"key": "ocupacion", "label": "(C) Ocupación", "width": 12}, {"key": "fecha", "label": "(D) Fecha", "width": 10},
                    {"key": "donde", "label": "(E) ¿Dónde ocurrió?", "width": 12},
                    {"key": "desc", "label": "(F) Lesión, parte del cuerpo y objeto/sustancia", "width": 24},
                    {"key": "clase", "label": "Clasificación", "width": 22, "options": CLASES},
                    {"key": "dias_fuera", "label": "(K) Días fuera", "width": 6},
                    {"key": "dias_restr", "label": "(L) Días restringido", "width": 7},
                    {"key": "tipo", "label": "(M) Tipo", "width": 16, "options": TIPOS}],
                 "highlight": lambda r: {"Muerte (G)": "rojo", "Días fuera del trabajo (H)": "ambar"}.get(r.get("clase"))},
                {"type": "fields", "key": "otros", "title": "Otros eventos del año (para índices)", "columns": 3, "fields": [
                    {"key": "cambio", "label": "Casos con cambio de actividad"}, {"key": "primeros", "label": "Primeros auxilios"},
                    {"key": "serias", "label": "Lesiones serias"}, {"key": "incidentes", "label": "Incidentes / casi accidentes"},
                    {"key": "alto_pot", "label": "Incidentes de alto potencial"}, {"key": "trayecto", "label": "Accidentes en trayecto"}]},
            ],
        }
        super().__init__(master, schema)

    def after_build(self):
        box = ttk.LabelFrame(self.scroll.inner, text="Resumen 300A e índices de accidentabilidad (automático)",
                             padding=8, style="Sec.TLabelframe")
        box.pack(fill="x", pady=6)
        self.res = ttk.Label(box, text="", justify="left", font=("Consolas", 10))
        self.res.pack(anchor="w")
        self.on_change()

    def resumen(self):
        rows = self.sections["casos"].nonempty_values()
        cnt = {c: sum(1 for r in rows if r.get("clase") == c) for c in CLASES}
        tipos = {t: sum(1 for r in rows if r.get("tipo") == t) for t in TIPOS}
        dias_fuera = sum(to_float(r.get("dias_fuera"), 0) for r in rows)
        dias_restr = sum(to_float(r.get("dias_restr"), 0) for r in rows)
        horas = self.sections["datos"]["horas"]
        idx = indices_osha(muertes=cnt[CLASES[0]], casos_dias_perdidos=cnt[CLASES[1]],
                           casos_restringidos=cnt[CLASES[2]], otros_registrables=cnt[CLASES[3]],
                           dias_perdidos=dias_fuera, dias_restringidos=dias_restr,
                           casos_cambio_actividad=to_float(self.sections["otros"]["cambio"], 0), horas=horas)
        return cnt, tipos, dias_fuera, dias_restr, idx

    def on_change(self):
        if not hasattr(self, "res"):
            return
        cnt, tipos, df, dr, idx = self.resumen()
        lines = ["Número de casos:  " + "   ".join(f"{k.split('(')[1][:-1]}={v}" for k, v in cnt.items()),
                 f"Días fuera del trabajo (K) = {df:g}    Días de trabajo restringido (L) = {dr:g}",
                 "Tipos (M):  " + " · ".join(f"{k}: {v}" for k, v in tipos.items()), "",
                 f"TRIR    = {_fmt(idx['TRIR'])}     casos registrables × 200 000 / horas",
                 f"DART    = {_fmt(idx['DART'])}     (H + I + cambio de actividad) × 200 000 / horas",
                 f"LWIR    = {_fmt(idx['LWIR'])}     casos con días perdidos × 200 000 / horas",
                 f"LWSR    = {_fmt(idx['LWSR'])}     días perdidos × 200 000 / horas",
                 f"OSHA SR = {_fmt(idx['OSHA SR'])}     (días perdidos + días restringidos) × 200 000 / horas"]
        if not to_float(self.sections["datos"]["horas"]):
            lines.append("\nCaptura las horas trabajadas para calcular los índices.")
        self.res.configure(text="\n".join(lines))

    def extra_blocks(self):
        cnt, tipos, df, dr, idx = self.resumen()
        return [
            {"type": "kv", "title": "Resumen OSHA 300A",
             "pairs": [(k, v) for k, v in cnt.items()] + [("Días fuera del trabajo (K)", df), ("Días restringidos (L)", dr)]
                      + [(k, v) for k, v in tipos.items()]},
            {"type": "table", "title": "Índices de accidentabilidad (por 200 000 h)", "headers": ["Índice", "Valor", "Fórmula"],
             "rows": [["TRIR", _fmt(idx["TRIR"]), "Casos registrables × 200 000 / horas"],
                      ["DART", _fmt(idx["DART"]), "(H + I + cambio de actividad) × 200 000 / horas"],
                      ["LWIR", _fmt(idx["LWIR"]), "Casos con días perdidos × 200 000 / horas"],
                      ["LWSR", _fmt(idx["LWSR"]), "Días perdidos × 200 000 / horas"],
                      ["OSHA SR", _fmt(idx["OSHA SR"]), "(Días perdidos + restringidos) × 200 000 / horas"]]}]
