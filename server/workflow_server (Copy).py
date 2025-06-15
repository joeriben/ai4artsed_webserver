# server.py
# last edit BJ June 5 2025

from pathlib import Path
from flask import Flask, jsonify, abort, request, Response, send_from_directory
from flask_cors import CORS
import json
import requests
import traceback

# Präfix für alle ComfyUI-Proxy-Routen
COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821"
#7801 for ComfyUI inside SwarmUI; 8188 for ComfyUI original installation)

# 1. Ermittelt den absoluten Pfad zu dieser Datei (server.py)
THIS_FILE = Path(__file__).resolve()

# 2. Geht eine Ebene nach oben (…/server) und noch eine Ebene nach oben (…/ai4artsed_webserver_api-format)
BASE_DIR = THIS_FILE.parent.parent

# 3. Hängt "workflows" an, also ./workflows im Projektverzeichnis
LOCAL_WORKFLOWS_DIR = BASE_DIR / "workflows"

# DEFINIERT DEN ORDNER, AUS DEM INDEX.HTML GELIEFERT WIRD (PUBLIC-ORDNER)
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(
    __name__,
    static_folder=str(PUBLIC_DIR),
    static_url_path=""  # "/" verweist direkt auf public
)
CORS(app)

# ----------------------------------------------------------------------
# Route "/" liefert public/index.html
# ----------------------------------------------------------------------
@app.route("/")
def serve_index():
    return send_from_directory(PUBLIC_DIR, "index.html")


# ----------------------------------------------------------------------
# Route "/list_workflows" liest den Ordner LOCAL_WORKFLOWS_DIR und liefert
# die Liste aller *.json-Dateien zurück.
# ----------------------------------------------------------------------
@app.route("/list_workflows")
def list_workflows():
    try:
        if LOCAL_WORKFLOWS_DIR.exists():
            # Nur JSON-Dateien listen, die nicht mit "." beginnen (z.B. ".index.json" überspringen)
            workflows = sorted(
                f.name
                for f in LOCAL_WORKFLOWS_DIR.glob("*.json")
                if not f.name.startswith(".")
            )
            print(f"{len(workflows)} Workflows gefunden in {LOCAL_WORKFLOWS_DIR}")
            return jsonify(workflows)
        else:
            print(f"Workflow-Verzeichnis existiert nicht: {LOCAL_WORKFLOWS_DIR}")
            return jsonify([]), 204
    except Exception as e:
        # Exception-Meldung ausgeben
        print(f"Fehler beim Lesen des Workflow-Verzeichnisses: {e}")
        traceback.print_exc()
        # Konsole anhalten, bis der Anwender Enter drückt
        input("Fehler aufgetreten. Drücken Sie die Eingabetaste, um fortzufahren...")
        return jsonify([]), 204  # oder: abort(500)


# ----------------------------------------------------------------------
# Route "/get_workflow/<name>" öffnet die angegebene JSON-Datei aus LOCAL_WORKFLOWS_DIR
# und gibt deren Inhalte zurück. Unterschiedliche Fehlerfälle werden behandelt.
# ----------------------------------------------------------------------
@app.route("/get_workflow/<name>")
def get_workflow(name):
    local_path = LOCAL_WORKFLOWS_DIR / name
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            workflow = json.load(f)
        print(f"Workflow '{name}' erfolgreich geladen")
        return jsonify(workflow)
    except FileNotFoundError:
        print(f"Workflow '{name}' nicht gefunden")
        traceback.print_exc()
        abort(404)
    except json.JSONDecodeError as e:
        print(f"Ungültiges JSON in '{name}': {e}")
        traceback.print_exc()
        input("Ungültiges JSON. Drücken Sie Enter, um fortzufahren...")
        return jsonify({"error": "Ungültiges JSON"}), 400
    except PermissionError as e:
        print(f"Zugriffsfehler bei '{name}': {e}")
        traceback.print_exc()
        input("Zugriffsfehler. Drücken Sie Enter, um fortzufahren...")
        return jsonify({"error": "Zugriff verweigert"}), 403
    except Exception as e:
        print(f"Unbekannter Fehler bei '{name}': {e}")
        traceback.print_exc()
        input("Unbekannter Fehler. Drücken Sie Enter, um fortzufahren...")
        return jsonify({"error": str(e)}), 500


