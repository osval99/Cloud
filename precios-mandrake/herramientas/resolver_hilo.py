import sys
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
labels = s.users().labels().list(userId='me').execute()['labels']
N = {l['id']: l['name'] for l in labels}; L = {l['name'].lower(): l['id'] for l in labels}
PEND, PROC, RES = L['precios para actualizar'], L['en proceso'], L['resuelto']
tid = sys.argv[1]
t = s.users().threads().get(userId='me', id=tid, format='metadata', metadataHeaders=['Subject', 'From']).execute()
for m in t['messages']:
    hd = {h['name']: h['value'] for h in m['payload']['headers']}
    print('antes  |', hd.get('From', '')[:30], '|', [N.get(i, i) for i in m.get('labelIds', [])])
s.users().threads().modify(userId='me', id=tid, body={'addLabelIds': [RES], 'removeLabelIds': [PEND, PROC]}).execute()
t = s.users().threads().get(userId='me', id=tid, format='minimal').execute()
for m in t['messages']: print('después|', [N.get(i, i) for i in m.get('labelIds', [])])
