"""Sustituto mínimo de tkinter para probar la interfaz sin pantalla (CI / servidores).

Las variables (StringVar, BooleanVar…) funcionan de verdad, con trazas; los widgets
aceptan cualquier argumento y guardan su configuración. Sólo para pruebas.
"""
import sys
import types


class TclError(Exception):
    pass


class Variable:
    _default = ""

    def __init__(self, master=None, value=None, name=None):
        self._v = self._default if value is None else value
        self._traces = []

    def get(self):
        return self._v

    def set(self, v):
        self._v = v
        for cb in list(self._traces):
            cb("x", "", "write")

    def trace_add(self, mode, cb):
        self._traces.append(cb)
        return str(len(self._traces))


class StringVar(Variable):
    def set(self, v):
        super().set("" if v is None else str(v))


class BooleanVar(Variable):
    _default = False

    def get(self):
        return bool(self._v)


class IntVar(Variable):
    _default = 0


class Misc:
    _counter = 0

    def __init__(self, master=None, *args, **kw):
        Misc._counter += 1
        self.master = master
        self._cfg = dict(kw)
        self._children = []
        self._name = f".w{Misc._counter}"
        if master is not None and hasattr(master, "_children"):
            master._children.append(self)
        tv = kw.get("textvariable")
        self._textvar = tv
        self._text = ""

    def __str__(self):
        return self._name

    # geometría / eventos
    def pack(self, *a, **k): pass
    def grid(self, *a, **k): pass
    def place(self, *a, **k): pass
    def pack_forget(self): pass
    def bind(self, *a, **k): pass
    def bind_all(self, *a, **k): pass
    def unbind_all(self, *a, **k): pass
    def columnconfigure(self, *a, **k): pass
    def rowconfigure(self, *a, **k): pass
    def after(self, ms, fn=None, *a):
        if fn:
            fn(*a)
    def after_idle(self, fn, *a):
        fn(*a)
    def update_idletasks(self): pass
    def destroy(self):
        if self.master is not None and self in getattr(self.master, "_children", []):
            self.master._children.remove(self)
    def winfo_reqwidth(self): return 100
    def option_add(self, *a, **k): pass
    def nametowidget(self, name): return name
    def focus_set(self): pass

    # configuración
    def configure(self, cnf=None, **kw):
        self._cfg.update(kw)
    config = configure
    def cget(self, k): return self._cfg.get(k, "")
    def __getitem__(self, k): return self._cfg.get(k)
    def __setitem__(self, k, v): self._cfg[k] = v
    def state(self, s=None): return ()

    # Entry / Combobox
    def get(self, *a):
        return self._textvar.get() if self._textvar is not None else self._text
    def insert(self, index, text, *a, **k):
        if self._textvar is not None:
            self._textvar.set(str(self._textvar.get()) + str(text))
        else:
            self._text += str(text)
        return None
    def delete(self, *a): self._text = ""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return lambda *a, **k: None


class Tk(Misc):
    def __init__(self, *a, **k):
        super().__init__(None)
    def title(self, *a): pass
    def geometry(self, *a): pass
    def minsize(self, *a): pass
    def protocol(self, *a): pass
    def mainloop(self): pass


class Toplevel(Misc):
    pass


class Text(Misc):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._text = ""
        self._mod = False
    def get(self, a="1.0", b="end"):
        return self._text
    def insert(self, idx, text, *tags):
        self._text += text
        self._mod = True
    def delete(self, a, b=None):
        self._text = ""
    def edit_modified(self, v=None):
        if v is None:
            return self._mod
        self._mod = v


class Canvas(Misc):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self.items = []
    def _create(self, kind, *a, **k):
        self.items.append((kind, a, k))
        return len(self.items)
    def create_line(self, *a, **k): return self._create("line", *a, **k)
    def create_rectangle(self, *a, **k): return self._create("rect", *a, **k)
    def create_oval(self, *a, **k): return self._create("oval", *a, **k)
    def create_text(self, *a, **k): return self._create("text", *a, **k)
    def create_window(self, *a, **k): return self._create("window", *a, **k)
    def delete(self, *a): self.items = []
    def bbox(self, *a): return (0, 0, 100, 100)


class Treeview(Misc):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._items = {}
        self._order = []
    def insert(self, parent, index, iid=None, **kw):
        iid = iid or f"I{len(self._items) + 1}"
        self._items[iid] = kw
        self._order.append(iid)
        return iid
    def delete(self, *iids):
        for i in iids:
            self._items.pop(i, None)
            if i in self._order:
                self._order.remove(i)
    def get_children(self, item=""):
        return tuple(self._order)
    def item(self, iid, **kw):
        return self._items.get(iid, {})
    def selection(self): return ()


class Notebook(Misc):
    def __init__(self, master=None, **kw):
        super().__init__(master, **kw)
        self._tabs = []
    def add(self, w, **kw): self._tabs.append(w)
    def select(self, w=None): return self._tabs[-1] if self._tabs else ""
    def tabs(self): return [str(t) for t in self._tabs]
    def forget(self, w):
        if w in self._tabs:
            self._tabs.remove(w)


class Style:
    def __init__(self, *a): pass
    def theme_use(self, *a): pass
    def configure(self, *a, **k): pass
    def map(self, *a, **k): pass


def _cls(name, base=Misc):
    return type(name, (base,), {})


def install():
    tk = types.ModuleType("tkinter")
    for n, o in dict(TclError=TclError, StringVar=StringVar, BooleanVar=BooleanVar, IntVar=IntVar, Tk=Tk,
                     Toplevel=Toplevel, Text=Text, Canvas=Canvas, Misc=Misc).items():
        setattr(tk, n, o)
    for n in ("Frame", "Label", "Entry", "Button", "Listbox", "Scrollbar", "Checkbutton", "Radiobutton", "Spinbox"):
        setattr(tk, n, _cls(n))
    tk.Listbox = _cls("Listbox")
    ttk = types.ModuleType("tkinter.ttk")
    for n in ("Frame", "Label", "Entry", "Button", "Scrollbar", "Checkbutton", "Radiobutton", "Combobox",
              "LabelFrame", "Separator", "PanedWindow", "Spinbox"):
        setattr(ttk, n, _cls(n))
    ttk.Treeview = Treeview
    ttk.Notebook = Notebook
    ttk.Style = Style
    mb = types.ModuleType("tkinter.messagebox")
    mb.showinfo = mb.showerror = mb.showwarning = lambda *a, **k: None
    mb.askyesno = lambda *a, **k: True
    fd = types.ModuleType("tkinter.filedialog")
    fd.askopenfilename = fd.asksaveasfilename = lambda *a, **k: ""
    tk.ttk, tk.messagebox, tk.filedialog = ttk, mb, fd
    sys.modules.update({"tkinter": tk, "tkinter.ttk": ttk, "tkinter.messagebox": mb, "tkinter.filedialog": fd})
    return tk
