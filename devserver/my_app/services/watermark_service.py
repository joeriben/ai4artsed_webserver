"""
Invisible Watermark Service for AI4ArtsEd

Embeds invisible watermarks into generated images using DWT-DCT method.
The watermark survives JPEG compression, noise, and brightness changes.

Usage:
    service = WatermarkService("AI4ArtsEd")
    watermarked_bytes = service.embed_watermark(image_bytes)
    extracted = service.extract_watermark(watermarked_bytes)
"""

import logging
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class WatermarkService:
    """Service for embedding and extracting invisible watermarks from images."""

    def __init__(self, watermark_text: str = "AI4ArtsEd"):
        """
        Initialize the watermark service.

        Args:
            watermark_text: Text to embed as watermark. Max ~32 bytes recommended
                           for reliable extraction.
        """
        # Lazy import to avoid loading heavy dependencies at module import time
        from imwatermark import WatermarkEncoder

        self.watermark_text = watermark_text
        self.watermark_bytes = watermark_text.encode('utf-8')
        self.watermark_length = len(self.watermark_bytes) * 8  # bits

        self.encoder = WatermarkEncoder()
        self.encoder.set_watermark('bytes', self.watermark_bytes)

        logger.info(f"WatermarkService initialized with text: '{watermark_text}' ({len(self.watermark_bytes)} bytes)")

    def embed_watermark(self, image_bytes: bytes, method: str = 'dwtDct') -> bytes:
        """
        Embed invisible watermark into image.

        Args:
            image_bytes: Raw image bytes (PNG, JPEG, etc.)
            method: Embedding method. Options:
                   - 'dwtDct': Fastest (300-350ms for 1080p), good robustness
                   - 'dwtDctSvd': Slower (1.5-2s), better robustness
                   - 'rivaGan': Slowest (~5s), best crop resistance

        Returns:
            PNG-encoded image bytes with embedded watermark.

        Raises:
            ValueError: If image cannot be decoded.
        """
        # Decode image bytes to numpy array (BGR format for OpenCV)
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if bgr is None:
            raise ValueError("Failed to decode image bytes")

        # Embed watermark
        bgr_encoded = self.encoder.encode(bgr, method)

        # Encode back to PNG bytes (lossless to preserve watermark)
        success, encoded = cv2.imencode('.png', bgr_encoded)
        if not success:
            raise ValueError("Failed to encode watermarked image")

        logger.debug(f"Watermark embedded using {method} method")
        return encoded.tobytes()

    def extract_watermark(self, image_bytes: bytes, method: str = 'dwtDct') -> Optional[str]:
        """
        Extract watermark from image.

        Args:
            image_bytes: Raw image bytes with potential watermark.
            method: Must match the method used during embedding.

        Returns:
            Extracted watermark text, or None if extraction fails.
        """
        # Lazy import
        from imwatermark import WatermarkDecoder

        # Decode image bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if bgr is None:
            logger.warning("Failed to decode image bytes for watermark extraction")
            return None

        # Extract watermark
        decoder = WatermarkDecoder('bytes', self.watermark_length)
        watermark_bytes = decoder.decode(bgr, method)

        if watermark_bytes is None:
            logger.debug("No watermark found in image")
            return None

        try:
            extracted = watermark_bytes.decode('utf-8')
            logger.debug(f"Watermark extracted: '{extracted}'")
            return extracted
        except UnicodeDecodeError:
            logger.warning("Watermark extraction failed: invalid UTF-8")
            return None

    def verify_watermark(self, image_bytes: bytes, method: str = 'dwtDct') -> bool:
        """
        Verify that image contains the expected watermark.

        Args:
            image_bytes: Raw image bytes to verify.
            method: Must match the method used during embedding.

        Returns:
            True if watermark matches expected text, False otherwise.
        """
        extracted = self.extract_watermark(image_bytes, method)
        matches = extracted == self.watermark_text

        if matches:
            logger.debug("Watermark verification successful")
        else:
            logger.debug(f"Watermark verification failed: expected '{self.watermark_text}', got '{extracted}'")

        return matches
