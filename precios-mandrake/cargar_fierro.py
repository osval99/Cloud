# Ayudante para importar tandas de precios en Fierro (pantalla virtual :5 de la PC Linux).
# Usa ~/fierro-claude/cu.py. Las tandas van en DIR con nombre precios_<mes>_tandaN.csv:
# ajustar DIR y los nombres de archivo cada mes.
# Uso: python3 cargar_fierro.py <fase> <n_tanda>
#   preparar  -> abre el asistente, configura CSV/ISBN/precio/filtro LINEA y hace Finish
#   errores   -> guarda errores_precios_nov2026_tandaN.csv y cierra resultados
#   aplicar   -> Aplicar y espera a que la grilla quede vacía
import ctypes, hashlib, os, subprocess, sys, time

CU = ['python3', '-I', '/home/oficina1/fierro-claude/cu.py']
DIR = '/home/oficina1/fierro-claude/importaciones/precios_nov2026'
os.makedirs('/tmp/fierro_tandas', exist_ok=True)
REF0 = 'ed3e162887d49ddfbb9e58d17401c5aa'   # captura de "Cambios de precio: 0"

def cu(*a):
    subprocess.run(CU + [str(x) for x in a], check=True, capture_output=True)

def teclas():
    x = ctypes.cdll.LoadLibrary('libX11.so.6'); t = ctypes.cdll.LoadLibrary('libXtst.so.6')
    x.XOpenDisplay.restype = ctypes.c_void_p
    d = ctypes.c_void_p(x.XOpenDisplay(b':5')); k = (ctypes.c_char * 32)(); x.XQueryKeymap(d, k)
    p = [i * 8 + b for i in range(32) for b in range(8) if k[i][0] >> b & 1]
    for code in p:                       # soltar cualquier tecla trabada (ej. Alt = 64)
        t.XTestFakeKeyEvent(d, code, False, 0)
    x.XFlush(d)
    if p: print('  [teclas trabadas soltadas]', p)

def ventanas():
    out = subprocess.run("DISPLAY=:5 xwininfo -root -tree", shell=True, capture_output=True, text=True).stdout
    res = {}
    for line in out.splitlines():
        if '("fierro"' in line:
            wid = line.split()[0]
            info = subprocess.run(f"DISPLAY=:5 xwininfo -id {wid}", shell=True, capture_output=True, text=True).stdout
            if 'IsViewable' in info:
                name = line.split('"')[1] if '"' in line else ''
                res[wid] = name
    return res

def reconectar_si_hace_falta():
    for wid, n in ventanas().items():
        if n == 'Reconectar':
            print('  [reconectando]'); cu('click', 895, 426); time.sleep(8)
            return True
    return False

def esperar(nombre, seg=120):
    t0 = time.time()
    while time.time() - t0 < seg:
        reconectar_si_hace_falta()
        for wid, n in ventanas().items():
            if n == nombre: return wid
        time.sleep(1.5)
    raise SystemExit(f'No apareció la ventana "{nombre}" en {seg}s')

def escribir(texto):
    teclas(); cu('type', texto); time.sleep(0.5); teclas()

def preparar(n):
    teclas(); reconectar_si_hace_falta()
    cu('move', 600, 400); time.sleep(1)
    abiertas = [v for v in ventanas().values() if v not in ('fierro', 'FIERRO - Predeterminado ')]
    if abiertas: raise SystemExit(f'Hay diálogos abiertos: {abiertas}')
    cu('click', 778, 46); esperar('Importación de precios'); time.sleep(1.5)
    cu('click', 1020, 171); time.sleep(1.2); cu('click', 1010, 232); time.sleep(1.2)   # Personalizado
    cu('click', 620, 132); escribir(f'{DIR}/precios_nov2026_tanda{n}.csv'); cu('key', 'Tab'); time.sleep(1)
    cu('click', 673, 172); time.sleep(0.8)                                             # línea 2
    cu('click', 1113, 172); time.sleep(2.5)                                            # vista previa
    cu('shot', f'/tmp/fierro_tandas/t{n}_1.png', 193, 102, 1146, 588)
    cu('click', 998, 560); time.sleep(2.5)                                             # Next: ISBN col 1
    cu('shot', f'/tmp/fierro_tandas/t{n}_2.png', 193, 102, 1146, 588)
    cu('click', 998, 560); time.sleep(2.5)                                             # Next: precio
    cu('click', 792, 131); time.sleep(0.8)                                             # col 2
    cu('shot', f'/tmp/fierro_tandas/t{n}_3.png', 193, 102, 1146, 588)
    cu('click', 998, 560); time.sleep(2.5)                                             # Next: filtro
    reconectar_si_hace_falta()
    cu('click', 1112, 134); esperar('Ingresar el filtro'); time.sleep(1.5)
    cu('click', 1120, 328); time.sleep(1.2); cu('click', 815, 422); time.sleep(1)      # LINEA
    cu('shot', f'/tmp/fierro_tandas/t{n}_4.png', 193, 102, 1146, 588)
    cu('click', 1002, 512); time.sleep(2)                                              # Aceptar filtro
    cu('shot', f'/tmp/fierro_tandas/t{n}_5.png', 193, 102, 1146, 588)
    print('  listo para Finish; revisar capturas t%d_1..5' % n)

