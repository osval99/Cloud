# -*- coding: utf-8 -*-
"""
Pipeline completo de actualización de precios:
1. Baja adjuntos Excel/ODS del mail
2. Procesa con agente2.py en modo automático
3. Mueve archivos procesados a Procesados/
4. Marca los mails como RESUELTO en Gmail
"""

import os
import sys
import glob
import shutil
import base64
import subprocess
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_FILE = os.path.join(BASE_DIR, 'credentials.json')
PROCESADOS_DIR = os.path.join(BASE_DIR, 'Procesados')
EXTENSIONES = ('.xlsx', '.xls', '.ods', '.csv')
LABEL_RESUELTO = 'Label_2923983642399414539'


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


def bajar_adjuntos(service):
    print("\n" + "="*60)
    print("PASO 1: Bajando adjuntos del mail")
    print("="*60)

    query = 'has:attachment (filename:xlsx OR filename:xls OR filename:ods OR filename:csv) -label:RESUELTO'
    results = service.users().messages().list(userId='me', q=query).execute()
    mensajes = results.get('messages', [])

    if not mensajes:
        print("No hay correos nuevos con adjuntos.")
        return [], []

    print(f"Encontrados {len(mensajes)} correos con adjuntos.")
    archivos_descargados = []
    ids_procesados = []

    for msg_ref in mensajes:
        msg = service.users().messages().get(userId='me', id=msg_ref['id']).execute()
        headers = {h['name']: h['value'] for h in msg['payload'].get('headers', [])}
        asunto = headers.get('Subject', '(sin asunto)')
        fecha_ts = int(msg['internalDate']) // 1000
        fecha = datetime.fromtimestamp(fecha_ts).strftime('%Y-%m-%dT%H-%M')
        remitente = headers.get('From', '')

        descargado_algo = False

        def procesar_partes(partes):
            nonlocal descargado_algo
            for parte in partes:
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
                nombre = f"{fecha} [{remitente.split('<')[-1].rstrip('>')}] {asunto} - {filename}"
                nombre = "".join(c for c in nombre if c not in r'\/:*?"<>|')
                ruta = os.path.join(BASE_DIR, nombre)
                with open(ruta, 'wb') as f:
                    f.write(data)
                print(f"  ✓ {filename}")
                archivos_descargados.append(ruta)
                descargado_algo = True

        if msg['payload'].get('parts'):
            procesar_partes(msg['payload']['parts'])

        if descargado_algo:
            ids_procesados.append(msg_ref['id'])

    print(f"Total descargados: {len(archivos_descargados)} archivos.")
    return ids_procesados, archivos_descargados


def procesar_archivos(archivos_descargados):
    print("\n" + "="*60)
    print("PASO 2: Procesando con agente2.py")
    print("="*60)

    cmd = [sys.executable, os.path.join(BASE_DIR, 'agente2.py'), '--auto'] + archivos_descargados
    resultado = subprocess.run(cmd, cwd=BASE_DIR)
    return resultado.returncode == 0


def mover_a_procesados(archivos_descargados):
    print("\n" + "="*60)
    print("PASO 3: Moviendo archivos procesados")
    print("="*60)

    os.makedirs(PROCESADOS_DIR, exist_ok=True)
    movidos = 0

    for archivo in archivos_descargados:
        nombre = os.path.basename(archivo)
        if nombre.startswith('~$'):
            continue
        destino = os.path.join(PROCESADOS_DIR, nombre)
        try:
            shutil.move(archivo, destino)
            print(f"  → {nombre}")
            movidos += 1
        except PermissionError:
            print(f"  [AVISO] No se pudo mover '{nombre}' — está abierto en otro programa.")

    print(f"Total movidos: {movidos} archivos.")


def marcar_resuelto(service, ids_mensajes):
    print("\n" + "="*60)
    print("PASO 4: Marcando mails como RESUELTO")
    print("="*60)

    for msg_id in ids_mensajes:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'addLabelIds': [LABEL_RESUELTO]}
        ).execute()
        print(f"  ✓ Mail {msg_id} marcado como RESUELTO")

    print(f"Total marcados: {len(ids_mensajes)} mails.")


def main():
    print("\n" + "="*60)
    print("ACTUALIZACIÓN DE PRECIOS — MANDRAKE")
    print(datetime.now().strftime('%d/%m/%Y %H:%M'))
    print("="*60)

    creds = autenticar()
    service = build('gmail', 'v1', credentials=creds)

    ids_procesados, archivos_descargados = bajar_adjuntos(service)

    if not ids_procesados:
        print("\nNo hay nada nuevo para procesar. Fin.")
        return

    ok = procesar_archivos(archivos_descargados)

    mover_a_procesados(archivos_descargados)

    if ok:
        marcar_resuelto(service, ids_procesados)

    print("\n" + "="*60)
    print("PROCESO COMPLETADO.")
    print("="*60)


if __name__ == '__main__':
    main()
