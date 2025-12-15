#!/usr/bin/env bash
set -euo pipefail

show_help() {
  cat <<'USAGE'
Usage: ./scripts/install_lora_env.sh [OPTIONS]

Install a dedicated Python environment for LoRA training together with
system-level prerequisites (when available).

Options:
  -n, --name NAME          Name of the virtual environment directory (default: venv-lora)
  -p, --python PATH        Python interpreter to use (default: python3)
  --skip-system           Skip installation of system packages via apt-get
  -h, --help               Show this help message

The script creates the virtual environment inside the repository root
and installs the packages listed in requirements/lora.txt.
USAGE
}

ENV_NAME="venv-lora"
PYTHON_BIN="python3"
INSTALL_SYSTEM_PACKAGES=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    -n|--name)
      ENV_NAME="$2"
      shift 2
      ;;
    -p|--python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --skip-system)
      INSTALL_SYSTEM_PACKAGES=0
      shift
      ;;
    -h|--help)
      show_help
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REQ_FILE="${REPO_ROOT}/requirements/lora.txt"
VENV_PATH="${REPO_ROOT}/${ENV_NAME}"

if [[ ! -f "${REQ_FILE}" ]]; then
  echo "[ERROR] requirements file not found: ${REQ_FILE}" >&2
  exit 1
fi

if [[ ${INSTALL_SYSTEM_PACKAGES} -eq 1 ]]; then
  if command -v apt-get >/dev/null 2>&1; then
    echo "[INFO] Installing system packages required for LoRA training"
    APT_CMD=(apt-get)
    if [[ $EUID -ne 0 ]]; then
      if command -v sudo >/dev/null 2>&1; then
        APT_CMD=(sudo apt-get)
      else
        echo "[WARNING] No sudo available. Skipping system package installation." >&2
        APT_CMD=()
      fi
    fi
    if [[ ${#APT_CMD[@]} -gt 0 ]]; then
      "${APT_CMD[@]}" update
      "${APT_CMD[@]}" install -y build-essential git python3-venv python3-dev ffmpeg libgl1
    fi
  else
    echo "[WARNING] apt-get not available. Skipping system package installation." >&2
  fi
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "[ERROR] Python interpreter not found: ${PYTHON_BIN}" >&2
  exit 1
fi

if [[ -d "${VENV_PATH}" ]]; then
  echo "[INFO] Reusing existing virtual environment at ${VENV_PATH}"
else
  echo "[INFO] Creating virtual environment at ${VENV_PATH}"
  "${PYTHON_BIN}" -m venv "${VENV_PATH}"
fi

# shellcheck source=/dev/null
source "${VENV_PATH}/bin/activate"

python -m pip install --upgrade pip wheel setuptools
python -m pip install -r "${REQ_FILE}"

cat <<NEXTSTEPS

[✔] LoRA environment installation complete.

Next steps:
  1. Activate the environment:
       source ${VENV_PATH}/bin/activate
  2. Configure Accelerate (only once):
       accelerate config
  3. (Optional) Log into Hugging Face to access gated models:
       huggingface-cli login

Afterwards you can launch trainings using the generated commands from the
LoRA web interface or follow docs/lora_training_setup.md.
NEXTSTEPS
