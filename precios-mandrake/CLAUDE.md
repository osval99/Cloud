# Librería Mandrake — Actualización de Precios

## Proyecto
Sistema automatizado de actualización de precios para Librería Mandrake.

- **Mail de operación**: actualizar.mandrakelibros@gmail.com
- **Carpeta de trabajo**: `C:\Users\osval\Desktop\Precios prueba 4\`
- **Archivos procesados**: subcarpeta `Procesados\`

## Scripts
| Script | Función |
|--------|---------|
| `actualizar_precios.py` | Pipeline completo: baja adjuntos de mails con etiqueta `PRECIOS PARA ACTUALIZAR` → procesa → mueve → les pone `Resuelto` y les saca la etiqueta |
| `agente2.py` | Procesa archivos Excel y genera resultado. Acepta `--auto` (sin preguntas) y lista de archivos específicos |
| `bajar_adjuntos.py` | Solo descarga adjuntos del mail (sin procesar) |

## Credenciales Gmail API
- `credentials.json` — en la carpeta de trabajo (no versionar)
- `token.json` — se genera automáticamente al autenticarse por primera vez
- Usuario de prueba OAuth: `actualizar.mandrakelibros@gmail.com`
- Proyecto Google Cloud: `mandrake-precios`
- Las etiquetas se buscan **por nombre** (`PRECIOS PARA ACTUALIZAR`, `Resuelto`), no por ID: los IDs cambian entre cuentas.
- Las listas a actualizar llegan a **mandrake.dis@gmail.com** con la etiqueta `PRECIOS PARA ACTUALIZAR`.
  El token debe estar autorizado con esa cuenta (si `token.json` es de otra, borrarlo y reautenticar). El script imprime la cuenta usada.

## Convenciones y reglas importantes
- El pipeline procesa **solo** los archivos recién bajados del mail, no los que ya están en la carpeta
- **Conflictos de precio**: tomar siempre el precio más alto — el script ya lo hace automáticamente
- Al terminar el pipeline se mueven a `Procesados\`: archivos descargados + RESULTADO_FINAL + DUDAS
- Si se pide resolver un archivo de conflictos manualmente, generar **solo** un archivo con los ISBNs conflictivos resueltos (pueden ser cualquier cantidad) — **no mezclar con el resultado anterior**
- Los archivos Excel de entrada pueden tener múltiples hojas; solo procesar las que son listas de precios

## Validación de ISBN (agente2.py)
- El ISBN es casi siempre de **13 dígitos** (rara vez 10). Si la columna elegida tiene mayormente ISBN-10
  y hay otra con ISBN-13 (978/979), se usa la de 13 (también sobre la config guardada).
- Se verifica el **dígito de control** (ISBN-13: pesos 1/3 mód. 10; ISBN-10: pesos 10..1 mód. 11, X=10).
  Los que no validan van a `ISBN_INVALIDOS_<hora>.xlsx`, no al resultado.
- Si la columna de "precio" tiene valores ≥ 100.000.000 (son códigos/ISBN), la hoja va a DUDAS.
- `agente2_config.json` guarda el mapeo de columnas por `archivo|hoja`; si un mapeo está mal, corregirlo ahí.

## Estado actual (31/10/2026) — tanda noviembre 2026
Corrida en la PC Linux `/home/oficina1/Cloud/precios-mandrake/` (no en Windows), cuenta mandrake.dis@gmail.com.
- 25 mails con adjuntos → 37 archivos bajados, movidos a `Procesados/`; los 25 mails quedaron con `Resuelto`.
- **Resultado**: `RESULTADO_FINAL_1321.xlsx` (29.335 registros: 29.258 ISBN-13, 77 ISBN-10).
- `ISBN_INVALIDOS_1321.xlsx`: 243 filas (113 ISBN distintos) con dígito verificador incorrecto — revisar.
- `DUDAS_1321.xlsx`: 18 casos (hojas) sin procesar:
  - Galerna / Aurelia Rivera (2 mails), Cien Flores, Herramienta (jaossanna): error "out-of-bounds" en varias hojas.
  - AKAL (facturacion): precio ambiguo "Precio $ Actual" vs "PVP PESOS FINAL".
  - Sigmar (una hoja) y Herramienta (2 hojas): no se encontró columna ISBN.
- `PRECIOS_CUERPO_MAIL.xlsx`: 9789875589964 Amancio Williams (UNL) $40.000; 9786313001170 Tarot para colorear $30.000.
- `Descartados/`: resultados de las corridas 1315 y 1318, con errores (Cuenco: precio = ISBN; Sigmar "Por Título":
  precio = código interno; Continente: ISBN-10). No usar.
- Se procesó también "Promos nov-dic.xlsx" (Librum): son promos, no lista — revisar si debe quedar en el resultado.

### Pendientes
- Listas por link (no las baja el script, no se intentó): Coma Cuatro (Drive, El Cuenco de Plata), Abrazandocuentos,
  Del Naranjo, Manolito (Mega Atlas, promo $29.900), FCE (lista PVP), Sigmar (botón en el mail).
- Promos, no lista: Librum (promos nov-dic), FCE (10 títulos a $18.000).
- Conflictos manuales viejos: 9789871374915 (Carbono, $23.000 vs $37.500); 9789872349417 (Herramienta, 2 títulos).
- El pipeline no mueve RESULTADO_FINAL/DUDAS a `Procesados/` (quedan en la carpeta).

## Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo
3. Arreglar el error "single positional indexer is out-of-bounds" (Galerna, Cien Flores, Herramienta)
4. Reconocer encabezados con tilde ("Código Barras")

## Google Apps Script (bajar adjuntos de Gmail)
- **Cuenta**: actualizar.mandrakelibros@gmail.com
- **Etiqueta Gmail**: `precios-para-actualizar`
- **Bug pendiente**: `getUserLabelByName()` devuelve `null` — la etiqueta no se está resolviendo correctamente
