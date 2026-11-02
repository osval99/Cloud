# Quita de la grilla de Fierro las filas con Variación 0 (grilla ordenada por Variación).
# Uso: python3 ceros.py prueba   -> solo lee la vista actual
#      python3 ceros.py quitar   -> busca y quita todas las filas en 0
import subprocess, sys, time, re, csv
sys.path.insert(0, '/home/oficina1/Cloud/precios-mandrake')
import cargar_fierro as ft
from PIL import Image

FILAS = [563, 586, 609, 631]          # centros de las filas visibles
SHOT = '/tmp/fierro_tandas/c_grid.png'

def ocr(img):
    img = img.convert('L').resize((img.width * 3, img.height * 3))
    img.save('/tmp/fierro_tandas/c_cell.png')
    r = subprocess.run(['tesseract', '/tmp/fierro_tandas/c_cell.png', 'stdout', '--psm', '7'],
                       capture_output=True, text=True).stdout.strip()
    return r

def leer():
    ft.cu('shot', SHOT, 0, 0, 1340, 700); time.sleep(0.3)
    im = Image.open(SHOT)
    out = []
    for y in FILAS:
        var = ocr(im.crop((905, y - 11, 1070, y + 11)))
        isbn = ocr(im.crop((150, y - 11, 320, y + 11)))
        nuevo = ocr(im.crop((785, y - 11, 905, y + 11)))
        viejo = ocr(im.crop((665, y - 11, 785, y + 11)))
        tit = ocr(im.crop((318, y - 11, 665, y + 11)))
        px = im.getpixel((20, y))
        naranja = px[0] > 200 and px[1] < 140
        m = re.search(r'-?\d+[.,]\d{2}', var.replace(' ', ''))
        v = float(m.group().replace(',', '.')) if m else None
        out.append(dict(y=y, var=v, txt=var, isbn=isbn, nuevo=nuevo, viejo=viejo, tit=tit, sel=naranja))
    return out

def mostrar(f):
    for r in f: print('  ', r['y'], r['sel'] and 'SEL' or '   ', r['var'], '|', r['isbn'], '|', r['viejo'], '->', r['nuevo'], '|', r['tit'][:30])

def quitar_todos(maxq=1000):
    reg = open(f'{ft.DIR}/QUITADOS_variacion_0_{ft.NOM}.csv', 'a', newline='', encoding='utf-8-sig')
    w = csv.writer(reg)
    ft.teclas()
    ft.cu('click', 500, 563); time.sleep(0.8); ft.cu('key', 'ctrl+Home'); time.sleep(1.2)
    quitados, pasos = 0, 0
    while quitados < maxq and pasos < 400:
        pasos += 1
        ft.reconectar_si_hace_falta()
        f = leer()
        vals = [r['var'] for r in f if r['var'] is not None]
        ceros = [r for r in f if r['var'] == 0.0]
        if ceros:
            r = ceros[0]
            ft.cu('click', 500, r['y']); time.sleep(0.8)
            g = [x for x in leer() if x['y'] == r['y']][0]
            if not (g['sel'] and g['var'] == 0.0):
                print('  selección no verificada, reintento'); mostrar([g]); continue
            ft.cu('click', 1186, 506); time.sleep(1.5)            # Quitar
            quitados += 1
            w.writerow([g['isbn'], g['tit'], g['viejo'], g['nuevo'], g['txt']]); reg.flush()
            print(f'  quitado {quitados}: {g["isbn"]} {g["viejo"]} -> {g["nuevo"]}')
            continue
        if vals and min(vals) > 0:
            # ya pasamos la zona de ceros: subir y confirmar que arriba no queden
            ft.cu('scroll', 500, 600, 'up', 1); time.sleep(0.8)
            f2 = leer()
            if not any(r['var'] == 0.0 for r in f2) and any(r['var'] is not None and r['var'] < 0 for r in f2):
                break
            if not any(r['var'] == 0.0 for r in f2) and f2 == f:
                break
            continue
        ft.cu('scroll', 500, 600, 'down', 1); time.sleep(0.8)
        if leer() == f:                                          # llegó al final
            break
    reg.close()
    print('quitados:', quitados)

if __name__ == '__main__':
    if sys.argv[1] == 'prueba':
        mostrar(leer())
    else:
        quitar_todos()
