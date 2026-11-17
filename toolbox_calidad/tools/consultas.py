"""Consultas: incompatibilidad química y materiales peligrosos para transporte."""
import csv
import tkinter as tk
from tkinter import ttk

from toolbox_calidad.core.calc import decodificar_reaccion, incompatibilidad
from toolbox_calidad.core.storage import data_path, load_json
from toolbox_calidad.ui.base import ToolBase

COLOR_CODIGO = {"E": "#C00000", "F": "#ED7D31", "gt": "#7030A0", "gf": "#ED7D31", "G": "#FFC000",
                "H": "#F4B183", "P": "#C00000", "S": "#8FAADC"}


def _color(code):
    if not code:
        return "#C6EFCE"
    if code == "EXTREMO" or "E" in code or "P" in code:
        return "#F8CBAD"
    if "F" in code or "gt" in code or "gf" in code or "GT" in code:
        return "#FCE4D6"
    return "#FFF2CC"


class IncompatibilidadTool(ToolBase):
    tool_id = "incompatibilidad"
    title = "Tabla de incompatibilidad química"
    code = "Grupos reactivos 1-34 y 101-107"
    source = "Tabla de Incompatibilidad Quimica_2.xls"
    description = ("Consulta la reacción esperada al mezclar dos grupos reactivos (H calor, F fuego, G gases, gt gases "
                   "tóxicos, gf gases inflamables, E explosión, P polimerización violenta, S solubilización de metales "
                   "tóxicos). Busca una sustancia para conocer su grupo. Útil para segregar el almacén de residuos y "
                   "materias primas. Siempre confirma con la hoja de datos de seguridad (HDS) del producto.")
    savable = False

    def build_body(self, parent):
        self.d = load_json("incompatibilidad_quimica.json")
        self.ultimo = None
        self.grupos = self.d["grupos"]
        opciones = [f"{k} – {v}" for k, v in self.grupos.items()]
        top = ttk.Frame(parent, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Grupo A:").grid(row=0, column=0, sticky="w")
        ttk.Label(top, text="Grupo B:").grid(row=1, column=0, sticky="w")
        self.a, self.b = tk.StringVar(), tk.StringVar()
        for i, v in enumerate((self.a, self.b)):
            cb = ttk.Combobox(top, textvariable=v, values=opciones, width=70, state="readonly")
            cb.grid(row=i, column=1, sticky="w", padx=6, pady=3)
            cb.bind("<<ComboboxSelected>>", lambda e: self.consultar())
        self.res = tk.Label(top, text="Elige dos grupos", font=("Segoe UI", 12, "bold"), anchor="w", justify="left",
                            background="#F2F2F2", padx=10, pady=8, width=90)
        self.res.grid(row=2, column=0, columnspan=2, sticky="we", pady=8)

        busq = ttk.LabelFrame(parent, text="¿En qué grupo está mi sustancia?", padding=8, style="Sec.TLabelframe")
        busq.pack(fill="x", padx=10)
        self.q = tk.StringVar()
        e = ttk.Entry(busq, textvariable=self.q, width=40)
        e.pack(side="left")
        e.bind("<Return>", lambda ev: self.buscar())
        ttk.Button(busq, text="Buscar", command=self.buscar).pack(side="left", padx=6)
        self.hits = ttk.Treeview(parent, columns=("grupo", "sustancia"), show="headings", height=6)  # ids no numéricos
        self.hits.heading("grupo", text="Grupo")
        self.hits.heading("sustancia", text="Sustancia (ejemplo de la tabla)")
        self.hits.column("grupo", width=320)
        self.hits.column("sustancia", width=520)
        self.hits.pack(fill="x", padx=10, pady=4)
        self.hits.bind("<Double-1>", self._usar_hit)
        ttk.Label(parent, text="Doble clic en un resultado para ponerlo como Grupo A (o B si A ya está elegido).",
                  style="Help.TLabel").pack(anchor="w", padx=10)

        mat = ttk.LabelFrame(parent, text="Matriz completa (filas = grupo, columnas = grupo con el que reacciona)",
                             padding=6, style="Sec.TLabelframe")
        mat.pack(fill="both", expand=True, padx=10, pady=6)
        keys = list(self.grupos)
        # Identificadores no numéricos: Tk interpreta "1", "2"… como índices de columna
        cols = ["g"] + [f"c{k}" for k in keys]
        self.tv = ttk.Treeview(mat, columns=cols, show="headings", height=12)
        self.tv.heading("g", text="Grupo")
        self.tv.column("g", width=260, stretch=False)
        for k in keys:
            self.tv.heading(f"c{k}", text=k)
            self.tv.column(f"c{k}", width=42, anchor="center", stretch=False)
        for k in keys:
            self.tv.insert("", "end", values=[f"{k} {self.grupos[k][:30]}"] +
                           [("—" if k == j else incompatibilidad(self.d["matriz"], k, j)) for j in keys])
        xs = ttk.Scrollbar(mat, orient="horizontal", command=self.tv.xview)
        ys = ttk.Scrollbar(mat, orient="vertical", command=self.tv.yview)
        self.tv.configure(xscrollcommand=xs.set, yscrollcommand=ys.set)
        ys.pack(side="right", fill="y")
        xs.pack(side="bottom", fill="x")
        self.tv.pack(fill="both", expand=True)

    def _key(self, var):
        return var.get().split(" – ")[0] if var.get() else None

    def consultar(self):
        a, b = self._key(self.a), self._key(self.b)
        if not a or not b:
            return
        code = incompatibilidad(self.d["matriz"], a, b)
        if a == b:
            txt = "Mismo grupo: normalmente compatibles entre sí (verifica la HDS)."
        elif code == "EXTREMO":
            txt = "⚠ Grupo 107: EXTREMADAMENTE REACTIVO — no se mezcle con ningún residuo o material químico."
        elif not code:
            txt = "✔ Sin reacción peligrosa indicada en la tabla para esta combinación."
        else:
            partes = decodificar_reaccion(code, self.d["nomenclatura"])
            txt = f"⚠ INCOMPATIBLES — código {code}:\n" + "\n".join(
                f"   {p}: {desc or 'código sin descripción en la tabla original'}" for p, desc in partes)
        self.res.configure(text=txt, background=_color(code if a != b else ""))
        self.ultimo = (a, b, code, txt)

    def buscar(self):
        q = self.q.get().strip().lower()
        self.hits.delete(*self.hits.get_children())
        if len(q) < 3:
            return
        n = 0
        for g, lst in self.d["ejemplos"].items():
            for s in lst:
                if q in s.lower():
                    self.hits.insert("", "end", values=(f"{g} – {self.grupos.get(g, '')}", s))
                    n += 1
        self.set_status(f"{n} coincidencias")

    def _usar_hit(self, _e):
        sel = self.hits.selection()
        if not sel:
            return
        g = self.hits.item(sel[0])["values"][0]
        (self.b if self.a.get() else self.a).set(g)
        self.consultar()

    def blocks(self):
        out = []
        if getattr(self, "ultimo", None):
            a, b, code, txt = self.ultimo
            out.append({"type": "kv", "title": "Consulta", "pairs": [
                ("Grupo A", f"{a} {self.grupos[a]}"), ("Grupo B", f"{b} {self.grupos[b]}"), ("Resultado", txt)]})
        keys = list(self.grupos)
        out.append({"type": "table", "title": "Matriz de incompatibilidad",
                    "headers": ["Grupo"] + keys,
                    "rows": [[f"{k} {self.grupos[k]}"] + [incompatibilidad(self.d["matriz"], k, j) if k != j else "—"
                                                          for j in keys] for k in keys]})
        out.append({"type": "kv", "title": "Nomenclatura", "pairs": list(self.d["nomenclatura"].items())})
        return out


class MaterialesPeligrososTool(ToolBase):
    tool_id = "matpel"
    title = "Materiales peligrosos para transporte (No. ONU)"
    code = "Lista de mercancías peligrosas"
    source = "Tablas de Materiales Peligrosos Para Su Transporte.xls (Tabla 2)"
    description = ("Busca por número ONU o por nombre: clase o división, riesgo secundario, grupo de envase/embalaje, "
                   "disposiciones especiales y cantidades limitadas/exceptuadas. Verifica siempre contra la edición "
                   "vigente de la NOM-002-SCT y las Recomendaciones de la ONU.")
    savable = False
    COLS = None

    def build_body(self, parent):
        with open(data_path("materiales_peligrosos.csv"), encoding="utf-8") as fh:
            rd = csv.reader(fh)
            self.COLS = next(rd)
            self.rows = [r for r in rd]
        top = ttk.Frame(parent, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Buscar (No. ONU o nombre):").pack(side="left")
        self.q = tk.StringVar()
        e = ttk.Entry(top, textvariable=self.q, width=40)
        e.pack(side="left", padx=6)
        e.bind("<KeyRelease>", lambda ev: self.after_idle(self.buscar))
        self.clase = tk.StringVar(value="Todas")
        clases = ["Todas"] + sorted({r[2].split()[0][:1] for r in self.rows if r[2]})
        ttk.Label(top, text="Clase:").pack(side="left", padx=(12, 2))
        cb = ttk.Combobox(top, textvariable=self.clase, values=clases, width=7, state="readonly")
        cb.pack(side="left")
        cb.bind("<<ComboboxSelected>>", lambda e: self.buscar())
        frame = ttk.Frame(parent, padding=(10, 0))
        frame.pack(fill="both", expand=True)
        ids = [f"c{i}" for i in range(len(self.COLS))]
        self.tv = ttk.Treeview(frame, columns=ids, show="headings")
        widths = [70, 420, 90, 90, 90, 120, 90, 90]
        for c, name, w in zip(ids, self.COLS, widths):
            self.tv.heading(c, text=name)
            self.tv.column(c, width=w, anchor="w" if w > 100 else "center")
        ys = ttk.Scrollbar(frame, orient="vertical", command=self.tv.yview)
        self.tv.configure(yscrollcommand=ys.set)
        ys.pack(side="right", fill="y")
        self.tv.pack(fill="both", expand=True)
        self.buscar()

    def resultados(self):
        q = self.q.get().strip().lower()
        cl = self.clase.get()
        out = []
        for r in self.rows:
            if cl != "Todas" and not r[2].startswith(cl):
                continue
            if q and not (q == r[0].lower() or (not q.isdigit() and q in r[1].lower()) or (q.isdigit() and r[0].startswith(q))):
                continue
            out.append(r)
        return out

    def buscar(self):
        self.tv.delete(*self.tv.get_children())
        res = self.resultados()
        for r in res[:1500]:
            self.tv.insert("", "end", values=r)
        self.set_status(f"{len(res)} registros" + (" (se muestran 1500)" if len(res) > 1500 else ""))

    def blocks(self):
        res = self.resultados()[:1500]
        return [{"type": "note", "text": f"Búsqueda: «{self.q.get()}» · clase {self.clase.get()} · {len(res)} registros"},
                {"type": "table", "title": "Resultados", "headers": self.COLS, "rows": res}]
