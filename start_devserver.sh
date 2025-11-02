#!/usr/bin/env bash

#===============================================================================
# AI4ArtsEd Development Server Startup Script
# Robuste Version mit vollständiger Fehlerbehandlung und Logging
#===============================================================================

set -euo pipefail  # Strict error handling

# ANSI Color Codes für bessere Lesbarkeit
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Konfiguration
readonly PORT=17801
readonly MAX_RETRIES=3
readonly RETRY_DELAY=2

# Skript-Verzeichnis ermitteln (funktioniert unabhängig vom Aufruf-Ort)
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_DIR="${SCRIPT_DIR}"
readonly SERVER_SCRIPT="devserver/server.py"
readonly LOG_FILE="/tmp/devserver_$(date +%Y%m%d_%H%M%S).log"

#===============================================================================
# Logging Functions
#===============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $*" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "${LOG_FILE}"
}

#===============================================================================
# Cleanup Handler
#===============================================================================

cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Script beendet mit Exit-Code: $exit_code"
        log_info "Log-Datei: ${LOG_FILE}"
    fi
    exit $exit_code
}

trap cleanup EXIT INT TERM

#===============================================================================
# Utility Functions
#===============================================================================

# Prüft ob ein Befehl verfügbar ist
command_exists() {
    command -v "$1" &> /dev/null
}

# Wartet bis Port frei ist
wait_for_port_free() {
    local port=$1
    local max_wait=10
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if ! lsof -i:"${port}" &> /dev/null; then
            return 0
        fi
        sleep 1
        ((waited++))
    done
    return 1
}

# Ermittelt PID des Prozesses auf Port
get_pid_on_port() {
    local port=$1

    if command_exists lsof; then
        lsof -ti:"${port}" 2>/dev/null | head -1
    elif command_exists ss; then
        ss -lptn "sport = :${port}" 2>/dev/null | grep -oP '(?<=pid=)\d+' | head -1
    elif command_exists netstat; then
        netstat -tlnp 2>/dev/null | grep ":${port}" | awk '{print $7}' | cut -d'/' -f1 | head -1
    else
        log_error "Kein Tool gefunden um Port-Belegung zu prüfen (lsof/ss/netstat)"
        return 1
    fi
}

#===============================================================================
# Main Functions
#===============================================================================

# Beendet Prozess auf Port falls belegt
kill_process_on_port() {
    local port=$1

    log_info "Prüfe Port ${port}..."

    local pid
    pid=$(get_pid_on_port "${port}")

    if [ -n "${pid}" ]; then
        log_warning "Port ${port} ist belegt von Prozess ${pid}"
        log_info "Beende Prozess ${pid}..."

        if kill -9 "${pid}" 2>/dev/null; then
            log_success "Prozess ${pid} beendet"

            if wait_for_port_free "${port}"; then
                log_success "Port ${port} ist jetzt frei"
                return 0
            else
                log_error "Port ${port} ist immer noch belegt nach 10 Sekunden"
                return 1
            fi
        else
            log_error "Konnte Prozess ${pid} nicht beenden"
            return 1
        fi
    else
        log_success "Port ${port} ist frei"
        return 0
    fi
}

# Aktiviert virtuelle Umgebung falls vorhanden
activate_venv() {
    local venv_path="${PROJECT_DIR}/venv"

    if [ -f "${venv_path}/bin/activate" ]; then
        log_info "Aktiviere virtuelle Umgebung..."
        # shellcheck disable=SC1091
        source "${venv_path}/bin/activate"
        log_success "Virtuelle Umgebung aktiviert"
        return 0
    else
        log_warning "Keine virtuelle Umgebung gefunden in ${venv_path}"
        log_warning "Verwende System-Python"
        return 0
    fi
}

# Validiert Python-Installation
validate_python() {
    if ! command_exists python3; then
        log_error "python3 nicht gefunden"
        return 1
    fi

    local python_version
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    log_info "Python Version: ${python_version}"

    return 0
}

# Startet den Server
start_server() {
    local server_path="${PROJECT_DIR}/${SERVER_SCRIPT}"

    # Validierung
    if [ ! -f "${server_path}" ]; then
        log_error "Server-Script nicht gefunden: ${server_path}"
        return 1
    fi

    log_info "Starte Waitress-Webserver..."
    log_info "Port: ${PORT}"
    log_info "Script: ${SERVER_SCRIPT}"
    log_info "Working Directory: ${PROJECT_DIR}"
    log_info "Log: ${LOG_FILE}"

    # Python-Pfad setzen
    export PYTHONPATH="${PROJECT_DIR}/server:${PYTHONPATH:-}"

    # Server starten
    cd "${PROJECT_DIR}" || {
        log_error "Konnte nicht in Verzeichnis ${PROJECT_DIR} wechseln"
        return 1
    }

    python3 "${server_path}" 2>&1 | tee -a "${LOG_FILE}"

    return 0
}

#===============================================================================
# Main Script
#===============================================================================

main() {
    log_info "=========================================="
    log_info "AI4ArtsEd Development Server Startup"
    log_info "=========================================="
    log_info "Zeit: $(date)"
    log_info "User: $(whoami)"
    log_info "Projekt: ${PROJECT_DIR}"
    log_info ""

    # 1. Port-Check und Cleanup
    if ! kill_process_on_port "${PORT}"; then
        log_error "Konnte Port ${PORT} nicht freigeben"
        return 1
    fi

    # 2. Python validieren
    if ! validate_python; then
        log_error "Python-Validierung fehlgeschlagen"
        return 1
    fi

    # 3. Virtuelle Umgebung aktivieren
    activate_venv

    # 4. Server starten
    log_info ""
    log_info "=========================================="
    if ! start_server; then
        log_error "Server-Start fehlgeschlagen"
        return 1
    fi

    return 0
}

# Script ausführen
main "$@"
