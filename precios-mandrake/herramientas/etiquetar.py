import json, sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
L = {l['name'].lower(): l['id'] for l in s.users().labels().list(userId='me').execute()['labels']}
PEND, PROC, RES = L['precios para actualizar'], L['en proceso'], L['resuelto']
mails = json.load(open('/tmp/links_scripts/mails_nuevos.json'))

def es(m, *claves):
    t = (m['de'] + ' ' + m['asunto']).lower()
    return all(c.lower() in t for c in claves)

for m in mails:
    if es(m, 'GRUPAL, ESTE DOLOR'):
        accion = None
    elif es(m, 'UNL') or es(m, 'Herramienta', 'Actualización de precios noviembre') or es(m, 'AKAL - AUMENTO'):
        accion = ('repetido -> Resuelto', [RES], [PEND, PROC])
    else:
        accion = ('nuevo -> En Proceso', [PROC], [])
    if not accion:
        print('sin cambios      |', m['asunto'][:70]); continue
    s.users().messages().modify(userId='me', id=m['id'], body={'addLabelIds': accion[1], 'removeLabelIds': accion[2]}).execute()
    print(f'{accion[0]:17}|', m['de'][:35], '|', m['asunto'][:60])
