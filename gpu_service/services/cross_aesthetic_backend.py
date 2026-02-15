"""
Cross-Aesthetic Backend - Exploiting the Indifference Thesis

Orchestrates cross-modal generation between image and audio models,
exploiting the fundamental modality indifference of generative AI.

Three strategies:
- A: CLIP image embeddings → Stable Audio conditioning (768d dimensional match)
- B: Shared noise seed → parallel image + audio from identical randomness
- C: Latent cross-decoding → force one VAE to interpret another's latent structure

The CLIP Vision model is managed internally (lazy load, evictable via VRAM coordinator).

Usage:
    backend = get_cross_aesthetic_backend()
    audio = await backend.image_to_audio(image_bytes, duration_seconds=10.0)
    image, audio = await backend.shared_seed(prompt="ocean", seed=42)
    audio = await backend.cross_decode(prompt="abstract", direction="image_to_audio")
"""

import logging
import time
from typing import Optional, Dict, Any, List, Tuple
import asyncio

logger = logging.getLogger(__name__)


class CrossAestheticGenerator:
    """
    Cross-aesthetic generation orchestrator.

    Coordinates between DiffusersBackend, StableAudioGenerator,
    and an internal CLIP Vision model to implement cross-modal strategies.
    """

    def __init__(self):
        from config import CLIP_VISION_MODEL_ID

        self.clip_model_id = CLIP_VISION_MODEL_ID

        # CLIP Vision (lazy-loaded, evictable)
        self._clip_model = None
        self._clip_processor = None
        self._clip_loaded = False
        self._clip_vram_mb: float = 0
        self._clip_last_used: float = 0
        self._clip_in_use: int = 0

        self._register_with_coordinator()

        logger.info(f"[CROSS-AESTHETIC] Initialized: clip_model={self.clip_model_id}")

    def _register_with_coordinator(self):
        try:
            from services.vram_coordinator import get_vram_coordinator
            coordinator = get_vram_coordinator()
            coordinator.register_backend(self)
            logger.info("[CROSS-AESTHETIC] Registered with VRAM coordinator")
        except Exception as e:
            logger.warning(f"[CROSS-AESTHETIC] Failed to register: {e}")

    # =========================================================================
    # VRAMBackend Protocol (for CLIP Vision model)
    # =========================================================================

    def get_backend_id(self) -> str:
        return "cross_aesthetic"

    def get_registered_models(self) -> List[Dict[str, Any]]:
        from services.vram_coordinator import EvictionPriority

        if not self._clip_loaded:
            return []

        return [
            {
                "model_id": self.clip_model_id,
                "vram_mb": self._clip_vram_mb,
                "priority": EvictionPriority.LOW,  # Easily evictable
                "last_used": self._clip_last_used,
                "in_use": self._clip_in_use,
            }
        ]

    def evict_model(self, model_id: str) -> bool:
        return self._unload_clip_sync()

    # =========================================================================
    # CLIP Vision Management
    # =========================================================================

    async def _load_clip(self) -> bool:
        """Load CLIP Vision model for image encoding."""
        if self._clip_loaded:
            return True

        try:
            import torch

            try:
                from services.vram_coordinator import get_vram_coordinator, EvictionPriority
                coordinator = get_vram_coordinator()
                coordinator.request_vram("cross_aesthetic", 1200, EvictionPriority.NORMAL)
            except Exception as e:
                logger.warning(f"[CROSS-AESTHETIC] VRAM request failed: {e}")

            logger.info(f"[CROSS-AESTHETIC] Loading CLIP Vision: {self.clip_model_id}")

            vram_before = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0

            def _load():
                from transformers import CLIPVisionModel, CLIPImageProcessor
                model = CLIPVisionModel.from_pretrained(self.clip_model_id)
                model = model.to("cuda").eval()
                processor = CLIPImageProcessor.from_pretrained(self.clip_model_id)
                return model, processor

            self._clip_model, self._clip_processor = await asyncio.to_thread(_load)
            self._clip_loaded = True
            self._clip_last_used = time.time()

            vram_after = torch.cuda.memory_allocated(0) if torch.cuda.is_available() else 0
            self._clip_vram_mb = (vram_after - vram_before) / (1024 * 1024)

            logger.info(f"[CROSS-AESTHETIC] CLIP Vision loaded (VRAM: {self._clip_vram_mb:.0f}MB)")
            return True

        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC] Failed to load CLIP Vision: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _unload_clip_sync(self) -> bool:
        if not self._clip_loaded:
            return False

        try:
            import torch
            del self._clip_model
            del self._clip_processor
            self._clip_model = None
            self._clip_processor = None
            self._clip_loaded = False
            self._clip_vram_mb = 0
            self._clip_in_use = 0

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("[CROSS-AESTHETIC] CLIP Vision unloaded")
            return True
        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC] CLIP unload error: {e}")
            return False

    async def _encode_image(self, image_bytes: bytes):
        """
        Encode image with CLIP Vision → [1, 256, 768] features.

        CLIP ViT-L/14 vision hidden states are 1024d. We project to 768d
        via adaptive avg pooling on the feature dimension to match
        Stable Audio's T5-Base conditioning space.

        Returns:
            torch.Tensor of shape [1, 256, 768]
        """
        import torch
        import torch.nn.functional as F
        from PIL import Image
        import io

        if not self._clip_loaded:
            if not await self._load_clip():
                return None

        self._clip_in_use += 1
        self._clip_last_used = time.time()

        try:
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            inputs = self._clip_processor(images=image, return_tensors="pt")
            pixel_values = inputs["pixel_values"].to("cuda")

            def _encode():
                with torch.no_grad():
                    outputs = self._clip_model(pixel_values, output_hidden_states=True)
                    # Penultimate hidden states: [1, 257, 1024] (256 patches + CLS)
                    hidden = outputs.hidden_states[-2]
                    # Drop CLS token → [1, 256, 1024]
                    features = hidden[:, 1:, :]
                    # Project 1024d → 768d via adaptive avg pool on feature dim
                    # [1, 256, 1024] → pool last dim → [1, 256, 768]
                    projected = F.adaptive_avg_pool1d(features, 768)
                    return projected

            features = await asyncio.to_thread(_encode)
            logger.info(f"[CROSS-AESTHETIC] Image encoded: shape={list(features.shape)}")
            return features

        finally:
            self._clip_in_use -= 1

    # =========================================================================
    # Strategy A: Image → Audio (CLIP Vision → Stable Audio)
    # =========================================================================

    async def image_to_audio(
        self,
        image_bytes: bytes,
        duration_seconds: float = 10.0,
        steps: int = 100,
        cfg_scale: float = 7.0,
        seed: int = -1,
    ) -> Optional[bytes]:
        """
        Strategy A: Convert image to audio via CLIP → Stable Audio conditioning.

        CLIP ViT-L/14 vision features (1024d) are projected to 768d to match
        Stable Audio's T5-Base conditioning space, then injected directly.

        1. Encode image with CLIP Vision → [1, 256, 1024] → project → [1, 256, 768]
        2. Adaptive pool to [1, 128, 768] (match T5 sequence length)
        3. Inject as Stable Audio conditioning (bypassing T5 encoding)
        4. Generate audio

        Returns:
            Audio bytes (WAV) or None
        """
        import torch
        import torch.nn.functional as F

        try:
            # Step 1: Encode image
            clip_features = await self._encode_image(image_bytes)
            if clip_features is None:
                return None

            # Step 2: Adaptive pool 256 patches → 128 tokens (match T5 seq length)
            # [1, 256, 768] → [1, 768, 256] → pool → [1, 768, 128] → [1, 128, 768]
            pooled = F.adaptive_avg_pool1d(
                clip_features.transpose(1, 2), 128
            ).transpose(1, 2)

            # Create attention mask (all tokens active)
            attention_mask = torch.ones(
                pooled.shape[0], pooled.shape[1],
                dtype=torch.long, device=pooled.device
            )

            logger.info(f"[CROSS-AESTHETIC] Strategy A: CLIP features pooled to {list(pooled.shape)}")

            # Step 3: Unload CLIP to free VRAM for Stable Audio
            self._unload_clip_sync()

            # Step 4: Generate audio with injected embeddings
            from services.stable_audio_backend import get_stable_audio_backend
            stable_audio = get_stable_audio_backend()

            audio_bytes = await stable_audio.generate_from_embeddings(
                prompt_embeds=pooled,
                attention_mask=attention_mask,
                seconds_start=0.0,
                seconds_end=duration_seconds,
                steps=steps,
                cfg_scale=cfg_scale,
                seed=seed,
            )

            if audio_bytes:
                logger.info(f"[CROSS-AESTHETIC] Strategy A complete: {len(audio_bytes)} bytes audio")

            return audio_bytes

        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC] Strategy A error: {e}")
            import traceback
            traceback.print_exc()
            return None

    # =========================================================================
    # Strategy B: Shared Noise Seed
    # =========================================================================

    async def shared_seed(
        self,
        prompt: str,
        seed: int = 42,
        image_model: str = "stabilityai/stable-diffusion-3.5-large",
        image_width: int = 1024,
        image_height: int = 1024,
        image_steps: int = 25,
        image_cfg: float = 4.5,
        audio_duration: float = 10.0,
        audio_steps: int = 100,
        audio_cfg: float = 7.0,
    ) -> Tuple[Optional[bytes], Optional[bytes]]:
        """
        Strategy B: Generate image + audio from identical noise seed.

        Same torch.Generator seed produces structurally correlated random
        initialization. Each model's learned dynamics then transforms
        the same randomness into its respective modality.

        Returns:
            (image_bytes, audio_bytes) tuple — either can be None on failure
        """
        try:
            logger.info(f"[CROSS-AESTHETIC] Strategy B: seed={seed}, prompt='{prompt[:60]}...'")

            # Generate image
            from services.diffusers_backend import get_diffusers_backend
            diffusers = get_diffusers_backend()

            image_bytes = await diffusers.generate_image(
                prompt=prompt,
                model_id=image_model,
                width=image_width,
                height=image_height,
                steps=image_steps,
                cfg_scale=image_cfg,
                seed=seed,
            )

            if image_bytes:
                logger.info(f"[CROSS-AESTHETIC] Strategy B: image generated ({len(image_bytes)} bytes)")

            # Generate audio with same seed
            from services.stable_audio_backend import get_stable_audio_backend
            stable_audio = get_stable_audio_backend()

            audio_bytes = await stable_audio.generate_audio(
                prompt=prompt,
                duration_seconds=audio_duration,
                steps=audio_steps,
                cfg_scale=audio_cfg,
                seed=seed,
            )

            if audio_bytes:
                logger.info(f"[CROSS-AESTHETIC] Strategy B: audio generated ({len(audio_bytes)} bytes)")

            logger.info("[CROSS-AESTHETIC] Strategy B complete")
            return (image_bytes, audio_bytes)

        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC] Strategy B error: {e}")
            import traceback
            traceback.print_exc()
            return (None, None)

    # =========================================================================
    # Strategy C: Latent Cross-Decoding
    # =========================================================================

    async def cross_decode(
        self,
        prompt: str,
        direction: str = "image_to_audio",
        seed: int = 42,
        image_model: str = "stabilityai/stable-diffusion-3.5-large",
        image_steps: int = 25,
        image_cfg: float = 4.5,
        audio_duration: float = 10.0,
        audio_steps: int = 100,
        audio_cfg: float = 7.0,
    ) -> Optional[bytes]:
        """
        Strategy C: Generate in one modality, decode with the other's VAE.

        image_to_audio: SD3.5 latents [1,16,128,128] → reshape [1,64,4096] → Oobleck decode
        audio_to_image: Stable Audio latents [1,64,T] → reshape [1,16,128,128] → SD3 VAE decode

        This forces a VAE to interpret latent structure from an alien modality.
        Results are intentionally chaotic/glitchy — corruption as artistic medium.

        Returns:
            Output bytes (audio WAV or image PNG) or None
        """
        import torch

        try:
            logger.info(
                f"[CROSS-AESTHETIC] Strategy C: direction={direction}, "
                f"seed={seed}, prompt='{prompt[:60]}...'"
            )

            if direction == "image_to_audio":
                return await self._cross_decode_image_to_audio(
                    prompt, seed, image_model, image_steps, image_cfg, audio_duration
                )
            elif direction == "audio_to_image":
                return await self._cross_decode_audio_to_image(
                    prompt, seed, audio_duration, audio_steps, audio_cfg
                )
            else:
                logger.error(f"[CROSS-AESTHETIC] Unknown direction: {direction}")
                return None

        except Exception as e:
            logger.error(f"[CROSS-AESTHETIC] Strategy C error: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _cross_decode_image_to_audio(
        self, prompt, seed, image_model, image_steps, image_cfg, audio_duration
    ) -> Optional[bytes]:
        """Image latents → Stable Audio VAE → audio.

        The Oobleck VAE expects temporally correlated latents (nearby frames similar).
        After reshaping [1,16,128,128] → [1,64,4096], the 2D spatial correlations from
        the image map partially to temporal correlations within each audio channel.
        We apply 1D temporal smoothing so the VAE has structure to decode,
        not just noise.
        """
        import torch
        import torch.nn.functional as F
        import numpy as np

        # Step 1: Generate image latents
        from services.diffusers_backend import get_diffusers_backend
        diffusers = get_diffusers_backend()

        if not await diffusers.load_model(image_model):
            logger.error("[CROSS-AESTHETIC] Failed to load image model")
            return None

        pipe = diffusers._pipelines[image_model]
        diffusers._model_in_use[image_model] = diffusers._model_in_use.get(image_model, 0) + 1

        try:
            if seed == -1:
                import random
                seed = random.randint(0, 2**32 - 1)

            generator = torch.Generator(device=diffusers.device).manual_seed(seed)

            def _gen_latents():
                with torch.no_grad():
                    gen_kwargs = {
                        "prompt": prompt,
                        "width": 1024,
                        "height": 1024,
                        "num_inference_steps": image_steps,
                        "guidance_scale": image_cfg,
                        "generator": generator,
                        "output_type": "latent",
                    }
                    if hasattr(pipe, 'tokenizer_3'):
                        gen_kwargs["max_sequence_length"] = 512
                    result = pipe(**gen_kwargs)
                    return result.images  # latent tensor [1, 16, 128, 128]

            image_latents = await asyncio.to_thread(_gen_latents)
            logger.info(f"[CROSS-AESTHETIC] Image latents: {list(image_latents.shape)}")
        finally:
            diffusers._model_in_use[image_model] -= 1

        # Step 2: Reshape image latents to audio latent shape
        # SD3.5: [1, 16, 128, 128] = 262,144 values
        # Stable Audio: [1, 64, 4096] = 262,144 values (exact match!)
        flat = image_latents.reshape(1, -1)
        total_values = flat.shape[1]
        audio_channels = 64
        audio_frames = total_values // audio_channels
        audio_latents = flat[:, :audio_channels * audio_frames].reshape(1, audio_channels, audio_frames)

        logger.info(f"[CROSS-AESTHETIC] Reshaped to audio latents: {list(audio_latents.shape)}")

        # Step 3: Per-channel normalization + temporal smoothing
        # Per-channel preserves inter-channel relationships (frequency bands)
        for c in range(audio_latents.shape[1]):
            ch = audio_latents[:, c, :]
            audio_latents[:, c, :] = (ch - ch.mean()) / (ch.std() + 1e-8)

        # 1D temporal smoothing: Oobleck VAE expects nearby frames to correlate
        # kernel_size=15 creates ~3.5ms correlation windows at 4096 frames
        kernel_size = 15
        pad = kernel_size // 2
        audio_latents = F.avg_pool1d(
            F.pad(audio_latents, (pad, pad), mode='reflect'),
            kernel_size=kernel_size, stride=1
        )

        # Step 4: Decode with Stable Audio's VAE
        from services.stable_audio_backend import get_stable_audio_backend
        stable_audio = get_stable_audio_backend()

        if not stable_audio._is_loaded:
            if not await stable_audio._load_pipeline():
                return None

        vae = stable_audio.get_vae()
        if vae is None:
            logger.error("[CROSS-AESTHETIC] Stable Audio VAE not available")
            return None

        audio_latents = audio_latents.to(device="cuda", dtype=vae.dtype)

        def _decode_audio():
            with torch.no_grad():
                decoded = vae.decode(audio_latents).sample
                return decoded  # [1, 2, audio_samples]

        audio_waveform = await asyncio.to_thread(_decode_audio)
        logger.info(f"[CROSS-AESTHETIC] Cross-decoded audio: {list(audio_waveform.shape)}")

        # Step 5: Crop to desired duration and encode
        sample_rate = stable_audio.sample_rate
        max_samples = int(audio_duration * sample_rate)
        audio_cropped = audio_waveform[:, :, :max_samples]

        # Convert to numpy for encoding
        audio_np = audio_cropped.squeeze(0).cpu().float().numpy().T  # [samples, channels]

        # Clamp to valid range
        audio_np = np.clip(audio_np, -1.0, 1.0)

        return stable_audio._encode_wav(audio_np)

    async def _cross_decode_audio_to_image(
        self, prompt, seed, audio_duration, audio_steps, audio_cfg
    ) -> Optional[bytes]:
        """Audio latents → SD3.5 VAE → image.

        The SD3.5 VAE expects spatially correlated latents (neighboring pixels similar).
        Audio latents [1,64,T] have temporal correlations (within channels) but when
        reshaped to [1,16,128,128], the temporal axis maps to horizontal rows only.
        We apply 2D Gaussian blur to introduce spatial correlation in both dimensions
        so the VAE decodes structured patterns instead of noise.
        """
        import torch
        import torch.nn.functional as F
        import io

        # Step 1: Generate audio latents
        from services.stable_audio_backend import get_stable_audio_backend
        stable_audio = get_stable_audio_backend()

        if not stable_audio._is_loaded:
            if not await stable_audio._load_pipeline():
                return None

        stable_audio._in_use += 1
        stable_audio._last_used = time.time()

        try:
            if seed == -1:
                import random
                seed = random.randint(0, 2**32 - 1)

            generator = torch.Generator(device="cuda").manual_seed(seed)

            def _gen_audio_latents():
                with torch.no_grad():
                    result = stable_audio._pipeline(
                        prompt=prompt,
                        audio_end_in_s=audio_duration,
                        num_inference_steps=audio_steps,
                        guidance_scale=audio_cfg,
                        generator=generator,
                        output_type="latent",
                    )
                    return result.audios  # latent tensor [1, 64, T]

            audio_latents = await asyncio.to_thread(_gen_audio_latents)
            logger.info(f"[CROSS-AESTHETIC] Audio latents: {list(audio_latents.shape)}")
        finally:
            stable_audio._in_use -= 1

        # Step 2: Reshape to image latent shape [1, 16, 128, 128]
        target_values = 16 * 128 * 128  # 262,144
        flat = audio_latents.reshape(1, -1)

        if flat.shape[1] < target_values:
            padding = torch.zeros(1, target_values - flat.shape[1], device=flat.device, dtype=flat.dtype)
            flat = torch.cat([flat, padding], dim=1)
        elif flat.shape[1] > target_values:
            flat = flat[:, :target_values]

        image_latents = flat.reshape(1, 16, 128, 128)

        # Step 3: Per-channel normalization + 2D spatial smoothing
        # Per-channel preserves cross-channel relationships (latent feature maps)
        for c in range(image_latents.shape[1]):
            ch = image_latents[:, c, :, :]
            image_latents[:, c, :, :] = (ch - ch.mean()) / (ch.std() + 1e-8)

        # 2D Gaussian blur: SD3.5 VAE expects spatial correlation between neighbors
        # sigma=2.0 creates ~6px correlation radius in latent space (= ~48px in pixel space)
        kernel_size = 9
        sigma = 2.0
        # Build 2D Gaussian kernel
        x = torch.arange(kernel_size, device=image_latents.device, dtype=image_latents.dtype) - kernel_size // 2
        gauss_1d = torch.exp(-0.5 * (x / sigma) ** 2)
        gauss_2d = gauss_1d[:, None] * gauss_1d[None, :]
        gauss_2d = gauss_2d / gauss_2d.sum()
        # Apply per-channel: [1, C, H, W] → grouped conv
        gauss_kernel = gauss_2d.expand(16, 1, kernel_size, kernel_size)
        pad = kernel_size // 2
        image_latents = F.conv2d(
            F.pad(image_latents, (pad, pad, pad, pad), mode='reflect'),
            gauss_kernel, groups=16
        )

        # Apply SD3.5 VAE denormalization
        # SD3.5 VAE: scaling_factor=1.5305, shift_factor=0.0609
        image_latents = image_latents / 1.5305 + 0.0609

        logger.info(f"[CROSS-AESTHETIC] Reshaped to image latents: {list(image_latents.shape)}")

        # Step 4: Decode with SD3.5 VAE
        from services.diffusers_backend import get_diffusers_backend
        diffusers = get_diffusers_backend()

        image_model = "stabilityai/stable-diffusion-3.5-large"
        if not await diffusers.load_model(image_model):
            return None

        pipe = diffusers._pipelines[image_model]
        image_latents = image_latents.to(device="cuda", dtype=pipe.vae.dtype)

        def _decode_image():
            with torch.no_grad():
                image = pipe.vae.decode(image_latents, return_dict=False)[0]
                image = pipe.image_processor.postprocess(image, output_type="pil")[0]
                return image

        image = await asyncio.to_thread(_decode_image)

        # Convert to PNG bytes
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()

        logger.info(f"[CROSS-AESTHETIC] Cross-decoded image: {len(image_bytes)} bytes")
        return image_bytes


# =============================================================================
# Singleton
# =============================================================================

_backend: Optional[CrossAestheticGenerator] = None


def get_cross_aesthetic_backend() -> CrossAestheticGenerator:
    global _backend
    if _backend is None:
        _backend = CrossAestheticGenerator()
    return _backend


def reset_cross_aesthetic_backend():
    global _backend
    _backend = None
