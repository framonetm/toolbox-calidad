"""Ventana principal: catálogo a la izquierda, herramientas abiertas en pestañas."""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import messagebox, ttk

from toolbox_calidad import APP_NAME, __version__
from toolbox_calidad.catalog import CATEGORIAS, build_catalog
from toolbox_calidad.ui.widgets import setup_styles


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{__version__}")
        self.geometry("1360x820")
        self.minsize(1000, 600)
        setup_styles(self)
        self.catalog = build_catalog()
        self.by_id = {it["id"]: it for it in self.catalog}
        self.open_tabs: dict[str, ttk.Frame] = {}

        pw = ttk.PanedWindow(self, orient="horizontal")
        pw.pack(fill="both", expand=True)
        left = ttk.Frame(pw, padding=6)
        pw.add(left, weight=0)
        ttk.Label(left, text="Herramientas", style="Title.TLabel").pack(anchor="w")
        self.filter = tk.StringVar()
        ent = ttk.Entry(left, textvariable=self.filter)
        ent.pack(fill="x", pady=4)
        ent.insert(0, "")
        self.filter.trace_add("write", lambda *a: self.fill_tree())
        self.tree = ttk.Treeview(left, show="tree", selectmode="browse")
        self.tree.column("#0", width=330)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.on_open)
        self.tree.bind("<Return>", self.on_open)
        ttk.Label(left, text="Doble clic para abrir · escribe arriba para filtrar", style="Help.TLabel").pack(anchor="w")

        right = ttk.Frame(pw)
        pw.add(right, weight=1)
        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True)
        self.nb.bind("<Button-2>", self.close_tab_at)
        self.nb.bind("<Button-3>", self.close_tab_at)
        self._home()
        self.fill_tree()
        self.bind_all("<Control-w>", lambda e: self.close_current())
        self.protocol("WM_DELETE_WINDOW", self.on_quit)

    # -- catálogo ----------------------------------------------------------
    def fill_tree(self):
        q = self.filter.get().strip().lower()
        self.tree.delete(*self.tree.get_children())
        for cat in CATEGORIAS:
            items = [it for it in self.catalog if it["category"] == cat and
                     (not q or q in (it["title"] + it["description"] + it["source"]).lower())]
            if not items:
                continue
            node = self.tree.insert("", "end", text=f"  {cat}  ({len(items)})", open=True)
            for it in items:
                self.tree.insert(node, "end", iid=it["id"], text=it["title"])

    def on_open(self, _e=None):
        sel = self.tree.selection()
        if sel and sel[0] in self.by_id:
            self.open_tool(sel[0])

    def open_tool(self, tool_id):
        if tool_id in self.open_tabs:
            self.nb.select(self.open_tabs[tool_id])
            return
        it = self.by_id[tool_id]
        self.config(cursor="watch")
        self.update_idletasks()
        try:
            frame = it["factory"](self.nb)
        except Exception as exc:
            messagebox.showerror(APP_NAME, f"No se pudo abrir «{it['title']}»:\n{exc}")
            raise
        finally:
            self.config(cursor="")
        title = it["title"] if len(it["title"]) < 34 else it["title"][:32] + "…"
        self.nb.add(frame, text=f" {title}  ✕ ")
        self.nb.select(frame)
        self.open_tabs[tool_id] = frame
        frame._tool_id = tool_id

    def close_tab_at(self, event):
        try:
            idx = self.nb.index(f"@{event.x},{event.y}")
        except tk.TclError:
            return
        self.close_tab(self.nb.tabs()[idx])

    def close_current(self):
        cur = self.nb.select()
        if cur:
            self.close_tab(cur)

    def close_tab(self, tab_name):
        w = self.nametowidget(tab_name)
        tid = getattr(w, "_tool_id", None)
        if tid is None:
            return
        if getattr(w, "dirty", False) and not messagebox.askyesno(APP_NAME, "Hay cambios sin guardar. ¿Cerrar de todos modos?"):
            return
        self.nb.forget(w)
        w.destroy()
        self.open_tabs.pop(tid, None)

    def on_quit(self):
        dirty = [self.by_id[t]["title"] for t, w in self.open_tabs.items() if getattr(w, "dirty", False)]
        if dirty and not messagebox.askyesno(APP_NAME, "Hay cambios sin guardar en:\n• " + "\n• ".join(dirty) + "\n\n¿Salir?"):
            return
        self.destroy()

    # -- inicio ------------------------------------------------------------
    def _home(self):
        f = ttk.Frame(self.nb, padding=24)
        self.nb.add(f, text=" Inicio ")
        ttk.Label(f, text=APP_NAME, style="Big.TLabel").pack(anchor="w")
        ttk.Label(f, text=f"Versión {__version__} · Software libre (MIT) para ingenieros de calidad, mejora continua, "
                          "seguridad e higiene y medio ambiente.", style="Help.TLabel").pack(anchor="w", pady=(2, 14))
        txt = ("Cómo se usa\n"
               "  1. Elige una herramienta en el panel izquierdo (doble clic).\n"
               "  2. Llena el formato; los cálculos (RPN, NER, índices, % de cumplimiento…) se actualizan solos.\n"
               "  3. «Guardar» crea un archivo .qtb.json que puedes volver a abrir, versionar en Git o compartir.\n"
               "  4. «Exportar Excel» genera un .xlsx con formato; «Imprimir / PDF» abre una versión HTML lista para "
               "imprimir o guardar como PDF (Ctrl+P).\n"
               "  5. Cierra pestañas con clic derecho / botón central sobre la pestaña o Ctrl+W.\n")
        ttk.Label(f, text=txt, justify="left").pack(anchor="w")
        grid = ttk.Frame(f)
        grid.pack(anchor="w", pady=10)
        for i, cat in enumerate(CATEGORIAS):
            items = [it for it in self.catalog if it["category"] == cat]
            box = ttk.LabelFrame(grid, text=f"{cat} ({len(items)})", padding=8, style="Sec.TLabelframe")
            box.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            for it in items:
                lb = ttk.Label(box, text="• " + it["title"], foreground="#1F4E79", cursor="hand2", wraplength=360)
                lb.pack(anchor="w")
                lb.bind("<Button-1>", lambda e, t=it["id"]: self.open_tool(t))
        ttk.Label(f, text="Aviso: los formatos legales (NOM, RLGPGIR, RLAN, OSHA) se basan en las plantillas originales; "
                          "verifica siempre la versión vigente de cada norma antes de una auditoría.",
                  style="Help.TLabel", wraplength=1000).pack(anchor="w", pady=(10, 0))


def main():
    try:
        app = App()
    except tk.TclError as exc:  # pragma: no cover
        print("No se pudo iniciar la interfaz gráfica (Tkinter):", exc, file=sys.stderr)
        sys.exit(1)
    app.mainloop()


if __name__ == "__main__":
    main()
