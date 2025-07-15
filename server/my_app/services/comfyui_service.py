"""
Service for interacting with ComfyUI API
"""
import logging
import requests
import uuid
from typing import Dict, Optional, Any, List

from config import (
    COMFYUI_PORT,
    COMFYUI_TIMEOUT,
    POLLING_TIMEOUT,
    MEDIA_DOWNLOAD_TIMEOUT
)

logger = logging.getLogger(__name__)


class ComfyUIService:
    """Service class for ComfyUI API interactions"""
    
    def __init__(self):
        self.base_url = f"http://localhost:{COMFYUI_PORT}"
        self.timeout = COMFYUI_TIMEOUT
        
    def submit_workflow(self, workflow: Dict[str, Any]) -> Optional[str]:
        """
        Submit a workflow to ComfyUI for execution
        
        Args:
            workflow: Workflow definition dictionary
            
        Returns:
            prompt_id if successful, None otherwise
        """
        try:
            # Debug logging for kids safety
            for node_id, node_data in workflow.items():
                if node_data.get("class_type") == "CLIPTextEncode":
                    text = node_data.get("inputs", {}).get("text", "")
                    if isinstance(text, str) and len(text) > 100:
                        logger.info(f"[COMFYUI SUBMIT] Node {node_id} negative prompt being sent: {text[:150]}...")
            
            payload = {
                "prompt": workflow,
                "client_id": str(uuid.uuid4())
            }
            
            response = requests.post(
                f"{self.base_url}/prompt",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            prompt_id = data.get("prompt_id")
            
            if not prompt_id:
                logger.error("ComfyUI did not return a prompt_id")
                return None
                
            logger.info(f"Successfully submitted workflow to ComfyUI: {prompt_id}")
            return prompt_id
            
        except requests.exceptions.RequestException as e:
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_details = e.response.json()
                except:
                    error_details = e.response.text
            logger.error(f"ComfyUI request failed: {error_details}")
            return None
    
    def get_history(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution history for a specific prompt_id
        
        Args:
            prompt_id: The prompt ID to get history for
            
        Returns:
            History data or None if not found/failed
        """
        try:
            response = requests.get(
                f"{self.base_url}/history/{prompt_id}",
                timeout=POLLING_TIMEOUT
            )
            
            if response.status_code == 404:
                # Workflow not ready yet
                return None
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get history for {prompt_id}: {e}")
            return None
    
    def download_media(self, url: str, target_path: str) -> bool:
        """
        Download a media file from ComfyUI
        
        Args:
            url: Relative URL of the media file
            target_path: Local path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract the path after the first slash
            if url.startswith('/'):
                url = url[1:]
            
            full_url = f"{self.base_url}/{url}"
            response = requests.get(full_url, timeout=MEDIA_DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            with open(target_path, 'wb') as f:
                f.write(response.content)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to download media file {url}: {e}")
            return False
    
    def get_workflow_outputs(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get outputs for a completed workflow
        
        Args:
            prompt_id: The prompt ID to get outputs for
            
        Returns:
            Dictionary with outputs and workflow definition, or None
        """
        history = self.get_history(prompt_id)
        if not history or prompt_id not in history:
            return None
        
        session_data = history[prompt_id]
        outputs = session_data.get("outputs", {})
        
        # Extract workflow definition from prompt
        prompt_data = session_data.get("prompt", [None, None, {}])
        workflow_def = prompt_data[2] if len(prompt_data) > 2 else {}
        
        if outputs:
            return {
                "outputs": outputs,
                "workflow_def": workflow_def
            }
        
        return None
    
    def proxy_request(self, path: str, params: Optional[Dict] = None) -> requests.Response:
        """
        Proxy a request to ComfyUI
        
        Args:
            path: The path to proxy to
            params: Optional query parameters
            
        Returns:
            The response object
        """
        return requests.get(
            f"{self.base_url}/{path}",
            params=params,
            timeout=POLLING_TIMEOUT * 2
        )


# Create a singleton instance
comfyui_service = ComfyUIService()
