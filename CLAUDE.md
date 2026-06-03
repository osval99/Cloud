# Librería Mandrake — Actualización de Precios

## Proyecto
Sistema automatizado de actualización de precios para Librería Mandrake.

- **Mail de operación**: actualizar.mandrakelibros@gmail.com
- **Script principal**: `agente2.py` en `C:\Users\osval\Desktop\Precios prueba 4\`
- **Configuración**: `agente2_config.json` (mismo directorio)
- **Archivos procesados**: subcarpeta `Procesados\`
- **Último resultado**: `RESULTADO_FINAL_1531.xlsx` (26.539 registros)
- **Conflictos pendientes**: `CONFLICTOS_PRECIO_1531.xlsx`
- **Archivos en duda**: carpeta `DUDAS\` (pendientes de procesar)

## Estado actual

### Mejoras pendientes al script
1. Descartar automáticamente hojas que no son listas de precios (Editoriales, Puntos de venta, Contactos)
2. Mostrar ISBN pre-detectado cuando el precio es ambiguo

### Conflictos manuales sin resolver
| ISBN | Problema | Fuente |
|------|----------|--------|
| 9789871374915 | Dos precios: $23.000 y $37.500 | Carbono |
| 9789872349417 | Mismo ISBN, dos títulos distintos | Herramienta |

### Google Apps Script (bajar adjuntos de Gmail)
- **Cuenta**: actualizar.mandrakelibros@gmail.com
- **Etiqueta Gmail**: `precios-para-actualizar`
- **Bug pendiente**: `getUserLabelByName()` devuelve `null` — la etiqueta no se está resolviendo correctamente

## Convenciones
- Los archivos Excel de entrada pueden tener múltiples hojas; solo procesar las que son listas de precios
- El ISBN puede aparecer pre-detectado aunque el precio sea ambiguo — mostrar ambos al usuario
- Los archivos ya procesados se mueven a `Procesados\` automáticamente
