"""Formatos de Mejora Continua / TPM (serie F-GO-MT del repositorio original)."""
from toolbox_calidad.core.calc import to_float

PILARES = ["EyE", "GA", "ME", "PM", "SEG", "KAIZEN"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

LUP = {
    "id": "lup", "title": "Lección de un punto (LUP / OPL)", "code": "F-GO-MT-XXX Rev. 0",
    "category": "Mejora continua (TPM)",
    "source": "003 FORMATO LECCIÓN DE UN PUNTO.xlsx",
    "description": "Documento visual de una sola idea para capacitar en pocos minutos: conocimiento "
                   "básico, problema o mejora. Incluye el registro de difusión al personal.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos generales", "columns": 3, "fields": [
            {"key": "no", "label": "No. LUP"},
            {"key": "pilar", "label": "Pilar", "options": PILARES},
            {"key": "titulo", "label": "Título", "width": 40},
            {"key": "maquina", "label": "Máquina"},
            {"key": "seccion", "label": "Sección"},
            {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"},
        ]},
        {"type": "choices", "key": "tipo", "title": "Tipo de lección", "multi": False,
         "options": ["Conocimientos básicos", "Problema", "Mejora"]},
        {"type": "choices", "key": "ambito", "title": "Ámbito",
         "options": ["Seguridad", "Productividad", "Calidad", "Mantenimiento"]},
        {"type": "choices", "key": "difundir", "title": "Difundir a personal de",
         "options": ["Mantenimiento", "Operación", "Otro"]},
        {"type": "text", "key": "contenido", "title": "Contenido de la lección (texto, pasos, referencia a fotos/croquis)", "height": 8},
        {"type": "text", "key": "problema", "title": "Problema", "height": 3},
        {"type": "text", "key": "mejora", "title": "Mejora", "height": 3},
        {"type": "text", "key": "resultados", "title": "Resultados", "height": 3},
        {"type": "signatures", "key": "firmas", "title": "Elaboración y revisión",
         "roles": ["Autor", "Revisó turno 1", "Revisó turno 2", "Revisó turno 3", "Revisó jefatura", "Aprobó"]},
        {"type": "table", "key": "difusion", "title": "Registro de difusión de la LUP", "rows": 10, "columns": [
            {"key": "fecha", "label": "Fecha de difusión", "width": 14},
            {"key": "nombre", "label": "Nombre del trabajador", "width": 34},
            {"key": "num", "label": "No. de trabajador", "width": 14},
            {"key": "firma", "label": "Firma", "width": 18}]},
    ],
}

