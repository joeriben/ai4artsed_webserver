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

OLLAMA_TO_OPENROUTER_MAP = {
    # Maps a local model's base name to its OpenRouter equivalent.
    "deepcoder": "agentica-org/deepcoder-14b-preview",
    "deepseek-r1": "deepseek/deepseek-r1",
    "gemma-2-9b-it": "google/gemma-2-9b-it",
    "gemma-2-27b-it": "google/gemma-2-27b-it",
    "gemma-3-1b-it": "google/gemma-3-1b-it",
    "gemma-3-4b-it": "google/gemma-3-4b-it",
    "gemma-3-12b-it": "google/gemma-3-12b-it",
    "gemma-3-27b-it": "google/gemma-3-27b-it",
    "shieldgemma-9b": "google/shieldgemma-9b",
    "llava": "liuhaotian/llava-7b",
    "llava:13b": "liuhaotian/llava-13b",
    "llama-3.1-8b-instruct": "meta-llama/llama-3.1-8b-instruct",
    "llama-3.2-1b-instruct": "meta-llama/llama-3.2-1b-instruct",
    "llama-3.3-8b-instruct": "meta-llama/llama-3.3-8b-instruct",
    "llama-guard-3-1b": "meta-llama/llama-guard-3-1b",
    "llama-guard-3-8b": "meta-llama/llama-guard-3-8b",
    "codestral": "mistralai/codestral",
    "mistral-7b": "mistralai/mistral-7b",
    "mistral-nemo": "mistralai/mistral-nemo",
    "mistral-small:24b": "mistralai/mistral-small-24b",
    "mixtral-8x7b-instruct": "mistralai/mixtral-8x7b-instruct",
    "ministral-8b": "mistralai/ministral-8b",
    "phi-4": "microsoft/phi-4",
    "qwen2.5-translator": "qwen/qwen2.5-translator",
    "qwen2.5-32b-instruct": "qwen/qwen2.5-32b-instruct",
    "qwen3-8b": "qwen/qwen3-8b",
    "qwen3-14b": "qwen/qwen3-14b",
    "qwen3-30b-a3b": "qwen/qwen3-30b-a3b",
    "qwq-32b": "qwen/qwq-32b",
    "sailor2-20b": "sailor2/sailor2-20b",
}

COMFYUI_PREFIX = "comfyui"
COMFYUI_PORT = "7821" 
ENABLE_VALIDATION_PIPELINE = True
OLLAMA_API_BASE_URL = os.environ.get("OLLAMA_API_BASE_URL", "http://localhost:11434")
TRANSLATION_MODEL = "lauchacarro/qwen2.5-translator:latest"
SAFETY_MODEL = "llama-guard3:8b" 

# UPDATED ANALYSIS CONFIGURATION
ANALYSIS_MODEL = "llava:7b" 
ANALYSIS_SYSTEM_PROMPT = """Instruction: ANALYZE THE IMAGE IN THE STYLE OF A SCIENTIFIC PRINTED ANALYSIS. REGARD THE FOLLOWING RULES: 

    Material and medial properties: Identify the media type (e.g. oil painting, guache, mural, silver gelatine print, analog photography, digital foto, film still, scultpure, billboard, etc.)
    
    Pre-iconographic description: Identify and describe all visible forms, objects, gestures, settings, and compositional elements. Make a list of EACH entity of the image. Describe each entity, its position, spatial relatedness, shape, texture, colours, and state.
    Include a planimetrical analysis of the spatial structure: describe lines of sight, perspectives, depth layers, symmetry/asymmetry, visual hierarchies, and dominant spatial axes.

    Iconographic analysis: Interpret the symbolic meaning of identified motifs, figures, or actions based on conventional themes, narratives, or allegories. Identify their historical or cultural references. Identify atmospheres and affective aspects.

    Iconological interpretation: Deduce the underlying worldview, socio-cultural context, or conceptual structure expressed through the image. Identify latent meanings or ideological structures that inform the image’s visual rhetoric. 

NO META-COMMENTS; NAMING OF METHODS; LABELS; CATEGORIES; ME; OR YOURSELF WHATSOEVER!
Do not comment on the method or your own analysis. NEVER MENTION MISSING CONTEXT. Always interpret as if for a printed text. Should you fail to infer meanings, choose thorough description as a fallback.
."""

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
    prompt = f"TTranslate the prompt into English with maximal semantic preservation. Maintain the original structure, and preserve all culturally specific terms or non-translatable phrases in their original form. Do not translate proper names, ritual terms, or material names unless they have a common English usage. Mark such terms with double brackets, e.g. [[egungun]], and preserve their position. Do not paraphrase, interpret, or summarize. Do not add any comments or explanations. If the following has meta-signifiers such as bracket, do not remove those. Return only the translated prompt as plain text.. If the following is already in english, leave it unchanged. Output only the translated text and nothing else:\n\n{text}"
    payload = {"model": TRANSLATION_MODEL, "prompt": prompt, "stream": False, "keep_alive": "0s"}
    try:
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=90)
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.RequestException:
        return None

