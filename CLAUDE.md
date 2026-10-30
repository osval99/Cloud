# Cloud — Osvaldo Scholer

Repositorio personal con varios proyectos independientes, uno por carpeta.
Cada carpeta puede tener su propio `CLAUDE.md` con el detalle; leerlo antes de trabajar en ella.

## Preferencias de trabajo
- Responder siempre en español.
- Explicaciones breves y precisas.
- Nunca inventar resultados: si algo no se verificó o falló, decirlo.
- Si no se conoce una respuesta, buscar en fuentes confiables de internet.
- Ante una tarea nueva, hacer primero las preguntas necesarias para realizarla bien.
- Al terminar un trabajo, enviar notificación a la app del celular.

## Proyectos
| Carpeta | Descripción |
|---------|-------------|
| `datos-tecnicos-libros/` | Buscar datos técnicos de libros a partir de ISBNs (en definición) |
| `escaner-fierro/` | PWA que escanea códigos de barra y los pasa a Fierro |
| `finanzas/` | Estrategia de manejo de liquidez en pesos |
| `mantenimiento-pc/` | Datos y tareas de mantenimiento de la PC (Windows 10) |
| `precios-mandrake/` | Scripts Python para actualizar precios de Librería Mandrake vía Gmail |

## Entorno
- Las sesiones de Claude Code corren en la nube y no recuerdan conversaciones anteriores:
  todo contexto que deba persistir se guarda en este archivo o en el `CLAUDE.md` de cada carpeta.
- La PC del usuario es Windows 10 (rutas tipo `C:\Users\osval\...`); los scripts deben funcionar ahí.
- No versionar credenciales (`credentials.json`, `token.json`, etc.).