OCHO_D = {
    "id": "8d", "title": "Metodología 8D — Solución de problemas", "code": "8D",
    "category": "Calidad",
    "source": "005-FORMATO METODOLOGIA 8´D.xlsx",
    "description": "Ocho disciplinas para resolver problemas de calidad con contención, causa raíz, "
                   "acciones correctivas permanentes y prevención de recurrencia.",
    "intro": "Ejemplo del formato original: «El eje del motor J27 de la impresora K20 se agrieta y se rompe a la "
             "mitad de su vida útil» → causas A/B → PCA: cambiar atornilladores, Poka-Yoke de calibración, hoja de registro visible, capacitación.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos generales", "columns": 3, "fields": [
            {"key": "titulo", "label": "Título", "width": 40},
            {"key": "inicio", "label": "Fecha inicio", "kind": "date", "default": "hoy"},
            {"key": "revision", "label": "Última revisión", "kind": "date"},
        ]},
        {"type": "text", "key": "contexto", "title": "Contexto", "height": 3},
        {"type": "fields", "key": "d1", "title": "D1. Formar el equipo", "columns": 2, "fields": [
            {"key": "lider", "label": "Lidera"}, {"key": "sponsor", "label": "Sponsor"},
            {"key": "facilitador", "label": "Facilitador"}, {"key": "equipo", "label": "Equipo de trabajo", "width": 40}]},
        {"type": "fields", "key": "d2", "title": "D2. Definir el problema", "columns": 1, "fields": [
            {"key": "enunciado", "label": "Enunciado del problema", "width": 90},
            {"key": "que", "label": "¿Qué? (objeto / defecto)", "width": 90},
            {"key": "donde", "label": "¿Dónde?", "width": 90},
            {"key": "cuando", "label": "¿Cuándo?", "width": 90},
            {"key": "cuanto", "label": "¿Cuánto? (magnitud)", "width": 90}]},
        {"type": "table", "key": "d3", "title": "D3. Acciones temporales de contención (ICA)", "rows": 3, "columns": [
            {"key": "accion", "label": "Acción de contención", "width": 40},
            {"key": "resp", "label": "Responsable", "width": 16},
            {"key": "fecha", "label": "Fecha", "width": 12},
            {"key": "eficacia", "label": "% eficacia estimada", "width": 10}]},
        {"type": "text", "key": "d3_eval", "title": "¿Cómo se ha evaluado la eficacia de las ICA?", "height": 2},
        {"type": "table", "key": "d4", "title": "D4. Analizar las causas raíz", "rows": 4, "columns": [
            {"key": "id", "label": "Causa", "width": 6},
            {"key": "causa", "label": "Descripción de la causa raíz", "width": 44},
            {"key": "m", "label": "Categoría 6M", "width": 14,
             "options": ["Mano de obra", "Método", "Máquina", "Material", "Medición", "Medio ambiente"]},
            {"key": "validada", "label": "¿Validada?", "width": 10, "options": ["Sí", "No", "En proceso"]}]},
        {"type": "text", "key": "d4_val", "title": "¿Cómo se han validado las hipótesis de causa raíz?", "height": 2},
        {"type": "table", "key": "d5", "title": "D5. Determinar las soluciones (acciones correctivas permanentes, PCA)", "rows": 4, "columns": [
            {"key": "causa", "label": "Causa", "width": 6},
            {"key": "pca", "label": "Acción correctiva permanente", "width": 48},
            {"key": "valoracion", "label": "Valoración", "width": 12, "options": ["Elegida", "Descartada", "En análisis"]},
            {"key": "eficacia", "label": "% eficacia estimada", "width": 10}]},
        {"type": "text", "key": "d5_eval", "title": "¿Cómo se ha evaluado que las soluciones serán eficaces?", "height": 2},
        {"type": "table", "key": "d6", "title": "D6. Implementar las soluciones — plan de implementación", "rows": 4, "columns": [
            {"key": "accion", "label": "Acción", "width": 40},
            {"key": "resp", "label": "Responsable", "width": 16},
            {"key": "plan", "label": "Fecha plan", "width": 12},
            {"key": "real", "label": "Fecha real", "width": 12},
            {"key": "estado", "label": "Estado", "width": 12, "options": ["Pendiente", "En curso", "Cerrada"]}]},
        {"type": "text", "key": "d6_val", "title": "Validación de resultados", "height": 2},
        {"type": "text", "key": "d7", "title": "D7. Prevenir problemas similares — ¿qué se ha estandarizado?", "height": 3},
        {"type": "text", "key": "d8", "title": "D8. Reconocer y compartir las lecciones aprendidas", "height": 3},
    ],
}

M4 = ["1.1 FC Falta de capacitación", "1.2 MO Mala operación", "1.3 APV Arreglo previo veloz",
      "2.1 MC Mala calidad", "2.2 DM Disponibilidad de material", "2.3 PVU Predicción vida útil",
      "2.4 DC Defectos de calidad", "3.1 DF Desgaste forzado", "3.2 DN Desgaste natural",
      "3.3 DP Debilidad del proyecto", "3.4 MMP Mejora/modificación no probada",
      "4.1 FMP Falta mantenimiento planeado", "4.2 FE Falta de estándares", "4.3 FI Falta de instructivo de trabajo"]

