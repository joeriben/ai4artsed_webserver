"""
Text Backend - Dekonstruktive LLM operations for Latent Text Lab

Session 175: Experimental text generation with access to model internals.

Features:
- Auto-quantization based on available VRAM (bf16 → int8 → int4)
- VRAM coordination via VRAMCoordinator
- Dekonstruktive methods:
  - Embedding extraction and interpolation
  - Attention map visualization
  - Token-level logit manipulation (surgery)
  - Layer-by-layer analysis
  - Deterministic seed variations

Usage:
    backend = get_text_backend()
    await backend.load_model("meta-llama/Llama-3.2-8B-Instruct")
    result = await backend.generate_with_token_surgery(
        prompt="Write a poem about nature",
        boost_tokens=["dark", "shadow"],
        suppress_tokens=["light", "sun"]
    )
"""

import logging
import threading
import time
import re
from typing import Optional, List, Dict, Any, AsyncGenerator
import asyncio

logger = logging.getLogger(__name__)


# =============================================================================
# VRAM Estimation
# =============================================================================

def estimate_model_vram(model_id: str, quantization: str = "bf16") -> float:
    """
    Estimate VRAM requirement for a model in GB.

    Uses config presets if available, falls back to parameter-count heuristic.
    """
    from config import TEXT_MODEL_PRESETS, TEXT_QUANT_MULTIPLIERS

    # Check presets first
    for preset in TEXT_MODEL_PRESETS.values():
        if preset["id"] == model_id:
            base_vram = preset["vram_gb"]
            break
    else:
        # Heuristic: ~2GB per billion parameters (bf16)
        match = re.search(r'(\d+)[Bb]', model_id)
        if match:
            params_b = int(match.group(1))
            base_vram = params_b * 2.0
        else:
            # Conservative default
            base_vram = 20.0
            logger.warning(f"[TEXT] Unknown model {model_id}, assuming {base_vram}GB")

    multiplier = TEXT_QUANT_MULTIPLIERS.get(quantization, 1.0)
    return base_vram * multiplier


def choose_quantization(model_id: str, available_vram_gb: float) -> tuple[str, float]:
    """
    Choose optimal quantization level for available VRAM.

    Strategy:
    1. Try bf16 (best quality)
    2. Fall back to int8 if needed
    3. Fall back to int4 as last resort

    Returns (quantization_string, estimated_vram_gb).
    """
    for quant in ["bf16", "int8", "int4"]:
        estimated = estimate_model_vram(model_id, quant)
        # Leave 10% headroom
        if estimated * 1.1 < available_vram_gb:
            return quant, estimated

    # Even int4 doesn't fit - return it anyway (will fail at load time)
    return "int4", estimate_model_vram(model_id, "int4")


