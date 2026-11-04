"""Uso: python3 bajar_msg.py <message_id> <carpeta destino>  -> baja los adjuntos de planilla de un mail."""
import base64, os, sys, hashlib, glob
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
mid, DEST = sys.argv[1], sys.argv[2]; os.makedirs(DEST, exist_ok=True)
x = s.users().messages().get(userId='me', id=mid).execute()
hd = {h['name']: h['value'] for h in x['payload']['headers']}
print(hd.get('Date'), '|', hd.get('From'), '|', hd.get('Subject'), '| thread', x['threadId'], '| labels', x.get('labelIds'))
previos = {hashlib.md5(open(f, 'rb').read()).hexdigest(): f for f in glob.glob('/home/oficina1/Cloud/precios-mandrake/Procesados/*') + glob.glob('/home/oficina1/Cloud/precios-mandrake/Nuevos_*/*') if os.path.isfile(f)}
fecha = datetime.fromtimestamp(int(x['internalDate']) // 1000).strftime('%Y-%m-%dT%H-%M')
rem = hd.get('From', '').split('<')[-1].rstrip('>')
def partes(p):
    for q in p.get('parts', []) or []: yield from partes(q)
    if p.get('filename'): yield p
for p in partes(x['payload']):
    print('adjunto:', p['filename'])
    if not p['filename'].lower().endswith(('.xlsx', '.xls', '.ods', '.csv')): continue
    data = base64.urlsafe_b64decode(s.users().messages().attachments().get(userId='me', messageId=mid, id=p['body']['attachmentId']).execute()['data'])
    h = hashlib.md5(data).hexdigest()
    if h in previos: print('  REPETIDO de', previos[h]); continue
    nombre = ''.join(c for c in f"{fecha} [{rem}] {hd.get('Subject','')} - {p['filename']}" if c not in '\\/:*?"<>|')
    open(os.path.join(DEST, nombre), 'wb').write(data); print('  guardado:', nombre)