FICHA_PERDIDA = {
    "id": "ficha_perdida", "title": "Ficha de análisis de pérdida (5 porqués + 4M)", "code": "F-GO-MT-008 Rev. 0",
    "category": "Mejora continua (TPM)",
    "source": "013 FICHA ANALISIS DE PÉRDIDA.xls",
    "description": "Registra una pérdida/avería, su acción inmediata, el análisis de 5 porqués, la clasificación "
                   "4M de causas raíz, los controles existentes y el plan de acción.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos de la pérdida", "columns": 3, "fields": [
            {"key": "folio", "label": "Folio"},
            {"key": "linea", "label": "Línea de producción"},
            {"key": "seccion", "label": "Sección"},
            {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"},
            {"key": "turno", "label": "Turno", "options": ["1", "2", "3"]},
            {"key": "modo", "label": "Modo de defecto"},
            {"key": "inicio", "label": "Hora de inicio"},
            {"key": "fin", "label": "Hora de término"},
            {"key": "reporta", "label": "Quién reporta"},
            {"key": "tecnico", "label": "Técnico de mantenimiento"},
            {"key": "grupo", "label": "Grupo que analizó"},
        ]},
        {"type": "text", "key": "descripcion", "title": "Descripción de la pérdida (qué pasó y dónde: sección/parte). Croquis o fotografía: indica la ruta del archivo", "height": 3},
        {"type": "text", "key": "senales", "title": "Señales de advertencia antes de la pérdida", "height": 2},
        {"type": "text", "key": "inmediata", "title": "Acción inmediata (dónde, cómo y qué se ajustó o reparó)", "height": 2},
        {"type": "table", "key": "porques", "title": "Análisis de 5 porqués", "rows": 5, "fixed": True, "columns": [
            {"key": "pq", "label": "¿Por qué?", "width": 80}]},
        {"type": "table", "key": "causas", "title": "Causas raíz y clasificación 4M", "rows": 3, "columns": [
            {"key": "causa", "label": "Causa raíz", "width": 40},
            {"key": "m", "label": "Clasificación 4M", "width": 34, "options": M4},
            {"key": "accion", "label": "Acción inmediata", "width": 30}]},
        {"type": "choices", "key": "hay_control", "title": "¿Existen controles para prevenir esta pérdida?", "multi": False, "options": ["Sí", "No"]},
        {"type": "table", "key": "controles", "title": "Controles existentes", "rows": 3, "columns": [
            {"key": "tipo", "label": "Tipo de control", "width": 26,
             "options": ["Estándar", "LUP", "Programa", "Check-list", "Manual", "Instructivo", "Otro"]},
            {"key": "resp", "label": "Responsable", "width": 20},
            {"key": "frecuencia", "label": "Frecuencia de revisión", "width": 22}]},
        {"type": "table", "key": "plan", "title": "Plan de acción para que la pérdida no vuelva a ocurrir", "rows": 4, "columns": [
            {"key": "accion", "label": "Acción", "width": 44},
            {"key": "resp", "label": "Responsable(s)", "width": 20},
            {"key": "prog", "label": "Fecha programada", "width": 13},
            {"key": "real", "label": "Fecha real", "width": 13}]},
    ],
}

