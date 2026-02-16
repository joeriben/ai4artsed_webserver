"""
Crossmodal Lab Backend — Latent Audio Synth

Replaces the old Strategy A/B/C approach with direct T5 embedding manipulation
for Stable Audio, analogous to the Surrealizer for images.

Operations:
- Interpolation: LERP between embedding A and B
- Extrapolation: alpha > 1.0 or < 0.0
- Magnitude: global scaling of embeddings
- Noise injection: Gaussian noise on embedding space
- Dimension shift: per-dimension offsets

Usage:
    backend = get_cross_aesthetic_backend()
    result = await backend.synth(
        prompt_a="ocean waves",
        prompt_b="piano melody",
        alpha=0.5,
    )
"""

import logging
import time
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class CrossmodalLabBackend:
    """
    Crossmodal Lab backend for Latent Audio Synth.

    Manipulates Stable Audio's T5 conditioning space (768d) directly,
    enabling interpolation, extrapolation, magnitude scaling, noise injection,
    and per-dimension shifts between text embeddings.
    """

    def __init__(self):
        logger.info("[CROSSMODAL] Initialized CrossmodalLabBackend")

    async def synth(
        self,
        prompt_a: str,
        prompt_b: Optional[str] = None,
        alpha: float = 0.5,
        magnitude: float = 1.0,
        noise_sigma: float = 0.0,
        dimension_offsets: Optional[Dict[int, float]] = None,
        duration_seconds: float = 1.0,
        steps: int = 20,
        cfg_scale: float = 3.5,
        seed: int = -1,
    ) -> Optional[Dict[str, Any]]:
        """
        Latent Audio Synth: manipulate T5 embeddings and generate audio.

        1. Encode prompt_a (and optionally prompt_b) via T5
        2. Apply manipulation operations on the embedding(s)
        3. Generate audio from manipulated embedding via Stable Audio

        Args:
            prompt_a: Base text prompt
            prompt_b: Optional second prompt for interpolation/extrapolation
            alpha: Interpolation factor (0=A, 1=B, >1 or <0 = extrapolation)
            magnitude: Global embedding scale (0.1-5.0)
            noise_sigma: Gaussian noise strength (0=none, 0.5=moderate)
            dimension_offsets: Per-dimension offset values {dim_idx: offset}
            duration_seconds: Audio duration (0.5-5.0s for looping)
            steps: Inference steps
            cfg_scale: Classifier-free guidance scale
            seed: Random seed (-1 = random)

        Returns:
            Dict with audio_base64, embedding_stats, generation_time_ms, seed
        """
        import torch
        import random as random_mod

        start_time = time.time()

        try:
            from services.stable_audio_backend import get_stable_audio_backend
            stable_audio = get_stable_audio_backend()

            # Step 1: Encode prompt(s)
            emb_a, mask_a = await stable_audio.encode_prompt(prompt_a)
            if emb_a is None:
                return None

            if prompt_b:
                emb_b, mask_b = await stable_audio.encode_prompt(prompt_b)
                if emb_b is None:
                    return None
            else:
                emb_b = None
                mask_b = None

            # Step 2: Apply manipulations
            result_emb = self._manipulate_embedding(
                emb_a, emb_b, alpha, magnitude, noise_sigma, dimension_offsets, seed
            )

            # Use mask from prompt_a (or combined mask if both prompts)
            result_mask = mask_a
            if mask_b is not None:
                result_mask = torch.maximum(mask_a, mask_b)

            # Step 3: Compute embedding stats for visualization
            stats = self._compute_stats(result_emb, emb_a, emb_b)

            # Step 4: Generate audio
            duration_seconds = max(0.5, min(duration_seconds, 47.0))

            if seed == -1:
                seed = random_mod.randint(0, 2**32 - 1)

            audio_bytes = await stable_audio.generate_from_embeddings(
                prompt_embeds=result_emb,
                attention_mask=result_mask,
                seconds_start=0.0,
                seconds_end=duration_seconds,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed,
            )

            if audio_bytes is None:
                return None

            elapsed_ms = int((time.time() - start_time) * 1000)

            logger.info(
                f"[CROSSMODAL] Synth complete: alpha={alpha}, magnitude={magnitude}, "
                f"noise={noise_sigma}, duration={duration_seconds}s, time={elapsed_ms}ms"
            )

            return {
                "audio_bytes": audio_bytes,
                "embedding_stats": stats,
                "generation_time_ms": elapsed_ms,
                "seed": seed,
            }

        except Exception as e:
            logger.error(f"[CROSSMODAL] Synth error: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _manipulate_embedding(
        self,
        emb_a,  # [1, seq, 768]
        emb_b,  # [1, seq, 768] or None
        alpha: float,
        magnitude: float,
        noise_sigma: float,
        dimension_offsets: Optional[Dict[int, float]],
        seed: int,
    ):
        """Apply embedding manipulation operations."""
        import torch

        # Interpolation / extrapolation
        if emb_b is not None:
            result = (1.0 - alpha) * emb_a + alpha * emb_b
        else:
            result = emb_a.clone()

        # Magnitude scaling
        if magnitude != 1.0:
            result = result * magnitude

        # Noise injection
        if noise_sigma > 0.0:
            generator = torch.Generator(device=result.device)
            if seed != -1:
                generator.manual_seed(seed + 1)  # Offset from generation seed
            noise = torch.randn_like(result, generator=generator) * noise_sigma
            result = result + noise

        # Per-dimension offsets
        if dimension_offsets:
            for dim_idx, offset_value in dimension_offsets.items():
                dim_idx = int(dim_idx)
                if 0 <= dim_idx < result.shape[-1]:
                    result[:, :, dim_idx] += offset_value

        return result

    def _compute_stats(self, embedding, emb_a=None, emb_b=None) -> Dict[str, Any]:
        """Compute embedding statistics for frontend visualization.

        When emb_b is provided, all_activations are sorted by prompt A/B difference
        (feature probing). Otherwise falls back to activation magnitude sorting.
        """
        import torch

        emb = embedding.detach()
        mean_val = emb.mean().item()
        std_val = emb.std().item()

        # Top dimensions by absolute mean activation (backward compat)
        dim_means_abs = emb.squeeze(0).mean(dim=0).abs()  # [768]
        top_k = min(10, dim_means_abs.shape[0])
        top_vals, top_indices = dim_means_abs.topk(top_k)

        # All 768 activations with diff-based or magnitude-based sorting
        dim_means_signed = emb.squeeze(0).mean(dim=0)  # [768], signed

        if emb_b is not None and emb_a is not None:
            # Feature probing: sort by prompt A/B difference
            diff = emb_a.detach().squeeze(0).mean(dim=0) - emb_b.detach().squeeze(0).mean(dim=0)
            sort_order = diff.abs().argsort(descending=True)
            sort_mode = "diff"
        else:
            # Single-prompt fallback: sort by activation magnitude
            sort_order = dim_means_signed.abs().argsort(descending=True)
            sort_mode = "magnitude"

        all_activations = [
            {"dim": int(idx), "value": round(float(dim_means_signed[idx].item()), 4)}
            for idx in sort_order.tolist()
        ]

        return {
            "mean": round(mean_val, 4),
            "std": round(std_val, 4),
            "top_dimensions": [
                {"dim": int(idx), "value": round(float(val), 4)}
                for idx, val in zip(top_indices.tolist(), top_vals.tolist())
            ],
            "all_activations": all_activations,
            "sort_mode": sort_mode,
        }


# =============================================================================
# Singleton
# =============================================================================

_backend: Optional[CrossmodalLabBackend] = None


def get_cross_aesthetic_backend() -> CrossmodalLabBackend:
    global _backend
    if _backend is None:
        _backend = CrossmodalLabBackend()
    return _backend


def reset_cross_aesthetic_backend():
    global _backend
    _backend = None
