"""
C2PA Content Credentials Service for AI4ArtsEd

Signs generated images with C2PA (Coalition for Content Provenance and Authenticity)
manifests, providing cryptographically verifiable provenance information.

The signed images can be verified at: https://verify.contentcredentials.org/

Usage:
    service = C2PAService(cert_path, key_path)
    service.sign_image(input_path, output_path)
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class C2PAService:
    """Service for signing images with C2PA Content Credentials."""

    def __init__(
        self,
        cert_path: Path,
        key_path: Path,
        generator_name: str = "AI4ArtsEd DevServer",
        tsa_url: Optional[str] = "http://timestamp.digicert.com"
    ):
        """
        Initialize the C2PA signing service.

        Args:
            cert_path: Path to PEM certificate file.
            key_path: Path to PEM private key file.
            generator_name: Name to embed as claim generator.
            tsa_url: Timestamp Authority URL. Set to None to disable timestamping.
        """
        self.cert_path = Path(cert_path)
        self.key_path = Path(key_path)
        self.generator_name = generator_name
        self.tsa_url = tsa_url

        # Validate paths exist
        if not self.cert_path.exists():
            raise FileNotFoundError(f"Certificate not found: {cert_path}")
        if not self.key_path.exists():
            raise FileNotFoundError(f"Private key not found: {key_path}")

        # Load certificate and key
        self._certs = self.cert_path.read_bytes()
        self._key = self.key_path.read_bytes()

        logger.info(f"C2PAService initialized with generator: '{generator_name}'")

    def _create_signer_callback(self):
        """Create the signing callback function."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.backends import default_backend

        key_bytes = self._key

        def callback_signer(data: bytes) -> bytes:
            private_key = serialization.load_pem_private_key(
                key_bytes, password=None, backend=default_backend()
            )
            signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))
            return signature

        return callback_signer

    def _create_manifest(
        self,
        title: Optional[str] = None,
        media_format: str = "image/png"
    ) -> dict:
        """
        Create a C2PA manifest definition.

        Args:
            title: Optional title for the asset.
            media_format: MIME type of the media.

        Returns:
            Manifest dictionary ready for Builder.
        """
        manifest = {
            "claim_generator": self.generator_name,
            "claim_generator_info": [
                {
                    "name": "AI4ArtsEd",
                    "version": "1.0.0"
                }
            ],
            "format": media_format,
            "assertions": [
                # Action assertion: this content was AI-generated
                {
                    "label": "c2pa.actions",
                    "data": {
                        "actions": [
                            {
                                "action": "c2pa.created",
                                "digitalSourceType": "http://cv.iptc.org/newscodes/digitalsourcetype/trainedAlgorithmicMedia",
                                "softwareAgent": self.generator_name
                            }
                        ]
                    }
                },
                # Training/mining assertion: do not use for AI training
                {
                    "label": "c2pa.training-mining",
                    "data": {
                        "entries": {
                            "c2pa.ai_generative_training": {"use": "notAllowed"},
                            "c2pa.ai_inference": {"use": "notAllowed"},
                            "c2pa.ai_training": {"use": "notAllowed"},
                            "c2pa.data_mining": {"use": "notAllowed"}
                        }
                    }
                }
            ]
        }

        if title:
            manifest["title"] = title

        return manifest

    def sign_image(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        title: Optional[str] = None
    ) -> Path:
        """
        Sign an image with C2PA Content Credentials.

        Args:
            input_path: Path to the image to sign.
            output_path: Path for the signed output. Defaults to overwriting input.
            title: Optional title for the manifest.

        Returns:
            Path to the signed image.

        Raises:
            FileNotFoundError: If input file doesn't exist.
            RuntimeError: If signing fails.
        """
        import c2pa

        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Default to overwriting input file
        if output_path is None:
            output_path = input_path
        else:
            output_path = Path(output_path)

        # Determine format from extension
        suffix = input_path.suffix.lower()
        format_map = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        media_format = format_map.get(suffix, 'image/png')

        # Create manifest
        manifest = self._create_manifest(title=title, media_format=media_format)

        logger.debug(f"Signing {input_path} with C2PA manifest")

        try:
            # Create signer with callback
            signer_callback = self._create_signer_callback()

            # Use temporary file if overwriting in-place
            if output_path == input_path:
                import tempfile
                import shutil

                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                    tmp_path = Path(tmp.name)

                try:
                    with c2pa.Signer.from_callback(
                        callback=signer_callback,
                        alg=c2pa.C2paSigningAlg.ES256,
                        certs=self._certs.decode('utf-8'),
                        tsa_url=self.tsa_url
                    ) as signer:
                        with c2pa.Builder(manifest) as builder:
                            builder.sign_file(
                                source_path=str(input_path),
                                dest_path=str(tmp_path),
                                signer=signer
                            )

                    # Replace original with signed version
                    shutil.move(str(tmp_path), str(output_path))

                except Exception:
                    # Clean up temp file on error
                    if tmp_path.exists():
                        tmp_path.unlink()
                    raise
            else:
                with c2pa.Signer.from_callback(
                    callback=signer_callback,
                    alg=c2pa.C2paSigningAlg.ES256,
                    certs=self._certs.decode('utf-8'),
                    tsa_url=self.tsa_url
                ) as signer:
                    with c2pa.Builder(manifest) as builder:
                        builder.sign_file(
                            source_path=str(input_path),
                            dest_path=str(output_path),
                            signer=signer
                        )

            logger.info(f"C2PA manifest signed: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"C2PA signing failed: {e}")
            raise RuntimeError(f"Failed to sign image with C2PA: {e}") from e

    def read_manifest(self, image_path: Path) -> Optional[dict]:
        """
        Read and validate C2PA manifest from an image.

        Args:
            image_path: Path to the image to read.

        Returns:
            Manifest data as dictionary, or None if no manifest found.
        """
        import c2pa

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            with open(image_path, 'rb') as f:
                file_bytes = f.read()

            suffix = image_path.suffix.lower()
            format_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.webp': 'image/webp'
            }
            media_format = format_map.get(suffix, 'image/png')

            with c2pa.Reader(media_format, file_bytes) as reader:
                manifest_json = reader.json()
                return json.loads(manifest_json) if manifest_json else None

        except Exception as e:
            logger.debug(f"No C2PA manifest found in {image_path}: {e}")
            return None

    def verify_image(self, image_path: Path) -> bool:
        """
        Verify that an image has a valid C2PA manifest.

        Args:
            image_path: Path to the image to verify.

        Returns:
            True if manifest exists and is valid, False otherwise.
        """
        manifest = self.read_manifest(image_path)
        return manifest is not None
