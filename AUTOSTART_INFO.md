# AI Services Autostart System

## Übersicht

Dieses System startet automatisch drei AI-Services beim Systemstart:

1. **SwarmUI** - AI User Interface
   - Läuft im Hintergrund
   - Log: `/home/joerissen/logs/swarmui.log`

2. **Werkraum-Tunnel** - Cloudflare Tunnel
   - Läuft im Hintergrund mit Auto-Restart
   - Log: `/home/joerissen/logs/werkraum-tunnel.log`

3. **AI4ArtsEd Webserver** - Python Webserver
   - Läuft im Vordergrund (Terminal-Fenster)
   - Port: 5000
   - Direktes Debugging im Terminal möglich

## Autostart-Mechanismus

Der Autostart erfolgt über einen systemd-Service:
- Service-Name: `ai-services.service`
- Konfiguration: `/etc/systemd/system/ai-services.service`
- Startet nach der grafischen Oberfläche
- Öffnet automatisch ein Terminal-Fenster für den Webserver

## Wichtige Befehle

### Service-Verwaltung
```bash
# Status prüfen
systemctl status ai-services.service

# Manuell starten
sudo systemctl start ai-services.service

# Stoppen
sudo systemctl stop ai-services.service

# Neustart
sudo systemctl restart ai-services.service

# Autostart deaktivieren
sudo systemctl disable ai-services.service

# Autostart wieder aktivieren
sudo systemctl enable ai-services.service
```

### Manuelle Verwaltung
```bash
# Alle Services manuell starten
~/start_all_services.sh

# Alle Services stoppen
~/stop_all_services.sh

# Status aller Services prüfen
~/check_services_status.sh
```

### Logs anzeigen
```bash
# Live-Logs aller Hintergrund-Services
tail -f ~/logs/*.log

# systemd Service-Logs
journalctl -u ai-services -f

# Nur SwarmUI-Logs
tail -f ~/logs/swarmui.log

# Nur Tunnel-Logs
tail -f ~/logs/werkraum-tunnel.log
```

## Dateipfade

### Skripte
- `/home/joerissen/start_all_services.sh` - Master Start-Skript
- `/home/joerissen/stop_all_services.sh` - Stop-Skript
- `/home/joerissen/check_services_status.sh` - Status-Check
- `/home/joerissen/startswarmui.sh` - Original SwarmUI Start-Skript
- `/home/joerissen/run_werkraum_tunnel.sh` - Original Tunnel-Skript
- `/home/joerissen/ai/ai4artsed_webserver/start_webserver.sh` - Original Webserver-Skript

### Logs und PIDs
- `/home/joerissen/logs/` - Log-Verzeichnis
- `/home/joerissen/logs/services.pid` - PID-Datei (aktive Prozesse)
- `/home/joerissen/logs/swarmui.log` - SwarmUI Logs
- `/home/joerissen/logs/werkraum-tunnel.log` - Tunnel Logs

### systemd
- `/etc/systemd/system/ai-services.service` - Service-Definition

## Port-Informationen

- **5000**: AI4ArtsEd Webserver
- SwarmUI und Tunnel verwenden dynamische Ports

## Troubleshooting

### Service startet nicht
1. Status prüfen: `systemctl status ai-services.service`
2. Journal-Logs prüfen: `journalctl -u ai-services -n 50`
3. Manuell testen: `~/start_all_services.sh`

### Port 5000 bereits belegt
Der Webserver-Skript prüft automatisch Port 5000 und beendet blockierende Prozesse.
Manuell prüfen: `lsof -i:5000`

### Kein Terminal-Fenster öffnet sich
1. Prüfen ob DISPLAY gesetzt ist: `echo $DISPLAY`
2. Service-Logs prüfen: `journalctl -u ai-services`
3. Alternativ ohne Terminal starten (Logs dann in journalctl)

### Service beim Boot deaktivieren
```bash
sudo systemctl disable ai-services.service
```

### Logs zu groß
Die Logs wachsen kontinuierlich. Regelmäßig alte Logs löschen:
```bash
# Logs älter als 7 Tage löschen
find ~/logs -name "*.log" -mtime +7 -delete
```

## Manuelle Installation (falls nötig)

Falls die Autostart-Konfiguration neu erstellt werden muss:

1. Service-Datei kopieren:
   ```bash
   sudo cp /tmp/ai-services.service /etc/systemd/system/
   ```

2. systemd neu laden:
   ```bash
   sudo systemctl daemon-reload
   ```

3. Service aktivieren:
   ```bash
   sudo systemctl enable ai-services.service
   ```

## Deinstallation

Um das Autostart-System komplett zu entfernen:

```bash
# Service stoppen und deaktivieren
sudo systemctl stop ai-services.service
sudo systemctl disable ai-services.service

# Service-Datei löschen
sudo rm /etc/systemd/system/ai-services.service

# systemd neu laden
sudo systemctl daemon-reload
```

Die Skripte in `/home/joerissen/` können behalten oder gelöscht werden.
