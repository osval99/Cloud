"""Pone 'En Proceso' a los mails de mails_nuevos.json (los que tienen listas nuevas)."""
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
L = {l['name'].lower(): l['id'] for l in s.users().labels().list(userId='me').execute()['labels']}
for m in json.load(open('/tmp/links_scripts/mails_nuevos.json')):
    s.users().messages().modify(userId='me', id=m['id'], body={'addLabelIds': [L['en proceso']]}).execute()
    print('En Proceso |', m['asunto'][:70])
