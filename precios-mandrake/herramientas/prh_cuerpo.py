import base64, json, re, html
import pandas as pd
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
m = [m for m in json.load(open('/tmp/links_scripts/mails_nuevos.json')) if 'Labati' in m['de']][0]
x = s.users().messages().get(userId='me', id=m['id']).execute()
htmls, txts = [], []
def rec(pl):
    for q in pl.get('parts', []) or []: rec(q)
    d = pl.get('body', {}).get('data')
    if d:
        t = base64.urlsafe_b64decode(d).decode('utf-8', 'ignore')
        (htmls if pl.get('mimeType') == 'text/html' else txts).append(t)
rec(x['payload'])
filas = []
if htmls:
    for tr in re.findall(r'<tr.*?</tr>', htmls[0], re.S | re.I):
        celdas = [html.unescape(re.sub(r'<[^>]+>', ' ', c)).strip() for c in re.findall(r'<t[dh].*?</t[dh]>', tr, re.S | re.I)]
        celdas = [re.sub(r'\s+', ' ', c) for c in celdas]
        if celdas and re.fullmatch(r'97[89]\d{10}', celdas[0].replace('-', '')):
            filas.append(celdas)
print('filas:', len(filas)); [print(f) for f in filas[:5]]
df = pd.DataFrame(filas)
print(df.shape)
df.columns = ['ISBN', 'TITULO', 'AUTOR', 'PVP Actual', 'PVP Nuevo', 'CAMBIO'][:df.shape[1]] + [f'c{i}' for i in range(max(0, df.shape[1] - 6))]
out = '/home/oficina1/Cloud/precios-mandrake/Nuevos_2026-11-02/2026-11-02T14-59 [Mariana.Labati@penguinrandomhouse.com] Cambios de PVP - 1-11-26 - cuerpo del mail.xlsx'
df.to_excel(out, index=False)
print(df.CAMBIO.value_counts() if 'CAMBIO' in df else '')
print(out)
