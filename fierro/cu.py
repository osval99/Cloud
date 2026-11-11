#!/usr/bin/env python3
"""Control mínimo de pantalla X11: captura (xwd → PNG) y mouse/teclado (XTest). Sin dependencias.

Uso:
  cu.py shot [salida.png] [x0 y0 x1 y1]   captura (opcionalmente recortada)
  cu.py click X Y [boton] [n]             clic (boton 1=izq, 3=der; n=veces)
  cu.py move X Y
  cu.py type "texto"
  cu.py key Return|Tab|Escape|F2|ctrl+a ...
  cu.py scroll X Y up|down [n]
  cu.py soltar                            suelta Alt/Ctrl/Shift trabadas (click/move/type/key/scroll
                                          ya lo hacen antes de actuar; CU_NO_SOLTAR=1 lo desactiva)

Por defecto trabaja en la pantalla virtual :5 (Xephyr), donde solo corre Fierro.
CU_DISPLAY=:1 para el escritorio real (ahí guard() exige que la ventana activa sea Fierro).
"""
import ctypes, os, struct, subprocess, sys, time, zlib

DISPLAY = os.environ.get("CU_DISPLAY", ":5")
os.environ["DISPLAY"] = DISPLAY  # también para xwd y xprop

X11 = ctypes.cdll.LoadLibrary("libX11.so.6")
XTST = ctypes.cdll.LoadLibrary("libXtst.so.6")
X11.XOpenDisplay.restype = ctypes.c_void_p
X11.XOpenDisplay.argtypes = [ctypes.c_char_p]
X11.XStringToKeysym.restype = ctypes.c_ulong
X11.XStringToKeysym.argtypes = [ctypes.c_char_p]
X11.XKeysymToKeycode.restype = ctypes.c_ubyte
X11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
X11.XKeycodeToKeysym.restype = ctypes.c_ulong
X11.XKeycodeToKeysym.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_int]
X11.XFlush.argtypes = [ctypes.c_void_p]
XTST.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
XTST.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]

DPY = None
WIN = None  # si se fija, shot captura solo esa ventana


def dpy():
    global DPY
    if DPY is None:
        DPY = X11.XOpenDisplay(None)
        if not DPY:
            sys.exit("No se pudo abrir el display X")
    return DPY


def shot(out="/home/oficina1/fierro-claude/capturas/pantalla.png", box=None):
    raw = subprocess.run(["xwd", "-silent"] + (["-id", WIN] if WIN else ["-root"]), capture_output=True, check=True).stdout
    h = struct.unpack(">25I", raw[:100])
    header_size, w, hgt, byte_order, bpp, bpl, ncolors = h[0], h[4], h[5], h[7], h[11], h[12], h[19]
    if bpp not in (24, 32):
        sys.exit(f"bpp no soportado: {bpp}")
    off = header_size + ncolors * 12
    x0, y0, x1, y1 = box or (0, 0, w, hgt)
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(w, x1), min(hgt, y1)
    px = bpp // 8
    # Posición de R, G y B dentro de cada píxel según el orden de bytes de xwd
    idx = {(32, 0): (2, 1, 0), (32, 1): (1, 2, 3), (24, 0): (2, 1, 0), (24, 1): (0, 1, 2)}[(bpp, byte_order)]
    filas = []
    for y in range(y0, y1):
        linea = raw[off + y * bpl + x0 * px: off + y * bpl + x1 * px]
        rgb = bytearray(3 * (x1 - x0))
        for c in range(3):
            rgb[c::3] = linea[idx[c]::px]
        filas.append(b"\x00" + bytes(rgb))
    escribir_png(out, x1 - x0, y1 - y0, b"".join(filas))
    print(f"{out} {x1 - x0}x{y1 - y0}")


def escribir_png(path, w, h, datos):
    """PNG RGB de 8 bits; `datos` son las filas ya con su byte de filtro."""
    def chunk(tipo, contenido):
        return (struct.pack(">I", len(contenido)) + tipo + contenido
                + struct.pack(">I", zlib.crc32(tipo + contenido) & 0xFFFFFFFF))
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(datos, 6)) + chunk(b"IEND", b""))


