# Toolbox de Calidad y Mejora Continua

Aplicación de escritorio **libre (MIT)** en Python con interfaz gráfica (Tkinter) que reúne
**30 formatos y calculadoras** para ingenieros de calidad, mejora continua (TPM/Kaizen),
seguridad e higiene, protección civil y medio ambiente.

Nace de digitalizar un conjunto de plantillas Excel/Word usadas en planta: cada formato se
llena en pantalla, **calcula solo** (RPN, NER/TMPE, índices OSHA, % de cumplimiento, Cpk…),
se **guarda** como `.qtb.json` y se **exporta a Excel** o a **HTML imprimible / PDF**.

- Sin instalación compleja: Python 3.9+ y `openpyxl` (Tkinter viene con Python en Windows y macOS).
- Funciona sin conexión; los datos nunca salen de tu equipo.
- Fácil de extender: la mayoría de los formatos son **esquemas declarativos** (diccionarios de Python).

## Inicio rápido

```bash
git clone https://github.com/framonetm/toolbox-calidad.git
cd toolbox-calidad
pip install -r requirements.txt
python run.py
```

En Windows basta con doble clic en `iniciar_windows.bat`.
En Linux, si falta Tkinter: `sudo apt install python3-tk`.

## Herramientas incluidas

| Categoría | Herramienta | Qué automatiza | Formato original |
|---|---|---|---|
| Calidad | **AMEF / FMEA** | RPN = S×O×D, nuevo RPN, umbral de acción, orden por RPN, escalas S/O/D | 009 AMEF |
| Calidad | **8D** | D1–D8 con contención, causas 6M, PCA y plan | 005 Metodología 8D |
| Mejora continua | **Lección de un punto (LUP/OPL)** | Tipo, pilar, firmas de revisión y registro de difusión | 003 LUP |
| Mejora continua | **Ficha de análisis de pérdida** | 5 porqués, clasificación 4M (14 subtipos), controles y plan | 013 (F-GO-MT-008) |
| Mejora continua | **Indicador de prestación (KPI)** | Gráfica semanal vs. inicio y objetivo, colores según sentido | 019 (F-GO-MT-013) |
| Mejora continua | **Auditoría del grupo de mejora** | 36 preguntas / 100 pts × 12 semanas, curva objetivo, acciones de los ceros | 026 (F-GO-MT-026) |
| Mejora continua | Quién hace qué · Marco de referencia · Master plan de pilares · Tarjeta de equipos de mejora · Informe inicial de proyecto · Entrega de formatos (precargada con los 20 formatos PM) | Totales de ahorro, actividades retrasadas, % validado | 014, 015, 020, 021, 023, 024, 025 |
| Seguridad e higiene | **Conservación de la audición (NOM-011-STPS)** | NER = 90 + 9.97·log(D/12.5T), TMPE = 8/2^((NER−90)/3), NRE = NER − R | Programa de Conservación de la Audición |
| Seguridad e higiene | **OSHA 300 / 300A** | Resumen anual e índices TRIR, DART, LWIR, LWSR, OSHA SR (×200 000 h) | Registro Accidentes OSHA |
| Seguridad e higiene | **Ventilación: cambios de aire/h** | N = Q·60/Vol, caudal requerido, varios extractores, m³/h ↔ CFM | VENTILACIÓN – Recambios por hora |
| Seguridad e higiene | Recorrido de la Comisión de Seguridad e Higiene · Diagnóstico de talleres · Check list de ventilación · Riesgos en soldadura · Expediente NOM-020-STPS | % de cumplimiento por rubro y general | Recorridos CSH, Seguridad en Talleres, Ventilación check list, Riesgos en soldadura (ppt), 020 Requisitos expedientes |
| Protección civil | **Evaluación de simulacro (PROFEPA)** | 6 roles, calificación 0–5 promediada sólo con apartados aplicables | Simulacros – Lista PROFEPA |
| Protección civil | Registro de simulacro de incendio · Análisis de riesgos del inmueble (≈ 230 reactivos) | Conteos y % por sección | Registro de Simulacro, Protección Civil – Evaluación de Riesgos |
| Medio ambiente | **Almacén de residuos peligrosos (RLGPGIR Art. 82)** | % de cumplimiento | Requisitos auditables – Almacenamiento RP |
| Medio ambiente | **Hoja de datos del registro de generador** | Total t/año y categoría (gran/pequeño/micro) | Registro de generadores de RP |
| Medio ambiente | **Matriz de requisitos legales – Agua (RLAN)** | Precargada con 12 artículos, % de cumplimiento | Reglamento Ley de Aguas Nacionales |
| Medio ambiente | **Incompatibilidad química** | Reacción entre 41 grupos, búsqueda en ~1 800 sustancias | Tabla de Incompatibilidad Química |
| Medio ambiente | **Materiales peligrosos (No. ONU)** | Buscador de 2 788 registros por número, nombre o clase | Tablas de Materiales Peligrosos |
| Estadística | **Pareto** · **Capacidad Cp/Cpk + carta I-MR** | Orden 80/20; Cp, Cpk, Pp, Ppk, histograma y carta de control | Herramientas adicionales |

