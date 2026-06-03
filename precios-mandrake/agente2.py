# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import pandas as pd
import glob
import os
import re
import json
from datetime import datetime

# ─────────────────────────────────────────────
#  CONFIGURACION GUARDADA
#  Se almacena en agente2_config.json
#  { "nombre_archivo|hoja": {"isbn": 3, "precio": 5, "titulo": 1} }
# ─────────────────────────────────────────────
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agente2_config.json")

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def guardar_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

# ─────────────────────────────────────────────
#  LIMPIEZA
# ─────────────────────────────────────────────

def limpiar_precio_ar(valor):
    if pd.isna(valor) or valor == '': return 0.0
    if isinstance(valor, (int, float)): return float(valor)
    s = re.sub(r'[^\d,.]', '', str(valor).strip())
    if not s: return 0.0
    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'): s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '')
    elif ',' in s: s = s.replace(',', '.')
    elif '.' in s:
        partes = s.split('.')
        if len(partes[-1]) == 3: s = s.replace('.', '')
    try: return float(s)
    except: return 0.0

def limpiar_isbn(valor):
    if pd.isna(valor): return ""
    return re.sub(r'[^\d]', '', str(valor).split('.')[0].strip())

def col_clean(col):
    return re.sub(r'[.\s_\-/]', '', str(col).lower())

# ─────────────────────────────────────────────
#  DETECCION ESTRICTA DE COLUMNAS
#  Solo retorna resultado si es 100% inequívoco
# ─────────────────────────────────────────────

# Keywords que claramente identifican ISBN (fuerte)
ISBN_KEYS   = ['isbn', 'ean13', 'ean', 'codigodebarra', 'codigodebarras', 'codbar',
               'codbarra', 'coddebarras', 'coddebarra', 'codigobarras',
               'isbnean', 'eanisbn', 'isbnissn']

# Keywords débiles para ISBN — solo válidos si el contenido confirma ISBNs
ISBN_KEYS_DEBIL = ['codigo', 'cod', 'codigointerno', 'codinterno', 'codigoproducto']

# Keywords que claramente identifican precio (sin ambigüedad)
PRECIO_KEYS = ['pvp', 'p.v.p', 'preciodelist', 'preciofinal']

# Keywords que refuerzan "precio nuevo"
NUEVO_KEYS  = ['nuevo', 'actual', 'vigente', 'final', 'junio', 'julio', 'agosto',
               'mayo', 'abril', 'marzo', 'enero', 'febrero', 'sept', 'oct', 'nov',
               'dic', 'ene', 'feb', '2026', '2025']

# Palabras que NO son precio aunque digan "precio" o "nuevo"
NO_PRECIO   = ['novedad', 'cambio', 'anio', 'año', 'edicion', 'stock', 'familia',
               'seccion', 'coleccion', 'genero', 'autor', 'titulo', 'descripcion',
               'editorial', 'estado', 'observ', 'nota', 'descuento', 'bonif']

def detectar_columnas_estricto(df):
    """
    Detección ESTRICTA. Solo retorna columnas si hay certeza total.
    Retorna (col_isbn, col_precio, col_titulo, motivo_fallo)
    Si hay cualquier duda retorna (None, None, None, motivo)
    """
    # ── ISBN ──────────────────────────────────────────────
    candidatos_isbn = []
    for i, col in enumerate(df.columns):
        c = col_clean(col)
        if any(k == c or c.startswith(k) or c.endswith(k) for k in ISBN_KEYS):
            candidatos_isbn.append((i, col))

    if len(candidatos_isbn) == 0:
        # Nivel 2: encabezado débil + contenido confirma ISBNs
        for i, col in enumerate(df.columns):
            c = col_clean(col)
            if any(k == c or c.startswith(k) for k in ISBN_KEYS_DEBIL):
                muestra = df.iloc[:20, i].dropna()
                hits_any = sum(1 for v in muestra if len(limpiar_isbn(v)) in [10, 13])
                if len(muestra) > 0 and hits_any / len(muestra) >= 0.6:
                    candidatos_isbn.append((i, col))

    if len(candidatos_isbn) == 0:
        # Nivel 3: buscar por contenido en TODAS las columnas
        # Acepta cualquier columna donde >= 60% de valores sean números de 10 o 13 dígitos
        mejor_col, mejor_score, mejor_score13 = -1, 0, 0
        for i in range(len(df.columns)):
            muestra = df.iloc[:30, i].dropna()
            if len(muestra) == 0: continue
            hits13  = sum(1 for v in muestra if len(limpiar_isbn(v)) == 13)
            hits_any = sum(1 for v in muestra if len(limpiar_isbn(v)) in [10, 13])
            score13  = hits13  / len(muestra)
            score_any = hits_any / len(muestra)
            # Preferir columnas con más ISBN de 13 dígitos
            if score_any >= 0.6 and (score13 > mejor_score13 or
               (score13 == mejor_score13 and score_any > mejor_score)):
                mejor_col, mejor_score, mejor_score13 = i, score_any, score13
        if mejor_col >= 0:
            candidatos_isbn.append((mejor_col, df.columns[mejor_col]))

    if len(candidatos_isbn) == 0:
        return None, None, None, "No se encontró columna ISBN (ni por encabezado ni por contenido)"

    # Si hay múltiples candidatos ISBN, preferir el de 13 dígitos
    if len(candidatos_isbn) > 1:
        mejor_isbn = None
        mejor_hits13 = -1
        for i, col in candidatos_isbn:
            muestra = df.iloc[:20, i].dropna()
            hits13 = sum(1 for v in muestra if len(limpiar_isbn(v)) == 13)
            if hits13 > mejor_hits13:
                mejor_hits13 = hits13
                mejor_isbn = (i, col)
        col_isbn, nombre_isbn = mejor_isbn
    else:
        col_isbn, nombre_isbn = candidatos_isbn[0]

    # Verificar que la columna ISBN realmente contenga ISBNs
    muestra_isbn = df.iloc[:20, col_isbn].dropna()
    hits_isbn = sum(1 for v in muestra_isbn if len(limpiar_isbn(v)) in [10, 13])
    if len(muestra_isbn) > 0 and hits_isbn / len(muestra_isbn) < 0.5:
        return None, None, None, f'Columna "{nombre_isbn}" no contiene ISBNs válidos ({hits_isbn}/{len(muestra_isbn)})'

    # ── PRECIO ────────────────────────────────────────────
    candidatos_precio_nuevo = []
    candidatos_precio_gen   = []

    for i, col in enumerate(df.columns):
        if i == col_isbn: continue
        c = col_clean(col)

        # Descartar si contiene palabras que no son precio
        if any(k in c for k in NO_PRECIO): continue

        tiene_precio = any(k in c for k in PRECIO_KEYS) or 'precio' in c
        tiene_nuevo  = any(k in c for k in NUEVO_KEYS)

        # Verificar que tenga valores numéricos > 100 (precio de libro AR)
        muestra_p = df.iloc[:20, i].dropna()
        precios_validos = [limpiar_precio_ar(v) for v in muestra_p]
        hits_precio = sum(1 for p in precios_validos if p > 100)
        es_numerico = len(muestra_p) > 0 and hits_precio / len(muestra_p) >= 0.5

        if tiene_precio and tiene_nuevo and es_numerico:
            candidatos_precio_nuevo.append((i, col))
        elif tiene_precio and es_numerico:
            candidatos_precio_gen.append((i, col))

    # Regla estricta: exactamente 1 candidato claro
    if len(candidatos_precio_nuevo) == 1:
        col_precio = candidatos_precio_nuevo[0][0]
    elif len(candidatos_precio_nuevo) == 0 and len(candidatos_precio_gen) == 1:
        col_precio = candidatos_precio_gen[0][0]
    elif len(candidatos_precio_nuevo) > 1:
        nombres = [str(df.columns[c[0]]) for c in candidatos_precio_nuevo]
        return None, None, None, f"Precio ambiguo: {', '.join(nombres)}"
    elif len(candidatos_precio_gen) > 1:
        nombres = [str(df.columns[c[0]]) for c in candidatos_precio_gen]
        return None, None, None, f"Precio ambiguo: {', '.join(nombres)}"
    else:
        # Fallback: buscar por contenido numérico en todas las columnas
        # (para columnas sin encabezado claro como "Unnamed: 8")
        mejor_col, mejor_score = -1, 0
        for i in range(len(df.columns)):
            if i == col_isbn: continue
            muestra_p = df.iloc[:20, i].dropna()
            if len(muestra_p) == 0: continue
            precios = [limpiar_precio_ar(v) for v in muestra_p]
            hits = sum(1 for p in precios if p > 100)
            score = hits / len(muestra_p)
            if score > mejor_score and score >= 0.6:
                mejor_score, mejor_col = score, i
        if mejor_col >= 0:
            col_precio = mejor_col
        else:
            return None, None, None, "No se encontró columna de precio (ni por encabezado ni por contenido)"

    # ── TITULO (opcional, no bloquea) ─────────────────────
    col_titulo = None
    for i, col in enumerate(df.columns):
        if i in [col_isbn, col_precio]: continue
        c = col_clean(col)
        if any(k in c for k in ['titulo', 'title', 'obra', 'detalle']):
            col_titulo = i
            break

    return col_isbn, col_precio, col_titulo, None

# ─────────────────────────────────────────────
#  DETECCION DE FILA HEADER
# ─────────────────────────────────────────────

def detectar_fila_header(df_raw):
    KEYWORDS = ['isbn', 'pvp', 'precio', 'ean', 'codigo', 'titulo', 'title', 'autor']
    mejor, mejor_hits = 0, 0
    for i, row in df_raw.iterrows():
        linea = [col_clean(str(x)) for x in row.values]
        hits = sum(1 for x in linea if any(k in x for k in KEYWORDS))
        if hits > mejor_hits:
            mejor_hits, mejor = hits, i
        if hits >= 3 and i >= 5:  # no romper antes de fila 5, puede haber headers tardíos
            break

    # Verificar que la fila detectada no sea en realidad una fila de datos
    # (si algún valor de esa fila es un ISBN, no es el header real)
    fila_candidata = df_raw.iloc[mejor]
    isbn_en_header = sum(1 for v in fila_candidata if len(limpiar_isbn(str(v))) in [10, 13])
    if isbn_en_header >= 1:
        # La "fila header" contiene ISBNs — no es un header real
        # Buscar la fila anterior como header, o usar 0
        return max(0, mejor - 1) if mejor > 0 else 0

    return mejor if mejor_hits >= 1 else 0

# ─────────────────────────────────────────────
#  INTERFAZ DE CONSULTA INTERACTIVA
# ─────────────────────────────────────────────

def consultar_usuario(archivo, hoja, df, motivo_fallo):
    """
    Muestra preview del archivo y pide al usuario que indique las columnas.
    Retorna (col_isbn, col_precio, col_titulo) o None si el usuario omite.
    """
    print(f"\n{'!'*60}")
    print(f"[CONSULTA] {os.path.basename(archivo)} | Hoja: '{hoja}'")
    print(f"Motivo: {motivo_fallo}")
    print(f"{'!'*60}")
    print("\nColumnas disponibles:")
    for i, col in enumerate(df.columns[:20]):
        muestra = df.iloc[:3, i].dropna().tolist()
        muestra_str = " | ".join(str(v)[:25] for v in muestra[:2])
        print(f"  [{i:2d}] {str(col)[:30]:<30} -> {muestra_str}")

    print(f"\nPrimeras 10 filas:")
    print(df.iloc[:10, :min(12, len(df.columns))].to_string())
    print()
    print("  Opciones:")
    print("  - Ingresa el numero de columna para cada campo")
    print("  - Enter  = omitir esta vez (queda en DUDAS, vuelve a preguntar la proxima)")
    print("  - D      = descartar esta vez (queda en DUDAS, vuelve a preguntar la proxima)")
    print("  - X      = descartar DEFINITIVAMENTE (no vuelve a preguntar)")
    print()

    try:
        isbn_in = input("  Numero de columna ISBN [numero / Enter / D / X]: ").strip().upper()
        if isbn_in == "" or isbn_in == "D":
            print("  [OMITIDO - quedara en DUDAS]")
            return None, None, None
        if isbn_in == "X":
            print("  [DESCARTADO DEFINITIVAMENTE]")
            return "DESCARTAR", None, None

        col_isbn = int(isbn_in)
        if col_isbn >= len(df.columns):
            print(f"  [ERROR] Columna {col_isbn} no existe (máximo: {len(df.columns)-1})")
            return None, None, None

        precio_in = input("  Numero de columna PRECIO NUEVO [numero / Enter / D / X]: ").strip().upper()
        if precio_in == "" or precio_in == "D":
            print("  [OMITIDO - quedara en DUDAS]")
            return None, None, None
        if precio_in == "X":
            print("  [DESCARTADO DEFINITIVAMENTE]")
            return "DESCARTAR", None, None
        col_precio = int(precio_in)
        if col_precio >= len(df.columns):
            print(f"  [ERROR] Columna {col_precio} no existe (máximo: {len(df.columns)-1})")
            return None, None, None

        titulo_in = input("  Numero de columna TITULO (Enter si no hay): ").strip()
        col_titulo = int(titulo_in) if titulo_in else None
        if col_titulo is not None and col_titulo >= len(df.columns):
            print(f"  [AVISO] Columna titulo {col_titulo} no existe, se ignora")
            col_titulo = None

        return col_isbn, col_precio, col_titulo

    except (ValueError, EOFError):
        print("  [OMITIDO por entrada invalida]")
        return None, None, None

