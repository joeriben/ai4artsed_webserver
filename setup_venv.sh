#!/usr/bin/env bash

# Setup-Skript für AI4ArtsEd Web Server Virtual Environment

echo "=== AI4ArtsEd Web Server - Virtual Environment Setup ==="
echo

# Prüfen ob Python3 verfügbar ist
if ! command -v python3 &> /dev/null; then
    echo "Fehler: Python3 ist nicht installiert!"
    exit 1
fi

# Virtuelle Umgebung erstellen, falls nicht vorhanden
if [ ! -d "venv" ]; then
    echo "Erstelle virtuelle Umgebung..."
    python3 -m venv venv
    echo "✓ Virtuelle Umgebung erstellt"
else
    echo "✓ Virtuelle Umgebung bereits vorhanden"
fi

# Virtuelle Umgebung aktivieren
echo "Aktiviere virtuelle Umgebung..."
source venv/bin/activate

# pip aktualisieren
echo "Aktualisiere pip..."
pip install --upgrade pip

# Requirements installieren
echo "Installiere Abhängigkeiten..."
pip install -r requirements.txt

echo
echo "=== Setup abgeschlossen! ==="
echo
echo "Die virtuelle Umgebung wurde erfolgreich eingerichtet."
echo "Zum Aktivieren der Umgebung verwenden Sie: source venv/bin/activate"
echo "Zum Starten des Servers verwenden Sie: ./start_webserver.sh"
echo
