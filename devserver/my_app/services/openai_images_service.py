"""
Service for OpenAI Images API (GPT-Image-1)
Direct API integration bypassing ComfyUI
"""
import logging
import requests
import os
from typing import Dict, Optional, Any
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)


class OpenAIImagesService:
    """Service class for OpenAI Images API interactions"""

    def __init__(self):
        # Try to load API key and org ID from multiple sources
        self.api_key, self.org_id = self._load_credentials()
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found in environment or api_keys.json")
        if self.org_id:
            logger.info(f"Using OpenAI Organization ID: {self.org_id}")
        self.base_url = "https://api.openai.com/v1"
        self.timeout = 120  # GPT-Image-1 can take longer than DALL-E

    def _load_credentials(self) -> tuple:
        """Load API key and organization ID from environment or JSON config

        Returns:
            Tuple of (api_key, org_id) where org_id may be None
        """
        import json
        from pathlib import Path

        api_key = None
        org_id = None

        # 1. Try environment variables first
        api_key = os.environ.get("OPENAI_API_KEY")
        org_id = os.environ.get("OPENAI_ORG_ID")

        # 2. Try JSON config file (overrides environment if present)
        try:
            devserver_root = Path(__file__).parent.parent.parent
            json_config_path = devserver_root / 'api_keys.json'
            if json_config_path.exists():
                with open(json_config_path, 'r', encoding='utf-8') as f:
                    api_keys_config = json.load(f)

                # Load API key
                if 'openai' in api_keys_config:
                    api_key = api_keys_config['openai']

                # Load organization ID
                if 'openai_org_id' in api_keys_config:
                    org_id = api_keys_config['openai_org_id']

        except Exception as e:
            logger.warning(f"Could not read api_keys.json: {e}")

        return api_key, org_id

    def generate_image(
        self,
        prompt: str,
        model: str = "gpt-image-1",
        quality: str = "high",
        size: str = "1024x1024",
        background: str = "opaque",
        n: int = 1,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate image using OpenAI Images API

        Args:
            prompt: Text prompt for image generation
            model: Model to use (gpt-image-1, dall-e-3, dall-e-2)
            quality: Image quality (low, medium, high for gpt-image-1; standard, hd for dall-e-3)
            size: Image dimensions
            background: opaque or transparent (gpt-image-1 only)
            n: Number of images to generate
            seed: Random seed (optional)

        Returns:
            Dictionary with:
            - success: Boolean
            - image_urls: List of generated image URLs
            - error: Error message if failed
        """
        if not self.api_key:
            return {"success": False, "error": "OPENAI_API_KEY not configured"}

        logger.info(f"Generating image with {model}: {prompt[:100]}...")

        # Build request payload
        payload = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
        }

        # Add model-specific parameters
        if model == "gpt-image-1":
            payload["quality"] = quality
            payload["background"] = background
            # Note: gpt-image-1 does NOT support seed parameter
        elif model == "dall-e-3":
            payload["quality"] = "hd" if quality == "high" else "standard"
            # DALL-E 3 doesn't support n > 1
            payload["n"] = 1
        elif model == "dall-e-2":
            # DALL-E 2 doesn't support quality parameter
            pass

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Add organization ID if available
        if self.org_id:
            headers["OpenAI-Organization"] = self.org_id

        try:
            response = requests.post(
                f"{self.base_url}/images/generations",
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()

            # Extract image URLs
            image_urls = [img["url"] for img in result.get("data", [])]

            if not image_urls:
                return {"success": False, "error": "No images returned from API"}

            logger.info(f"Successfully generated {len(image_urls)} image(s)")
            return {
                "success": True,
                "image_urls": image_urls,
                "revised_prompt": result["data"][0].get("revised_prompt") if result.get("data") else None
            }

        except requests.exceptions.RequestException as e:
            error_msg = f"OpenAI API request failed: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"OpenAI API error: {error_detail.get('error', {}).get('message', str(e))}"
                except:
                    pass
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def download_image(self, url: str, save_path: Path) -> bool:
        """
        Download image from URL to local file

        Args:
            url: Image URL from OpenAI API
            save_path: Local path to save image

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading image from {url[:100]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            with open(save_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Image saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to download image: {e}")
            return False

    def generate_and_save(
        self,
        prompt: str,
        output_dir: Path,
        model: str = "gpt-image-1",
        quality: str = "high",
        size: str = "1024x1024",
        background: str = "opaque",
        n: int = 1,
        seed: Optional[int] = None,
        filename_prefix: str = "openai_image"
    ) -> Dict[str, Any]:
        """
        Generate image and save to local storage

        Args:
            prompt: Text prompt for image generation
            output_dir: Directory to save images
            model: Model to use
            quality: Image quality
            size: Image dimensions
            background: Background setting
            n: Number of images
            seed: Random seed
            filename_prefix: Prefix for saved filenames

        Returns:
            Dictionary with:
            - success: Boolean
            - image_paths: List of local file paths
            - error: Error message if failed
        """
        # Generate images
        result = self.generate_image(
            prompt=prompt,
            model=model,
            quality=quality,
            size=size,
            background=background,
            n=n,
            seed=seed
        )

        if not result["success"]:
            return result

        # Download and save images
        image_paths = []
        for i, url in enumerate(result["image_urls"]):
            # Generate unique filename
            filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}_{i:02d}.png"
            save_path = output_dir / filename

            if self.download_image(url, save_path):
                image_paths.append(str(save_path))
            else:
                logger.warning(f"Failed to download image {i+1}/{len(result['image_urls'])}")

        if not image_paths:
            return {"success": False, "error": "Failed to download any images"}

        return {
            "success": True,
            "image_paths": image_paths,
            "revised_prompt": result.get("revised_prompt")
        }


# Create singleton instance
openai_images_service = OpenAIImagesService()
