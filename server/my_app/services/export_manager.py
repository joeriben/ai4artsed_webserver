"""
Service for managing session exports
"""
import logging
import json
import zipfile
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

from config import (
    EXPORTS_DIR,
    ENABLE_AUTO_EXPORT
)
from my_app.utils.helpers import (
    generate_timestamp,
    calculate_node_execution_order
)
from my_app.services.comfyui_service import comfyui_service

logger = logging.getLogger(__name__)


class ExportManager:
    """Manager for session exports"""
    
    def __init__(self):
        self.exports_dir = EXPORTS_DIR
        self.exports_dir.mkdir(exist_ok=True)
    
    def generate_export_html(self, session_data: Dict[str, Any], media_files: List[str]) -> str:
        """Generate HTML file for a session export"""
        user_id = session_data.get('user_id', 'DOE_J')
        timestamp = session_data.get('timestamp', generate_timestamp())
        session_id = session_data.get('session_id', 'unknown')
        workflow_name = session_data.get('workflow_name', 'Unknown Workflow')
        prompt = session_data.get('prompt', '')
        outputs = session_data.get('outputs', [])
        
        html_content = f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI4ArtsEd Export - {user_id}_{timestamp}_{session_id}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
               background-color: #f0f2f5; color: #1c1e21; padding: 20px; line-height: 1.6; }}
        .container {{ max-width: 800px; margin: 0 auto; background-color: #ffffff; 
                     border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); padding: 24px; }}
        h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 12px; }}
        .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .metadata-item {{ margin-bottom: 8px; }}
        .metadata-label {{ font-weight: bold; color: #495057; }}
        .prompt-section {{ background-color: #e7f3ff; padding: 15px; border-radius: 6px; margin-bottom: 20px; }}
        .output-item {{ margin-bottom: 30px; padding: 15px; border: 1px solid #ddd; 
                       border-radius: 6px; background-color: #f9f9f9; }}
        .output-header {{ font-weight: bold; color: #555; margin-bottom: 10px; font-size: 1.1em; }}
        .output-content img {{ max-width: 100%; height: auto; border-radius: 8px; 
                              box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .output-content audio {{ width: 100%; margin-top: 10px; }}
        .text-content {{ white-space: pre-wrap; word-wrap: break-word; font-family: monospace; 
                        background: white; padding: 12px; border-radius: 4px; border: 1px solid #ddd; }}
        .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; 
                  text-align: center; color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>AI4ArtsEd Workflow Export</h1>
        
        <div class="metadata">
            <div class="metadata-item"><span class="metadata-label">User ID:</span> {user_id}</div>
            <div class="metadata-item"><span class="metadata-label">Session ID:</span> {session_id}</div>
            <div class="metadata-item"><span class="metadata-label">Timestamp:</span> {timestamp}</div>
            <div class="metadata-item"><span class="metadata-label">Workflow:</span> {workflow_name}</div>
            <div class="metadata-item"><span class="metadata-label">Export Date:</span> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        </div>
        
        <div class="prompt-section">
            <h3>Original Prompt</h3>
            <div class="text-content">{prompt}</div>
        </div>
        
        <h3>Workflow Outputs (in Processing Order)</h3>
"""
        
        for i, output in enumerate(outputs, 1):
            html_content += f"""
        <div class="output-item">
            <div class="output-header">{i}. {output['title']} ({output['type'].upper()})</div>
            <div class="output-content">
"""
            
            if output['type'] == 'image':
                filename = output.get('filename', f"image_{i:03d}.png")
                html_content += f'<img src="media/{filename}" alt="Generated Image {i}">'
            elif output['type'] == 'text':
                html_content += f'<div class="text-content">{output["content"]}</div>'
            elif output['type'] == 'audio':
                filename = output.get('filename', f"audio_{i:03d}.wav")
                html_content += f'<audio controls><source src="media/{filename}" type="audio/wav">Your browser does not support the audio element.</audio>'
            
            html_content += """
            </div>
        </div>
"""
        
        html_content += f"""
        <div class="footer">
            <p>Generated by AI4ArtsEd - Artificial Intelligence for Arts Education</p>
            <p>Export created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </div>
</body>
</html>"""
        
        return html_content
    
    def process_outputs(self, outputs: Dict[str, Any], workflow_def: Dict[str, Any], 
                       media_dir: Path) -> tuple:
        """
        Process workflow outputs and download media files
        
        Returns:
            Tuple of (processed_outputs, media_files)
        """
        processed_outputs = []
        media_files = []
        
        for node_id, output in outputs.items():
            node_title = workflow_def.get(node_id, {}).get("_meta", {}).get("title", f"Node {node_id}")
            execution_order = calculate_node_execution_order(node_id, workflow_def)
            
            if output.get("text"):
                processed_outputs.append({
                    "title": node_title,
                    "type": "text",
                    "content": "\n".join(output["text"]),
                    "execution_order": execution_order
                })
            
            if output.get("images"):
                for idx, img in enumerate(output["images"]):
                    filename = f"image_{len(media_files)+1:03d}.png"
                    img_url = f"view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                    
                    # Download image
                    if comfyui_service.download_media(img_url, media_dir / filename):
                        processed_outputs.append({
                            "title": node_title,
                            "type": "image",
                            "filename": filename,
                            "execution_order": execution_order
                        })
                        media_files.append(filename)
            
            if output.get("audio"):
                for idx, aud in enumerate(output["audio"]):
                    filename = f"audio_{len(media_files)+1:03d}.wav"
                    aud_url = f"view?filename={aud['filename']}&subfolder={aud['subfolder']}&type={aud['type']}"
                    
                    # Download audio
                    if comfyui_service.download_media(aud_url, media_dir / filename):
                        processed_outputs.append({
                            "title": node_title,
                            "type": "audio",
                            "filename": filename,
                            "execution_order": execution_order
                        })
                        media_files.append(filename)
        
        # Sort outputs by execution order
        processed_outputs.sort(key=lambda x: x["execution_order"])
        
        return processed_outputs, media_files
    
    def auto_export_session(self, prompt_id: str, workflow_name: str, prompt_text: str) -> bool:
        """
        Automatically export a session after successful completion
        
        Returns:
            True if export successful, False otherwise
        """
        if not ENABLE_AUTO_EXPORT:
            logger.info(f"Auto-export disabled for session {prompt_id}")
            return False
        
        try:
            logger.info(f"Starting auto-export for session {prompt_id}")
            
            # Get session data from ComfyUI
            result = comfyui_service.get_workflow_outputs(prompt_id)
            if not result:
                logger.warning(f"No outputs found for session {prompt_id}")
                return False
            
            outputs = result["outputs"]
            workflow_def = result["workflow_def"]
            
            # Generate session identifiers
            timestamp = generate_timestamp()
            session_id = prompt_id[:8]
            user_id = "DOE_J"  # Default user for auto-export
            
            # Create export directory structure
            session_dir_name = f"session_{user_id}_{timestamp}_{session_id}"
            session_dir = self.exports_dir / session_dir_name
            session_dir.mkdir(exist_ok=True)
            
            media_dir = session_dir / "media"
            media_dir.mkdir(exist_ok=True)
            
            # Process outputs and collect media
            processed_outputs, media_files = self.process_outputs(outputs, workflow_def, media_dir)
            
            # Create session data
            session_data = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "workflow_name": workflow_name,
                "prompt": prompt_text,
                "outputs": processed_outputs
            }
            
            # Generate HTML file
            html_filename = f"output_{user_id}_{timestamp}_{session_id}.html"
            html_content = self.generate_export_html(session_data, media_files)
            
            with open(session_dir / html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create metadata.json
            metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "workflow_name": workflow_name,
                "prompt": prompt_text,
                "export_date": datetime.now().isoformat(),
                "media_files": media_files,
                "output_count": len(processed_outputs)
            }
            
            with open(session_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(
                f"Auto-export completed for session {session_id}: "
                f"{session_dir_name} ({len(media_files)} media, {len(processed_outputs)} outputs)"
            )
            
            # Update the sessions overview
            self._update_sessions_js()
            
            return True
            
        except Exception as e:
            logger.error(f"Auto-export failed for session {prompt_id}: {e}")
            return False
    
    def export_session(self, prompt_id: str, user_id: str, workflow_name: str, 
                      prompt_text: str) -> Dict[str, Any]:
        """
        Manually export a session
        
        Returns:
            Export result dictionary
        """
        try:
            # Get session data from ComfyUI
            result = comfyui_service.get_workflow_outputs(prompt_id)
            if not result:
                return {"success": False, "error": "Session nicht in ComfyUI History gefunden."}
            
            outputs = result["outputs"]
            workflow_def = result["workflow_def"]
            
            # Generate session identifiers
            timestamp = generate_timestamp()
            session_id = prompt_id[:8]
            
            # Create export directory structure
            session_dir_name = f"session_{user_id}_{timestamp}_{session_id}"
            session_dir = self.exports_dir / session_dir_name
            session_dir.mkdir(exist_ok=True)
            
            media_dir = session_dir / "media"
            media_dir.mkdir(exist_ok=True)
            
            # Process outputs and collect media
            processed_outputs, media_files = self.process_outputs(outputs, workflow_def, media_dir)
            
            # Create session data
            session_data = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "workflow_name": workflow_name,
                "prompt": prompt_text,
                "outputs": processed_outputs
            }
            
            # Generate HTML file
            html_filename = f"output_{user_id}_{timestamp}_{session_id}.html"
            html_content = self.generate_export_html(session_data, media_files)
            
            with open(session_dir / html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Create metadata.json
            metadata = {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp": timestamp,
                "workflow_name": workflow_name,
                "prompt": prompt_text,
                "export_date": datetime.now().isoformat(),
                "media_files": media_files,
                "output_count": len(processed_outputs)
            }
            
            with open(session_dir / "metadata.json", 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Successfully exported session {session_id} to {session_dir_name}")
            
            # Update the sessions overview
            self._update_sessions_js()
            
            return {
                "success": True,
                "export_path": session_dir_name,
                "html_file": html_filename,
                "media_count": len(media_files),
                "output_count": len(processed_outputs)
            }
            
        except Exception as e:
            logger.error(f"Export failed: {e}")
            return {"success": False, "error": f"Export fehlgeschlagen: {str(e)}"}
    
    def create_download_zip(self, prompt_id: str, user_id: str, workflow_name: str, 
                           prompt_text: str) -> Optional[bytes]:
        """
        Create a ZIP file for download
        
        Returns:
            ZIP file bytes or None if failed
        """
        try:
            # Get session data from ComfyUI
            result = comfyui_service.get_workflow_outputs(prompt_id)
            if not result:
                return None
            
            outputs = result["outputs"]
            workflow_def = result["workflow_def"]
            
            # Generate session identifiers
            timestamp = generate_timestamp()
            session_id = prompt_id[:8]
            
            # Process outputs and collect media
            processed_outputs = []
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                media_counter = 1
                
                for node_id, output in outputs.items():
                    node_title = workflow_def.get(node_id, {}).get("_meta", {}).get("title", f"Node {node_id}")
                    execution_order = calculate_node_execution_order(node_id, workflow_def)
                    
                    if output.get("text"):
                        processed_outputs.append({
                            "title": node_title,
                            "type": "text",
                            "content": "\n".join(output["text"]),
                            "execution_order": execution_order
                        })
                    
                    if output.get("images"):
                        for idx, img in enumerate(output["images"]):
                            filename = f"image_{media_counter:03d}.png"
                            img_url = f"view?filename={img['filename']}&subfolder={img['subfolder']}&type={img['type']}"
                            
                            # Download and add to ZIP
                            try:
                                response = comfyui_service.proxy_request(img_url)
                                if response.status_code == 200:
                                    zip_file.writestr(f"media/{filename}", response.content)
                                    processed_outputs.append({
                                        "title": node_title,
                                        "type": "image",
                                        "filename": filename,
                                        "execution_order": execution_order
                                    })
                                    media_counter += 1
                            except Exception as e:
                                logger.error(f"Failed to add image to ZIP: {e}")
                    
                    if output.get("audio"):
                        for idx, aud in enumerate(output["audio"]):
                            filename = f"audio_{media_counter:03d}.wav"
                            aud_url = f"view?filename={aud['filename']}&subfolder={aud['subfolder']}&type={aud['type']}"
                            
                            # Download and add to ZIP
                            try:
                                response = comfyui_service.proxy_request(aud_url)
                                if response.status_code == 200:
                                    zip_file.writestr(f"media/{filename}", response.content)
                                    processed_outputs.append({
                                        "title": node_title,
                                        "type": "audio",
                                        "filename": filename,
                                        "execution_order": execution_order
                                    })
                                    media_counter += 1
                            except Exception as e:
                                logger.error(f"Failed to add audio to ZIP: {e}")
                
                # Sort outputs by execution order
                processed_outputs.sort(key=lambda x: x["execution_order"])
                
                # Create session data
                session_data = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "workflow_name": workflow_name,
                    "prompt": prompt_text,
                    "outputs": processed_outputs
                }
                
                # Generate HTML file and add to ZIP
                html_filename = f"output_{user_id}_{timestamp}_{session_id}.html"
                html_content = self.generate_export_html(session_data, [])
                zip_file.writestr(html_filename, html_content.encode('utf-8'))
                
                # Create metadata.json and add to ZIP
                metadata = {
                    "user_id": user_id,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "workflow_name": workflow_name,
                    "prompt": prompt_text,
                    "export_date": datetime.now().isoformat(),
                    "media_files": [out.get("filename") for out in processed_outputs if out.get("filename")],
                    "output_count": len(processed_outputs)
                }
                zip_file.writestr("metadata.json", json.dumps(metadata, indent=2, ensure_ascii=False).encode('utf-8'))
            
            zip_buffer.seek(0)
            logger.info(f"Successfully created ZIP download for session {session_id}")
            
            return zip_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to create download ZIP: {e}")
            return None


    def _update_sessions_js(self):
        """
        Scans the export directory and updates a sessions.js file
        for the local overview page.
        """
        try:
            sessions = []
            for item in self.exports_dir.iterdir():
                if item.is_dir() and item.name.startswith('session_'):
                    metadata_path = item / 'metadata.json'
                    if metadata_path.exists():
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        user_id = data.get('user_id', 'N/A')
                        session_id = data.get('session_id', 'N/A')
                        timestamp = data.get('timestamp', 'N/A')
                        html_file = f"output_{user_id}_{timestamp}_{session_id}.html"

                        sessions.append({
                            'user_id': user_id,
                            'session_id': session_id,
                            'timestamp': timestamp,
                            'workflow_name': data.get('workflow_name', 'N/A'),
                            'output_count': data.get('output_count', 0),
                            'media_count': len(data.get('media_files', [])),
                            'export_date': data.get('export_date'),
                            'folder_name': item.name,
                            'html_file': html_file
                        })
            
            # Write to sessions.js
            js_content = f"const allSessions = {json.dumps(sessions, indent=2, ensure_ascii=False)};"
            with open(self.exports_dir / "sessions.js", 'w', encoding='utf-8') as f:
                f.write(js_content)
            
            logger.info(f"Successfully updated sessions.js with {len(sessions)} sessions.")

        except Exception as e:
            logger.error(f"Failed to update sessions.js: {e}")

# Create a singleton instance
export_manager = ExportManager()
