"""
Utility functions for injecting nodes into ComfyUI workflows.
Provides reusable functionality for workflow manipulation tasks.
"""
import logging
from typing import Dict, Any, List, Optional, Union

logger = logging.getLogger(__name__)


class NodeInjector:
    """Handler for injecting specific node types into workflows"""
    
    # Definierte Node-Typen und ihre Injection-Logik
    SUPPORTED_NODE_TYPES = {
        "StringConcatenate": {
            "required_inputs": ["string_a", "string_b", "delimiter"],
            "output_type": "STRING",
            "compatible_targets": ["CLIPTextEncode", "Text", "PrimitiveString", "PrimitiveStringMultiline"]
        },
        # Weitere Node-Typen können hier ergänzt werden
        # "TextMultiline": {...},
        # "MathExpression": {...},
    }
    
    def inject_node(
        self,
        workflow: Dict[str, Any],
        node_class_type: str,
        source_connection: List[Union[str, int]],
        target_node_id: str,
        target_input_name: str,
        additional_params: Dict[str, Any]
    ) -> bool:
        """
        Inject a node of specified type between two connected nodes.
        
        Args:
            workflow: The workflow to modify
            node_class_type: Type of node to inject (e.g., "Concatenate")
            source_connection: [node_id, output_idx] of the source
            target_node_id: ID of the target node
            target_input_name: Input name in target node (e.g., "text", "negative")
            additional_params: Node-specific parameters (e.g., {"string2": "text", "delimiter": ", "})
            
        Returns:
            True if successful, False otherwise
        """
        
        # 1. Prüfe ob Node-Typ unterstützt wird
        if node_class_type not in self.SUPPORTED_NODE_TYPES:
            logger.error(
                f"Unsupported node type: {node_class_type}. "
                f"Supported types: {list(self.SUPPORTED_NODE_TYPES.keys())}"
            )
            return False
            
        # 2. Prüfe ob Target-Node existiert
        if target_node_id not in workflow:
            logger.error(f"Target node {target_node_id} not found in workflow")
            return False
            
        target_node = workflow[target_node_id]
        target_class_type = target_node.get("class_type", "")
        
        # 3. Prüfe Kompatibilität
        node_config = self.SUPPORTED_NODE_TYPES[node_class_type]
        compatible_targets = node_config.get("compatible_targets", [])
        
        if compatible_targets and target_class_type not in compatible_targets:
            logger.error(
                f"Node type {node_class_type} is not compatible with target {target_class_type}. "
                f"Compatible targets: {compatible_targets}"
            )
            return False
        
        # 4. Führe spezifische Injection-Logik aus
        if node_class_type == "StringConcatenate":
            return self._inject_string_concatenate(
                workflow, source_connection, target_node_id, 
                target_input_name, additional_params
            )
        
        # Weitere Node-Typen können hier ergänzt werden
        
        logger.error(f"No injection logic implemented for node type: {node_class_type}")
        return False
    
    def _inject_string_concatenate(
        self,
        workflow: Dict[str, Any],
        source_connection: List[Union[str, int]],
        target_node_id: str,
        target_input_name: str,
        params: Dict[str, Any]
    ) -> bool:
        """
        Spezifische Logik für StringConcatenate-Node Injection.
        
        Args:
            workflow: The workflow to modify
            source_connection: [node_id, output_idx] of the source
            target_node_id: ID of the target node
            target_input_name: Input name in target node
            params: Must contain "string_b", optionally "delimiter" and "title"
            
        Returns:
            True if successful
        """
        
        # Validiere erforderliche Parameter
        if "string_b" not in params:
            logger.error("Missing required parameter 'string_b' for StringConcatenate node")
            return False
            
        # Generiere neue Node-ID
        new_node_id = self._find_next_node_id(workflow)
        
        # Erstelle StringConcatenate-Node
        workflow[new_node_id] = {
            "class_type": "StringConcatenate",
            "inputs": {
                "string_a": source_connection,  # Original connection
                "string_b": params.get("string_b", ""),
                "delimiter": params.get("delimiter", ", ")
            },
            "_meta": {
                "title": params.get("title", "Injected StringConcatenate")
            }
        }
        
        # Update Target-Verbindung
        workflow[target_node_id]["inputs"][target_input_name] = [new_node_id, 0]
        
        logger.info(
            f"Successfully injected StringConcatenate node {new_node_id} between "
            f"connection {source_connection} and node {target_node_id}.{target_input_name}"
        )
        return True
    
    def _find_next_node_id(self, workflow: Dict[str, Any]) -> str:
        """
        Find the next available node ID in a workflow.
        
        Args:
            workflow: ComfyUI workflow dictionary
            
        Returns:
            String ID for the next node
        """
        existing_ids = [int(k) for k in workflow.keys() if k.isdigit()]
        return str(max(existing_ids) + 1) if existing_ids else "1000"


# Singleton instance for convenience
node_injector = NodeInjector()


# Convenience functions
def inject_concatenate_for_safety_terms(
    workflow: Dict[str, Any],
    target_node_id: str,
    target_input_name: str,
    source_connection: List[Union[str, int]],
    safety_terms: str,
    title: str = "Safety Terms Concatenation"
) -> bool:
    """
    Convenience function to inject a StringConcatenate node for safety terms.
    
    Args:
        workflow: The workflow to modify
        target_node_id: ID of the CLIPTextEncode node
        target_input_name: Usually "text"
        source_connection: The original connection [node_id, output_idx]
        safety_terms: The safety terms to concatenate
        title: Title for the injected node
        
    Returns:
        True if successful
    """
    return node_injector.inject_node(
        workflow=workflow,
        node_class_type="StringConcatenate",
        source_connection=source_connection,
        target_node_id=target_node_id,
        target_input_name=target_input_name,
        additional_params={
            "string_b": safety_terms,
            "delimiter": ", ",
            "title": title
        }
    )
