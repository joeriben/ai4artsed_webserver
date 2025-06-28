# server.py
# SIMPLIFIED LOGIC: No more dynamic workflow stitching.
# - Image analysis is a separate, preceding step.
# - /run_workflow only injects the final text prompt.
# - FINAL: Using llava:7b, new prompt, and unloading the model after use.

from pathlib import Path
from flask import Flask, jsonify, abort, request, Response, send_from_directory
from flask_cors import CORS
import json
import requests
import traceback
import os
import logging
import uuid
import math
import random

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821" 
ENABLE_VALIDATION_PIPELINE = True
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
TRANSLATION_MODEL = "lauchacarro/qwen2.5-translator:latest"
SAFETY_MODEL = "llama-guard3:8b" 

# UPDATED ANALYSIS CONFIGURATION
ANALYSIS_MODEL = "llava:7b" 
ANALYSIS_SYSTEM_PROMPT = """Instruction: ANALYZE THE IMAGE. REGARD THE FOLLOWING RULES: 

    Material and medial propertiesr: Estimate the aspect ratio as width:height, e.g. "Aspect Ratio 4:3". EXPLICITELY MENTION THE ASPECT RATIO in your output. Identify the media type (e.g. oil painting, guache, mural, silver gelatine print, analog photography, digital foto, film still, scultpure, billboard, etc.)
    
    Pre-iconographic description: Identify and describe all visible forms, objects, gestures, settings, and compositional elements. Include a planimetrical analysis of the spatial structure: describe lines of sight, perspectives, depth layers, symmetry/asymmetry, visual hierarchies, and dominant spatial axes.

    Iconographic analysis: Interpret the symbolic meaning of identified motifs, figures, or actions based on conventional themes, narratives, or allegories. Identify their historical or cultural references. Identify atmospheres and affective aspects.

    Iconological interpretation: Deduce the underlying worldview, socio-cultural context, or conceptual structure expressed through the image. Identify latent meanings or ideological structures that inform the image’s visual rhetoric. NEVER MAKE TRIVIAL REMARKS SUCH AS "Without specific historical or cultural references, it is difficult to deduce the underlying worldview or socio-cultural context directly from this image." AS AN EXPERT, YOU INFER SUCH INFORMATIONS AS GOOD AS POSSIBLE.
    
Do not comment on the method or your own analysis. Output the results structured in three sections, without labels."""

THIS_FILE = Path(__file__).resolve()
BASE_DIR = THIS_FILE.parent.parent
LOCAL_WORKFLOWS_DIR = BASE_DIR / "workflows"
PUBLIC_DIR = BASE_DIR / "public"

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")
CORS(app)

# --- Helper Functions ---
def calculate_dimensions(size_str, ratio_str):
    try:
        side = int(size_str); total_pixels = side * side; w_ratio, h_ratio = map(int, ratio_str.split(':'))
        aspect_value = w_ratio / h_ratio; width = round(math.sqrt(total_pixels * aspect_value))
        height = round(width / aspect_value); width = round(width / 8) * 8; height = round(height / 8) * 8
        return {"width": width, "height": height}
    except: return {"width": 1024, "height": 1024}

def translate_text_ollama(text):
    prompt = f"Translate the following text to English. Output only the translated text and nothing else:\n\n{text}"
    payload = {"model": TRANSLATION_MODEL, "prompt": prompt, "stream": False, "keep_alive": "0s"}
    try:
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=45)
        response.raise_for_status(); return response.json().get("response", "").strip()
    except: return None

def check_safety_ollama(english_text):
    prompt = f"Is the following text safe? Please classify it. The text is:\n\n{english_text}"
    payload = {"model": SAFETY_MODEL, "prompt": prompt, "stream": False, "keep_alive": "0s"}
    try:
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=30)
        response.raise_for_status(); safety_response = response.json().get("response", "").strip()
        if safety_response.lower().strip().startswith("safe"): return {"is_safe": True}
        else:
            codes = [p.strip() for p in safety_response.strip().split('\n') if p.strip() in SAFETY_CATEGORY_MAP]
            reasons = [SAFETY_CATEGORY_MAP.get(code) for code in codes] or ["an unspecified policy violation"]
            return {"is_safe": False, "reason": f"Sorry, your prompt has been rejected due to potential issues: {', '.join(sorted(list(set(reasons))))}."}
    except: return {"is_safe": True, "note": "Safety check service failed, bypassing check."}

