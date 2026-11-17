"""Gráficas simples dibujadas en ``tk.Canvas`` (sin dependencias externas)."""
from __future__ import annotations

import math
import tkinter as tk

AZUL = "#1F4E79"
AZUL_CLARO = "#5B9BD5"
NARANJA = "#ED7D31"
VERDE = "#70AD47"
ROJO = "#C00000"
GRIS = "#7F7F7F"


def _nice_max(v):
    if v <= 0:
        return 1
    exp = 10 ** math.floor(math.log10(v))
    for m in (1, 1.2, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if m * exp >= v:
            return m * exp
    return 10 * exp


def _fmt(v):
    if abs(v) >= 1000:
        return f"{v:,.0f}"
    if abs(v) >= 10 or v == int(v):
        return f"{v:.0f}"
    return f"{v:.2f}".rstrip("0").rstrip(".")


class Chart(tk.Canvas):
    """Lienzo con ejes; ``draw(...)`` redibuja con los datos dados."""

    def __init__(self, master, width=760, height=320, **kw):
        super().__init__(master, width=width, height=height, background="white",
                         highlightthickness=1, highlightbackground="#BFBFBF", **kw)
        self.w, self.h = width, height
        self.m = dict(l=58, r=58, t=34, b=58)

    def _frame(self, title, ymin, ymax, labels, y2=False, ylabel=""):
        self.delete("all")
        m = self.m
        x0, x1, y0, y1 = m["l"], self.w - m["r"], self.h - m["b"], m["t"]
        self.create_text(self.w / 2, 14, text=title, font=("Segoe UI", 10, "bold"), fill=AZUL)
        for i in range(6):
            v = ymin + (ymax - ymin) * i / 5
            y = y0 - (y0 - y1) * i / 5
            self.create_line(x0, y, x1, y, fill="#E7E6E6")
            self.create_text(x0 - 6, y, text=_fmt(v), anchor="e", font=("Segoe UI", 8))
            if y2:
                self.create_text(x1 + 6, y, text=f"{20 * i}%", anchor="w", font=("Segoe UI", 8), fill=NARANJA)
        self.create_line(x0, y0, x1, y0, fill="#595959")
        self.create_line(x0, y0, x0, y1, fill="#595959")
        if ylabel:
            self.create_text(12, (y0 + y1) / 2, text=ylabel, angle=90, font=("Segoe UI", 8), fill=GRIS)
        n = max(1, len(labels))
        step = (x1 - x0) / n
        every = max(1, math.ceil(n / 20))
        for i, lab in enumerate(labels):
            if i % every == 0:
                self.create_text(x0 + step * (i + 0.5), y0 + 6, text=str(lab)[:14], anchor="ne" if n > 8 else "n",
                                 angle=35 if n > 8 else 0, font=("Segoe UI", 8))
        def sx(i):
            return x0 + step * (i + 0.5)
        def sy(v):
            return y0 - (y0 - y1) * (v - ymin) / ((ymax - ymin) or 1)
        return sx, sy, step, (x0, x1, y0, y1)

    def bars_and_lines(self, title, labels, bars=None, lines=(), ylabel="", bar_colors=None):
        """``bars``: valores; ``lines``: [(nombre, valores, color, discontinua)]."""
        vals = [v for v in (bars or []) if v is not None]
        for _, lv, _, _ in lines:
            vals += [v for v in lv if v is not None]
        if not vals:
            self._empty(title)
            return
        ymin = min(0, min(vals))
        ymax = _nice_max(max(vals) * 1.05) if max(vals) > 0 else 1
        sx, sy, step, (x0, x1, y0, y1) = self._frame(title, ymin, ymax, labels, ylabel=ylabel)
        if bars:
            for i, v in enumerate(bars):
                if v is None:
                    continue
                c = (bar_colors[i] if bar_colors and i < len(bar_colors) else None) or AZUL_CLARO
                self.create_rectangle(sx(i) - step * 0.35, sy(v), sx(i) + step * 0.35, sy(0), fill=c, outline="")
                if len(bars) <= 20:
                    self.create_text(sx(i), sy(v) - 3, text=_fmt(v), anchor="s", font=("Segoe UI", 7))
        legend_x = x0
        for name, lv, color, dash in lines:
            pts = [(sx(i), sy(v)) for i, v in enumerate(lv) if v is not None]
            if len(pts) >= 2:
                self.create_line(*[c for p in pts for c in p], fill=color, width=2, dash=(5, 3) if dash else None)
            for x, y in pts:
                self.create_oval(x - 2, y - 2, x + 2, y + 2, fill=color, outline=color)
            self.create_line(legend_x, self.h - 10, legend_x + 18, self.h - 10, fill=color, width=2,
                             dash=(5, 3) if dash else None)
            self.create_text(legend_x + 22, self.h - 10, text=name, anchor="w", font=("Segoe UI", 8))
            legend_x += 30 + 7 * len(name)

    def pareto(self, title, labels, values, cumulative_pct):
        if not values:
            self._empty(title)
            return
        ymax = _nice_max(sum(values))
        sx, sy, step, (x0, x1, y0, y1) = self._frame(title, 0, ymax, labels, y2=True, ylabel="Frecuencia")
        for i, v in enumerate(values):
            color = AZUL if cumulative_pct[i] - (100 * v / sum(values)) < 80 else AZUL_CLARO
            self.create_rectangle(sx(i) - step * 0.4, sy(v), sx(i) + step * 0.4, sy(0), fill=color, outline="white")
        pts = [(sx(i), y0 - (y0 - y1) * p / 100) for i, p in enumerate(cumulative_pct)]
        if len(pts) >= 2:
            self.create_line(*[c for p in pts for c in p], fill=NARANJA, width=2)
        for x, y in pts:
            self.create_oval(x - 3, y - 3, x + 3, y + 3, fill=NARANJA, outline=NARANJA)
        y80 = y0 - (y0 - y1) * 0.8
        self.create_line(x0, y80, x1, y80, fill=ROJO, dash=(4, 3))
        self.create_text(x1 - 4, y80 - 2, text="80 %", anchor="se", fill=ROJO, font=("Segoe UI", 8))

    def histogram(self, title, data, lie=None, lse=None, bins=None):
        data = [d for d in data if d is not None]
        if len(data) < 2:
            self._empty(title)
            return
        lo = min(data + [v for v in (lie,) if v is not None])
        hi = max(data + [v for v in (lse,) if v is not None])
        if hi == lo:
            hi = lo + 1
        k = bins or max(5, min(25, int(round(math.sqrt(len(data))))))
        width = (hi - lo) / k
        counts = [0] * k
        for d in data:
            counts[min(k - 1, int((d - lo) / width))] += 1
        labels = [_fmt(lo + width * (i + 0.5)) for i in range(k)]
        sx, sy, step, (x0, x1, y0, y1) = self._frame(title, 0, _nice_max(max(counts)), labels, ylabel="Frecuencia")
        for i, c in enumerate(counts):
            self.create_rectangle(sx(i) - step / 2, sy(c), sx(i) + step / 2, sy(0), fill=AZUL_CLARO, outline="white")
        def xval(v):
            return x0 + (x1 - x0) * (v - lo) / (hi - lo)
        for v, name in ((lie, "LIE"), (lse, "LSE")):
            if v is not None:
                self.create_line(xval(v), y0, xval(v), y1, fill=ROJO, width=2, dash=(5, 3))
                self.create_text(xval(v), y1 - 2, text=name, anchor="s", fill=ROJO, font=("Segoe UI", 8, "bold"))

    def control(self, title, data, center, ucl, lcl):
        labels = [str(i + 1) for i in range(len(data))]
        if not data:
            self._empty(title)
            return
        vals = data + [ucl, lcl]
        span = (max(vals) - min(vals)) or 1
        ymin, ymax = min(vals) - span * 0.1, max(vals) + span * 0.1
        sx, sy, step, (x0, x1, y0, y1) = self._frame(title, ymin, ymax, labels)
        for v, c, n in ((center, VERDE, "LC"), (ucl, ROJO, "LCS"), (lcl, ROJO, "LCI")):
            self.create_line(x0, sy(v), x1, sy(v), fill=c, dash=(5, 3) if n != "LC" else None)
            self.create_text(x1 + 4, sy(v), text=f"{n} {_fmt(v)}", anchor="w", fill=c, font=("Segoe UI", 8))
        pts = [(sx(i), sy(v)) for i, v in enumerate(data)]
        if len(pts) >= 2:
            self.create_line(*[c for p in pts for c in p], fill=AZUL, width=1.5)
        for i, (x, y) in enumerate(pts):
            out = data[i] > ucl or data[i] < lcl
            r = 4 if out else 2.5
            self.create_oval(x - r, y - r, x + r, y + r, fill=ROJO if out else AZUL, outline="")

    def _empty(self, title):
        self.delete("all")
        self.create_text(self.w / 2, 14, text=title, font=("Segoe UI", 10, "bold"), fill=AZUL)
        self.create_text(self.w / 2, self.h / 2, text="Captura datos para ver la gráfica", fill=GRIS)
