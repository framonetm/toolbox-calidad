"""Formatos de Medio Ambiente y cumplimiento legal (México)."""
from toolbox_calidad.core.calc import categoria_generador, to_float
from toolbox_calidad.core.storage import load_json
from toolbox_calidad.forms.seguridad import checklist_from_json

_rp, _rp_d = checklist_from_json("almacen_residuos_peligrosos", title="Requisitos del almacén (S = cumple, N = no cumple)")
ALMACEN_RP = {
    "id": "almacen_rp", "title": "Requisitos auditables — Almacén de residuos peligrosos", "code": "RLGPGIR Art. 82",
    "category": "Medio ambiente", "source": _rp_d["source"],
    "description": "Auditoría del almacén temporal de residuos peligrosos (generales, áreas cerradas y áreas abiertas) "
                   "conforme al Art. 82 del Reglamento de la LGPGIR. Calcula el % de cumplimiento.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 3, "fields": [
            {"key": "centro", "label": "Centro de trabajo"}, {"key": "fecha", "label": "Fecha de evaluación", "kind": "date", "default": "hoy"},
            {"key": "evaluador", "label": "Evaluador"}]},
        dict(_rp, help="Tipo de requisito: documental (D), físico (F) u otro (O). Puedes anotarlo en observaciones."),
    ],
}

_rlan = load_json("requisitos_rlan.json")
MATRIZ_RLAN = {
    "id": "matriz_rlan", "title": "Matriz de requisitos legales — Agua (Reglamento de la Ley de Aguas Nacionales)",
    "code": "Matriz requisitos legales", "category": "Medio ambiente",
    "source": "REGLAMENTO DE LA LEY DE AGUAS NACIONALES.xls",
    "description": "Seguimiento de requisitos documentales del RLAN: cumplimiento, fechas y, en caso de no "
                   "cumplimiento, causas, acciones y responsable. Precargada con los artículos del formato "
                   "original; puedes agregar otras normas (NOM-001/002-SEMARNAT, etc.).",
    "intro": "Verifica la vigencia de los artículos citados antes de usar esta matriz en una auditoría: "
             "la matriz original es de 2012.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Centro de trabajo", "columns": 2, "fields": [
            {"key": "centro", "label": "Nombre del centro de trabajo", "width": 40},
            {"key": "fecha", "label": "Fecha de revisión", "kind": "date", "default": "hoy"}]},
        {"type": "table", "key": "requisitos", "title": "Requisitos", "rows": 0,
         "default_rows": [{"aspecto": r[0], "norma": r[1] + " " + r[2], "req": r[3], "doc": r[4], "frec": r[5]} for r in _rlan],
         "columns": [
             {"key": "aspecto", "label": "Aspecto", "width": 7},
             {"key": "norma", "label": "Normatividad", "width": 12},
             {"key": "req", "label": "Requerimiento", "width": 46},
             {"key": "doc", "label": "Documento o actividad", "width": 20},
             {"key": "frec", "label": "Frecuencia", "width": 18},
             {"key": "cumple", "label": "Cumple", "width": 6, "options": ["SI", "NO", "N/A"]},
             {"key": "prog", "label": "Fecha programación", "width": 11},
             {"key": "real", "label": "Fecha realización", "width": 11},
             {"key": "causas", "label": "Causas (si no cumple)", "width": 16},
             {"key": "acciones", "label": "Acciones", "width": 16},
             {"key": "resp", "label": "Responsable", "width": 12}],
         "highlight": lambda r: {"SI": "verde", "NO": "rojo"}.get(r.get("cumple")),
         "summary": lambda rows: "Cumplimiento: {}".format(
             (lambda si, no: f"{100 * si / (si + no):.0f} % ({si} de {si + no})" if si + no else "—")(
                 sum(r.get("cumple") == "SI" for r in rows), sum(r.get("cumple") == "NO" for r in rows)))},
    ],
}

