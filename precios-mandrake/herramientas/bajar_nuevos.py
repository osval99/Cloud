import base64, json, os, hashlib, glob, re
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

DEST = '/home/oficina1/Cloud/precios-mandrake/Nuevos_2026-11-02'
os.makedirs(DEST, exist_ok=True)
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
mails = json.load(open('/tmp/links_scripts/mails_nuevos.json'))

def md5(b): return hashlib.md5(b).hexdigest()
previos = {}
for f in glob.glob('/home/oficina1/Cloud/precios-mandrake/Procesados/*'):
    previos[md5(open(f, 'rb').read())] = os.path.basename(f)

vistos = {}
salida = []
for m in mails:
    x = s.users().messages().get(userId='me', id=m['id']).execute()
    fecha = datetime.fromtimestamp(int(x['internalDate']) // 1000).strftime('%Y-%m-%dT%H-%M')
    rem = m['de'].split('<')[-1].rstrip('>')
    def partes(pl):
        for q in pl.get('parts', []) or []:
            yield from partes(q)
        if pl.get('filename', '').lower().endswith(('.xlsx', '.xls', '.ods', '.csv')):
            yield pl
    for pl in partes(x['payload']):
        att = s.users().messages().attachments().get(userId='me', messageId=m['id'], id=pl['body']['attachmentId']).execute()
        data = base64.urlsafe_b64decode(att['data'])
        h = md5(data)
        estado = 'NUEVO'
        if h in previos: estado = f'REPETIDO (ya procesado: {previos[h][:70]})'
        elif h in vistos: estado = f'REPETIDO (mismo adjunto en otro mail de esta tanda)'
        else:
            nombre = f"{fecha} [{rem}] {m['asunto']} - {pl['filename']}"
            nombre = ''.join(c for c in nombre if c not in '\\/:*?"<>|')
            open(os.path.join(DEST, nombre), 'wb').write(data)
            vistos[h] = nombre
        salida.append((m['id'], rem, pl['filename'], estado))
        print(f"{estado[:60]:60} | {rem[:30]:30} | {pl['filename']}")
json.dump(salida, open('/tmp/links_scripts/adjuntos_estado.json', 'w'), ensure_ascii=False, indent=1)