# ----------------------------------------------------------------------
# Route f"/{COMFYUI_PREFIX}/<path:path>" leitet alle POST- und OPTIONS-Anfragen
# an den lokalen ComfyUI-Server weiter (Proxy).
# ----------------------------------------------------------------------
@app.route(f"/{COMFYUI_PREFIX}/<path:path>", methods=["GET", "POST", "OPTIONS"])
def proxy_to_comfyui(path):
    comfyui_url = f"http://localhost:{COMFYUI_PORT}/{path}"

    # 1) Preflight (CORS) abfangen
    if request.method == "OPTIONS":
        return "", 200

    try:
        # 2) POST-Zweig: JSON an ComfyUI senden
        if request.method == "POST":
            data = request.get_json()
            resp = requests.post(
                comfyui_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
        else:
            # 3) GET-Zweig: alle URL-Parameter (z.B. /history/ID oder /view?…) an ComfyUI weiterleiten
            resp = requests.get(
                comfyui_url,
                params=request.args,
                timeout=5
            )

        # Antwort unverändert an den Browser zurückgeben
        return Response(
            resp.content,
            status=resp.status_code,
            content_type=resp.headers.get("Content-Type", "application/json")
        )

    except requests.exceptions.ConnectionError as e:
        print(f"Proxy-Verbindung fehlgeschlagen (ConnectionError): {e}")
        return jsonify({
            "error": "Verbindung zu ComfyUI fehlgeschlagen.",
            "action": (
                "Bitte starten Sie den ComfyUI-Server oder prüfen Sie, ob er auf Port {COMFYUI_PORT} lauscht. "
                "Dieses Fenster muss nicht geschlossen werden; der Server wartet weiterhin auf neue Anfragen."
            )
        }), 502

    except requests.exceptions.Timeout as e:
        print(f"Proxy-Verbindung abgelaufen (Timeout): {e}")
        return jsonify({
            "error": "Timeout beim Verbinden zu ComfyUI.",
            "action": (
                "Überprüfen Sie, ob ComfyUI reagiert (ggf. ist gerade eine aufwendige Berechnung im Gang). "
                "Falls nötig, starten Sie ComfyUI neu. Dieses Fenster muss nicht geschlossen werden; "
                "der Server wartet auf neue Anfragen."
            )
        }), 504

    except requests.exceptions.InvalidURL as e:
        print(f"Ungültige URL im Proxy-Aufruf: {comfyui_url} – {e}")
        return jsonify({
            "error": "Interner Fehler: Ungültige URL.",
            "action": (
                "Bitte kontaktieren Sie den Entwickler mit folgender Information: "
                "'Ungültige URL im Proxy-Aufruf'."
            )
        }), 500

    except requests.exceptions.RequestException as e:
        print(f"Proxy-Fehler (RequestException): {e}")
        return jsonify({
            "error": "Netzwerkfehler beim Proxy zu ComfyUI.",
            "action": (
                "Prüfen Sie Ihre lokale Netzwerkumgebung und ob ComfyUI korrekt läuft. "
                "Dieses Fenster muss nicht geschlossen werden; der Server wartet auf neue Anfragen. "
                "Details: " + str(e)
            )
        }), 500

    except Exception as e:
        print(f"Unbekannter Fehler im Proxy: {e}")
        traceback.print_exc()
        return jsonify({
            "error": "Ein interner Fehler ist aufgetreten.",
            "action": (
                "Bitte prüfen Sie das übergebene JSON oder kontaktieren Sie den Entwickler. "
                "Dieses Fenster muss nicht geschlossen werden; der Server wartet auf neue Anfragen. "
                "Details: " + str(e)
            )
        }), 500


if __name__ == "__main__":
    print(f"Starte Workflow-Server (nur API-Workflows) auf Port 5000")
    app.run(host="0.0.0.0", port=5000, debug=False)

