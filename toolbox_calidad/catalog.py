"""Catálogo de herramientas: categoría, título, fábrica y metadatos."""
from __future__ import annotations

from toolbox_calidad.forms import ambiental, mejora, seguridad

CATEGORIAS = ["Calidad", "Mejora continua (TPM)", "Seguridad e higiene", "Protección civil", "Medio ambiente",
              "Herramientas estadísticas"]


def _form(schema):
    def factory(master):
        from toolbox_calidad.ui.base import FormTool
        return FormTool(master, schema)
    return factory


def _lazy(module, cls):
    def factory(master):
        import importlib
        return getattr(importlib.import_module(f"toolbox_calidad.tools.{module}"), cls)(master)
    return factory


def build_catalog() -> list[dict]:
    items = []
    for schema in mejora.FORMS + seguridad.FORMS + ambiental.FORMS:
        items.append({"id": schema["id"], "title": schema["title"], "category": schema["category"],
                      "code": schema.get("code", ""), "description": schema.get("description", ""),
                      "source": schema.get("source", ""), "factory": _form(schema)})
    special = [
        ("amef", "AMEF / FMEA (RPN automático)", "Calidad", "amef", "AmefTool",
         "Análisis de modo y efecto de falla con RPN, umbral de acción y escalas S/O/D.", "009 AMEF-FORMATO Y CONTROL DE AYUDA.xls"),
        ("kpi", "Indicador de prestación (KPI)", "Mejora continua (TPM)", "kpi", "KpiTool",
         "Seguimiento semanal del KPI frente a inicio y objetivo, con gráfica.", "019 FORMATO INDICADOR DE PRESTACIÓN.xls"),
        ("auditoria_grupo", "Auditoría del grupo de mejora", "Mejora continua (TPM)", "auditoria", "AuditoriaTool",
         "36 preguntas / 100 puntos por semana contra la curva objetivo, con registro de acciones.",
         "026 AUDITORIA DEL GRUPO DE MEJORA.xls"),
        ("ruido", "Conservación de la audición (NOM-011)", "Seguridad e higiene", "ruido", "RuidoTool",
         "Programa completo con dosimetría: NER, TMPE y NRE automáticos.", "Programa de Conservación de la Audición.xls"),
        ("osha", "Registro OSHA 300 / 300A e índices", "Seguridad e higiene", "osha", "OshaTool",
         "Bitácora de casos, resumen anual e índices TRIR, DART, LWIR, LWSR.", "Registro Accidentes OSHA.xls"),
        ("ventilacion_calc", "Ventilación: cambios de aire por hora", "Seguridad e higiene", "calculadoras", "VentilacionTool",
         "N = Q·60/Vol y caudal requerido.", "VENTILACIÓN - Cálculo del Número de Recambios Por Hora.xls"),
        ("incompatibilidad", "Incompatibilidad química", "Medio ambiente", "consultas", "IncompatibilidadTool",
         "Reacción entre grupos reactivos y búsqueda de sustancias.", "Tabla de Incompatibilidad Quimica_2.xls"),
        ("matpel", "Materiales peligrosos (No. ONU)", "Medio ambiente", "consultas", "MaterialesPeligrososTool",
         "Buscador de la lista de mercancías peligrosas para transporte.", "Tablas de Materiales Peligrosos Para Su Transporte.xls"),
        ("pareto", "Diagrama de Pareto", "Herramientas estadísticas", "calculadoras", "ParetoTool",
         "Prioriza pérdidas, averías o defectos (80/20).", "Herramienta adicional"),
        ("capacidad", "Capacidad de proceso Cp/Cpk + carta I-MR", "Herramientas estadísticas", "calculadoras", "CapacidadTool",
         "Índices de capacidad, histograma y carta de control.", "Herramienta adicional"),
    ]
    for tid, title, cat, mod, cls, desc, src in special:
        items.append({"id": tid, "title": title, "category": cat, "code": "", "description": desc, "source": src,
                      "factory": _lazy(mod, cls)})
    orden = {c: i for i, c in enumerate(CATEGORIAS)}
    items.sort(key=lambda it: (orden.get(it["category"], 99), it["title"]))
    return items