CPR = ["C", "R", "E", "T", "Te", "Th", "Tt", "I", "B"]
CLAVES_GENERICAS = ["O1 Aceites lubricantes", "O2 Aceites solubles", "O3 Aceites hidráulicos", "O5 Aceites dieléctricos",
                    "O6 Aceites de templado", "O4 Otros aceites", "B1 Breas catalíticas", "B2 Breas de destilación",
                    "B3 Otras breas", "BI1 Cultivos y cepas", "BI2 Punzocortantes", "BI3 Patológicos", "BI4 No anatómicos",
                    "BI5 Sangre", "E1 Escorias finas", "E2 Escorias granulares", "LR1 Líquidos residuales corrosivos",
                    "LR2 Líquidos residuales no corrosivos", "L1 Lodos de aguas negras", "L2 Lodos de aguas de proceso",
                    "L3 Lodos de galvanoplastia", "L4 Lodos de templado", "L5 Lodos de pinturas", "L6 Lodos aceitosos",
                    "L7 Otros lodos", "SO1 Telas, pieles o asbesto encapsulado", "SO2 Sólidos de mantenimiento automotriz",
                    "SO3 Tortas de filtrado", "SO4 Otros sólidos", "SO5 Sólidos con metales pesados",
                    "S1 Solventes orgánicos", "S2 Solventes organoclorados", "C1 Ácidos", "C2 Álcalis", "O Otros"]


def _resumen_generador(rows):
    total = sum(to_float(r.get("cantidad"), 0) for r in rows)
    return f"Total anual estimado: {total:.3f} t  →  {categoria_generador(total) or '—'}"


GENERADOR_RP = {
    "id": "generador_rp", "title": "Hoja de datos — Registro de generador de residuos peligrosos",
    "code": "Apoyo al trámite SEMARNAT-07-017", "category": "Medio ambiente",
    "source": "REGISTRO DE GENERADORES DE RESIDUOS PELIGROSOS.xls",
    "description": "Hoja de trabajo para reunir los datos del registro de generador (Art. 43 RLGPGIR): identificación, "
                   "domicilios y clasificación de residuos con su código de peligrosidad (CPR) y cantidad anual. "
                   "Calcula la categoría: gran generador ≥ 10 t/año; pequeño > 0.4 t y < 10 t; microgenerador ≤ 0.4 t.",
    "intro": "Esta hoja NO sustituye el formato oficial: úsala para preparar la información y captúrala en el "
             "trámite vigente de SEMARNAT.",
    "sections": [
        {"type": "fields", "key": "generador", "title": "Identificación del generador", "columns": 2, "fields": [
            {"key": "nra", "label": "NRA"}, {"key": "rupa", "label": "RUPA"},
            {"key": "razon", "label": "Nombre o razón social", "width": 40}, {"key": "rfc", "label": "RFC"},
            {"key": "rep", "label": "Representante legal"}, {"key": "actividad", "label": "Actividad principal (SCIAN/CMAP)"},
            {"key": "inicio", "label": "Fecha de inicio de operaciones"}, {"key": "correo", "label": "Correo electrónico"}]},
        {"type": "fields", "key": "domicilio", "title": "Domicilio donde se generan los residuos", "columns": 3, "fields": [
            {"key": "calle", "label": "Calle y número"}, {"key": "colonia", "label": "Colonia"}, {"key": "cp", "label": "C.P."},
            {"key": "municipio", "label": "Municipio"}, {"key": "entidad", "label": "Entidad federativa"},
            {"key": "tel", "label": "Teléfono"}, {"key": "lat", "label": "Latitud N (opcional)"},
            {"key": "lon", "label": "Longitud O (opcional)"}, {"key": "alt", "label": "Altitud (msnm)"}]},
        {"type": "table", "key": "residuos", "title": "Clasificación de los residuos peligrosos que estima generar", "rows": 6,
         "columns": [
             {"key": "desc", "label": "Descripción del residuo", "width": 30},
             {"key": "clave", "label": "Clave del residuo (NOM-052)", "width": 12},
             {"key": "cpr", "label": "CPR (" + ", ".join(CPR) + ")", "width": 12},
             {"key": "generica", "label": "Clave genérica (Tabla 1)", "width": 22, "options": CLAVES_GENERICAS},
             {"key": "cas", "label": "No. CAS", "width": 12},
             {"key": "cantidad", "label": "Cantidad anual (t)", "width": 10}],
         "summary": _resumen_generador},
    ],
}