> **Aviso legal.** Los formatos normativos (NOM, RLGPGIR, RLAN, OSHA) reproducen las plantillas
> originales y algunas datan de 2012–2013. Verifica la versión vigente de cada norma antes de
> usarlos en una auditoría. La hoja de generador de residuos **no sustituye** el trámite oficial.
> En OSHA, el TRIR se calcula con todos los casos registrables (G+H+I+J), como lo define OSHA.

## Cómo se usa

1. Doble clic en una herramienta del panel izquierdo (puedes filtrar escribiendo).
2. Llena el formato; los resultados y colores se actualizan al instante.
3. **Guardar** → archivo `.qtb.json` (texto legible, ideal para versionar).
4. **Exportar Excel** → `.xlsx` con formato y colores. **Imprimir / PDF** → HTML; en el navegador usa Ctrl+P → Guardar como PDF.
5. Cierra pestañas con clic derecho o Ctrl+W.

## Estructura

```
toolbox_calidad/
  app.py            ventana principal (catálogo + pestañas)
  catalog.py        registro de herramientas
  core/calc.py      cálculos puros (probados en tests/test_calc.py)
  core/export.py    exportación a Excel y HTML
  core/storage.py   guardar / abrir documentos
  ui/widgets.py     secciones reutilizables: campos, tabla, checklist, texto, firmas
  ui/base.py        ToolBase y FormTool (formatos por esquema)
  ui/charts.py      gráficas en Canvas (sin matplotlib)
  forms/            esquemas: mejora.py, seguridad.py, ambiental.py
  tools/            herramientas con lógica propia (AMEF, KPI, auditoría, ruido, OSHA…)
  data/             listas de verificación y tablas extraídas de los Excel originales
scripts/extraer_datos_excel.py   regenera data/ desde las plantillas
tests/              pruebas (la GUI se prueba sin pantalla con un Tkinter simulado)
```

## Añadir un formato nuevo

Crea un diccionario en `forms/` y agrégalo a la lista `FORMS` del módulo:

```python
MI_FORMATO = {
    "id": "5s", "title": "Auditoría 5S", "category": "Mejora continua (TPM)",
    "description": "…", "source": "…",
    "sections": [
        {"type": "fields", "key": "datos", "title": "Datos", "columns": 3,
         "fields": [{"key": "area", "label": "Área"}, {"key": "fecha", "label": "Fecha", "kind": "date", "default": "hoy"}]},
        {"type": "checklist", "key": "lista", "title": "Evaluación", "options": ["Sí", "No", "N/A"],
         "groups": [{"name": "Seiri", "items": [{"code": "1.1", "text": "Sólo hay lo necesario"}]}]},
        {"type": "table", "key": "acciones", "title": "Acciones", "rows": 3,
         "columns": [{"key": "accion", "label": "Acción", "width": 40},
                     {"key": "resp", "label": "Responsable", "width": 16}]},
    ],
}
```

Tipos de sección: `fields`, `choices`, `text`, `table` (con columnas calculadas `compute`,
`highlight` y `summary`), `checklist` (con `score` 0–5 opcional) y `signatures`.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Contribuir

Se agradecen formatos nuevos (5S, SMED, OEE, MSA/R&R, plan de control, Ishikawa…), traducciones
y correcciones normativas. Abre un *issue* o un *pull request*.

## Licencia

MIT — ver [LICENSE](LICENSE).
