import math

import pytest

from toolbox_calidad.core import calc


def test_rpn():
    assert calc.rpn(8, 8, 1) == 64          # ejemplo del AMEF original
    assert calc.rpn("5", "9", "3") == 135
    assert calc.rpn("", 2, 3) is None
    with pytest.raises(ValueError):
        calc.rpn(11, 1, 1)


def test_ventilacion_formato_original():
    # Hoja original: 1 m³ = 35.3 ft³, Q = 1 CFM → N = 1.6997
    assert calc.cambios_aire_por_hora(1, 35.3) == pytest.approx(1.69971671, rel=1e-6)
    assert calc.caudal_requerido_cfm(6, 600) == pytest.approx(60)


def test_nom011():
    assert calc.ner_desde_dosis(100, 8) == pytest.approx(90.0)
    assert calc.tmpe_horas(90) == pytest.approx(8)
    assert calc.tmpe_horas(93) == pytest.approx(4)
    assert calc.tmpe_horas(105) == pytest.approx(0.25)
    assert calc.ner_desde_dosis(200, 8) == pytest.approx(90 + 9.97 * math.log10(2))
    assert calc.nre(95, 12) == 83
    assert "vigilancia" in calc.clasificar_ner(86)


def test_osha():
    r = calc.indices_osha(muertes=0, casos_dias_perdidos=2, casos_restringidos=1, otros_registrables=3,
                          dias_perdidos=20, dias_restringidos=5, horas=400_000)
    assert r["TRIR"] == pytest.approx(3.0)
    assert r["DART"] == pytest.approx(1.5)
    assert r["LWIR"] == pytest.approx(1.0)
    assert r["LWSR"] == pytest.approx(10.0)
    assert r["OSHA SR"] == pytest.approx(12.5)
    assert calc.indices_osha(horas=0)["TRIR"] is None


def test_generador():
    assert calc.categoria_generador(12) == "Gran generador"
    assert calc.categoria_generador(10) == "Gran generador"
    assert calc.categoria_generador(1) == "Pequeño generador"
    assert calc.categoria_generador(0.4) == "Microgenerador"


def test_checklist():
    r = calc.resumen_checklist(["Sí", "No", "N/A", "", "Sí"])
    assert r == {"cumple": 2, "no_cumple": 1, "na": 1, "sin_respuesta": 1, "porcentaje": pytest.approx(66.666, 0.01)}
    assert calc.promedio_calificaciones(["5", "", "3"]) == 4


def test_pareto():
    p = calc.pareto([("A", 10), ("B", 60), ("C", 30)])
    assert [x["categoria"] for x in p] == ["B", "C", "A"]
    assert p[-1]["acumulado"] == pytest.approx(100)


def test_capacidad():
    datos = [10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 10.1, 9.9]
    r = calc.capacidad(datos, 9, 11)
    assert r["media"] == pytest.approx(10.0)
    assert r["Cp"] > 1 and r["Cpk"] > 1
    assert r["fuera_especificacion"] == 0


def test_incompatibilidad():
    from toolbox_calidad.core.storage import load_json
    d = load_json("incompatibilidad_quimica.json")
    assert calc.incompatibilidad(d["matriz"], 1, 104) == calc.incompatibilidad(d["matriz"], 104, 1) == "Hgt"
    assert calc.incompatibilidad(d["matriz"], 107, 3) == "EXTREMO"
    partes = calc.decodificar_reaccion("HFgt", d["nomenclatura"])
    assert [p for p, _ in partes] == ["H", "F", "gt"]
