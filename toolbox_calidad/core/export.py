"""Exportación de reportes a Excel (.xlsx) y HTML imprimible.

Las herramientas convierten su contenido a una lista de *bloques* sencillos y
estos exportadores los escriben. Tipos de bloque:

* ``{"type": "heading", "text": str}``
* ``{"type": "kv", "title": str, "pairs": [(etiqueta, valor), ...]}``
* ``{"type": "table", "title": str, "headers": [...], "rows": [[...]],
  "highlight": {indice_fila: "rojo"|"ambar"|"verde"}}``
* ``{"type": "text", "title": str, "text": str}``
* ``{"type": "note", "text": str}``
"""
from __future__ import annotations

import datetime as _dt
import html
from pathlib import Path

from toolbox_calidad import APP_NAME

COLORES = {"rojo": "F8CBAD", "ambar": "FFE699", "verde": "C6EFCE", "gris": "E7E6E6"}
AZUL = "1F4E79"


def _s(v):
    if v is None:
        return ""
    if isinstance(v, float):
        return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))
    return str(v)


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------

def to_xlsx(path, title: str, blocks: list[dict], code: str = "") -> Path:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
    except ImportError as exc:  # pragma: no cover - depende del entorno
        raise RuntimeError("Para exportar a Excel instala openpyxl:  pip install openpyxl") from exc

    wb = Workbook()
    ws = wb.active
    clean = "".join(ch for ch in title if ch not in '[]:*?/\\¿').strip()
    ws.title = clean[:28] or "Formato"
    thin = Side(style="thin", color="9E9E9E")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    wrap = Alignment(wrap_text=True, vertical="top")
    head_fill = PatternFill("solid", fgColor=AZUL)
    sec_fill = PatternFill("solid", fgColor="DDEBF7")

    ncols = max([len(b.get("headers", [])) for b in blocks if b["type"] == "table"] + [4])
    widths = [12] * ncols

    def merge_row(r, text, font=None, fill=None, height=None):
        ws.cell(r, 1, text)
        if ncols > 1:
            ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=ncols)
        c = ws.cell(r, 1)
        c.alignment = wrap
        if font:
            c.font = font
        if fill:
            c.fill = fill
        if height:
            ws.row_dimensions[r].height = height

    r = 1
    merge_row(r, title, Font(bold=True, size=14, color="FFFFFF"), head_fill, 24)
    r += 1
    meta = f"{code + '  ·  ' if code else ''}Generado con {APP_NAME} el {_dt.date.today():%d/%m/%Y}"
    merge_row(r, meta, Font(italic=True, size=9, color="595959"))
    r += 2

    for b in blocks:
        t = b["type"]
        if t == "heading":
            merge_row(r, b["text"], Font(bold=True, size=12, color=AZUL))
            r += 1
        elif t == "note":
            merge_row(r, b["text"], Font(italic=True, size=9, color="595959"))
            r += 1
        elif t == "text":
            if b.get("title"):
                merge_row(r, b["title"], Font(bold=True), sec_fill)
                r += 1
            text = b.get("text") or ""
            lines = max(1, len(text) // 110 + text.count("\n") + 1)
            merge_row(r, text, height=min(400, 15 * lines))
            for col in range(1, ncols + 1):
                ws.cell(r, col).border = border
            r += 2
        elif t == "kv":
            if b.get("title"):
                merge_row(r, b["title"], Font(bold=True), sec_fill)
                r += 1
            for label, value in b["pairs"]:
                ws.cell(r, 1, label).font = Font(bold=True)
                ws.cell(r, 1).alignment = wrap
                ws.cell(r, 2, _s(value)).alignment = wrap
                if ncols > 2:
                    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=ncols)
                for col in range(1, ncols + 1):
                    ws.cell(r, col).border = border
                widths[0] = max(widths[0], min(40, len(str(label)) + 2))
                r += 1
            r += 1
        elif t == "table":
            if b.get("title"):
                merge_row(r, b["title"], Font(bold=True), sec_fill)
                r += 1
            for ci, h in enumerate(b["headers"], start=1):
                c = ws.cell(r, ci, h)
                c.font = Font(bold=True, color="FFFFFF")
                c.fill = head_fill
                c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
                c.border = border
                widths[ci - 1] = max(widths[ci - 1], min(18, len(str(h)) + 2))
            r += 1
            hl = b.get("highlight", {})
            for ri, row in enumerate(b["rows"]):
                fill = PatternFill("solid", fgColor=COLORES[hl[ri]]) if ri in hl else None
                for ci, v in enumerate(row, start=1):
                    num = v if isinstance(v, (int, float)) else None
                    c = ws.cell(r, ci, num if num is not None else _s(v))
                    c.alignment = wrap
                    c.border = border
                    if fill:
                        c.fill = fill
                    widths[ci - 1] = max(widths[ci - 1], min(60, len(_s(v)) + 2))
                r += 1
            r += 1

    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.page_setup.orientation = "landscape" if ncols > 6 else "portrait"
    ws.page_setup.fitToWidth = 1
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToHeight = 0
    path = Path(path)
    wb.save(path)
    return path