QUIEN_HACE_QUE = {
    "id": "quien_hace_que", "title": "¿Quién hace qué?", "code": "F-GO-MT-009",
    "category": "Mejora continua (TPM)", "source": "014 QUIEN HACE QUE.xls",
    "description": "Matriz de responsabilidades del grupo de mejora.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Grupo", "columns": 2, "fields": [
            {"key": "grupo", "label": "Grupo / proyecto"}, {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"}]},
        {"type": "table", "key": "tareas", "title": "Responsabilidades", "rows": 8, "columns": [
            {"key": "quien", "label": "Quién", "width": 24},
            {"key": "que", "label": "Qué", "width": 50},
            {"key": "cuando", "label": "Cuándo", "width": 18}]},
    ],
}

MARCO_REFERENCIA = {
    "id": "marco_referencia", "title": "Marco de referencia de reuniones (proyecto o pilar)", "code": "F-GO-MT-010 Rev. 0",
    "category": "Mejora continua (TPM)", "source": "015 MARCO DE REFERENCIA.xls",
    "description": "Define frecuencia, lugar, asistentes, objetivo, documentos de entrada/salida, agenda, "
                   "indicadores y reglas básicas de las reuniones. Los proyectos duran como máximo 4 meses; "
                   "los pilares mantienen calendario anual.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 2, "fields": [
            {"key": "nombre", "label": "Nombre del proyecto o pilar", "width": 40},
            {"key": "tipo", "label": "Tipo", "options": ["Proyecto", "Pilar"]},
            {"key": "frecuencia", "label": "Frecuencia"}, {"key": "dia", "label": "Día"},
            {"key": "hora", "label": "Hora"}, {"key": "lugar", "label": "Lugar"}]},
        {"type": "table", "key": "revision", "title": "Revisión", "rows": 3, "columns": [
            {"key": "revision", "label": "Revisión", "width": 20},
            {"key": "asistentes", "label": "Asistentes", "width": 34},
            {"key": "objetivo", "label": "Objetivo", "width": 34}]},
        {"type": "text", "key": "entrada", "title": "Documentos de entrada", "height": 3},
        {"type": "text", "key": "salida", "title": "Documentos de salida", "height": 3},
        {"type": "text", "key": "agenda", "title": "Agenda", "height": 4},
        {"type": "text", "key": "indicadores", "title": "Indicadores a revisar", "height": 3},
        {"type": "text", "key": "reglas", "title": "Reglas básicas", "height": 3},
        {"type": "text", "key": "calendario", "title": "Calendario de reuniones", "height": 3},
    ],
}

MASTER_PLAN = {
    "id": "master_plan", "title": "Master plan de pilares", "code": "F-GO-MT-020",
    "category": "Mejora continua (TPM)", "source": "020 FORMATO MASTER PLAN PILARES.xls",
    "description": "Plan anual por pasos y actividades del pilar. Estado mensual: 1 = Aplicación continua, "
                   "2 = Introducción, 3 = Retrasado.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 2, "fields": [
            {"key": "pilar", "label": "Pilar", "options": PILARES}, {"key": "anio", "label": "Año"}]},
        {"type": "table", "key": "plan", "title": "Plan (1 = Aplicación continua · 2 = Introducción · 3 = Retrasado)", "rows": 8,
         "columns": [{"key": "paso", "label": "Paso", "width": 6},
                     {"key": "actividad", "label": "Actividad", "width": 30}] +
                    [{"key": m.lower(), "label": m, "width": 4, "options": ["", "1", "2", "3"]} for m in MESES],
         "highlight": lambda r: "rojo" if "3" in [r.get(m.lower()) for m in MESES] else None,
         "summary": lambda rows: f"Actividades con meses retrasados: "
                                 f"{sum(1 for r in rows if '3' in [r.get(m.lower()) for m in MESES])}"},
    ],
}

