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

## Estado actual
- **Último resultado**: `RESULTADO_FINAL_1531.xlsx` (26.539 registros)
- **Conflictos pendientes**: `CONFLICTOS_PRECIO_1531.xlsx`
- **Archivos en duda**: carpeta `DUDAS\` (pendientes de procesar)

### Conflictos manuales sin resolver
| ISBN | Problema | Fuente |
|------|----------|--------|
| 9789871374915 | Dos precios: $23.000 y $37.500 | Carbono |
| 9789872349417 | Mismo ISBN, dos títulos distintos | Herramienta |

## Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo

## Tanda noviembre 2026 (pendiente de correr, 30/10/2026)
33 mails con la etiqueta. No se procesaron: desde la nube no se pueden bajar adjuntos (el conector Gmail no baja archivos)
ni abrir links externos (bloqueados por la red del entorno). Hay que correr `actualizar_precios.py` en la PC.
- **Lista por link, bajar a mano**: Coma Cuatro (Drive, El Cuenco de Plata), Abrazandocuentos, Del Naranjo,
  Manolito (Mega Atlas, promo $29.900), FCE (lista PVP), Sigmar (botón en el mail).
- **Precio en el cuerpo del mail** (cargar a mano): 9789875589964 Amancio Williams (UNL) → $40.000;
  9786313001170 Tarot para colorear → $30.000.
- **Promos, no lista**: Librum (promos nov-dic), FCE (10 títulos a $18.000).

## Google Apps Script (bajar adjuntos de Gmail)
- **Cuenta**: actualizar.mandrakelibros@gmail.com
- **Etiqueta Gmail**: `precios-para-actualizar`
- **Bug pendiente**: `getUserLabelByName()` devuelve `null` — la etiqueta no se está resolviendo correctamente
