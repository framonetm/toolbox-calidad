"""Formatos de Seguridad e Higiene y Protección Civil."""
from toolbox_calidad.core.storage import load_json


def checklist_from_json(name, key="lista", title=None, score=False):
    d = load_json("checklists", f"{name}.json")
    opts = d.get("options", ["Sí", "No", "N/A"])
    spec = {"type": "checklist", "key": key, "title": title or "Lista de verificación",
            "options": opts, "positive": (opts[0],), "negative": (opts[1],),
            "groups": d["sections"], "score": score}
    if d.get("nota"):
        spec["help"] = d["nota"]
    return spec, d


_rec, _rec_d = checklist_from_json("recorrido_comision_sh", title="Inspección por rubros")
RECORRIDO_SH = {
    "id": "recorrido_sh", "title": "Acta de verificación de recorrido — Comisión de Seguridad e Higiene",
    "code": "Recorrido CSH", "category": "Seguridad e higiene", "source": _rec_d["source"],
    "description": "Recorrido de verificación de la Comisión de Seguridad e Higiene: inspección física, "
                   "instalaciones eléctricas, servicios, materiales, EPP, orden y limpieza, sistema contra "
                   "incendio y señalamientos, con registro de hallazgos.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Centro de trabajo y recorrido", "columns": 3, "fields": [
            {"key": "centro", "label": "Centro de trabajo", "width": 34}, {"key": "calle", "label": "Calle y número"},
            {"key": "colonia", "label": "Colonia"}, {"key": "municipio", "label": "Municipio / alcaldía"},
            {"key": "ciudad", "label": "Ciudad"}, {"key": "cp", "label": "C.P."},
            {"key": "entidad", "label": "Entidad federativa"}, {"key": "trabajadores", "label": "No. de trabajadores"},
            {"key": "tipo", "label": "Tipo de recorrido", "options": ["Ordinario", "Extraordinario"]},
            {"key": "area", "label": "Área / zona"}, {"key": "turno", "label": "Turno"},
            {"key": "fecha_ini", "label": "Fecha de inicio", "kind": "date", "default": "hoy"},
            {"key": "fecha_fin", "label": "Fecha de término"}, {"key": "hora_ini", "label": "Hora de inicio"},
            {"key": "hora_fin", "label": "Hora de término"}]},
        {"type": "table", "key": "auditores", "title": "Integrantes de la comisión / auditores", "rows": 4, "columns": [
            {"key": "nombre", "label": "Nombre", "width": 34}, {"key": "rep", "label": "Representación", "width": 18,
                                                              "options": ["Patrón", "Trabajadores"]}]},
        _rec,
        {"type": "table", "key": "hallazgos", "title": "Hallazgos: agentes, condiciones peligrosas o inseguras y actos inseguros",
         "rows": 5, "columns": [
            {"key": "hallazgo", "label": "Hallazgo", "width": 40}, {"key": "causas", "label": "Causas", "width": 28},
            {"key": "medidas", "label": "Medidas de prevención", "width": 34},
            {"key": "resp", "label": "Responsable", "width": 14}, {"key": "fecha", "label": "Fecha compromiso", "width": 12}]},
    ],
}