# ─────────────────────────────────────────────
#  PROCESO PRINCIPAL
# ─────────────────────────────────────────────

def procesar(modo_auto=False, archivos_especificos=None):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if archivos_especificos:
        archivos = sorted([f for f in archivos_especificos if os.path.exists(f)])
    else:
        archivos = sorted([
            f for f in glob.glob("*.xls*")
            if not any(x in f.lower() for x in ['resultado', 'duplicado', 'duda', 'conflict'])
            and not os.path.basename(f).startswith("~$")
        ])

    if not archivos:
        print("[AVISO] No se encontraron archivos Excel para procesar.")
        return

    config = cargar_config()
    lista_final = []
    lista_dudas = []
    ts = datetime.now().strftime('%H%M')

    for archivo in archivos:
        print(f"\n{'='*60}\n[ARCHIVO] {os.path.basename(archivo)}\n{'='*60}")
        try:
            xl = pd.ExcelFile(archivo)
        except Exception as e:
            lista_dudas.append({'Archivo': archivo, 'Hoja': '-',
                                'Motivo': f'Error al abrir: {e}', 'Columnas': ''})
            print(f"  [ERROR] No se pudo abrir: {e}")
            continue

        # Si hay una hoja "unificada" que incluye todas las demás, usar solo esa
        HOJAS_UNIFICADAS = ['unificad', 'unifica', 'todos', 'todo', 'completo', 'completa',
                            'general', 'total', 'consolidado', 'consolidada', 'listadogeneral',
                            'listado general', 'listadoprecios', 'lista general']
        hoja_unificada = None
        for h in xl.sheet_names:
            h_clean = col_clean(h)
            if any(k in h_clean for k in HOJAS_UNIFICADAS):
                hoja_unificada = h
                break

        hojas_a_procesar = [hoja_unificada] if hoja_unificada else xl.sheet_names
        if hoja_unificada:
            print(f"  [INFO] Hoja unificada detectada: '{hoja_unificada}' — se omiten las demás")

        for hoja in hojas_a_procesar:
            config_key = f"{os.path.basename(archivo)}|{hoja}"
            print(f"  [HOJA] '{hoja}'")
            try:
                df_raw = pd.read_excel(archivo, sheet_name=hoja, header=None, nrows=40)
                fila_h = detectar_fila_header(df_raw)
                df = pd.read_excel(archivo, sheet_name=hoja, skiprows=fila_h)
                df = df.dropna(how='all')

                if len(df) < 3:
                    print(f"     [VACIO] Muy pocas filas ({len(df)}), omitida.")
                    continue

                # ── Verificar si ya tiene configuración guardada ──
                if config_key in config:
                    cfg = config[config_key]
                    if cfg.get("descartado"):
                        print(f"     [DESCARTADO] Omitido por configuracion guardada.")
                        continue
                    col_isbn   = cfg.get("isbn")
                    col_precio = cfg.get("precio")
                    col_titulo = cfg.get("titulo")
                    print(f"     [CONFIG] Usando configuracion guardada: ISBN={col_isbn}, Precio={col_precio}, Titulo={col_titulo}")
                else:
                    # ── Detección estricta ──
                    col_isbn, col_precio, col_titulo, motivo_fallo = detectar_columnas_estricto(df)

                    if motivo_fallo:
                        if modo_auto:
                            print(f"     [AUTO] No se pudo detectar columnas: {motivo_fallo} — enviado a DUDAS")
                            lista_dudas.append({
                                'Archivo': archivo, 'Hoja': hoja,
                                'Motivo': motivo_fallo,
                                'Columnas': ', '.join(f"[{i}]{str(c)[:20]}"
                                                      for i, c in enumerate(df.columns[:15]))
                            })
                            continue
                        # Consultar al usuario
                        col_isbn, col_precio, col_titulo = consultar_usuario(
                            archivo, hoja, df, motivo_fallo)

                        if col_isbn == "DESCARTAR":
                            config[config_key] = {"descartado": True}
                            guardar_config(config)
                            print(f"     [DESCARTADO] No se procesara en futuras ejecuciones.")
                            continue

                        if col_isbn is None:
                            lista_dudas.append({
                                'Archivo': archivo, 'Hoja': hoja,
                                'Motivo': motivo_fallo,
                                'Columnas': ', '.join(f"[{i}]{str(c)[:20]}"
                                                      for i, c in enumerate(df.columns[:15]))
                            })
                            continue

                    # Guardar configuración para próxima vez
                    config[config_key] = {
                        "isbn": col_isbn,
                        "precio": col_precio,
                        "titulo": col_titulo
                    }
                    guardar_config(config)

                print(f"     ISBN  -> col [{col_isbn}] '{df.columns[col_isbn]}'")
                print(f"     Precio-> col [{col_precio}] '{df.columns[col_precio]}'")
                if col_titulo is not None:
                    print(f"     Titulo-> col [{col_titulo}] '{df.columns[col_titulo]}'")

                df_res = pd.DataFrame()
                df_res['ISBN']   = df.iloc[:, col_isbn].apply(limpiar_isbn)
                df_res['Titulo'] = df.iloc[:, col_titulo].fillna('').astype(str) \
                                   if col_titulo is not None else ''
                df_res['Precio'] = df.iloc[:, col_precio].apply(limpiar_precio_ar)
                df_res['Origen'] = f"{os.path.basename(archivo)} | {hoja}"

                df_valido = df_res[
                    df_res['ISBN'].str.len().isin([10, 13]) &
                    (df_res['Precio'] > 0)
                ].copy()

                if df_valido.empty:
                    print(f"     [AVISO] Sin registros validos.")
                    lista_dudas.append({
                        'Archivo': archivo, 'Hoja': hoja,
                        'Motivo': 'Sin registros validos tras filtrar ISBN y precio',
                        'Columnas': ''
                    })
                else:
                    print(f"     [OK] {len(df_valido)} registros validos.")
                    lista_final.append(df_valido)

            except Exception as e:
                lista_dudas.append({'Archivo': archivo, 'Hoja': hoja,
                                    'Motivo': f'Error: {e}', 'Columnas': ''})
                print(f"     [ERROR] {e}")

    # ── CONSOLIDAR ────────────────────────────────────────
    print(f"\n{'='*60}\nCONSOLIDANDO RESULTADOS\n{'='*60}")

    if lista_final:
        resultado = pd.concat(lista_final, ignore_index=True).drop_duplicates()

        conflictos = resultado.groupby('ISBN').filter(lambda x: x['Precio'].nunique() > 1)
        isbns_conf = set(conflictos['ISBN'])
        limpio = (resultado[~resultado['ISBN'].isin(isbns_conf)]
                  .drop_duplicates(subset='ISBN')
                  [['ISBN', 'Titulo', 'Precio', 'Origen']])

        nombre_out = f"RESULTADO_FINAL_{ts}.xlsx"
        limpio.to_excel(nombre_out, index=False)
        print(f"[OK] Resultado principal : {nombre_out}  ({len(limpio)} registros)")

        if not conflictos.empty:
            nombre_conf = f"CONFLICTOS_PRECIO_{ts}.xlsx"
            conflictos.sort_values('ISBN').to_excel(nombre_conf, index=False)
            print(f"[AVISO] Conflictos de precio: {nombre_conf}  "
                  f"({conflictos['ISBN'].nunique()} ISBNs)")
    else:
        print("[AVISO] No se genero resultado.")

    if lista_dudas:
        nombre_dudas = f"DUDAS_{ts}.xlsx"
        pd.DataFrame(lista_dudas).to_excel(nombre_dudas, index=False)
        print(f"[DUDA] Dudas y errores   : {nombre_dudas}  ({len(lista_dudas)} casos)")

    print(f"\n[LISTO] PROCESO COMPLETADO.\n")

if __name__ == "__main__":
    modo_auto = "--auto" in sys.argv
    # Archivos específicos pasados como argumentos (excluyendo flags)
    archivos_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    procesar(modo_auto=modo_auto, archivos_especificos=archivos_args if archivos_args else None)