def active_class():
    """WM_CLASS de la ventana activa (ej. 'fierro'), o '' si no se puede leer."""
    out = subprocess.run(["xprop", "-root", "_NET_ACTIVE_WINDOW"], capture_output=True, text=True).stdout
    win = out.strip().split()[-1] if "#" in out else ""
    if not win or win == "0x0":
        return ""
    cls = subprocess.run(["xprop", "-id", win, "WM_CLASS"], capture_output=True, text=True).stdout
    return cls.split("=", 1)[-1].strip().lower()


def guard():
    """Cancela si la ventana activa no es de Fierro: nunca tocar otras ventanas."""
    if DISPLAY != ":1":
        return  # pantalla virtual dedicada: no hay otras ventanas del usuario
    cls = active_class()
    if "fierro" not in cls:
        sys.exit(f"CANCELADO: la ventana activa no es Fierro ({cls or 'desconocida'})")


def soltar_trabadas(verbose=False):
    """Suelta modificadores que quedaron apretados (pasa seguido con Alt en :5).

    Solo en las pantallas virtuales: en :1 el teclado es el del usuario."""
    if DISPLAY == ":1" or os.environ.get("CU_NO_SOLTAR"):
        return []  # CU_NO_SOLTAR=1: para Ctrl+clic con Ctrl apretado aparte
    d = dpy()
    mapa = (ctypes.c_char * 32)()
    X11.XQueryKeymap(d, mapa)
    mods = {_kc(n) for n in ("Alt_L", "Alt_R", "Control_L", "Control_R", "Shift_L", "Shift_R",
                             "ISO_Level3_Shift", "Super_L", "Meta_L")} - {0}
    trabadas = [kc for kc in mods if mapa[kc // 8][0] >> (kc % 8) & 1]
    for kc in trabadas:
        XTST.XTestFakeKeyEvent(d, kc, 0, 0)
    if trabadas:
        X11.XFlush(d)
        time.sleep(0.05)
    if verbose or trabadas:
        print(f"Teclas trabadas soltadas: {trabadas}" if trabadas else "No había teclas trabadas",
              file=sys.stderr)
    return trabadas


def move(x, y):
    XTST.XTestFakeMotionEvent(dpy(), -1, x, y, 0)
    X11.XFlush(dpy())


def click(x, y, button=1, n=1):
    move(x, y)
    time.sleep(0.05)
    for _ in range(n):
        XTST.XTestFakeButtonEvent(dpy(), button, 1, 0)
        XTST.XTestFakeButtonEvent(dpy(), button, 0, 0)
        X11.XFlush(dpy())
        time.sleep(0.08)


def scroll(x, y, direction, n=3):
    click(x, y, 4 if direction == "up" else 5, n)


class XClientMessageEvent(ctypes.Structure):
    _fields_ = [("type", ctypes.c_int), ("serial", ctypes.c_ulong), ("send_event", ctypes.c_int),
                ("display", ctypes.c_void_p), ("window", ctypes.c_ulong), ("message_type", ctypes.c_ulong),
                ("format", ctypes.c_int), ("data", ctypes.c_long * 5)]


class XEvent(ctypes.Union):
    _fields_ = [("xclient", XClientMessageEvent), ("pad", ctypes.c_long * 24)]


def activate(win):
    """Trae al frente una ventana (por id) vía _NET_ACTIVE_WINDOW."""
    d = dpy()
    X11.XInternAtom.restype = ctypes.c_ulong
    X11.XInternAtom.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    X11.XDefaultRootWindow.restype = ctypes.c_ulong
    X11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    X11.XSendEvent.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_long, ctypes.POINTER(XEvent)]
    ev = XEvent()
    ev.xclient.type = 33  # ClientMessage
    ev.xclient.send_event = 1
    ev.xclient.window = win
    ev.xclient.message_type = X11.XInternAtom(d, b"_NET_ACTIVE_WINDOW", 0)
    ev.xclient.format = 32
    ev.xclient.data[0] = 2  # origen: herramienta de control
    mask = (1 << 20) | (1 << 19)  # SubstructureRedirect | SubstructureNotify
    X11.XSendEvent(d, X11.XDefaultRootWindow(d), 0, mask, ctypes.byref(ev))
    X11.XFlush(d)


def fit(win):
    """Mueve la ventana a (0,0) y la estira a toda la pantalla (sin gestor de ventanas)."""
    d = dpy()
    X11.XDefaultScreen.argtypes = [ctypes.c_void_p]
    X11.XDisplayWidth.argtypes = X11.XDisplayHeight.argtypes = [ctypes.c_void_p, ctypes.c_int]
    X11.XMoveResizeWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
    scr = X11.XDefaultScreen(d)
    X11.XMoveResizeWindow(d, win, 0, 0, X11.XDisplayWidth(d, scr), X11.XDisplayHeight(d, scr))
    X11.XFlush(d)


def _kc(name):
    ks = X11.XStringToKeysym(name.encode())
    return X11.XKeysymToKeycode(dpy(), ks)


def _press(kcs):
    for kc in kcs:
        XTST.XTestFakeKeyEvent(dpy(), kc, 1, 0)
    for kc in reversed(kcs):
        XTST.XTestFakeKeyEvent(dpy(), kc, 0, 0)
    X11.XFlush(dpy())
    time.sleep(0.03)


MODS = {"ctrl": "Control_L", "shift": "Shift_L", "alt": "Alt_L", "altgr": "ISO_Level3_Shift", "super": "Super_L"}


def key(combo):
    parts = combo.split("+")
    kcs = [_kc(MODS.get(p.lower(), p)) for p in parts]
    if 0 in kcs:
        sys.exit(f"Tecla desconocida: {combo}")
    _press(kcs)


DEAD = {"́": "dead_acute", "̀": "dead_grave", "̈": "dead_diaeresis", "̃": "dead_tilde"}


def _press_keysym(ks):
    """Pulsa la tecla que produce el keysym, con Shift/AltGr si hace falta. False si no hay tecla."""
    d = dpy()
    kc = X11.XKeysymToKeycode(d, ks)
    if not kc:
        return False
    level = next((i for i in (0, 1, 4, 5) if X11.XKeycodeToKeysym(d, kc, i) == ks), 0)
    shift, altgr = _kc("Shift_L"), _kc("ISO_Level3_Shift")
    mods = {0: [], 1: [shift], 4: [altgr], 5: [altgr, shift]}[level]
    _press(mods + [kc])
    return True


def type_text(text):
    import unicodedata
    for ch in text:
        if ch == "\n":
            key("Return")
            continue
        ks = ord(ch) if ord(ch) < 0x100 else 0x01000000 + ord(ch)
        if _press_keysym(ks):
            continue
        # Sin tecla directa (ej. 'í'): tecla muerta + letra base
        base, *marks = unicodedata.normalize("NFD", ch)
        dead = DEAD.get(marks[0]) if len(marks) == 1 else None
        if not (dead and _press_keysym(X11.XStringToKeysym(dead.encode())) and _press_keysym(ord(base))):
            sys.exit(f"Carácter sin tecla: {ch!r}")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0]
    if cmd == "shot":
        out = a[1] if len(a) > 1 else None
        box = tuple(map(int, a[2:6])) if len(a) >= 6 else None
        shot(out, box) if out else shot(box=box)
    elif cmd == "shotwin":
        WIN = a[1]
        shot(a[2] if len(a) > 2 else "/home/oficina1/fierro-claude/capturas/ventana.png")
    elif cmd == "active":
        print(active_class() or "desconocida")
    elif cmd in ("click", "move", "type", "key", "scroll"):
        guard()
        soltar_trabadas()
    elif cmd == "soltar":
        soltar_trabadas(verbose=True)
    if cmd == "click":
        click(int(a[1]), int(a[2]), int(a[3]) if len(a) > 3 else 1, int(a[4]) if len(a) > 4 else 1)
    elif cmd == "move":
        move(int(a[1]), int(a[2]))
    elif cmd == "type":
        type_text(a[1])
    elif cmd == "key":
        for k in a[1:]:
            key(k)
    elif cmd == "fit":
        fit(int(a[1], 0))
    elif cmd == "activate":
        activate(int(a[1], 0))
    elif cmd == "scroll":
        scroll(int(a[1]), int(a[2]), a[3], int(a[4]) if len(a) > 4 else 3)