_tal, _tal_d = checklist_from_json("seguridad_talleres", title="Diagnóstico")
TALLERES = {
    "id": "talleres", "title": "Diagnóstico de seguridad y medio ambiente — Talleres", "code": "Talleres",
    "category": "Seguridad e higiene", "source": _tal_d["source"],
    "description": "Diagnóstico de instalaciones, equipo contra incendio, maquinaria, sustancias químicas, "
                   "señalización/EPP y actividades de corte y soldadura en talleres.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 3, "fields": [
            {"key": "taller", "label": "Taller / área"}, {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"},
            {"key": "evaluador", "label": "Evaluador"}, {"key": "superficie", "label": "Superficie (m²)"},
            {"key": "ventilacion", "label": "Tipo de ventilación", "options": ["Natural", "Artificial"]},
            {"key": "tmax", "label": "Temperatura máxima generada (°C)"}]},
        {"type": "choices", "key": "quimicos", "title": "Tipo de químicos con los que se trabaja",
         "options": ["Corrosivos", "Irritantes", "Tóxicas", "Inflamables", "Explosivas"]},
        _tal,
        {"type": "table", "key": "epp", "title": "Equipo de protección personal por región anatómica", "rows": 0, "fixed": True,
         "default_rows": [{"region": r, "riesgo": k} for r, k in [
             ("Cabeza", "Golpes · temperaturas · partículas"), ("Ojos y cara", "Proyección de partículas/líquidos · vapores · soldadura eléctrica"),
             ("Oídos", "Nivel del área dB(A) / NRR del equipo"), ("Aparato respiratorio", "Polvos · gases y vapores"),
             ("Extremidades superiores", "Sustancias químicas · descargas eléctricas · temperaturas"),
             ("Tronco", "Temperaturas · sustancias químicas"), ("Extremidades inferiores", "Golpes · descargas eléctricas")]],
         "columns": [{"key": "region", "label": "Región anatómica", "width": 22, "readonly": True},
                     {"key": "riesgo", "label": "Riesgos a considerar", "width": 46, "readonly": True},
                     {"key": "epp", "label": "Descripción del EPP utilizado", "width": 36}]},
        {"type": "text", "key": "obs", "title": "Observaciones / reacción ante fuga de gases combustibles", "height": 3},
    ],
}

_ven, _ven_d = checklist_from_json("ventilacion_climatizacion", title="Condiciones medioambientales")
VENTILACION_CHECK = {
    "id": "ventilacion_check", "title": "Check list de ventilación y climatización", "code": "Ventilación",
    "category": "Seguridad e higiene", "source": _ven_d["source"],
    "description": "Verificación de extracción localizada, ventilación general y climatización del área de trabajo.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 3, "fields": [
            {"key": "area", "label": "Área de trabajo"}, {"key": "personas", "label": "Personas afectadas"},
            {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"},
            {"key": "proxima", "label": "Próxima revisión"}, {"key": "realizo", "label": "Realizado por"}]},
        _ven,
    ],
}

_sim, _sim_d = checklist_from_json("simulacro_profepa", title="Evaluación por rol (calificación 0 a 5)", score=True)
SIMULACRO_PROFEPA = {
    "id": "simulacro_profepa", "title": "Evaluación de simulacro — listas de verificación PROFEPA", "code": "Simulacros PROFEPA",
    "category": "Protección civil", "source": _sim_d["source"],
    "description": "Evalúa los roles de un simulacro: respuesta a emergencias, comando del incidente, brigada "
                   "contra incendio, evacuación, servicio médico y coordinación con autoridades. Cada apartado se "
                   "califica de 0 a 5 y el promedio se calcula sólo con los apartados que aplicaron.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Simulacro", "columns": 3, "fields": [
            {"key": "centro", "label": "Centro de trabajo"}, {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"},
            {"key": "escenario", "label": "Escenario"}, {"key": "evaluador", "label": "Evaluador"},
            {"key": "hora_ini", "label": "Hora de inicio"}, {"key": "hora_fin", "label": "Hora de término"}]},
        _sim,
        {"type": "text", "key": "mejoras", "title": "Áreas de oportunidad y recomendaciones específicas", "height": 4},
    ],
}