class TextBackend:
    """
    Dekonstruktive LLM operations with VRAM coordination.

    Integrates with VRAMCoordinator for cross-backend eviction.
    """

    def __init__(self):
        """Initialize text backend."""
        from config import TEXT_DEVICE, TEXT_DEFAULT_DTYPE

        self.device = TEXT_DEVICE
        self.default_dtype = TEXT_DEFAULT_DTYPE

        # Model cache (mirrors DiffusersBackend pattern)
        self._models: Dict[str, tuple] = {}  # model_id -> (model, tokenizer)
        self._model_last_used: Dict[str, float] = {}
        self._model_vram_mb: Dict[str, float] = {}
        self._model_in_use: Dict[str, int] = {}
        self._model_quant: Dict[str, str] = {}
        self._load_lock = threading.Lock()

        # Register with VRAM coordinator
        self._register_with_coordinator()

        # Get total VRAM for planning
        try:
            import torch
            if torch.cuda.is_available():
                props = torch.cuda.get_device_properties(0)
                self._total_vram_gb = props.total_memory / 1024**3
            else:
                self._total_vram_gb = 0
        except ImportError:
            self._total_vram_gb = 0

        logger.info(f"[TEXT] Initialized: device={self.device}, total_vram={self._total_vram_gb:.1f}GB")

    def _register_with_coordinator(self):
        """Register with VRAM coordinator for cross-backend eviction."""
        try:
            from services.vram_coordinator import get_vram_coordinator
            coordinator = get_vram_coordinator()
            coordinator.register_backend(self)
            logger.info("[TEXT] Registered with VRAM coordinator")
        except Exception as e:
            logger.warning(f"[TEXT] Failed to register with VRAM coordinator: {e}")

    # =========================================================================
    # VRAMBackend Protocol Implementation
    # =========================================================================

    def get_backend_id(self) -> str:
        """Unique identifier for this backend."""
        return "text"

    def get_registered_models(self) -> List[Dict[str, Any]]:
        """Return list of models with VRAM info for coordinator."""
        from services.vram_coordinator import EvictionPriority

        return [
            {
                "model_id": mid,
                "vram_mb": self._model_vram_mb.get(mid, 0),
                "priority": EvictionPriority.NORMAL,
                "last_used": self._model_last_used.get(mid, 0),
                "in_use": self._model_in_use.get(mid, 0),
            }
            for mid in self._models
        ]

    def evict_model(self, model_id: str) -> bool:
        """Evict a specific model (called by coordinator)."""
        return self._unload_model_sync(model_id)

    # =========================================================================
    # Model Loading
    # =========================================================================

    def _get_free_vram_gb(self) -> float:
        """Get currently free VRAM in GB."""
        import torch
        if not torch.cuda.is_available():
            return 0
        total = torch.cuda.get_device_properties(0).total_memory
        allocated = torch.cuda.memory_allocated(0)
        return (total - allocated) / 1024**3

    def _load_model_sync(
        self,
        model_id: str,
        quantization: Optional[str] = None
    ) -> bool:
        """
        Load model with VRAM coordination.

        1. Estimate VRAM requirement
        2. Choose quantization if not specified
        3. Request VRAM from coordinator (triggers cross-backend eviction)
        4. Load model
        """
        with self._load_lock:
            import torch

            # Already loaded?
            if model_id in self._models:
                self._model_last_used[model_id] = time.time()
                return True

            # Determine quantization
            free_vram = self._get_free_vram_gb()
            if quantization is None:
                quantization, estimated_gb = choose_quantization(model_id, free_vram)
            else:
                estimated_gb = estimate_model_vram(model_id, quantization)

            required_mb = estimated_gb * 1024

            logger.info(
                f"[TEXT] Loading {model_id}: "
                f"quant={quantization}, estimated={estimated_gb:.1f}GB, "
                f"free={free_vram:.1f}GB"
            )

            # Request VRAM from coordinator (may evict other backends' models)
            try:
                from services.vram_coordinator import get_vram_coordinator, EvictionPriority
                coordinator = get_vram_coordinator()
                coordinator.request_vram("text", required_mb, EvictionPriority.NORMAL)
            except Exception as e:
                logger.warning(f"[TEXT] VRAM coordinator request failed: {e}")

            # Load model
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer

                vram_before = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0

                tokenizer = AutoTokenizer.from_pretrained(model_id)

                # Build load kwargs based on quantization
                load_kwargs = {
                    "device_map": "auto",
                    "low_cpu_mem_usage": True,
                }

                if quantization == "bf16":
                    load_kwargs["torch_dtype"] = torch.bfloat16
                elif quantization == "fp16":
                    load_kwargs["torch_dtype"] = torch.float16
                elif quantization in ("int8", "int4", "nf4"):
                    from transformers import BitsAndBytesConfig

                    if quantization == "int8":
                        load_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_8bit=True
                        )
                    else:  # int4/nf4
                        load_kwargs["quantization_config"] = BitsAndBytesConfig(
                            load_in_4bit=True,
                            bnb_4bit_compute_dtype=torch.bfloat16,
                            bnb_4bit_quant_type="nf4" if quantization == "nf4" else "fp4"
                        )

                model = AutoModelForCausalLM.from_pretrained(
                    model_id,
                    output_hidden_states=True,
                    output_attentions=True,
                    **load_kwargs
                )
                model.eval()

                vram_after = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0
                actual_vram_mb = (vram_after - vram_before) / (1024 * 1024)

                self._models[model_id] = (model, tokenizer)
                self._model_last_used[model_id] = time.time()
                self._model_vram_mb[model_id] = actual_vram_mb
                self._model_quant[model_id] = quantization

                logger.info(
                    f"[TEXT] Loaded {model_id}: "
                    f"quant={quantization}, actual_vram={actual_vram_mb:.0f}MB"
                )
                return True

            except Exception as e:
                logger.error(f"[TEXT] Failed to load {model_id}: {e}")
                import traceback
                traceback.print_exc()
                return False

    def _unload_model_sync(self, model_id: str) -> bool:
        """Unload a model from memory."""
        import torch

        if model_id not in self._models:
            return False

        try:
            del self._models[model_id]
            self._model_last_used.pop(model_id, None)
            self._model_vram_mb.pop(model_id, None)
            self._model_in_use.pop(model_id, None)
            self._model_quant.pop(model_id, None)

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info(f"[TEXT] Unloaded {model_id}")
            return True
        except Exception as e:
            logger.error(f"[TEXT] Error unloading {model_id}: {e}")
            return False

    async def load_model(
        self,
        model_id: str,
        quantization: Optional[str] = None
    ) -> bool:
        """Async wrapper for model loading."""
        return await asyncio.to_thread(self._load_model_sync, model_id, quantization)

    async def unload_model(self, model_id: str) -> bool:
        """Async wrapper for model unloading."""
        return await asyncio.to_thread(self._unload_model_sync, model_id)

    def get_loaded_models(self) -> List[Dict[str, Any]]:
        """Get info about currently loaded models."""
        return [
            {
                "model_id": mid,
                "vram_mb": self._model_vram_mb.get(mid, 0),
                "quantization": self._model_quant.get(mid, "unknown"),
                "in_use": self._model_in_use.get(mid, 0) > 0,
                "last_used": self._model_last_used.get(mid, 0),
            }
            for mid in self._models
        ]

    # =========================================================================
    # DEKONSTRUKTIVE METHODS
    # =========================================================================

    async def get_prompt_embedding(
        self,
        text: str,
        model_id: str,
        layer: int = -1
    ) -> Dict[str, Any]:
        """
        Extract embedding representation of a prompt.

        Args:
            text: Input text
            model_id: Model to use
            layer: Which layer's hidden state (-1 = last)

        Returns:
            Dict with embedding stats and optionally the embedding itself
        """
        import torch

        if not await self.load_model(model_id):
            return {"error": f"Failed to load model {model_id}"}

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            with torch.no_grad():
                outputs = model(**inputs)

            # Get specified layer's hidden state
            hidden_states = outputs.hidden_states
            if layer < 0:
                layer = len(hidden_states) + layer
            embedding = hidden_states[layer]

            # Mean pool over sequence, convert to float32 for numpy/stats compatibility
            pooled = embedding.mean(dim=1).float()

            return {
                "model_id": model_id,
                "text": text,
                "layer": layer,
                "num_layers": len(hidden_states),
                "embedding_dim": pooled.shape[-1],
                "embedding_norm": float(pooled.norm()),
                "embedding_mean": float(pooled.mean()),
                "embedding_std": float(pooled.std()),
            }
        finally:
            self._model_in_use[model_id] -= 1

    async def interpolate_prompts(
        self,
        prompt_a: str,
        prompt_b: str,
        model_id: str,
        steps: int = 5,
        layer: int = -1
    ) -> Dict[str, Any]:
        """
        Analyze embedding space between two prompts.

        Returns statistics at each interpolation point.
        (Full generation from interpolated embeddings requires more complex projection)
        """
        import torch

        if not await self.load_model(model_id):
            return {"error": f"Failed to load model {model_id}"}

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            # Encode both prompts
            inputs_a = tokenizer(prompt_a, return_tensors="pt").to(model.device)
            inputs_b = tokenizer(prompt_b, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs_a = model(**inputs_a)
                outputs_b = model(**inputs_b)

            # Convert to float32 for consistent numeric operations
            hidden_a = outputs_a.hidden_states[layer].mean(dim=1).float()
            hidden_b = outputs_b.hidden_states[layer].mean(dim=1).float()

            distance = (hidden_a - hidden_b).norm().item()

            results = []
            for i in range(steps):
                alpha = i / (steps - 1) if steps > 1 else 0
                interpolated = (1 - alpha) * hidden_a + alpha * hidden_b

                results.append({
                    "alpha": alpha,
                    "prompt_a_influence": 1 - alpha,
                    "prompt_b_influence": alpha,
                    "embedding_norm": float(interpolated.norm()),
                    "distance_from_a": float((interpolated - hidden_a).norm()),
                    "distance_from_b": float((interpolated - hidden_b).norm()),
                })

            return {
                "model_id": model_id,
                "prompt_a": prompt_a,
                "prompt_b": prompt_b,
                "layer": layer,
                "total_distance": distance,
                "interpolation_points": results,
            }
        finally:
            self._model_in_use[model_id] -= 1

    async def get_attention_map(
        self,
        text: str,
        model_id: str,
        layer: Optional[int] = None,
        head: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Extract attention patterns for visualization.

        Args:
            text: Input text
            model_id: Model to use
            layer: Specific layer (None = all layers, aggregated)
            head: Specific head (None = all heads, averaged)

        Returns:
            Dict with tokens and attention weights
        """
        import torch

        if not await self.load_model(model_id):
            return {"error": f"Failed to load model {model_id}"}

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            inputs = tokenizer(text, return_tensors="pt").to(model.device)
            tokens = tokenizer.convert_ids_to_tokens(inputs.input_ids[0])

            with torch.no_grad():
                outputs = model(**inputs)

            attentions = outputs.attentions  # tuple of (batch, heads, seq, seq)
            num_layers = len(attentions)
            num_heads = attentions[0].shape[1]

            if layer is not None:
                # Single layer
                attn = attentions[layer].float()  # (1, heads, seq, seq)
                if head is not None:
                    attn = attn[:, head:head+1, :, :]
                attn = attn.mean(dim=1)  # Average over heads
                attention_matrix = attn[0].cpu().tolist()
            else:
                # Average over all layers and heads
                stacked = torch.stack([a.float().mean(dim=1) for a in attentions])
                attention_matrix = stacked.mean(dim=0)[0].cpu().tolist()

            return {
                "model_id": model_id,
                "text": text,
                "tokens": tokens,
                "num_layers": num_layers,
                "num_heads": num_heads,
                "layer_selected": layer,
                "head_selected": head,
                "attention_matrix": attention_matrix,
            }
        finally:
            self._model_in_use[model_id] -= 1

    async def generate_with_token_surgery(
        self,
        prompt: str,
        model_id: str,
        boost_tokens: Optional[List[str]] = None,
        suppress_tokens: Optional[List[str]] = None,
        boost_factor: float = 2.0,
        max_new_tokens: int = 50,
        temperature: float = 0.7,
        seed: int = -1
    ) -> Dict[str, Any]:
        """
        Generate text with logit manipulation for bias exploration.

        Args:
            prompt: Input prompt
            model_id: Model to use
            boost_tokens: Words to make more likely
            suppress_tokens: Words to suppress
            boost_factor: Multiplier for boosted tokens
            max_new_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            seed: Random seed (-1 for random)

        Returns:
            Dict with generated text and metadata
        """
        import torch
        import random

        if not await self.load_model(model_id):
            return {"error": f"Failed to load model {model_id}"}

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)
            torch.manual_seed(seed)

            # Convert boost/suppress tokens to IDs
            boost_ids = set()
            suppress_ids = set()

            for tok in (boost_tokens or []):
                ids = tokenizer.encode(tok, add_special_tokens=False)
                boost_ids.update(ids)

            for tok in (suppress_tokens or []):
                ids = tokenizer.encode(tok, add_special_tokens=False)
                suppress_ids.update(ids)

            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            generated = inputs.input_ids.clone()
            prompt_length = inputs.input_ids.shape[1]

            for _ in range(max_new_tokens):
                with torch.no_grad():
                    outputs = model(generated)
                    logits = outputs.logits[:, -1, :].float()  # float32 for stable softmax

                    # Apply surgery
                    for tid in boost_ids:
                        if tid < logits.shape[-1]:
                            logits[:, tid] *= boost_factor
                    for tid in suppress_ids:
                        if tid < logits.shape[-1]:
                            logits[:, tid] = -float('inf')

                    probs = torch.softmax(logits / temperature, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                    generated = torch.cat([generated, next_token], dim=-1)

                    if next_token.item() == tokenizer.eos_token_id:
                        break

            generated_text = tokenizer.decode(generated[0], skip_special_tokens=True)
            new_text = tokenizer.decode(generated[0, prompt_length:], skip_special_tokens=True)

            return {
                "model_id": model_id,
                "prompt": prompt,
                "generated_text": generated_text,
                "new_text": new_text,
                "seed": seed,
                "temperature": temperature,
                "boost_tokens": list(boost_tokens or []),
                "suppress_tokens": list(suppress_tokens or []),
                "boost_factor": boost_factor,
                "tokens_generated": generated.shape[1] - prompt_length,
            }
        finally:
            self._model_in_use[model_id] -= 1

    async def generate_streaming(
        self,
        prompt: str,
        model_id: str,
        max_new_tokens: int = 100,
        temperature: float = 0.7,
        seed: int = -1
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generate text with real-time token streaming (SSE).

        Yields:
            {"type": "token", "token": "...", "token_id": N}
            {"type": "done", "full_text": "..."}
            {"type": "error", "message": "..."}
        """
        import torch
        import random

        if not await self.load_model(model_id):
            yield {"type": "error", "message": f"Failed to load model {model_id}"}
            return

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            if seed == -1:
                seed = random.randint(0, 2**32 - 1)
            torch.manual_seed(seed)

            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            generated = inputs.input_ids.clone()

            for i in range(max_new_tokens):
                with torch.no_grad():
                    outputs = model(generated)
                    logits = outputs.logits[:, -1, :].float()  # float32 for stable softmax

                    probs = torch.softmax(logits / temperature, dim=-1)
                    next_token = torch.multinomial(probs, num_samples=1)

                    generated = torch.cat([generated, next_token], dim=-1)

                    token_id = next_token.item()
                    token_text = tokenizer.decode([token_id])

                    yield {
                        "type": "token",
                        "token": token_text,
                        "token_id": token_id,
                        "step": i,
                    }

                    if token_id == tokenizer.eos_token_id:
                        break

            full_text = tokenizer.decode(generated[0], skip_special_tokens=True)
            yield {
                "type": "done",
                "full_text": full_text,
                "seed": seed,
                "tokens_generated": generated.shape[1] - inputs.input_ids.shape[1],
            }

        except Exception as e:
            yield {"type": "error", "message": str(e)}
        finally:
            self._model_in_use[model_id] -= 1

    async def compare_layer_outputs(
        self,
        text: str,
        model_id: str
    ) -> Dict[str, Any]:
        """
        Analyze how representations change through layers.

        Returns statistics for each layer's hidden state.
        """
        import torch
        import numpy as np

        if not await self.load_model(model_id):
            return [{"error": f"Failed to load model {model_id}"}]

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            inputs = tokenizer(text, return_tensors="pt").to(model.device)

            with torch.no_grad():
                outputs = model(**inputs)

            results = []
            prev_hidden = None

            for i, hidden_state in enumerate(outputs.hidden_states):
                hs = hidden_state[0].float().cpu().numpy()

                layer_stats = {
                    "layer": i,
                    "mean_activation": float(np.mean(hs)),
                    "std_activation": float(np.std(hs)),
                    "max_activation": float(np.max(hs)),
                    "min_activation": float(np.min(hs)),
                    "sparsity": float(np.mean(np.abs(hs) < 0.01)),
                    "l2_norm": float(np.linalg.norm(hs)),
                }

                # Change from previous layer
                if prev_hidden is not None:
                    delta = hs - prev_hidden
                    layer_stats["delta_norm"] = float(np.linalg.norm(delta))
                    layer_stats["delta_mean"] = float(np.mean(np.abs(delta)))

                prev_hidden = hs
                results.append(layer_stats)

            return {
                "model_id": model_id,
                "text": text,
                "num_layers": len(results),
                "layers": results,
            }
        finally:
            self._model_in_use[model_id] -= 1

    async def generate_variations(
        self,
        prompt: str,
        model_id: str,
        num_variations: int = 5,
        temperature: float = 0.8,
        base_seed: int = 42,
        max_new_tokens: int = 50
    ) -> Dict[str, Any]:
        """
        Generate deterministic variations with different seeds.

        Useful for exploring the stochastic nature of generation.
        """
        import torch

        if not await self.load_model(model_id):
            return {"error": f"Failed to load model {model_id}"}

        model, tokenizer = self._models[model_id]
        self._model_in_use[model_id] = self._model_in_use.get(model_id, 0) + 1

        try:
            inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
            results = []

            for i in range(num_variations):
                seed = base_seed + i
                torch.manual_seed(seed)

                outputs = model.generate(
                    inputs.input_ids,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=0.9,
                    pad_token_id=tokenizer.eos_token_id,
                )

                text = tokenizer.decode(outputs[0], skip_special_tokens=True)

                results.append({
                    "variation": i,
                    "seed": seed,
                    "temperature": temperature,
                    "text": text,
                })

            return {
                "model_id": model_id,
                "prompt": prompt,
                "num_variations": num_variations,
                "base_seed": base_seed,
                "variations": results,
            }
        finally:
            self._model_in_use[model_id] -= 1


# =============================================================================
# Singleton
# =============================================================================

_backend: Optional[TextBackend] = None


def get_text_backend() -> TextBackend:
    """Get TextBackend singleton."""
    global _backend
    if _backend is None:
        _backend = TextBackend()
    return _backend


def reset_text_backend():
    """Reset singleton (for testing)."""
    global _backend
    _backend = None