TARJETA_EQUIPOS = {
    "id": "tarjeta_equipos", "title": "Tarjeta de identificación de equipos de mejora", "code": "F-GO-MT-015",
    "category": "Mejora continua (TPM)", "source": "021 FORMATO TARJETA DE IDENTIFICACIÓN DE EQUIPOS DE MEJORA.xls",
    "description": "Registro de los equipos de mejora: ruta, fechas, situación inicial vs. objetivo, resultados, "
                   "ahorros anuales, impacto, líderes y tipo de equipo.",
    "sections": [
        {"type": "table", "key": "equipos", "title": "Equipos de mejora", "rows": 6, "columns": [
            {"key": "id", "label": "Identificación del equipo", "width": 18},
            {"key": "ruta", "label": "Ruta (tipo de proyecto)", "width": 14},
            {"key": "inicio", "label": "Inicio", "width": 10},
            {"key": "fin", "label": "Fin", "width": 10},
            {"key": "unidad", "label": "Medida / unidad", "width": 10},
            {"key": "inicial", "label": "Situación inicial", "width": 10},
            {"key": "objetivo", "label": "Objetivo", "width": 10},
            {"key": "resultado", "label": "Resultados", "width": 10},
            {"key": "ahorro", "label": "Ahorros anuales", "width": 11},
            {"key": "impacto", "label": "Impacto (P, EF, C, CO, V, S, E, I, M, A)", "width": 12},
            {"key": "lider", "label": "Líder y sublíder", "width": 16},
            {"key": "tipo", "label": "Tipo de equipo", "width": 15,
             "options": ["Replicación horizontal", "Replicación vertical", "Nueva aplicación horizontal", "Nueva aplicación vertical"]}],
         "summary": lambda rows: "Ahorro anual total: $ {:,.0f}".format(
             sum(to_float(r.get("ahorro"), 0) for r in rows))},
    ],
}

INFORME_INICIAL = {
    "id": "informe_inicial", "title": "Informe inicial de proyecto", "code": "F-GO-MT-017",
    "category": "Mejora continua (TPM)", "source": "023 FORMATO INFORME INICIAL DE PROYECTO.xls",
    "description": "Arranque (charter) del proyecto de mejora: título, alcance, equipo, objetivos, resultado esperado "
                   "a 4 meses y ahorros potenciales, con firmas de aprobación.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos generales", "columns": 2, "fields": [
            {"key": "inicio", "label": "Fecha inicio del proyecto", "kind": "date", "default": "hoy"},
            {"key": "fin", "label": "Fecha término del proyecto"},
            {"key": "tarjeta", "label": "# Tarjeta de identificación"},
            {"key": "perdida", "label": "Tipo de pérdida"},
            {"key": "titulo", "label": "1.1 Título del proyecto", "width": 40},
            {"key": "depto", "label": "1.2 Departamento y máquina"},
            {"key": "reuniones", "label": "Reuniones semanales (día y hora)"},
            {"key": "cliente", "label": "2.2 Cliente interno"},
            {"key": "ahorro", "label": "5. Ahorros potenciales (miles $/año)"}]},
        {"type": "text", "key": "problema", "title": "1.3 Descripción breve del problema", "height": 3},
        {"type": "table", "key": "integrantes", "title": "2.1 Integrantes del grupo de mejora", "rows": 5, "columns": [
            {"key": "nombre", "label": "Nombre", "width": 34}, {"key": "funcion", "label": "Función", "width": 30}]},
        {"type": "text", "key": "didacticos", "title": "3. Objetivos didácticos / de conocimiento (métodos y herramientas)", "height": 3},
        {"type": "text", "key": "resultado", "title": "4. Resultado esperado del proyecto (en 4 meses)", "height": 3},
        {"type": "signatures", "key": "firmas", "title": "Aprobaciones", "roles": [
            "Gerente de Operaciones", "Gerente de Mantenimiento Corporativo", "Superintendente de Producción",
            "Coordinador TPM", "Responsable de proyecto (grupo de mejora)", "Líder de pilar responsable"]},
    ],
}

