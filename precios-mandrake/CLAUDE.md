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

## Reglas del proyecto "Listas De Precios" (claude.ai, memoria al 2/10/2026)
- Salida: `RESULTADO_FINAL_<hora>.csv` UTF-8, separador **coma** (con punto y coma no carga en Fierro),
  4 columnas: ISBN, Precio (entero), Titulo, Origen. Para Fierro se divide en tandas de ~5.000 filas.
- **Consultar al usuario las decisiones editoriales** antes de cerrar: qué columna de precio usar si hay varias,
  promo vs. PVP normal, identidad dudosa de una distribuidora. Decisiones ya tomadas:
  - Si hay PVP viejo y PVP nuevo, siempre el nuevo.
  - Las promos de distribuidoras (ej. Librum "Promos nov-dic") se cargan.
  - El Ateneo manda precios muy bajos (< $1.000) de libros descatalogados: no se cargan.
- DUDAS suele traer hojas vacías ("out-of-bounds"): no requieren acción.
- `agente2_config.json` guarda los mapeos por `archivo|hoja`. Si no hay entrada exacta, el script busca una
  de un archivo parecido (mismas palabras sin fecha/mes/remitente) y misma hoja, y la usa solo si el contenido
  valida (ISBN y precios razonables). Hojas marcadas `descartado` se omiten.

## Cargar precios en Fierro
Ventas > Listas de precios > LISTA MOSTRADOR > Precios > ícono "Importar precios desde un archivo".
Formato del archivo: **Personalizado** (CSV), separador coma, fin de línea Windows, empezar desde línea 2.
Vincular por **ISBN**, columna 1. **No** tildar "Actualizar el precio si se encuentra más de un libro con el
mismo código" (hay libros duplicados, ej. gemelos outlet). Ir paso a paso con el usuario; Aceptar/Aplicar solo
con su visto bueno. Tandas en `~/fierro-claude/importaciones/precios_nov2026/`.

## Validación de ISBN (agente2.py)
- El ISBN es casi siempre de **13 dígitos** (rara vez 10). Si la columna elegida tiene mayormente ISBN-10
  y hay otra con ISBN-13 (978/979), se usa la de 13 (también sobre la config guardada).
- Solo valen ISBN-13 con prefijo **978/979**; los ISBN-10 válidos se convierten a ISBN-13. Los demás códigos
  (779…, 750…, 290…) van a `ISBN_INVALIDOS_<hora>.xlsx` con el motivo.
- Se descartan las filas ocultas de los Excel.
- Se verifica el **dígito de control** (ISBN-13: pesos 1/3 mód. 10; ISBN-10: pesos 10..1 mód. 11, X=10).
  Los que no validan van a `ISBN_INVALIDOS_<hora>.xlsx`, no al resultado.
- Un valor con letras (ej. código interno "0084PT0000") no se toma como precio.
- Si la columna de "precio" tiene valores ≥ 100.000.000 (son códigos/ISBN), la hoja va a DUDAS.
- `agente2_config.json` guarda el mapeo de columnas por `archivo|hoja`; si un mapeo está mal, corregirlo ahí.

## Listas que llegan por link
El script solo baja adjuntos. Las listas por link se bajan resolviendo el link de seguimiento del mail
(curl -L; los de Brevo/sendibm redirigen con JavaScript: buscar la URL dentro del HTML).
Google Sheets: `.../export?format=xlsx`; Drive: `drive.google.com/uc?export=download&id=<ID>`.
Se guardan en `Procesados/` como `2026-10-31 [link] <nombre>.xlsx` y se procesan junto con los adjuntos.

## Estado actual (31/10/2026) — tanda noviembre 2026
Corrida en la PC Linux `/home/oficina1/Cloud/precios-mandrake/`, cuenta mandrake.dis@gmail.com.
Los 34 mails de la etiqueta quedaron con `Resuelto`.
- 37 adjuntos (25 mails) + 6 listas por link (Coma Cuatro, FCE, Sigmar, Abrazandocuentos, Del Naranjo, Manolito).
- **Resultado**: `RESULTADO_FINAL_1418.csv` (36.538) + `PRECIOS_CUERPO_MAIL.xlsx` (2) → 8 tandas en
  `~/fierro-claude/importaciones/precios_nov2026/` (36.532 precios; sin los 7 descatalogados de El Ateneo).
- `ISBN_INVALIDOS_1418.xlsx`: 430 filas que no son ISBN válidos. `DUDAS_1418.xlsx`: 17, todas hojas vacías o repetidas.
- **Carga en Fierro: pendiente**, se hace paso a paso con el usuario.
- `Descartados/`: corridas anteriores con errores. No usar.

### Pendientes
- Conflictos manuales viejos: 9789871374915 (Carbono, $23.000 vs $37.500); 9789872349417 (Herramienta, 2 títulos).
- El pipeline no mueve RESULTADO_FINAL/DUDAS a `Procesados/` (quedan en la carpeta).

## Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo
3. Arreglar el error "single positional indexer is out-of-bounds" (Galerna, Cien Flores, Herramienta)
4. Reconocer encabezados con tilde ("Código Barras")
5. Bajar automáticamente las listas por link desde `actualizar_precios.py`

## Google Apps Script (bajar adjuntos de Gmail)
- **Cuenta**: actualizar.mandrakelibros@gmail.com
- **Etiqueta Gmail**: `precios-para-actualizar`
- **Bug pendiente**: `getUserLabelByName()` devuelve `null` — la etiqueta no se está resolviendo correctamente
