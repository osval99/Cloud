# Con la primera fila en 0 ya seleccionada, extiende la selección con Shift+Abajo mientras
# la fila siga en 0, registra las filas y quita todo el bloque de una vez.
import sys, time, csv
sys.path.insert(0, '/home/oficina1/Cloud/precios-mandrake')
import cargar_fierro as ft, quitar_ceros_fierro as ceros

def main(ejecutar, arriba=False):
    ADEL, ATR = ('shift+Up', 'shift+Down') if arriba else ('shift+Down', 'shift+Up')
    sel = []
    f = ceros.leer()
    vistos = {r['isbn'] for r in f if r['sel']}
    sel += [r for r in f if r['sel']]
    for _ in range(400):
        ft.cu('key', ADEL); time.sleep(0.7)
        f = ceros.leer()
        nuevos = [r for r in f if r['sel'] and r['isbn'] not in vistos]
        if not nuevos:
            break                                   # fin de la grilla
        r = nuevos[0] if arriba else nuevos[-1]
        if r['var'] != 0.0:
            ft.cu('key', ATR); time.sleep(0.7)   # esa fila no es 0: sacarla de la selección
            break
        vistos.add(r['isbn']); sel.append(r)
    f = ceros.leer(); ceros.mostrar(f)
    print('filas en 0 seleccionadas:', len(sel))
    if any(r['sel'] and r['var'] != 0.0 for r in f):
        raise SystemExit('Hay una fila seleccionada que no es 0: no quito nada')
    if ejecutar:
        with open(f'{ft.DIR}/QUITADOS_variacion_0_{ft.NOM}.csv', 'a', newline='', encoding='utf-8-sig') as fh:
            w = csv.writer(fh)
            for r in sel: w.writerow([r['isbn'], r['tit'], r['viejo'], r['nuevo'], r['txt']])
        ft.cu('click', 1186, 506); time.sleep(2)     # Quitar
        ft.cu('shot', '/tmp/fierro_tandas/bloque_despues.png', 0, 490, 1340, 690)

if __name__ == '__main__':
    main('quitar' in sys.argv, 'arriba' in sys.argv)
