"""Guardar y abrir documentos (JSON legible, fácil de versionar en Git)."""
from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path

from toolbox_calidad import __version__

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
EXTENSION = ".qtb.json"


def data_path(*parts) -> Path:
    return DATA_DIR.joinpath(*parts)


def load_json(*parts):
    with open(data_path(*parts), encoding="utf-8") as fh:
        return json.load(fh)


def new_document(tool_id: str, title: str) -> dict:
    return {"herramienta": tool_id, "titulo": title, "app_version": __version__,
            "guardado": None, "secciones": {}}


def save_document(path, doc: dict) -> Path:
    path = Path(path)
    doc = dict(doc)
    doc["guardado"] = _dt.datetime.now().isoformat(timespec="seconds")
    doc["app_version"] = __version__
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_document(path, expected_tool: str | None = None) -> dict:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or "secciones" not in doc:
        raise ValueError("El archivo no es un documento de la toolbox")
    if expected_tool and doc.get("herramienta") != expected_tool:
        raise ValueError(f"El archivo corresponde a «{doc.get('titulo') or doc.get('herramienta')}», "
                         "no a esta herramienta")
    return doc