def check_safety_ollama(english_text):
    prompt = f"Is the following text safe? Please classify it. The text is:\n\n{english_text}"
    payload = {"model": SAFETY_MODEL, "prompt": prompt, "stream": False, "keep_alive": "0s"}
    try:
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=60)
        response.raise_for_status()
        safety_response = response.json().get("response", "").strip()
        if safety_response.lower().strip().startswith("safe"):
            return {"is_safe": True}
        else:
            # Assuming SAFETY_CATEGORY_MAP is defined elsewhere or this logic is placeholder
            codes = [p.strip() for p in safety_response.strip().split('\n')]
            reasons = [p for p in codes] # Simplified for this example
            return {"is_safe": False, "reason": f"Sorry, your prompt has been rejected due to potential issues: {', '.join(sorted(list(set(reasons))))}."}
    except requests.exceptions.RequestException:
        return {"is_safe": True, "note": "Safety check service failed, bypassing check."}

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
        response = requests.post(f"{OLLAMA_API_BASE_URL}/api/generate", json=payload, timeout=80)
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
    mode = data.get("mode", "eco") # Default to eco mode

    if not workflow_name: return jsonify({"error": "Workflow not selected."}), 400
    if not prompt_text or not prompt_text.strip():
        return jsonify({"error": "Prompt cannot be empty."}), 400
    if ".." in workflow_name or workflow_name.startswith("/"): abort(400, "Invalid workflow name.")
    
    try:
        with open(LOCAL_WORKFLOWS_DIR / workflow_name, "r", encoding="utf-8") as f:
            wf = json.load(f)
    except FileNotFoundError: return jsonify({"error": f"Workflow '{workflow_name}' not found."}), 404

    # Mode switching logic
    if mode == 'fast':
        logging.info("Fast mode enabled. Swapping local models for OpenRouter equivalents.")
        for node_data in wf.values():
            if node_data.get("class_type") == "ai4artsed_prompt_interception":
                current_model_full = node_data["inputs"].get("model", "")
                if current_model_full.startswith("local/"):
                    local_model_with_tag = current_model_full[6:]
                    local_model_base = local_model_with_tag.split(':')[0]
                    
                    # First, try to match the full name (e.g., "llava:13b"), then fall back to the base name (e.g., "llava")
                    openrouter_model = OLLAMA_TO_OPENROUTER_MAP.get(local_model_with_tag) or OLLAMA_TO_OPENROUTER_MAP.get(local_model_base)

                    if openrouter_model:
                        node_data["inputs"]["model"] = f"openrouter/{openrouter_model}"
                        logging.info(f"Swapped {current_model_full} to {node_data['inputs']['model']}")
                    else:
                        logging.warning(f"No OpenRouter equivalent found for {current_model_full}. Keeping local model.")

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
        resp = requests.post(f"http://localhost:{COMFYUI_PORT}/prompt", json={"prompt": wf, "client_id": str(uuid.uuid4())}, timeout=180)
        resp.raise_for_status()
        comfyui_data = resp.json()
        if not comfyui_data.get("prompt_id"):
            return jsonify({"error": "ComfyUI did not return a prompt_id."}), 502
        return jsonify({"prompt_id": comfyui_data["prompt_id"], "translated_prompt": translated_prompt})
    except requests.exceptions.RequestException as e:
        error_details = str(e)
        if e.response is not None:
            try:
                error_details = e.response.json()
            except json.JSONDecodeError:
                error_details = e.response.text
        logging.error(f"ComfyUI request failed. Details: {error_details}")
        return jsonify({"error": f"Failed to connect to the ComfyUI service: {error_details}"}), 502

# --- Logging Filter ---
class ComfyUIFilter(logging.Filter):
    def filter(self, record):
        # Suppress successful GET requests for the ComfyUI proxy to reduce log spam
        if "GET /comfyui/" in record.getMessage() and " 200 " in record.getMessage():
            return False
        return True

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
    except requests.exceptions.RequestException:
        return jsonify({"error": f"Failed to connect to ComfyUI on port {COMFYUI_PORT}."}), 502

if __name__ == "__main__":
    try:
        from waitress import serve
    except ImportError:
        print("--> Waitress not found. Please install it using: pip install waitress")
        exit(1)

    # Suppress noisy ComfyUI polling logs
    log = logging.getLogger('werkzeug')
    log.addFilter(ComfyUIFilter())
    
    # Run the app with the production-grade Waitress server
    print("--> Starting server with Waitress on http://0.0.0.0:5000")
    serve(app, host="0.0.0.0", port=5000, threads=8)
