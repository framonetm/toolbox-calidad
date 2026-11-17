"""Cálculos puros (sin interfaz) usados por las herramientas.

Todas las funciones son deterministas y están cubiertas por pruebas en
``tests/test_calc.py``. Las fórmulas de seguridad e higiene reproducen las
de las hojas de cálculo originales del repositorio; donde se corrigió algo,
se indica en el docstring.
"""
from __future__ import annotations

import math
import statistics
from typing import Iterable, Sequence

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------

def to_float(value, default=None):
    """Convierte texto con coma o punto decimal a float; ``default`` si no se puede."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", ".").replace("%", "")
    if not text:
        return default
    try:
        return float(text)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# AMEF / FMEA
# ---------------------------------------------------------------------------

def rpn(severidad, ocurrencia, deteccion):
    """Número de prioridad de riesgo RPN = S × O × D (cada uno de 1 a 10)."""
    vals = [to_float(v) for v in (severidad, ocurrencia, deteccion)]
    if any(v is None for v in vals):
        return None
    for v in vals:
        if not 1 <= v <= 10:
            raise ValueError("Severidad, ocurrencia y detección deben estar entre 1 y 10")
    s, o, d = vals
    return int(round(s * o * d))


# ---------------------------------------------------------------------------
# Ventilación
# ---------------------------------------------------------------------------
M3_A_FT3 = 35.3146667


def cambios_aire_por_hora(caudal_cfm, volumen_ft3):
    """N = Q × 60 / Vol  (Q en ft³/min, Vol en ft³). Fórmula del formato original."""
    q, v = to_float(caudal_cfm), to_float(volumen_ft3)
    if q is None or not v:
        return None
    return q * 60.0 / v


def caudal_requerido_cfm(cambios_hora, volumen_ft3):
    """Caudal necesario (ft³/min) para lograr N cambios de aire por hora."""
    n, v = to_float(cambios_hora), to_float(volumen_ft3)
    if n is None or v is None:
        return None
    return n * v / 60.0


def m3h_a_cfm(m3h):
    return to_float(m3h, 0.0) * M3_A_FT3 / 60.0


# ---------------------------------------------------------------------------
# Ruido — NOM-011-STPS-2001
# ---------------------------------------------------------------------------

def ner_desde_dosis(dosis_pct, tiempo_h):
    """NER = 90 + 9.97·log10(D / (12.5·T)).

    D = dosis en %, T = tiempo de medición en horas. Fórmula empleada en la hoja
    "Ejemplo - Dosimetría" del Programa de Conservación de la Audición.
    """
    d, t = to_float(dosis_pct), to_float(tiempo_h)
    if not d or not t or d <= 0 or t <= 0:
        return None
    return 90.0 + 9.97 * math.log10(d / (12.5 * t))


def tmpe_horas(ner):
    """Tiempo máximo permisible de exposición: TMPE = 8 / 2^((NER − 90)/3)."""
    n = to_float(ner)
    if n is None:
        return None
    return 8.0 / (2 ** ((n - 90.0) / 3.0))


def nre(ner, factor_reduccion):
    """Nivel de ruido efectivo con protector: NRE = NER − R."""
    n, r = to_float(ner), to_float(factor_reduccion)
    if n is None or r is None:
        return None
    return n - r


def clasificar_ner(ner):
    """Devuelve una etiqueta de acción según los umbrales citados en el programa."""
    n = to_float(ner)
    if n is None:
        return ""
    if n >= 90:
        return "≥ LMPE (90 dB(A) a 8 h): controles obligatorios"
    if n >= 85:
        return "≥ 85 dB(A): vigilancia médica anual"
    if n >= 80:
        return "≥ 80 dB(A): programa de conservación y capacitación"
    return "< 80 dB(A)"


# ---------------------------------------------------------------------------
# Accidentabilidad — OSHA 300 / 300A
# ---------------------------------------------------------------------------
BASE_OSHA = 200_000


def _tasa(n, horas):
    n, h = to_float(n, 0.0), to_float(horas)
    if not h:
        return None
    return n * BASE_OSHA / h


def indices_osha(*, muertes=0, casos_dias_perdidos=0, casos_restringidos=0,
                 otros_registrables=0, dias_perdidos=0, dias_restringidos=0,
                 casos_cambio_actividad=0, horas=0):
    """Índices por 200 000 horas trabajadas.

    Columnas del OSHA 300: G = muertes, H = casos con días fuera, I = casos con
    trabajo transferido/restringido, J = otros casos registrables.

    * TRIR = (G+H+I+J) × 200 000 / horas  (definición estándar de OSHA; la hoja
      original sumaba H + J, lo que omitía G e I).
    * DART = (H + I + cambios de actividad) × 200 000 / horas.
    * LWIR = H × 200 000 / horas.
    * LWSR = días perdidos × 200 000 / horas.
    * OSHA SR = (días perdidos + días restringidos) × 200 000 / horas.
    """
    registrables = sum(to_float(x, 0.0) for x in (muertes, casos_dias_perdidos,
                                                  casos_restringidos, otros_registrables))
    return {
        "TRIR": _tasa(registrables, horas),
        "DART": _tasa(to_float(casos_dias_perdidos, 0) + to_float(casos_restringidos, 0)
                      + to_float(casos_cambio_actividad, 0), horas),
        "LWIR": _tasa(casos_dias_perdidos, horas),
        "LWSR": _tasa(dias_perdidos, horas),
        "OSHA SR": _tasa(to_float(dias_perdidos, 0) + to_float(dias_restringidos, 0), horas),
        "Casos registrables": registrables,
    }


# ---------------------------------------------------------------------------
# Residuos peligrosos
# ---------------------------------------------------------------------------

def categoria_generador(toneladas_anuales):
    """Categoría de generador (LGPGIR): gran ≥ 10 t; pequeño > 0.4 t y < 10 t; micro ≤ 0.4 t."""
    t = to_float(toneladas_anuales)
    if t is None:
        return ""
    if t >= 10:
        return "Gran generador"
    if t > 0.4:
        return "Pequeño generador"
    return "Microgenerador"


# ---------------------------------------------------------------------------
# Listas de verificación
# ---------------------------------------------------------------------------

def resumen_checklist(respuestas: Iterable[str], positivos=("Sí", "S", "Cumple", "SI"),
                      negativos=("No", "N", "No cumple", "NO")):
    """Cuenta respuestas y calcula % de cumplimiento = positivos / (positivos + negativos)."""
    pos = neg = na = vacio = 0
    for r in respuestas:
        r = (r or "").strip()
        if r in positivos:
            pos += 1
        elif r in negativos:
            neg += 1
        elif r:
            na += 1
        else:
            vacio += 1
    evaluados = pos + neg
    pct = (100.0 * pos / evaluados) if evaluados else None
    return {"cumple": pos, "no_cumple": neg, "na": na, "sin_respuesta": vacio, "porcentaje": pct}


def promedio_calificaciones(calificaciones: Iterable):
    """Promedio 0-5 sólo sobre los apartados que aplicaron (criterio PROFEPA del formato)."""
    vals = [to_float(c) for c in calificaciones]
    vals = [v for v in vals if v is not None]
    return (sum(vals) / len(vals)) if vals else None


# ---------------------------------------------------------------------------
# Pareto
# ---------------------------------------------------------------------------

def pareto(datos: Sequence[tuple[str, float]]):
    """Ordena de mayor a menor y añade % y % acumulado. Devuelve lista de dicts."""
    limpios = [(str(k), to_float(v, 0.0)) for k, v in datos if str(k).strip()]
    limpios.sort(key=lambda kv: kv[1], reverse=True)
    total = sum(v for _, v in limpios)
    out, acum = [], 0.0
    for k, v in limpios:
        acum += v
        out.append({"categoria": k, "valor": v,
                    "pct": 100 * v / total if total else 0.0,
                    "acumulado": 100 * acum / total if total else 0.0})
    return out


# ---------------------------------------------------------------------------
# Capacidad de proceso y carta I-MR
# ---------------------------------------------------------------------------
D2_N2 = 1.128  # constante d2 para rangos móviles de 2


def capacidad(datos: Sequence[float], lie=None, lse=None):
    """Cp, Cpk (σ dentro de subgrupo por rango móvil) y Pp, Ppk (σ global)."""
    x = [to_float(v) for v in datos]
    x = [v for v in x if v is not None]
    if len(x) < 2:
        raise ValueError("Se necesitan al menos 2 datos")
    lie, lse = to_float(lie), to_float(lse)
    media = statistics.fmean(x)
    s_global = statistics.stdev(x)
    mr = [abs(b - a) for a, b in zip(x, x[1:])]
    mr_bar = statistics.fmean(mr) if mr else 0.0
    s_dentro = mr_bar / D2_N2 if mr_bar else s_global

    def _idx(sigma):
        if not sigma:
            return None, None
        cp = (lse - lie) / (6 * sigma) if lie is not None and lse is not None else None
        cands = []
        if lse is not None:
            cands.append((lse - media) / (3 * sigma))
        if lie is not None:
            cands.append((media - lie) / (3 * sigma))
        return cp, (min(cands) if cands else None)

    cp, cpk = _idx(s_dentro)
    pp, ppk = _idx(s_global)
    fuera = sum(1 for v in x if (lie is not None and v < lie) or (lse is not None and v > lse))
    return {
        "n": len(x), "media": media, "min": min(x), "max": max(x),
        "sigma_dentro": s_dentro, "sigma_global": s_global,
        "Cp": cp, "Cpk": cpk, "Pp": pp, "Ppk": ppk,
        "LCS": media + 3 * s_dentro, "LCI": media - 3 * s_dentro,
        "MR_promedio": mr_bar, "LCS_MR": 3.267 * mr_bar,
        "fuera_especificacion": fuera,
        "fuera_control": [i + 1 for i, v in enumerate(x)
                          if v > media + 3 * s_dentro or v < media - 3 * s_dentro],
    }


# ---------------------------------------------------------------------------
# Incompatibilidad química
# ---------------------------------------------------------------------------

def incompatibilidad(matriz: dict, g1, g2):
    """Busca el código de reacción entre dos grupos en una matriz triangular."""
    g1, g2 = str(g1), str(g2)
    if g1 == g2:
        return ""
    if "107" in (g1, g2):
        return "EXTREMO"
    return matriz.get(g1, {}).get(g2) or matriz.get(g2, {}).get(g1) or ""


def decodificar_reaccion(codigo: str, nomenclatura: dict):
    """Separa un código como 'HFgt' en sus partes ['H', 'F', 'gt'] y las describe."""
    partes, i = [], 0
    codigo = (codigo or "").replace(" ", "")
    while i < len(codigo):
        dos = codigo[i:i + 2]
        if dos in ("gt", "gf", "GT"):
            partes.append(dos.lower())
            i += 2
        else:
            partes.append(codigo[i])
            i += 1
    return [(p, nomenclatura.get(p, nomenclatura.get(p.upper(), ""))) for p in partes]
