#!/bin/bash
# Arranca la pantalla virtual :5 (Xephyr) con Fierro adentro, para que Claude lo maneje
# sin tocar el escritorio del usuario. El login de Fierro lo hace siempre el usuario.
#
# Uso: ./iniciar_fierro.sh          → arranca lo que falte
#      ./iniciar_fierro.sh ajustar  → estira la ventana principal de Fierro a toda la pantalla
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"
export DISPLAY_VIRTUAL=:5
mkdir -p "$DIR/logs"

ventana_fierro() {
    DISPLAY=:5 xwininfo -root -tree 2>/dev/null | grep '"FIERRO - ' | grep -o '0x[0-9a-f]*' | head -1
}

if [ "${1:-}" = "ajustar" ]; then
    W=$(ventana_fierro)
    [ -n "$W" ] || { echo "Fierro todavía no tiene la sesión iniciada en :5"; exit 1; }
    python3 -I "$DIR/cu.py" fit "$W" && echo "Ventana $W ajustada a la pantalla virtual"
    exit 0
fi

# 1. Pantalla virtual
if [ -S /tmp/.X11-unix/X5 ] && DISPLAY=:5 xwininfo -root >/dev/null 2>&1; then
    echo "Pantalla virtual :5 ya activa"
else
    setsid nohup Xephyr :5 -screen 1340x690 -title "Fierro (Claude)" -br -no-host-grab -nolisten tcp \
        > "$DIR/logs/xephyr.log" 2>&1 < /dev/null &
    for _ in $(seq 20); do sleep 0.5; DISPLAY=:5 xwininfo -root >/dev/null 2>&1 && break; done
    echo "Pantalla virtual :5 iniciada"
fi
DISPLAY=:5 setxkbmap es   # sin esto no se pueden escribir acentos

# 2. Fierro
if pgrep -f "fierroclient.*/fierro" >/dev/null && DISPLAY=:5 xwininfo -root -tree | grep -qi '"fierro"'; then
    echo "Fierro ya está abierto en :5"
else
    DISPLAY=:5 setsid nohup /opt/bin/fierro > "$DIR/logs/fierro-virtual.log" 2>&1 < /dev/null &
    echo "Fierro iniciado en :5"
fi

if [ -n "$(ventana_fierro)" ]; then
    echo "Sesión de Fierro activa: $(ventana_fierro)"
else
    echo "FALTA LOGIN: el usuario tiene que iniciar sesión en la ventana \"Fierro (Claude)\"."
    echo "Después: ./iniciar_fierro.sh ajustar"
fi