NOM020_I = ["Presión de operación", "Presión de trabajo máxima", "Capacidad volumétrica", "Temperatura de diseño",
            "Temperatura de operación", "Descripción breve de operación", "Registro de revisiones", "Registro de mantenimiento",
            "Ubicación del equipo"]
NOM020_II = ["Año de fabricación", "Código o norma de construcción", "Certificado de fabricación", "Presión de diseño",
             "Presión de operación", "Presión de trabajo máxima", "Presión de prueba hidrostática", "Temperatura de diseño",
             "Temperatura de operación", "Descripción breve de operación", "Registro de revisiones", "Registro de mantenimiento",
             "Registro de prueba de presión", "Exámenes no destructivos", "Registro de modificaciones", "Registro de alteraciones",
             "Registro de reparaciones con soldadura", "Dibujo o plano del equipo", "Croquis de localización",
             "Bitácora de ubicación (equipo móvil)"]
NOM020_III = ["Número de dictamen de la Unidad de Verificación", "Número de control STPS", "Año de fabricación",
              "Código o norma de construcción", "Certificado de fabricación", "Placa de datos del equipo", "Presión de diseño",
              "Presión de operación", "Presión de trabajo máxima", "Presión de prueba hidrostática", "Temperatura de diseño",
              "Temperatura de operación", "Dispositivos de relevo de presión (número)", "Descripción breve de operación",
              "Descripción de los riesgos", "Elementos de seguridad", "Resumen cronológico de mantenimiento",
              "Resumen cronológico de pruebas", "Resumen cronológico de modificaciones", "Resumen cronológico de soldadura",
              "Dibujo o plano: cortes, dimensiones, detalles relevantes, ubicación de relevos y arreglo del sistema",
              "Memoria de cálculo: presión interna máxima, espesores mínimos, área de desfogue, superficie de calefacción, capacidad volumétrica y generativa",
              "Croquis de localización", "Bitácora de ubicación (equipo móvil)"]


def _items(lst, pref):
    return [{"code": f"{pref}.{i}", "text": t} for i, t in enumerate(lst, start=1)]


NOM020 = {
    "id": "nom020", "title": "Requisitos para integrar el expediente de recipientes a presión (NOM-020-STPS)",
    "code": "NOM-020-STPS-2011", "category": "Seguridad e higiene",
    "source": "020 - Requisitos Para Integrar Expedientes.xls",
    "description": "Verifica que el expediente de cada recipiente sujeto a presión, criogénico o generador de vapor "
                   "contenga la información requerida según su categoría (I, II o III). Llena sólo la categoría del equipo.",
    "sections": [
        {"type": "fields", "key": "equipo", "title": "Datos generales del equipo", "columns": 2, "fields": [
            {"key": "nombre", "label": "Nombre genérico del equipo", "width": 34},
            {"key": "tag", "label": "No. de serie / TAG"}, {"key": "fluidos", "label": "Fluidos manejados"},
            {"key": "calibracion", "label": "Presión de calibración"}, {"key": "volumen", "label": "Capacidad volumétrica"},
            {"key": "termica", "label": "Capacidad térmica (calderas)"},
            {"key": "categoria", "label": "Categoría", "options": ["I", "II", "III"]}]},
        {"type": "checklist", "key": "expediente", "title": "Contenido del expediente", "options": ["Sí", "No", "N/A"],
         "groups": [{"name": "Categoría I", "items": _items(NOM020_I, "I")},
                    {"name": "Categoría II", "items": _items(NOM020_II, "II")},
                    {"name": "Categoría III", "items": _items(NOM020_III, "III")}]},
    ],
}

FORMS = [ALMACEN_RP, MATRIZ_RLAN, GENERADOR_RP, NOM020]