_FORMATOS_PM = [
    ("PASO 1 Identificar los tipos de avería", "Reporte de averías", "FO-C-A-REV.0"),
    ("PASO 2 Restablecer condiciones básicas y formular estándares", "Check list «Condiciones básicas de máquina» (operación)", "FO-C-CBM-REV.0"),
    ("PASO 2", "Concentrado general de estándares", "FO-C-CGE-REV.0"),
    ("PASO 2", "Estándar (limpieza, inspección, lubricación, SOP)", "FO-C-SLIL-REV.0"),
    ("PASO 2", "Mapa de limpieza", "FO-C-ML-REV.0"),
    ("PASO 2", "Programa de limpieza", "FO-C-PLCT-REV.0"),
    ("PASO 2", "Tarjetas de anomalías de operación", "FO-TAO-REV 1"),
    ("PASO 2", "Tarjeta de anomalías de mantenimiento", "FO-TAM-REV.1"),
    ("PASO 2", "Tarjeta de anomalías de seguridad, salud y medio ambiente", "FO-TAS-REV.1"),
    ("PASO 3 Atajar las averías frecuentes", "Análisis de los 5 porqués", "FO-C-A5P-REV.1"),
    ("PASO 3", "Medidas preventivas a aplicar", "FO-C-MPA-REV.0"),
    ("PASO 3", "Plan de acción", "FO-C-PA-REV.0"),
    ("PASO 3", "Control de repetitividad", "FO-C-CR-REV.0"),
    ("PASO 4 Evidenciar causas de averías esporádicas", "Ficha de análisis de pérdida", "FO-C-FAP-REV.0"),
    ("PASO 4", "Reporte general de averías", "FO-C-GA-REV.0"),
    ("PASO 4", "Medición MTBF y MTTR", "FO-C-MFM-REV.0"),
    ("PASO 4", "Flujo de averías", "FO-C-FA-REV.0"),
    ("PASO 5 Definir el plan de mantenimiento preventivo", "Matriz «X» averías, causas y medidas", "FO-C-MXA-REV.0"),
    ("PASO 5", "Plan de acción", "FO-C-PA-REV.0"),
    ("PASO 5", "Tarjeta «T»", "FO-C-TT-REV.0"),
]

ENTREGA_FORMATOS = {
    "id": "entrega_formatos", "title": "Documento de entrega de formatos / sistemas", "code": "F-GO-MT-019 / F-GO-MT-018",
    "category": "Mejora continua (TPM)",
    "source": "025 FORMATO DOCUMENTO DE ENTREGA DE FORMATOS.xls · 024 DOCUMENTO ENTREGA SISTEMAS.xlsx",
    "description": "Valida la entrega de los formatos de cada paso del proyecto Kaizen / pilar. Precargado con el "
                   "ejemplo de Mantenimiento Planificado (pasos 1 a 5) del formato original; edítalo libremente.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Proyecto", "columns": 2, "fields": [
            {"key": "tarjeta", "label": "# Tarjeta de identificación"}, {"key": "proyecto", "label": "Nombre del proyecto", "width": 40},
            {"key": "fecha", "label": "Fecha de entrega", "kind": "date", "default": "hoy"}, {"key": "pilar", "label": "Pilar", "options": PILARES}]},
        {"type": "table", "key": "formatos", "title": "Formatos por paso", "rows": 0,
         "default_rows": [{"paso": p, "nombre": n, "codigo": c} for p, n, c in _FORMATOS_PM],
         "columns": [
             {"key": "paso", "label": "Paso del proyecto", "width": 30},
             {"key": "nombre", "label": "Nombre del formato", "width": 40},
             {"key": "codigo", "label": "Código", "width": 16},
             {"key": "valido", "label": "Validación", "width": 10, "options": ["", "✓", "✗"]}],
         "highlight": lambda r: {"✓": "verde", "✗": "rojo"}.get(r.get("valido")),
         "summary": lambda rows: "Validados: {} de {}".format(
             sum(1 for r in rows if r.get("valido") == "✓"), sum(1 for r in rows if r.get("nombre")))},
        {"type": "signatures", "key": "firmas", "title": "Entrega y recepción", "roles": [
            "Operadores de máquina", "Coordinador TPM", "Supervisor de área", "Superintendente de Producción",
            "Gerente de Operaciones"]},
    ],
}

FORMS = [LUP, OCHO_D, FICHA_PERDIDA, QUIEN_HACE_QUE, MARCO_REFERENCIA, MASTER_PLAN, TARJETA_EQUIPOS,
         INFORME_INICIAL, ENTREGA_FORMATOS]
