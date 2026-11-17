"""Construye TODAS las herramientas con un tkinter simulado y prueba guardar/abrir/exportar."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import fake_tk  # noqa: E402

fake_tk.install()

import openpyxl  # noqa: E402
import pytest  # noqa: E402

from toolbox_calidad.catalog import build_catalog  # noqa: E402
from toolbox_calidad.core import export, storage  # noqa: E402

CATALOGO = build_catalog()


@pytest.mark.parametrize("item", CATALOGO, ids=[c["id"] for c in CATALOGO])
def test_herramienta(item, tmp_path):
    import tkinter as tk
    root = tk.Tk()
    tool = item["factory"](root)
    state = tool.get_state()
    blocks = tool.blocks()
    assert isinstance(blocks, list)
    x = export.to_xlsx(tmp_path / "f.xlsx", tool.title, blocks, tool.code)
    h = export.to_html(tmp_path / "f.html", tool.title, blocks, tool.code)
    assert openpyxl.load_workbook(x).active.max_row > 2
    assert "<table" in h.read_text(encoding="utf-8") or blocks == []
    if tool.savable:
        doc = storage.new_document(tool.tool_id, tool.title)
        doc["secciones"] = state
        p = storage.save_document(tmp_path / "d.qtb.json", doc)
        tool.set_state(storage.load_document(p, tool.tool_id)["secciones"])
        assert tool.get_state() == state


def _tool(tid):
    import tkinter as tk
    it = next(c for c in CATALOGO if c["id"] == tid)
    return it["factory"](tk.Tk())


def test_amef_rpn_y_orden():
    t = _tool("amef")
    sec = t.sections["amef"]
    sec.set([{"funcion": "A", "s": "8", "o": "8", "d": "1"}, {"funcion": "B", "s": "5", "o": "9", "d": "3"}])
    vals = sec.values()
    assert vals[0]["rpn"] == "64" and vals[1]["rpn"] == "135"
    t.sort_rpn()
    assert sec.values()[0]["funcion"] == "B"
    assert t._highlight(sec.values()[0]) == "rojo"


def test_dosimetria():
    t = _tool("ruido")
    sec = t.sections["dosimetria"]
    sec.set([{"nombre": "X", "tiempo": "8", "dosis": "200"}])
    v = sec.values()[0]
    assert v["ner"] == "93" and v["tmpe"] == "4.00 h"


def test_osha_resumen():
    t = _tool("osha")
    t.sections["datos"].put("horas", "200000")
    t.sections["casos"].set([{"caso": "1", "clase": "Días fuera del trabajo (H)", "dias_fuera": "5"},
                             {"caso": "2", "clase": "Otro caso registrable (J)"}])
    *_, idx = t.resumen()
    assert idx["TRIR"] == 2 and idx["LWIR"] == 1 and idx["LWSR"] == 5


def test_auditoria_total_y_acciones():
    t = _tool("auditoria_grupo")
    t.vars[(1, 0)].set(True)
    t.vars[(3, 0)].set(True)
    assert t.week_total(0) == 5
    t.generar_acciones()
    assert len(t.acciones.nonempty_values()) == 34


def test_checklist_resumen():
    t = _tool("almacen_rp")
    sec = t.sections["lista"]
    sec.fill_empty("S")
    sec.items[0][4].set("N")
    st = sec.stats()
    assert st["no_cumple"] == 1 and st["cumple"] == len(sec.items) - 1


def test_ventilacion():
    t = _tool("ventilacion_calc")
    d = t.sections["datos"]
    for k, v in (("l1", "10"), ("l2", "5"), ("l3", "3"), ("q", "1000")):
        d.put(k, v)
    r = t.calcular()
    assert r["vol_m3"] == 150 and round(r["n"], 2) == round(1000 * 60 / (150 * 35.3146667), 2)


def test_entrega_formatos_precargado_tras_nuevo():
    t = _tool("entrega_formatos")
    t.reset()
    assert len(t.sections["formatos"].values()) == 20


def test_ids_unicos():
    ids = [c["id"] for c in CATALOGO]
    assert len(ids) == len(set(ids))


def test_app_arranca():
    from toolbox_calidad.app import App
    app = App()
    for it in CATALOGO:
        app.open_tool(it["id"])
    assert len(app.open_tabs) == len(CATALOGO)
