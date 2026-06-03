# -*- coding: utf-8 -*-
"""
Descarga adjuntos Excel/ODS de Gmail (actualizar.mandrakelibros@gmail.com)
y los guarda en la carpeta actual listos para procesar con agente2.py.

Primera vez: abre el navegador para autenticarte con Google.
Las siguientes veces usa el token guardado (token.json).
"""

import os
import base64
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
EXTENSIONES = ('.xlsx', '.xls', '.ods', '.csv')


def autenticar():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    return creds


def descargar_adjuntos():
    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    # Buscar correos con adjuntos Excel/ODS no marcados como RESUELTO
    query = 'has:attachment (filename:xlsx OR filename:xls OR filename:ods OR filename:csv) -label:RESUELTO'
    results = service.users().messages().list(userId='me', q=query).execute()
    mensajes = results.get('messages', [])

    if not mensajes:
        print("No hay correos nuevos con adjuntos.")
        return

    print(f"Encontrados {len(mensajes)} correos con adjuntos.\n")
    descargados = 0

    for msg_ref in mensajes:
        msg = service.users().messages().get(userId='me', id=msg_ref['id']).execute()

        # Obtener asunto para mostrar
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
        asunto = headers.get('Subject', '(sin asunto)')
        fecha_ts = int(msg['internalDate']) // 1000
        fecha = datetime.fromtimestamp(fecha_ts).strftime('%Y-%m-%dT%H-%M')
        remitente = headers.get('From', '')

        def procesar_partes(partes):
            nonlocal descargados
            for parte in partes:
                # Recursivo para partes anidadas
                if parte.get('parts'):
                    procesar_partes(parte['parts'])

                filename = parte.get('filename', '')
                if not filename or not filename.lower().endswith(EXTENSIONES):
                    continue

                att_id = parte['body'].get('attachmentId')
                if not att_id:
                    continue

                att = service.users().messages().attachments().get(
                    userId='me', messageId=msg_ref['id'], id=att_id
                ).execute()

                data = base64.urlsafe_b64decode(att['data'])
                nombre_archivo = f"{fecha} [{remitente.split('<')[-1].rstrip('>')}] {asunto} - {filename}"
                # Limpiar caracteres inválidos para nombre de archivo
                nombre_archivo = "".join(c for c in nombre_archivo if c not in r'\/:*?"<>|')
                ruta = os.path.join(BASE_DIR, nombre_archivo)

                with open(ruta, 'wb') as f:
                    f.write(data)

                print(f"  ✓ {filename}")
                print(f"    → {nombre_archivo}")
                descargados += 1

        if msg['payload'].get('parts'):
            procesar_partes(msg['payload']['parts'])

    print(f"\nTotal descargados: {descargados} archivos.")
    print("Ahora podés correr agente2.py para procesarlos.")


if __name__ == '__main__':
    descargar_adjuntos()
