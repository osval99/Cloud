# Repite: seleccionar la fila en 0 más cercana al extremo de los negativos y quitar el bloque hacia arriba,
# hasta que no queden filas en 0 junto a los negativos. Grilla ordenada por Variación descendente.
import sys, time
sys.path.insert(0, '/home/oficina1/Cloud/precios-mandrake')
import cargar_fierro as ft, quitar_ceros_fierro as ceros, quitar_ceros_bloque as ceros_bloque
for vuelta in range(30):
    ft.cu('click', 500, 563); time.sleep(0.8); ft.cu('key', 'ctrl+End'); time.sleep(1.2)
    f = ceros.leer()
    zs = [r for r in f if r['var'] == 0.0]
    if not zs:
        print('no quedan ceros al final de la grilla'); ceros.mostrar(f); break
    ft.cu('click', 500, zs[-1]['y']); time.sleep(0.8)
    g = [x for x in ceros.leer() if x['y'] == zs[-1]['y']][0]
    if not (g['sel'] and g['var'] == 0.0):
        print('selección no verificada'); continue
    ceros_bloque.main(True, arriba=True)
    ft.cu('shot', '/tmp/fierro_tandas/cambios_n.png', 0, 495, 200, 518)
    print('vuelta', vuelta + 1, 'hecha')
