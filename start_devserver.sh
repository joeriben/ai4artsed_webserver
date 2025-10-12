#!/usr/bin/env bash

# Definition von Projektverzeichnis und Server-Skript
PROJECT_DIR="."
SERVER_SCRIPT="devserver/server.py"
PORT=17801

# Ins Projektverzeichnis wechseln
cd "${PROJECT_DIR}" || {
  echo "Fehler: Konnte Verzeichnis ${PROJECT_DIR} nicht betreten."
  exit 1
}

# Prüfen ob Port belegt ist und ggf. Prozess beenden
echo "Prüfe ob Port ${PORT} belegt ist..."
if command -v lsof &> /dev/null; then
  # Verwende lsof wenn verfügbar
  PID=$(lsof -ti:${PORT})
  if [ -n "$PID" ]; then
    echo "Port ${PORT} ist belegt von Prozess ${PID}. Beende Prozess..."
    kill -9 ${PID} 2>/dev/null
    sleep 1
  fi
elif command -v ss &> /dev/null; then
  # Verwende ss als Alternative
  PID=$(ss -lptn "sport = :${PORT}" 2>/dev/null | grep -oP '(?<=pid=)\d+' | head -1)
  if [ -n "$PID" ]; then
    echo "Port ${PORT} ist belegt von Prozess ${PID}. Beende Prozess..."
    kill -9 ${PID} 2>/dev/null
    sleep 1
  fi
else
  # Verwende netstat als letzte Option
  PID=$(netstat -tlnp 2>/dev/null | grep ":${PORT}" | awk '{print $7}' | cut -d'/' -f1)
  if [ -n "$PID" ]; then
    echo "Port ${PORT} ist belegt von Prozess ${PID}. Beende Prozess..."
    kill -9 ${PID} 2>/dev/null
    sleep 1
  fi
fi

# Virtuelle Umgebung aktivieren, falls vorhanden
if [ -f "venv/bin/activate" ]; then
  echo "Aktiviere virtuelle Umgebung..."
  source venv/bin/activate
fi

# Python-Pfad setzen und Waitress-Server starten
export PYTHONPATH="${PROJECT_DIR}/server:${PYTHONPATH}"
echo "Starte Waitress-Webserver auf Port ${PORT}: ${SERVER_SCRIPT} …"
python3 "${SERVER_SCRIPT}"

# Wenn der Prozess durch STRG+C oder SIGINT/SIGTERM beendet wird, endet das Skript automatisch.
