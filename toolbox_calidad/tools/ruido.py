"""Programa de conservación de la audición (NOM-011-STPS-2001) con cálculos de dosimetría."""
from toolbox_calidad.core.calc import clasificar_ner, ner_desde_dosis, nre, tmpe_horas, to_float
from toolbox_calidad.forms.mejora import MESES
from toolbox_calidad.ui.base import FormTool


def _ner_hl(key):
    def f(r):
        v = to_float(r.get(key))
        if v is None:
            return None
        return "rojo" if v >= 90 else ("ambar" if v >= 85 else ("verde" if v < 80 else None))
    return f


def _fmt_h(h):
    if h is None:
        return None
    return f"{h:.2f} h" if h >= 1 else f"{h * 60:.0f} min"


INSTRUMENTOS = {"type": "table", "rows": 2, "columns": [
    {"key": "instrumento", "label": "Instrumento", "width": 20}, {"key": "marca", "label": "Marca", "width": 14},
    {"key": "serie", "label": "No. de serie", "width": 14}, {"key": "certificado", "label": "Certificado de calibración", "width": 20},
    {"key": "obs", "label": "Observaciones", "width": 20}]}


class RuidoTool(FormTool):
    def __init__(self, master):
        schema = {
            "id": "ruido", "title": "Programa de conservación de la audición (NOM-011-STPS)", "code": "NOM-011-STPS-2001",
            "source": "Programa de Conservación de la Audición.xls",
            "description": "Reconocimiento, evaluación del NER y NPA, equipo de protección personal, capacitación, "
                           "vigilancia a la salud y medidas de control. Calcula NER = 90 + 9.97·log(D/(12.5·T)) y "
                           "TMPE = 8 / 2^((NER−90)/3) a partir de la dosis, y NRE = NER − R con protector. "
                           "Conserva este documento al menos 5 años.",
            "intro": "Colores: rojo ≥ 90 dB(A) (LMPE a 8 h) · ámbar ≥ 85 dB(A) (vigilancia médica anual) · "
                     "verde < 80 dB(A). Repite el reconocimiento cada dos años o dentro de los 90 días posteriores a un "
                     "cambio de producción, procesos, equipos o controles.",
            "sections": [
                {"type": "fields", "key": "portada", "title": "Centro de trabajo", "columns": 2, "fields": [
                    {"key": "centro", "label": "Nombre del centro de trabajo", "width": 40},
                    {"key": "direccion", "label": "Dirección", "width": 40},
                    {"key": "responsable", "label": "Responsable del programa"},
                    {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"}]},
                {"type": "table", "key": "reconocimiento", "title": "1. Reconocimiento inicial", "rows": 4, "columns": [
                    {"key": "area", "label": "Área", "width": 16}, {"key": "fuentes", "label": "Fuente(s) emisora(s)", "width": 22},
                    {"key": "t1", "label": "Trab. 1T", "width": 6}, {"key": "t2", "label": "Trab. 2T", "width": 6},
                    {"key": "t3", "label": "Trab. 3T", "width": 6}, {"key": "otro", "label": "Otro", "width": 6},
                    {"key": "total", "label": "Total", "width": 6,
                     "compute": lambda r: int(sum(to_float(r[k], 0) for k in ("t1", "t2", "t3", "otro"))) or ""},
                    {"key": "nsa", "label": "NSA dB(A)", "width": 8}, {"key": "fecha", "label": "Última evaluación", "width": 11},
                    {"key": "resp", "label": "Responsable", "width": 14}, {"key": "obs", "label": "Observaciones", "width": 16}],
                 "highlight": _ner_hl("nsa")},
                dict(INSTRUMENTOS, key="instrumentos", title="2. Evaluación del NER — instrumentos empleados"),
                {"type": "fields", "key": "evaluador", "title": "Responsable de la medición", "columns": 2, "fields": [
                    {"key": "nombre", "label": "Responsable"}, {"key": "acreditacion", "label": "Acreditación"},
                    {"key": "fecha", "label": "Fecha de evaluación"}, {"key": "vigencia", "label": "Vigencia de acreditación"}]},
                {"type": "table", "key": "dosimetria", "title": "2.1 Evaluación personal por dosimetría", "rows": 5, "columns": [
                    {"key": "nombre", "label": "Trabajador", "width": 20}, {"key": "puesto", "label": "Puesto / punto", "width": 16},
                    {"key": "instrumento", "label": "Instrumento", "width": 10},
                    {"key": "tiempo", "label": "Tiempo de medición (h)", "width": 9},
                    {"key": "dosis", "label": "Dosis (%)", "width": 8},
                    {"key": "ner", "label": "NER dB(A)", "width": 8,
                     "compute": lambda r: ner_desde_dosis(r["dosis"], r["tiempo"])},
                    {"key": "tmpe", "label": "TMPE", "width": 9,
                     "compute": lambda r: _fmt_h(tmpe_horas(ner_desde_dosis(r["dosis"], r["tiempo"])))},
                    {"key": "accion", "label": "Clasificación", "width": 34,
                     "compute": lambda r: clasificar_ner(ner_desde_dosis(r["dosis"], r["tiempo"]))}],
                 "highlight": _ner_hl("ner")},
                {"type": "table", "key": "ner_puntos", "title": "2.2 NER por punto (resultado de estudio)", "rows": 3, "columns": [
                    {"key": "punto", "label": "Identificación del punto", "width": 22},
                    {"key": "metodo", "label": "Método de evaluación", "width": 18,
                     "options": ["Dosimetría", "Sonómetro (NSA)", "Ruido estable", "Ruido inestable", "Ruido impulsivo"]},
                    {"key": "ner", "label": "NER dB(A)", "width": 8}, {"key": "lmpe", "label": "LMPE dB(A)", "width": 8, "default": "90"},
                    {"key": "resultado", "label": "Resultado", "width": 12,
                     "compute": lambda r: "" if to_float(r["ner"]) is None else
                     ("Excede" if to_float(r["ner"]) > to_float(r["lmpe"], 90) else "Dentro")},
                    {"key": "tmpe", "label": "TMPE", "width": 9, "compute": lambda r: _fmt_h(tmpe_horas(r["ner"]))},
                    {"key": "obs", "label": "Observaciones", "width": 20}],
                 "highlight": _ner_hl("ner")},
                {"type": "table", "key": "npa", "title": "3. Nivel de presión acústica por bandas de octava (dB)", "rows": 3, "columns": [
                    {"key": "punto", "label": "Punto", "width": 14}, {"key": "area", "label": "Área", "width": 12}] +
                    [{"key": f"f{f}", "label": f"{f} Hz", "width": 6} for f in ("31.5", "63", "125", "250", "500", "1k", "2k", "4k", "8k")] +
                    [{"key": "ref", "label": "Referencia", "width": 10}]},
                {"type": "table", "key": "epp", "title": "4. Equipo de protección personal auditiva", "rows": 3, "columns": [
                    {"key": "punto", "label": "Punto", "width": 18}, {"key": "epp", "label": "Descripción del EPP", "width": 24},
                    {"key": "ner", "label": "NER dB(A)", "width": 8}, {"key": "r", "label": "R (factor de reducción) dB(A)", "width": 10},
                    {"key": "nre", "label": "NRE dB(A)", "width": 8, "compute": lambda r: nre(r["ner"], r["r"])},
                    {"key": "obs", "label": "Observaciones", "width": 20}],
                 "highlight": _ner_hl("nre")},
                {"type": "table", "key": "procedimientos", "title": "4.1 EPP — registro de procedimientos", "rows": 0,
                 "default_rows": [{"proc": p} for p in (
                     "Selección técnica y médica",
                     "Capacitación en uso, mantenimiento, limpieza, cuidado, reemplazo y limitaciones",
                     "Supervisión de su uso por parte de los trabajadores")],
                 "columns": [{"key": "proc", "label": "Procedimiento", "width": 50}, {"key": "clave", "label": "Clave", "width": 12},
                             {"key": "fecha", "label": "Fecha de revisión", "width": 12}, {"key": "obs", "label": "Observaciones", "width": 22}]},
                {"type": "table", "key": "capacitacion", "title": "5. Cronograma de capacitación (marca X)", "rows": 0,
                 "default_rows": [{"tema": t} for t in ("El ruido y sus efectos a la salud", "Niveles máximos permisibles de exposición",
                                                        "Medidas de control y protección", "Uso de equipo de protección personal")],
                 "columns": [{"key": "tema", "label": "Tema", "width": 34}] +
                            [{"key": m.lower(), "label": m, "width": 3, "options": ["", "X"]} for m in MESES]},
                {"type": "text", "key": "vigilancia", "title": "6. Vigilancia a la salud (exámenes anuales a expuestos ≥ 85 dB(A)): "
                 "historial otológico, antecedentes, exploración ORL y audiometría tonal", "height": 4},
                {"type": "table", "key": "control", "title": "7. Medidas de control adoptadas", "rows": 0,
                 "default_rows": [{"tipo": "Técnica", "medida": m} for m in (
                     "Mantenimiento preventivo y correctivo de las fuentes generadoras de ruido",
                     "Sustitución o modificación de equipos o procesos", "Reducción de las fuerzas generadoras del ruido",
                     "Modificar los componentes de frecuencia con mayor posibilidad de daño",
                     "Distribución planificada y adecuada del equipo en la planta",
                     "Acondicionamiento acústico de las superficies interiores de los recintos",
                     "Cabinas, envolventes o barreras entre fuentes y receptores",
                     "Tratamiento de trayectorias de propagación (aislamiento de máquinas)")] +
                                 [{"tipo": "Administrativa", "medida": m} for m in (
                     "Manejo de los tiempos de exposición", "Programación de la producción", "Otros métodos administrativos")],
                 "columns": [{"key": "tipo", "label": "Tipo", "width": 13}, {"key": "medida", "label": "Medida", "width": 52},
                             {"key": "area", "label": "Área o lugar de implementación", "width": 24},
                             {"key": "eval", "label": "Evaluación de eficacia (≤ 30 días)", "width": 20}]},
            ],
        }
        super().__init__(master, schema)