# ---------------------------------------------------------------------------
# HTML imprimible (Ctrl+P → Guardar como PDF)
# ---------------------------------------------------------------------------
CSS = """
body{font-family:Segoe UI,Arial,sans-serif;font-size:11pt;color:#222;margin:24px}
h1{background:#1F4E79;color:#fff;padding:10px 14px;font-size:16pt;margin:0}
.meta{color:#666;font-size:9pt;margin:4px 0 18px}
h2{color:#1F4E79;font-size:13pt;border-bottom:2px solid #1F4E79;padding-bottom:2px;margin-top:22px}
h3{background:#DDEBF7;font-size:11pt;padding:4px 8px;margin:14px 0 0}
table{border-collapse:collapse;width:100%;margin:0 0 12px}
th{background:#1F4E79;color:#fff;font-weight:600;padding:4px;border:1px solid #999;font-size:9.5pt}
td{border:1px solid #bbb;padding:4px;vertical-align:top;font-size:9.5pt}
td.k{font-weight:600;width:30%;background:#fafafa}
.txt{border:1px solid #bbb;padding:8px;min-height:40px;white-space:pre-wrap;margin-bottom:12px}
.note{color:#666;font-style:italic;font-size:9pt}
tr.rojo td{background:#F8CBAD} tr.ambar td{background:#FFE699} tr.verde td{background:#C6EFCE}
@media print{body{margin:8mm} h1{-webkit-print-color-adjust:exact;print-color-adjust:exact}
 th,tr.rojo td,tr.ambar td,tr.verde td,h3{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""


def to_html(path, title: str, blocks: list[dict], code: str = "") -> Path:
    e = html.escape
    out = [f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>{e(title)}</title>"
           f"<style>{CSS}</style></head><body><h1>{e(title)}</h1>"
           f"<div class='meta'>{e(code + ' · ') if code else ''}Generado con {e(APP_NAME)} "
           f"el {_dt.date.today():%d/%m/%Y}</div>"]
    for b in blocks:
        t = b["type"]
        if t == "heading":
            out.append(f"<h2>{e(b['text'])}</h2>")
        elif t == "note":
            out.append(f"<p class='note'>{e(b['text'])}</p>")
        elif t == "text":
            if b.get("title"):
                out.append(f"<h3>{e(b['title'])}</h3>")
            out.append(f"<div class='txt'>{e(b.get('text') or '')}</div>")
        elif t == "kv":
            if b.get("title"):
                out.append(f"<h3>{e(b['title'])}</h3>")
            out.append("<table>" + "".join(
                f"<tr><td class='k'>{e(str(k))}</td><td>{e(_s(v))}</td></tr>" for k, v in b["pairs"])
                + "</table>")
        elif t == "table":
            if b.get("title"):
                out.append(f"<h3>{e(b['title'])}</h3>")
            hl = b.get("highlight", {})
            rows = "".join(
                f"<tr class='{hl.get(i, '')}'>" + "".join(f"<td>{e(_s(v))}</td>" for v in row) + "</tr>"
                for i, row in enumerate(b["rows"]))
            out.append("<table><tr>" + "".join(f"<th>{e(str(h))}</th>" for h in b["headers"])
                       + f"</tr>{rows}</table>")
    out.append("</body></html>")
    path = Path(path)
    path.write_text("".join(out), encoding="utf-8")
    return path
