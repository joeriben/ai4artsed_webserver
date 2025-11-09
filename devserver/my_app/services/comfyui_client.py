"""
ComfyUI API Client
Sendet generierte Workflows an ComfyUI und überwacht die Bildgenerierung
"""
import aiohttp
import asyncio
import logging
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import uuid

logger = logging.getLogger(__name__)

class ComfyUIClient:
    """Client für ComfyUI API-Kommunikation"""
    
    def __init__(self, base_url: str = None):
        """
        Initialize ComfyUI client with auto-discovery
        
        Args:
            base_url: ComfyUI server URL (default: auto-discover)
        """
        self.base_url = base_url or self._discover_comfyui_port()
        self.client_id = str(uuid.uuid4())
        logger.info(f"ComfyUI client initialized for: {self.base_url}")
    
    @staticmethod
    def _discover_comfyui_port() -> str:
        """
        Auto-discover ComfyUI port by checking common ports
        
        Returns:
            Base URL of discovered ComfyUI instance or default
        """
        import socket
        
        # Common ComfyUI ports to check
        ports_to_check = [
            (8188, "ComfyUI standalone"),
            (7821, "SwarmUI integrated ComfyUI"),
            (8189, "ComfyUI alternative"),
            (7860, "SwarmUI main"),
        ]
        
        for port, description in ports_to_check:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            try:
                result = sock.connect_ex(('127.0.0.1', port))
                sock.close()
                
                if result == 0:
                    # Port is open, verify it's actually ComfyUI
                    url = f"http://127.0.0.1:{port}"
                    try:
                        import requests
                        response = requests.get(f"{url}/system_stats", timeout=2)
                        if response.status_code == 200:
                            logger.info(f"✅ Discovered ComfyUI on port {port} ({description})")
                            return url
                    except:
                        pass
            except:
                pass
        
        # Default fallback
        logger.warning("⚠️ No ComfyUI instance found, using default port 8188")
        return "http://127.0.0.1:8188"
        
    async def submit_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """
        Submit workflow to ComfyUI
        
        Args:
            workflow: ComfyUI workflow JSON
            
        Returns:
            prompt_id if successful, None otherwise
        """
        try:
            # ComfyUI /prompt endpoint erwartet {"prompt": workflow, "client_id": ...}
            payload = {
                "prompt": workflow,
                "client_id": self.client_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/prompt",
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        prompt_id = result.get("prompt_id")
                        logger.info(f"Workflow submitted successfully: {prompt_id}")
                        return prompt_id
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to submit workflow: {response.status} - {error_text}")
                        return None
                        
        except aiohttp.ClientError as e:
            logger.error(f"Connection error submitting workflow: {e}")
            return None
        except Exception as e:
            logger.error(f"Error submitting workflow: {e}")
            return None
    
    async def get_queue_status(self) -> Optional[Dict[str, Any]]:
        """
        Get current queue status from ComfyUI
        
        Returns:
            Queue status dict or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/queue") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get queue status: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting queue status: {e}")
            return None
    
    async def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get generation history for a specific prompt_id
        
        Args:
            prompt_id: The prompt ID to check
            
        Returns:
            History dict or None
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/history/{prompt_id}") as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to get history: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting history: {e}")
            return None
    
    async def wait_for_completion(
        self, 
        prompt_id: str, 
        timeout: int = 300,
        poll_interval: float = 2.0
    ) -> Optional[Dict[str, Any]]:
        """
        Wait for workflow completion
        
        Args:
            prompt_id: The prompt ID to monitor
            timeout: Maximum wait time in seconds
            poll_interval: How often to check status
            
        Returns:
            Final history dict or None if timeout/error
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                logger.error(f"Timeout waiting for prompt {prompt_id}")
                return None
            
            # Check history
            history = await self.get_history(prompt_id)
            if history and prompt_id in history:
                # Prompt completed
                logger.info(f"Prompt {prompt_id} completed")
                return history[prompt_id]
            
            # Check if still in queue
            queue = await self.get_queue_status()
            if queue:
                # Check if prompt_id is in running or pending
                queue_running = queue.get("queue_running", [])
                queue_pending = queue.get("queue_pending", [])
                
                # Flatten and check
                all_ids = []
                for item in queue_running + queue_pending:
                    if isinstance(item, list) and len(item) >= 2:
                        all_ids.append(item[1])  # prompt_id is at index 1
                
                if prompt_id not in all_ids:
                    # Not in queue anymore, check history one more time
                    history = await self.get_history(prompt_id)
                    if history and prompt_id in history:
                        return history[prompt_id]
                    else:
                        logger.error(f"Prompt {prompt_id} disappeared from queue without completion")
                        return None
            
            await asyncio.sleep(poll_interval)
    
    async def get_image(self, filename: str, subfolder: str = "", folder_type: str = "output") -> Optional[bytes]:
        """
        Download generated image from ComfyUI
        
        Args:
            filename: Image filename
            subfolder: Subfolder in output directory
            folder_type: Folder type (usually "output")
            
        Returns:
            Image bytes or None
        """
        try:
            params = {
                "filename": filename,
                "subfolder": subfolder,
                "type": folder_type
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/view",
                    params=params
                ) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        logger.error(f"Failed to get image: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error getting image: {e}")
            return None
    
    async def get_generated_images(self, history_entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract generated images from history entry
        
        Args:
            history_entry: History dict for a completed prompt
            
        Returns:
            List of dicts with image info
        """
        images = []
        
        try:
            outputs = history_entry.get("outputs", {})
            for node_id, node_output in outputs.items():
                if "images" in node_output:
                    for img in node_output["images"]:
                        images.append({
                            "filename": img.get("filename"),
                            "subfolder": img.get("subfolder", ""),
                            "type": img.get("type", "output"),
                            "node_id": node_id
                        })
        except Exception as e:
            logger.error(f"Error extracting images from history: {e}")
        
        return images
    
    async def health_check(self) -> bool:
        """
        Check if ComfyUI server is accessible
        
        Returns:
            True if server is reachable, False otherwise
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/system_stats",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"ComfyUI health check failed: {e}")
            return False

# Singleton instance
_client = None

def get_comfyui_client(base_url: str = None) -> ComfyUIClient:
    """
    Get ComfyUI client singleton with auto-discovery
    
    Args:
        base_url: Optional explicit URL, otherwise auto-discover
    """
    global _client
    if _client is None:
        _client = ComfyUIClient(base_url)
    return _client
