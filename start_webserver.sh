#!/usr/bin/env bash

# 1) Definition von Port, Projektverzeichnis und Server-Skript
PORT=5000
PROJECT_DIR="/home/joerissen/ai/ai4artsed_webserver"
SERVER_SCRIPT="server/workflow_server.py"

# 2) Prüfen, ob bereits ein Prozess auf PORT läuft; PID ermitteln (falls vorhanden)
PID=$(lsof -tiTCP:${PORT} -sTCP:LISTEN)

if [ -n "$PID" ]; then
  echo "Beende bereits laufenden Server (PID: $PID) auf Port ${PORT}..."
  kill "$PID"
  # Falls SIGTERM nicht ausreicht, kann alternativ 'kill -9 $PID' verwendet werden:
  # kill -9 "$PID"
  # Kurze Pause, damit sich der Port freigibt
  sleep 1
else
  echo "Kein Prozess auf Port ${PORT} gefunden. Kein Beenden erforderlich."
fi

# 3) Ins Projektverzeichnis wechseln (Annahme: Skript liegt in ai4artsed_webserver_api-format/)
cd "${PROJECT_DIR}" || {
  echo "Fehler: Konnte Verzeichnis ${PROJECT_DIR} nicht betreten."
  exit 1
}

# 4) Virtuelle Umgebung aktivieren, falls vorhanden
if [ -f "venv/bin/activate" ]; then
  echo "Aktiviere virtuelle Umgebung..."
  source venv/bin/activate
fi

# 5) Flask-Server starten (errechnet und zeigt URL in der Konsole an)
echo "Starte Flask-Webserver: ${PROJECT_DIR}/${SERVER_SCRIPT} …"
python3 "${SERVER_SCRIPT}"

# Wenn der Prozess durch STRG+C oder SIGINT/SIGTERM beendet wird, endet das Skript automatisch.