def finish(n):
    teclas(); cu('click', 998, 560)
    esperar('Resultados de la importación de precios', 600); time.sleep(2)
    cu('shot', f'/tmp/fierro_tandas/t{n}_6.png', 304, 102, 1035, 588)

def errores(n):
    teclas(); cu('click', 380, 567)
    wid = esperar('Guardar archivo de errores'); time.sleep(1.5)
    cu('fit', wid); time.sleep(1.5)
    cu('click', 700, 27); time.sleep(0.5)
    ruta = f'{DIR}/errores_precios_nov2026_tanda{n}.csv'
    escribir(ruta)
    cu('shot', f'/tmp/fierro_tandas/t{n}_7.png', 0, 0, 1340, 60)
    if 'Guardar archivo de errores' not in ventanas().values():
        raise SystemExit('El diálogo de guardar se cerró solo: revisar')
    cu('key', 'Return'); time.sleep(3)
    if not os.path.exists(ruta): raise SystemExit('No se guardó el archivo de errores')
    print('  errores guardados:', ruta)
    esperar('Resultados de la importación de precios', 10)
    cu('click', 988, 567); time.sleep(2)                                               # Cerrar
    cu('click', 960, 539); time.sleep(2)                                               # ordenar por variación
    cu('shot', f'/tmp/fierro_tandas/t{n}_8.png', 0, 490, 1340, 690)
    cu('click', 500, 563); time.sleep(0.8); cu('key', 'ctrl+Home'); time.sleep(1.5)
    cu('shot', f'/tmp/fierro_tandas/t{n}_9.png', 0, 490, 1340, 690)
    cu('key', 'ctrl+End'); time.sleep(1.5)
    cu('shot', f'/tmp/fierro_tandas/t{n}_10.png', 0, 490, 1340, 690)

def aplicar(n):
    teclas(); cu('click', 1280, 609)
    t0 = time.time()
    while time.time() - t0 < 900:
        time.sleep(10); reconectar_si_hace_falta()
        cu('shot', '/tmp/fierro_tandas/cambios.png', 0, 495, 200, 518)
        if hashlib.md5(open('/tmp/fierro_tandas/cambios.png', 'rb').read()).hexdigest() == REF0:
            print(f'  aplicado en {int(time.time()-t0)}s'); return
    raise SystemExit('La grilla no quedó vacía en 15 min')

def quitar(n, extremo, cuantas):
    """Quita 'cuantas' filas del principio ('arriba') o del final ('abajo') de la grilla,
    seleccionándolas con clic. Deja capturas antes y después."""
    teclas()
    for i in range(cuantas):
        cu('click', 500, 563); time.sleep(0.8)
        cu('key', 'ctrl+Home' if extremo == 'arriba' else 'ctrl+End'); time.sleep(1.2)
        y = 563 if extremo == 'arriba' else 631          # primera / última fila visible
        cu('click', 500, y); time.sleep(0.8)
        cu('shot', f'/tmp/fierro_tandas/t{n}_sel{i+1}.png', 0, 490, 1340, 690)
        cu('click', 1186, 506); time.sleep(1.5)                                         # Quitar
    cu('click', 500, 563); time.sleep(0.8)
    cu('key', 'ctrl+Home' if extremo == 'arriba' else 'ctrl+End'); time.sleep(1.2)
    cu('shot', f'/tmp/fierro_tandas/t{n}_despues.png', 0, 490, 1340, 690)

def registrar(fila):
    """fila = 'tanda|isbn|titulo|precio fierro|precio nuevo|variacion|motivo'"""
    import csv
    f = f'{DIR}/RAROS_precios_nov2026.csv'
    with open(f, 'a', newline='', encoding='utf-8-sig') as fh:
        csv.writer(fh).writerow(fila.split('|'))
    print(open(f, encoding='utf-8-sig').read())

def captura(nombre, *zona):
    cu('shot', f'/tmp/fierro_tandas/{nombre}.png', *zona)

if __name__ == '__main__':
    fase = sys.argv[1]
    if fase == 'quitar':
        quitar(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]))
    elif fase == 'registrar':
        for fila in sys.argv[2:]: registrar(fila)
    elif fase == 'captura':
        captura(sys.argv[2], *sys.argv[3:])
    else:
        n = int(sys.argv[2])
        {'preparar': preparar, 'finish': finish, 'errores': errores, 'aplicar': aplicar}[fase](n)
    print('  ventanas:', list(ventanas().values()))
