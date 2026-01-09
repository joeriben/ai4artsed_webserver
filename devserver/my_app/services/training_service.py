import os
import shutil
import subprocess
import threading
import time
import toml
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

# Logger Setup
logger = logging.getLogger(__name__)

# Constants
KOHYA_DIR = Path("/home/joerissen/ai/kohya_ss_new")
KOHYA_VENV = KOHYA_DIR / "venv"
DATASET_BASE_DIR = KOHYA_DIR / "dataset"
OUTPUT_DIR = Path("/home/joerissen/ai/SwarmUI/Models/Lora") # Direct output to ComfyUI
LOG_DIR = KOHYA_DIR / "logs"

# Ensure directories exist
DATASET_BASE_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

class TrainingService:
    def __init__(self):
        self._current_process: Optional[subprocess.Popen] = None
        self._training_status = {
            "is_training": False,
            "project_name": None,
            "progress": 0,
            "current_step": 0,
            "total_steps": 0,
            "log_lines": [],
            "error": None
        }
        self._log_lock = threading.Lock()

    def get_gpu_vram(self) -> int:
        """Detects available VRAM in GB using nvidia-smi."""
        try:
            # Run nvidia-smi to get total memory (in MiB)
            # Query format: memory.total
            result = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
                encoding="utf-8"
            )
            # Sum up memory of all GPUs (if multi-gpu) or take the first one
            # For simplicity in Kohya single-process, we usually target GPU 0
            # But let's assume we use the first GPU found.
            lines = result.strip().split('\n')
            if not lines:
                return 0
            
            total_mib = int(lines[0].strip())
            total_gb = total_mib / 1024
            logger.info(f"Detected GPU VRAM: {total_gb:.1f} GB")
            return int(total_gb)
        except Exception as e:
            logger.error(f"Failed to detect VRAM: {e}")
            return 24 # Fallback assumption (Consumer High-End)

    def calculate_training_params(self, vram_gb: int) -> Dict[str, Any]:
        """
        Determines optimal training parameters based on VRAM.
        SD3.5 Large LoRA Training VRAM Requirements (Approximate @ 1024x1024):
        - Batch 1, GradCheckpointing=True: ~18-22 GB
        - Batch 1, GradCheckpointing=False: ~30-35 GB
        - Batch 4, GradCheckpointing=False: ~48-50 GB
        - Batch 8, GradCheckpointing=False: ~80+ GB
        """
        params = {
            "batch_size": 1,
            "gradient_checkpointing": True,
            "cache_latents_to_disk": True,
            "persistent_workers": True,
            "workers": 4
        }

        if vram_gb >= 80: # A100 80G, H100, or Multi-GPU setups acting as one
            params.update({
                "batch_size": 8,
                "gradient_checkpointing": False, # Max speed
                "workers": 16
            })
        elif vram_gb >= 40: # RTX 6000 Ada (48GB), A6000 (48GB), A40
            params.update({
                "batch_size": 4, # Safer fit than 8
                "gradient_checkpointing": False, # Speed priority
                "workers": 8
            })
        elif vram_gb >= 24: # RTX 3090/4090 (24GB)
            params.update({
                "batch_size": 1,
                "gradient_checkpointing": True, # Needed to fit
                "workers": 8
            })
        else: # < 24GB (e.g. 16GB Cards) - might OOM for SD3.5 Large
            params.update({
                "batch_size": 1,
                "gradient_checkpointing": True,
                "cache_latents_to_disk": True,
                "workers": 4
            })
            logger.warning("VRAM < 24GB. Training SD3.5 Large might fail or be extremely slow.")

        logger.info(f"Auto-Config for {vram_gb}GB VRAM: {params}")
        return params

    def create_project(self, project_name: str, images: List[Any], trigger_word: str):
        """Prepares dataset and config for a new training project."""
        if self._training_status["is_training"]:
            raise Exception("Training already in progress")

        # 1. Setup Directories
        # Sanitation: simple alphanumeric only for folder safety
        safe_name = "".join([c for c in project_name if c.isalnum() or c in ('-', '_')])
        project_dir = DATASET_BASE_DIR / safe_name
        image_dir = project_dir / "images"
        
        # 10_ prefix means 10 repeats per image (standard for LoRA)
        # We append the trigger word to the folder name so Kohya uses it as a tag
        # Format: <repeats>_<trigger_word>
        img_folder_name = f"40_{trigger_word}" if trigger_word else "40_lora"
        final_image_dir = image_dir / img_folder_name
        
        if project_dir.exists():
            shutil.rmtree(project_dir)
        final_image_dir.mkdir(parents=True, exist_ok=True)

        # 2. Save Images
        for img in images:
            file_path = final_image_dir / img.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(img.file, buffer)

        # 3. Detect Hardware & Optimize Config
        vram = self.get_gpu_vram()
        optim_params = self.calculate_training_params(vram)

        # 4. Create Config
        config = self._generate_sd35_config(
            project_dir=project_dir,
            image_dir=image_dir, 
            output_name=safe_name,
            params=optim_params
        )
        
        config_path = project_dir / "train_config.toml"
        with open(config_path, "w") as f:
            toml.dump(config, f)
            
        return {
            "project_name": safe_name,
            "image_count": len(images),
            "config_path": str(config_path),
            "hardware_info": {
                "vram_gb": vram,
                "config_used": optim_params
            }
        }

    def _generate_sd35_config(self, project_dir: Path, image_dir: Path, output_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generates TOML config for SD 3.5 Large with dynamic hardware params"""
        return {
            "model_arguments": {
                "pretrained_model_name_or_path": "/home/joerissen/ai/SwarmUI/Models/Stable-Diffusion/OfficialStableDiffusion/sd3.5_large.safetensors",
                "vae": "" # Built-in VAE
            },
            "dataset_arguments": {
                "train_data_dir": str(image_dir),
                "resolution": "1024,1024",
                "enable_bucket": True,
                "min_bucket_reso": 512,
                "max_bucket_reso": 2048,
                "batch_size": params["batch_size"]
            },
            "training_arguments": {
                "output_dir": str(OUTPUT_DIR),
                "output_name": output_name,
                "save_precision": "bf16",
                "mixed_precision": "bf16",
                "max_train_epochs": 10,
                "save_every_n_epochs": 2,
                "learning_rate": 4e-4, 
                "lr_scheduler": "cosine",
                "optimizer_type": "AdamW8bit",
                "gradient_checkpointing": params["gradient_checkpointing"],
                "gradient_accumulation_steps": 1, 
                "cache_latents": True,
                "cache_latents_to_disk": params["cache_latents_to_disk"],
                "logging_dir": str(LOG_DIR),
                "bf16": True,
                "persistent_data_loader_workers": params["persistent_workers"],
                "max_data_loader_n_workers": params["workers"]
            },
            "network_arguments": {
                "network_module": "networks.lora_sd3",
                "network_dim": 32,
                "network_alpha": 16,
                "network_train_unet_only": False 
            },
            "optimization_arguments": {
                "xformers": True # SD3 often prefers Flash Attention
            }
        }

    def start_training_process(self, project_name: str):
        """Starts the training subprocess."""
        if self._training_status["is_training"]:
            return False

        safe_name = "".join([c for c in project_name if c.isalnum() or c in ('-', '_')])
        config_path = DATASET_BASE_DIR / safe_name / "train_config.toml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Config not found for project {safe_name}")

        self._reset_status(safe_name)
        self._training_status["is_training"] = True

        # Construct Command
        # We execute via 'bash -c' to source the venv correctly
        # Explicitly pass Text Encoders as CLI args
        clip_l = "/home/joerissen/ai/SwarmUI/Models/clip/clip_l.safetensors"
        clip_g = "/home/joerissen/ai/SwarmUI/Models/clip/clip_g.safetensors"
        t5xxl = "/home/joerissen/ai/SwarmUI/Models/clip/t5xxl_fp16.safetensors"
        
        cmd = [
            "/bin/bash", "-c",
            f"source {KOHYA_VENV}/bin/activate && "
            f"python {KOHYA_DIR}/sd-scripts/sd3_train_network.py --config_file {config_path} "
            f"--clip_l={clip_l} --clip_g={clip_g} --t5xxl={t5xxl}"
        ]

        def run_proc():
            try:
                self._current_process = subprocess.Popen(
                    cmd,
                    cwd=str(KOHYA_DIR),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, # Merge stderr into stdout
                    text=True,
                    bufsize=1
                )

                # Stream logs
                if self._current_process.stdout:
                    for line in iter(self._current_process.stdout.readline, ''):
                        self._append_log(line)
                        if "steps:" in line.lower():
                            pass
                    
                    self._current_process.stdout.close()
                return_code = self._current_process.wait()
                
                if return_code == 0:
                    self._append_log("TRAINING SUCCESSFUL! LoRA saved to ComfyUI.")
                else:
                    self._append_log(f"TRAINING FAILED with code {return_code}")
                    self._training_status["error"] = f"Process exited with {return_code}"

            except Exception as e:
                self._append_log(f"CRITICAL ERROR: {str(e)}")
                self._training_status["error"] = str(e)
            finally:
                self._training_status["is_training"] = False
                self._current_process = None

        # Run in separate thread to not block API
        t = threading.Thread(target=run_proc, daemon=True)
        t.start()
        
        return True

    def stop_training(self):
        if self._current_process:
            self._current_process.terminate()
            self._append_log("Training manually stopped by user.")
            return True
        return False
        
    def delete_project_files(self, project_name: str):
        """GDPR Compliance: Deletes ALL training images for a project."""
        if self._training_status["is_training"] and self._training_status["project_name"] == project_name:
            return False # Cannot delete while training
            
        safe_name = "".join([c for c in project_name if c.isalnum() or c in ('-', '_')])
        project_dir = DATASET_BASE_DIR / safe_name
        
        if project_dir.exists():
            try:
                shutil.rmtree(project_dir)
                return True
            except Exception as e:
                logger.error(f"Failed to delete project files for {safe_name}: {e}")
                return False
        return True # Already deleted or didn't exist

    def get_status(self):
        return self._training_status

    def _reset_status(self, project_name):
        self._training_status = {
            "is_training": False,
            "project_name": project_name,
            "progress": 0,
            "current_step": 0,
            "total_steps": 0,
            "log_lines": [],
            "error": None
        }

    def _append_log(self, line: str):
        line = line.strip()
        if not line: return
        with self._log_lock:
            self._training_status["log_lines"].append(line)
            # Keep log size manageable (last 1000 lines)
            if len(self._training_status["log_lines"]) > 1000:
                self._training_status["log_lines"].pop(0)

# Global Instance
training_service = TrainingService()