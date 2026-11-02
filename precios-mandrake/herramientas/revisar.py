import base64, re, json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
s = build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('/home/oficina1/Cloud/precios-mandrake/token.json'))
labs = s.users().labels().list(userId='me').execute()['labels']
nombre = {l['id']: l['name'] for l in labs}
lid = {l['name'].lower(): l['id'] for l in labs}['precios para actualizar']
msgs, p = [], None
while True:
    r = s.users().messages().list(userId='me', labelIds=[lid], pageToken=p).execute()
    msgs += r.get('messages', []); p = r.get('nextPageToken')
    if not p: break
print('MAILS CON LA ETIQUETA:', len(msgs))

def recorrer(pl, adj, txt):
    for q in pl.get('parts', []) or []:
        recorrer(q, adj, txt)
    if pl.get('filename'): adj.append(pl['filename'])
    d = pl.get('body', {}).get('data')
    if d and pl.get('mimeType', '').startswith('text/'):
        txt.append(base64.urlsafe_b64decode(d).decode('utf-8', 'ignore'))

res = []
for m in msgs:
    x = s.users().messages().get(userId='me', id=m['id']).execute()
    h = {k['name']: k['value'] for k in x['payload']['headers']}
    adj, txt = [], []; recorrer(x['payload'], adj, txt)
    adj = [a for a in adj if not a.lower().endswith(('.png', '.jpg', '.gif', '.jpeg'))]
    body = '\n'.join(txt)
    links = sorted(set(l.rstrip('.,);"\'') for l in re.findall(r'https?://[^\s"\'<>]+', body)))
    links = [l for l in links if not re.search(r'\.(png|jpe?g|gif)|fonts\.|w3\.org|unsubscribe|facebook|instagram|twitter|wa\.me|whatsapp|linkedin|youtube|schema', l, re.I)]
    etiquetas = [nombre.get(i, i) for i in x.get('labelIds', []) if not i.isupper() or i in nombre and nombre[i] != i]
    res.append({'id': m['id'], 'thread': x['threadId'], 'fecha': h.get('Date', ''), 'de': h.get('From', ''),
                'asunto': h.get('Subject', ''), 'adjuntos': adj, 'links': links, 'etiquetas': etiquetas,
                'texto': re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', body))[:600]})
    print(f"\n- {h.get('Date','')[:22]} | {h.get('From','')[:50]}\n  {h.get('Subject','')[:100]}\n  adjuntos: {adj}\n  etiquetas: {etiquetas}\n  links: {len(links)}")
json.dump(res, open('/tmp/links_scripts/mails_nuevos.json', 'w'), ensure_ascii=False, indent=1)