# NEW, SEPARATE ENDPOINT FOR IMAGE ANALYSIS
@app.route("/analyze_image", methods=["POST"])
def analyze_image():
    data = request.get_json()
    image_data = data.get("image_data")
    if not image_data:
        return jsonify({"error": "No image data provided."}), 400

    payload = {
        "model": ANALYSIS_MODEL,
        "prompt": "Analyze the image.",
        "system": ANALYSIS_SYSTEM_PROMPT,
        "images": [image_data.split(',', 1)[-1]],
        "stream": False,
        "keep_alive": "0s"  # Unload model immediately after use
    }
    try:
        logging.info(f"Sending image to Ollama model: {ANALYSIS_MODEL} (will unload after).")
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        analysis_result = response.json()
        generated_text = analysis_result.get("response", "").strip()
        logging.info(f"Ollama analysis successful.")
        return jsonify({"generated_prompt": generated_text})
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        if e.response is not None:
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = e.response.text
        logging.error(f"Failed to connect to Ollama for image analysis: {error_details}")
        return jsonify({"error": f"Image analysis service failed: {error_details}"}), 503

@app.route("/run_workflow", methods=["POST"])
def run_workflow():
    data = request.get_json()
    prompt_text = data.get("prompt")
    workflow_name = data.get("workflow")
    aspect_ratio = data.get("aspectRatio", "1:1")

    if not workflow_name: return jsonify({"error": "Workflow not selected."}), 400
    if not prompt_text or not prompt_text.strip():
        return jsonify({"error": "Prompt cannot be empty."}), 400
    if ".." in workflow_name or workflow_name.startswith("/"): abort(400, "Invalid workflow name.")
    
    try:
        with open(LOCAL_WORKFLOWS_DIR / workflow_name, "r", encoding="utf-8") as f:
            wf = json.load(f)
    except FileNotFoundError: return jsonify({"error": f"Workflow '{workflow_name}' not found."}), 404

    translated_prompt = prompt_text
    if ENABLE_VALIDATION_PIPELINE:
        translated_prompt = translate_text_ollama(prompt_text)
        if not translated_prompt: return jsonify({"error": "Translation service failed."}), 503
        safety_result = check_safety_ollama(translated_prompt)
        if not safety_result["is_safe"]: return jsonify(safety_result), 400
    
    prompt_injected = False
    for node_data in wf.values():
        if node_data.get("_meta", {}).get("title") == "ai4artsed_text_prompt":
            target_input = "value" if "value" in node_data["inputs"] else "text"
            if target_input in node_data["inputs"]:
                node_data["inputs"][target_input] = translated_prompt
                prompt_injected = True
                logging.info(f"Injected prompt into node with title 'ai4artsed_text_prompt'")
                break
    
    if not prompt_injected:
        logging.warning("Could not find a node with _meta.title 'ai4artsed_text_prompt' in the workflow.")
        return jsonify({"error": "Workflow does not have a designated prompt input node."}), 500

    dims = calculate_dimensions("1024", aspect_ratio)
    for node_data in wf.values():
      if node_data["class_type"] == "EmptyLatentImage":
          if not isinstance(node_data["inputs"].get("width"), list): node_data["inputs"]["width"] = dims["width"]
          if not isinstance(node_data["inputs"].get("height"), list): node_data["inputs"]["height"] = dims["height"]
      if "KSampler" in node_data["class_type"] and "seed" in node_data["inputs"]:
          node_data["inputs"]["seed"] = random.randint(0, 2**32 - 1)

    try:
        logging.info("Forwarding final workflow to ComfyUI.")
        resp = requests.post(f"http://localhost:{COMFYUI_PORT}/prompt", json={"prompt": wf, "client_id": str(uuid.uuid4())}, timeout=60)
        resp.raise_for_status()
        comfyui_data = resp.json()
        if not comfyui_data.get("prompt_id"): return jsonify({"error": "ComfyUI did not return a prompt_id."}), 502
        return jsonify({"prompt_id": comfyui_data["prompt_id"], "translated_prompt": translated_prompt})
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        if e.response is not None:
            try: error_details = e.response.json()
            except json.JSONDecodeError: error_details = e.response.text
        logging.error(f"ComfyUI request failed. Details: {error_details}")
        return jsonify({"error": f"Failed to connect to the ComfyUI service: {error_details}"}), 502

# --- Static and Proxy Routes ---
@app.route("/")
def serve_index(): return send_from_directory(PUBLIC_DIR, "index.html")

@app.route("/list_workflows")
def list_workflows():
    try:
        workflows = sorted([f.name for f in LOCAL_WORKFLOWS_DIR.glob("*.json") if not f.name.startswith(".")])
        return jsonify(workflows if workflows else []), 200 if workflows else 204
    except: return jsonify({"error": "Failed to read workflow directory"}), 500

@app.route("/config")
def get_config(): return jsonify({"comfyui_proxy_prefix": COMFYUI_PREFIX})

@app.route(f"/{COMFYUI_PREFIX}/<path:path>")
def proxy_to_comfyui(path):
    try:
        resp = requests.get(f"http://localhost:{COMFYUI_PORT}/{path}", params=request.args, timeout=30)
        return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))
    except: return jsonify({"error": f"Failed to connect to ComfyUI on port {COMFYUI_PORT}."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

