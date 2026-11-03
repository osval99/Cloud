"""Uso: python3 tandas.py RESULTADO.csv carpeta  -> divide todo el resultado en tandas de <=5000 (sin filtrar)."""
import pandas as pd, math, os, sys
BASE = '/home/oficina1/fierro-claude/importaciones'
DEST = f'{BASE}/{sys.argv[2]}'; os.makedirs(DEST, exist_ok=True)
r = pd.read_csv(sys.argv[1], dtype={'ISBN': str})
bajos = r.Precio < 1000
r[bajos].to_excel(f'{DEST}/EXCLUIDOS_precio_menor_1000.xlsx', index=False)
ok = r[~bajos].sort_values('ISBN')[['ISBN', 'Precio', 'Titulo', 'Origen']].copy()
for c in ['Titulo', 'Origen']:
    ok[c] = ok[c].astype(object).where(ok[c].notna(), '').astype(str).str.replace(r'[\r\n]+', ' ', regex=True).str.strip()
n = max(1, math.ceil(len(ok) / 5000)); size = math.ceil(len(ok) / n); nom = os.path.basename(DEST)
for i in range(n):
    ok.iloc[i * size:(i + 1) * size].to_csv(f'{DEST}/{nom}_tanda{i+1}.csv', index=False, encoding='utf-8-sig', lineterminator='\r\n')
    print(f'{nom}_tanda{i+1}', len(ok.iloc[i * size:(i + 1) * size]))
print('excluidos < $1.000:', bajos.sum())
