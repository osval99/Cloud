"""Al terminar la carga en Fierro: los mails con 'PRECIOS PARA ACTUALIZAR' Y 'En Proceso'
pasan a 'Resuelto' (se les quitan las dos). No toca mails que solo tengan 'En Proceso'
(esa etiqueta también se usa para transferencias, devoluciones, etc.)."""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
L = {l['name'].lower(): l['id'] for l in s.users().labels().list(userId='me').execute()['labels']}
PEND, PROC, RES = L['precios para actualizar'], L['en proceso'], L['resuelto']
msgs = s.users().messages().list(userId='me', labelIds=[PEND, PROC], maxResults=200).execute().get('messages', [])
for m in msgs:
    h = s.users().messages().get(userId='me', id=m['id'], format='metadata', metadataHeaders=['Subject', 'From']).execute()
    hd = {x['name']: x['value'] for x in h['payload']['headers']}
    if not {PEND, PROC} <= set(h.get('labelIds', [])):
        continue
    s.users().messages().modify(userId='me', id=m['id'], body={'addLabelIds': [RES], 'removeLabelIds': [PEND, PROC]}).execute()
    print('Resuelto |', hd.get('From', '')[:35], '|', hd.get('Subject', '')[:60])
quedan = s.users().messages().list(userId='me', labelIds=[PEND], maxResults=100).execute().get('messages', [])
print('quedan con PRECIOS PARA ACTUALIZAR:', len(quedan))
