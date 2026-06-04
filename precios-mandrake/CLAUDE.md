# Librería Mandrake — Actualización de Precios

## Proyecto
Sistema automatizado de actualización de precios para Librería Mandrake.

- **Mail de operación**: actualizar.mandrakelibros@gmail.com
- **Carpeta de trabajo**: `C:\Users\osval\Desktop\Precios prueba 4\`
- **Archivos procesados**: subcarpeta `Procesados\`

## Scripts
| Script | Función |
|--------|---------|
| `actualizar_precios.py` | Pipeline completo: baja adjuntos → procesa → mueve → marca RESUELTO en Gmail |
| `agente2.py` | Procesa archivos Excel y genera resultado. Acepta `--auto` (sin preguntas) y lista de archivos específicos |
| `bajar_adjuntos.py` | Solo descarga adjuntos del mail (sin procesar) |

## Credenciales Gmail API
- `credentials.json` — en la carpeta de trabajo (no versionar)
- `token.json` — se genera automáticamente al autenticarse por primera vez
- Usuario de prueba OAuth: `actualizar.mandrakelibros@gmail.com`
- Proyecto Google Cloud: `mandrake-precios`
- Etiqueta Gmail RESUELTO: `Label_2923983642399414539`

## Convenciones y reglas importantes
- El pipeline procesa **solo** los archivos recién bajados del mail, no los que ya están en la carpeta
- **Conflictos de precio**: tomar siempre el precio más alto — el script ya lo hace automáticamente
- Al terminar el pipeline se mueven a `Procesados\`: archivos descargados + RESULTADO_FINAL + DUDAS
- Si se pide resolver un archivo de conflictos manualmente, generar **solo** un archivo con los ISBNs conflictivos resueltos (pueden ser cualquier cantidad) — **no mezclar con el resultado anterior**
- Los archivos Excel de entrada pueden tener múltiples hojas; solo procesar las que son listas de precios

## Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo
