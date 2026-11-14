# pomodoro

PWA de temporizador pomodoro configurable. HTML + JS puro, sin dependencias ni build.

## Archivos
- `index.html`: toda la app (estilos, lógica y sonidos con Web Audio).
- `manifest.json`, `icon.svg`, `sw.js`: instalación como app y funcionamiento offline.

## Funciones
- Fases: trabajo, descanso corto, descanso largo (pestañas para cambiar a mano).
- Configurable: minutos de cada fase, pomodoros por ciclo antes del descanso largo,
  sonido (campana / digital / suave / ninguno), volumen y aviso del sistema.
- Nombre de la tarea actual e historial del día (cantidad, tiempo total, tarea y hora).
- Botones Iniciar/Pausar (también barra espaciadora), Reiniciar y Saltar.
- La fase siguiente NO arranca sola (decisión del usuario).
- "Saltar" un trabajo avanza el ciclo pero no lo suma al historial.

## Detalles técnicos
- Todo se guarda en `localStorage` (claves `pomo.cfg`, `pomo.state`, `pomo.hist`, `pomo.task`):
  si se recarga la página el temporizador sigue donde estaba.
- El tiempo se calcula con la hora de fin (no acumulando ticks); el tick corre en un
  Web Worker para que el navegador no lo frene con la pestaña en segundo plano.
- Avisos: usa `Notification` o el service worker. En el celular conviene instalarla
  (Agregar a pantalla de inicio). Necesita HTTPS o localhost (no anda abriendo el archivo con `file://`).

## Estado
- Probado con Playwright (Chromium): cuenta, pausa, cambio de fase, historial,
  persistencia al recargar y ciclo de puntos. Sonido y avisos no verificados en un dispositivo real.

## Pendientes
- Publicarla en algún hosting HTTPS (p. ej. GitHub Pages) para usarla desde el celular.