REGISTRO_SIMULACRO = {
    "id": "registro_simulacro", "title": "Registro de simulacro de incendio", "code": "Registro de simulacro",
    "category": "Protección civil", "source": "Registro de Simulacro de Incendio.doc",
    "description": "Registro de la ejecución de un simulacro: coordinadores, tiempos, alcance, personal involucrado, "
                   "desviaciones detectadas, recomendaciones para el plan de emergencias y recursos externos.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos del simulacro", "columns": 3, "fields": [
            {"key": "centro", "label": "Centro de trabajo", "width": 34},
            {"key": "fecha", "label": "Fecha de ejecución", "kind": "date", "default": "hoy"},
            {"key": "hora_ini", "label": "Hora de inicio"}, {"key": "hora_fin", "label": "Hora de término"},
            {"key": "tiempo", "label": "Tiempo (min)"}, {"key": "integral", "label": "Alcance integral", "options": ["Sí", "No"]},
            {"key": "personas", "label": "No. de personas que intervinieron"}, {"key": "areas", "label": "Área(s) involucrada(s)"},
            {"key": "escenario", "label": "Escenario", "width": 34}]},
        {"type": "table", "key": "coordinadores", "title": "Coordinadores del simulacro", "rows": 2, "columns": [
            {"key": "nombre", "label": "Nombre (apellido paterno, materno, nombre)", "width": 40},
            {"key": "cargo", "label": "Cargo o función", "width": 30}]},
        {"type": "table", "key": "personal", "title": "Personal involucrado", "rows": 6, "columns": [
            {"key": "nombre", "label": "Nombre", "width": 34}, {"key": "cargo", "label": "Cargo", "width": 22},
            {"key": "actividad", "label": "Actividad a desempeñar", "width": 34}]},
        {"type": "table", "key": "desviaciones", "title": "Resultados — detección de desviaciones planeadas", "rows": 4, "columns": [
            {"key": "desc", "label": "Descripción de la desviación", "width": 80}]},
        {"type": "table", "key": "recomendaciones", "title": "Recomendaciones para actualizar el plan de atención a emergencias de incendio",
         "rows": 4, "columns": [{"key": "rec", "label": "Recomendación", "width": 80}]},
        {"type": "choices", "key": "recursos", "title": "Recursos externos utilizados",
         "options": ["Cruz Roja", "Protección Civil", "Bomberos", "Otro"]},
        {"type": "text", "key": "otro", "title": "Otro recurso (¿cuál?) / observaciones", "height": 2},
    ],
}

_pc, _pc_d = checklist_from_json("proteccion_civil_riesgos", title="Riesgos internos y externos")
PROTECCION_CIVIL = {
    "id": "proteccion_civil", "title": "Identificación y análisis de riesgos — Protección Civil", "code": "Análisis de riesgos PC",
    "category": "Protección civil", "source": _pc_d["source"],
    "description": "Formato para el programa interno de protección civil: identificación del inmueble, riesgos "
                   "estructurales, de instalaciones, no estructurales, acabados, equipos de emergencia, objetos que "
                   "pueden caer/deslizarse/volcar/inflamarse y riesgos externos. «Sí» = riesgo o condición presente.",
    "sections": [
        {"type": "fields", "key": "inmueble", "title": "1. Identificación del inmueble", "columns": 3, "fields": [
            {"key": "propietario", "label": "Propietario o responsable"}, {"key": "fecha", "label": "Fecha de elaboración", "kind": "date", "default": "hoy"},
            {"key": "responsable_pipc", "label": "Responsable del programa interno"}, {"key": "tel", "label": "Teléfono"},
            {"key": "domicilio", "label": "Domicilio"}, {"key": "entre", "label": "Entre calles"},
            {"key": "colonia", "label": "Colonia"}, {"key": "municipio", "label": "Municipio"},
            {"key": "entidad", "label": "Entidad"}, {"key": "giro", "label": "Giro o actividad"},
            {"key": "niveles", "label": "Número de niveles"}, {"key": "sup_total", "label": "Superficie total (m²)"},
            {"key": "sup_const", "label": "Superficie construida (m²)"}, {"key": "antiguedad", "label": "Antigüedad (años)"},
            {"key": "pob_fija", "label": "Población fija"}, {"key": "pob_flot", "label": "Población flotante"}]},
        {"type": "checklist", "key": "croquis", "title": "Croquis de localización por nivel", "options": ["Sí", "No", "N/A"],
         "groups": [{"name": "El croquis señala", "items": [
             {"code": "1.021", "text": "Norte geográfico del inmueble"}, {"code": "1.022", "text": "Riesgos internos identificados"},
             {"code": "1.023", "text": "Zonas consideradas de alto riesgo"}, {"code": "1.024", "text": "Equipos y servicios de emergencia"},
             {"code": "1.025", "text": "Rutas de evacuación y salidas de emergencia"},
             {"code": "1.026", "text": "Zona de menor riesgo y zona de conteo dentro del predio"}]}]},
        dict(_pc, positive=("No",), negative=("Sí",),
             help="En esta sección «Sí» significa que el riesgo está presente; el % indica la proporción de "
                  "elementos SIN riesgo. Para dictámenes y escaleras invierte la lectura en observaciones."),
        {"type": "text", "key": "conclusiones", "title": "Resumen ejecutivo y medidas recomendadas", "height": 4},
    ],
}

SOLDADURA = {
    "id": "soldadura", "title": "Lista de verificación — Riesgos en soldadura", "code": "Soldadura",
    "category": "Seguridad e higiene", "source": "RIESGOS EN SOLDADURA.ppt (medidas preventivas de la presentación)",
    "description": "Lista derivada de las medidas preventivas y del EPP de la presentación «Riesgos en soldadura»: "
                   "contacto térmico, proyección de partículas, ergonomía, incendio/explosión, riesgo eléctrico e higiénico.",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 3, "fields": [
            {"key": "area", "label": "Área / puesto"}, {"key": "proceso", "label": "Proceso de soldadura",
                                                       "options": ["Arco eléctrico", "Plasma", "Oxigas (acetilénica)", "Resistencia", "Fuerte y blanda", "Presión o forja"]},
            {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"}, {"key": "soldador", "label": "Soldador"},
            {"key": "revisor", "label": "Revisó"}]},
        {"type": "checklist", "key": "lista", "title": "Medidas preventivas", "options": ["Sí", "No", "N/A"], "groups": [
            {"name": "Contacto térmico (quemaduras)", "items": [
                {"code": "1", "text": "Las piezas recién soldadas se señalizan para evitar quemaduras"},
                {"code": "2", "text": "Se usan herramientas para manipular piezas pequeñas a alta temperatura"},
                {"code": "3", "text": "El soldador usa guantes"}]},
            {"name": "Proyección de partículas", "items": [
                {"code": "4", "text": "Se conoce la dirección de las partículas antes de iniciar"},
                {"code": "5", "text": "Hay pantallas o mamparas que evitan las proyecciones hacia personas o zonas con riesgo de incendio"},
                {"code": "6", "text": "Se usa delantal de cuero, gafas y pantalla facial"}]},
            {"name": "Ergonomía", "items": [
                {"code": "7", "text": "La posición de la pieza evita inclinaciones y torsiones innecesarias de la columna"},
                {"code": "8", "text": "Lugar de trabajo ordenado"}, {"code": "9", "text": "Iluminación adecuada"}]},
            {"name": "Incendio y explosión", "items": [
                {"code": "10", "text": "No hay sustancias inflamables o combustibles sin proteger en la proximidad"},
                {"code": "11", "text": "Ventilación suficiente para evitar acumulación de gases"},
                {"code": "12", "text": "Extintor ABC disponible cerca del puesto"}]},
            {"name": "Riesgo eléctrico", "items": [
                {"code": "13", "text": "No se suelda en lugar o suelo húmedo"},
                {"code": "14", "text": "Guantes, vestimenta y lugar de trabajo totalmente secos"},
                {"code": "15", "text": "El equipo está aterrizado y cables/pinzas en buen estado"}]},
            {"name": "Riesgos higiénicos y EPP", "items": [
                {"code": "16", "text": "Extracción o protección respiratoria contra humos (neumoconiosis, fiebre de los metales)"},
                {"code": "17", "text": "Protección ocular adecuada contra radiación UV/IR (pantalla de mano o de cabeza)"},
                {"code": "18", "text": "Ropa de protección, calzado de seguridad y protección auditiva cuando aplica"}]}]},
        {"type": "text", "key": "obs", "title": "Observaciones y acciones", "height": 3},
    ],
}

FORMS = [RECORRIDO_SH, TALLERES, VENTILACION_CHECK, SOLDADURA, SIMULACRO_PROFEPA, REGISTRO_SIMULACRO, PROTECCION_CIVIL]
