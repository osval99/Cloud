"""Uso: python3 solo_cambios.py RESULTADO_FINAL_xxxx.csv carpeta_destino
Compara con todas las tandas ya cargadas en importaciones/precios_*/ y deja solo ISBN nuevos o con precio distinto."""
import pandas as pd, glob, math, os, sys
BASE = '/home/oficina1/fierro-claude/importaciones'
NUEVO, DEST = sys.argv[1], f'{BASE}/{sys.argv[2]}'
os.makedirs(DEST, exist_ok=True)
pv = sorted(glob.glob(f'{BASE}/precios_*/precios_*_tanda*.csv'), key=os.path.getmtime)
pv = [f for f in pv if not f.startswith(DEST)]
prev = {}
for f in pv:                                   # el más reciente pisa al anterior
    d = pd.read_csv(f, dtype={'ISBN': str}); prev.update(zip(d.ISBN, d.Precio))
r = pd.read_csv(NUEVO, dtype={'ISBN': str})
r['Prev'] = r.ISBN.map(prev)
igual = r.Prev == r.Precio
print('registros:', len(r), '| ya cargados igual:', igual.sum(),
      '| precio distinto:', (r.Prev.notna() & ~igual).sum(), '| ISBN nuevos:', r.Prev.isna().sum())
cambios = r[~igual].copy()
bajos = cambios.Precio < 1000
cambios[bajos].to_excel(f'{DEST}/EXCLUIDOS_precio_menor_1000.xlsx', index=False)
ok = cambios[~bajos].sort_values('ISBN')[['ISBN', 'Precio', 'Titulo', 'Origen']]
for c in ['Titulo', 'Origen']:
    ok[c] = ok[c].fillna('').astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
n = max(1, math.ceil(len(ok) / 5000)); size = math.ceil(len(ok) / n)
nombre = os.path.basename(DEST)
for i in range(n):
    p = ok.iloc[i * size:(i + 1) * size]
    p.to_csv(f'{DEST}/{nombre}_tanda{i+1}.csv', index=False, sep=',', encoding='utf-8-sig', lineterminator='\r\n')
    print(f'{nombre}_tanda{i+1}', len(p))
print('a cargar:', len(ok), '| excluidos < $1.000:', bajos.sum())
