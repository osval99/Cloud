# Grilla ordenada por Variación descendente. Selecciona desde la primera fila en 0 (clic) hasta la última
# (Shift+clic), navegando con Ctrl+Home/Ctrl+End (mueven el foco sin cambiar la selección), verifica y Quitar.
import sys, time, ctypes
sys.path.insert(0, '/home/oficina1/Cloud/precios-mandrake')
import cargar_fierro as ft, quitar_ceros_fierro as ceros

def mod(code, down):
    x = ctypes.cdll.LoadLibrary('libX11.so.6'); t = ctypes.cdll.LoadLibrary('libXtst.so.6')
    x.XOpenDisplay.restype = ctypes.c_void_p
    d = ctypes.c_void_p(x.XOpenDisplay(b':5')); t.XTestFakeKeyEvent(d, code, down, 0); x.XFlush(d); x.XCloseDisplay(d)

def buscar_cero(direccion, ultimo):
    for _ in range(300):
        f = ceros.leer()
        z = [r for r in f if r['var'] == 0.0]
        if z: return f, (z[-1] if ultimo else z[0])
        ft.cu('scroll', 500, 600, direccion, 1); time.sleep(0.8)
    raise SystemExit('No encontré ceros')

def main(ejecutar):
    ft.teclas()
    ft.cu('click', 500, 563); time.sleep(0.6); ft.cu('key', 'ctrl+Home'); time.sleep(1.2)
    f, z1 = buscar_cero('down', False)
    ft.cu('click', 500, z1['y']); time.sleep(0.8)
    g = [r for r in ceros.leer() if r['y'] == z1['y']][0]
    if not (g['sel'] and g['var'] == 0.0): raise SystemExit('No se seleccionó la primera fila en 0')
    print('primer 0:', g['isbn'], g['tit'][:30])
    ft.cu('scroll', 500, 600, 'down', 1500); time.sleep(1.5)
    f, z2 = buscar_cero('up', True)
    mod(50, True); time.sleep(0.2); ft.cu('click', 500, z2['y']); time.sleep(0.3); mod(50, False); time.sleep(1.2)
    ft.teclas()
    f = ceros.leer(); ceros.mostrar(f)
    if any(r['sel'] and r['var'] != 0.0 for r in f) or not [r for r in f if r['y'] == z2['y']][0]['sel']:
        raise SystemExit('Selección de abajo incorrecta: no quito nada')
    ft.cu('scroll', 500, 600, 'up', 1500); time.sleep(1.5)
    for _ in range(300):
        f = ceros.leer()
        if any(r['sel'] and r['var'] != 0.0 for r in f): ceros.mostrar(f); raise SystemExit('Fila no-0 seleccionada arriba')
        if any(r['var'] == 0.0 for r in f):
            if not all(r['sel'] for r in f if r['var'] == 0.0): ceros.mostrar(f); raise SystemExit('Ceros sin seleccionar arriba')
            break
        ft.cu('scroll', 500, 600, 'down', 1); time.sleep(0.8)
    ceros.mostrar(f); print('selección verificada')
    if ejecutar:
        ft.cu('click', 1186, 506); time.sleep(5)
        ft.cu('shot', '/tmp/fierro_tandas/rapido_despues.png', 0, 490, 1340, 690)
        print('quitado')

if __name__ == '__main__':
    main('quitar' in sys.argv)
