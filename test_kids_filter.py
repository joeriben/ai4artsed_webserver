#!/usr/bin/env python3
"""
Test script for kids safety filter functionality
"""
import json
import logging
from pathlib import Path
import sys

# Add server directory to path
sys.path.append(str(Path(__file__).parent / "server"))

from config import KIDS_SAFETY_NEGATIVE_TERMS
from my_app.services.workflow_logic_service import workflow_logic_service

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_kids_filter():
    """Test the kids safety filter with a sample workflow"""
    
    # Test workflow name
    workflow_name = "ai4artsed_MODEL_Stable-Diffusion-3.5_simple_2506151231.json"
    
    print(f"\n=== Testing Kids Safety Filter ===")
    print(f"Workflow: {workflow_name}")
    print(f"Number of safety terms: {len(KIDS_SAFETY_NEGATIVE_TERMS)}")
    print(f"First few safety terms: {KIDS_SAFETY_NEGATIVE_TERMS[:5]}")
    
    # Load workflow
    workflow = workflow_logic_service.load_workflow(workflow_name)
    if not workflow:
        print(f"ERROR: Could not load workflow {workflow_name}")
        return
    
    print(f"\nWorkflow loaded successfully")
    print(f"Number of nodes: {len(workflow)}")
    
    # Find negative prompt before enhancement
    print("\n--- BEFORE Enhancement ---")
    for node_id, node_data in workflow.items():
        if node_data.get("class_type") == "CLIPTextEncode":
            text = node_data.get("inputs", {}).get("text", "")
            print(f"Node {node_id} (CLIPTextEncode): '{text}'")
    
    # Apply kids safety enhancement
    print("\n--- Applying Kids Safety Enhancement ---")
    enhanced_count = workflow_logic_service.enhance_negative_prompts_for_kids(workflow)
    print(f"Enhanced count: {enhanced_count}")
    
    # Check negative prompts after enhancement
    print("\n--- AFTER Enhancement ---")
    for node_id, node_data in workflow.items():
        if node_data.get("class_type") == "CLIPTextEncode":
            text = node_data.get("inputs", {}).get("text", "")
            print(f"Node {node_id} (CLIPTextEncode):")
            print(f"  Length: {len(text)} chars")
            print(f"  First 200 chars: '{text[:200]}...'")
            print(f"  Contains 'violence': {'violence' in text}")
            print(f"  Contains 'blood': {'blood' in text}")
            print(f"  Contains 'horror': {'horror' in text}")
    
    # Test full workflow preparation
    print("\n--- Testing Full Workflow Preparation ---")
    result = workflow_logic_service.prepare_workflow(
        workflow_name=workflow_name,
        prompt="A peaceful garden scene",
        aspect_ratio="1:1",
        mode="eco",
        seed_mode="random",
        custom_seed=None,
        safety_level="kids"
    )
    
    if result["success"]:
        print("Workflow preparation successful")
        print(f"Status updates: {result['status_updates']}")
        
        # Check final workflow
        final_workflow = result["workflow"]
        print("\n--- Final Workflow Check ---")
        for node_id, node_data in final_workflow.items():
            if node_data.get("class_type") == "CLIPTextEncode":
                text = node_data.get("inputs", {}).get("text", "")
                if len(text) > 50:  # Likely the enhanced negative prompt
                    print(f"Node {node_id} negative prompt enhanced: {len(text)} chars")
    else:
        print(f"ERROR: {result.get('error')}")

if __name__ == "__main__":
    test_kids_filter()
