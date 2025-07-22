#!/usr/bin/env python3
"""
Synchronize Note nodes between GUI workflows (SwarmUI) and API workflows
Also normalizes filenames by removing CAPSLOCK category prefixes
"""

import json
import os
from pathlib import Path
import re
import shutil
from typing import Dict, List, Tuple, Optional

# Paths
SWARMUI_WORKFLOWS = Path("/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/user/default/workflows/ai4artsed_comfyui_workflows")
API_WORKFLOWS = Path("/home/joerissen/ai/ai4artsed_webserver/workflows")

# Categories to process
CATEGORIES = ['across', 'aesthetics', 'arts', 'culture', 'flow', 'model', 'semantics', 'sound', 'vector']

def normalize_filename(filename: str) -> str:
    """
    Normalize filename by removing CAPSLOCK category prefixes
    e.g. ai4artsed_MODEL_Comparison_2507191526.json -> ai4artsed_Comparison_2507191526.json
    """
    # Pattern to match category in CAPSLOCK after ai4artsed_
    for category in CATEGORIES:
        pattern = f"ai4artsed_{category.upper()}_"
        if pattern in filename:
            return filename.replace(pattern, "ai4artsed_")
    return filename

def extract_note_nodes_from_gui(workflow_data: Dict) -> Dict[str, Dict]:
    """Extract all Note nodes from a GUI workflow"""
    note_nodes = {}
    
    if "nodes" in workflow_data:
        # GUI format with nodes array
        for node in workflow_data["nodes"]:
            if node.get("type") == "Note":
                title = node.get("title", "")
                if title in ["über", "about"]:
                    # Convert to API format
                    api_node = {
                        "inputs": {},
                        "class_type": "Note",
                        "_meta": {
                            "title": title
                        }
                    }
                    
                    # Extract text from widgets_values
                    widgets = node.get("widgets_values", [])
                    if widgets and len(widgets) > 0:
                        api_node["inputs"]["text"] = widgets[0]
                    
                    note_nodes[title] = {
                        "node_id": str(node.get("id", "")),
                        "node_data": api_node
                    }
    
    return note_nodes

def extract_note_nodes_from_api(workflow_data: Dict) -> Dict[str, Dict]:
    """Extract all Note nodes from an API workflow"""
    note_nodes = {}
    
    for node_id, node_data in workflow_data.items():
        if isinstance(node_data, dict) and node_data.get("class_type") == "Note":
            title = node_data.get("_meta", {}).get("title", "")
            if title in ["über", "about"]:
                note_nodes[title] = {
                    "node_id": node_id,
                    "node_data": node_data
                }
    
    return note_nodes

def add_note_nodes_to_api_workflow(workflow_data: Dict, note_nodes: Dict[str, Dict]) -> Tuple[Dict, List[str]]:
    """
    Add missing Note nodes to an API workflow
    Returns updated workflow and list of added nodes
    """
    added_nodes = []
    
    # Check which nodes are missing
    existing_notes = extract_note_nodes_from_api(workflow_data)
    
    # Find the highest node ID
    max_id = 0
    for node_id in workflow_data.keys():
        try:
            if node_id not in ["id", "revision", "last_node_id", "last_link_id", "nodes", "links", "groups", "config", "extra", "version"]:
                id_num = int(node_id)
                max_id = max(max_id, id_num)
        except ValueError:
            continue
    
    # Add missing nodes
    for title, node_info in note_nodes.items():
        if title not in existing_notes:
            max_id += 1
            new_node_id = str(max_id)
            
            # Copy node data
            new_node = node_info["node_data"].copy()
            workflow_data[new_node_id] = new_node
            
            added_nodes.append(f"{new_node_id} ({title})")
    
    return workflow_data, added_nodes

def add_note_nodes_to_gui_workflow(workflow_data: Dict, note_nodes: Dict[str, Dict]) -> Tuple[Dict, List[str]]:
    """
    Add missing Note nodes to a GUI workflow
    Returns updated workflow and list of added nodes
    """
    added_nodes = []
    
    # Check which nodes are missing
    existing_notes = extract_note_nodes_from_gui(workflow_data)
    
    # Get nodes array or create it
    if "nodes" not in workflow_data:
        workflow_data["nodes"] = []
    
    # Find the highest node ID
    max_id = workflow_data.get("last_node_id", 0)
    for node in workflow_data["nodes"]:
        node_id = node.get("id", 0)
        if node_id > max_id:
            max_id = node_id
    
    # Add missing nodes
    for title, node_info in note_nodes.items():
        if title not in existing_notes:
            max_id += 1
            
            # Create GUI format node
            text = node_info["node_data"].get("inputs", {}).get("text", "")
            new_node = {
                "id": max_id,
                "type": "Note",
                "pos": [500, 500],  # Default position
                "size": [400, 200],  # Default size
                "flags": {},
                "order": len(workflow_data["nodes"]),
                "mode": 0,
                "inputs": [],
                "outputs": [],
                "title": title,
                "properties": {},
                "widgets_values": [text]
            }
            
            workflow_data["nodes"].append(new_node)
            workflow_data["last_node_id"] = max_id
            
            added_nodes.append(f"{max_id} ({title})")
    
    return workflow_data, added_nodes

def find_matching_workflows() -> List[Tuple[Path, Path]]:
    """Find matching workflow pairs between GUI and API directories"""
    matches = []
    
    for category in CATEGORIES:
        gui_category_path = SWARMUI_WORKFLOWS / category
        api_category_path = API_WORKFLOWS / category
        
        if not gui_category_path.exists():
            print(f"GUI category path not found: {gui_category_path}")
            continue
            
        if not api_category_path.exists():
            print(f"API category path not found: {api_category_path}")
            continue
        
        # Get all JSON files in GUI directory
        for gui_file in gui_category_path.glob("*.json"):
            # Normalize the filename
            normalized_name = normalize_filename(gui_file.name)
            
            # Check if corresponding file exists in API directory
            api_file = api_category_path / normalized_name
            if api_file.exists():
                matches.append((gui_file, api_file))
            else:
                # Try to find with original name
                api_file_original = api_category_path / gui_file.name
                if api_file_original.exists():
                    matches.append((gui_file, api_file_original))
                else:
                    print(f"No matching API file for: {gui_file.name}")
    
    return matches

def sync_workflows():
    """Main synchronization function"""
    print("Starting workflow synchronization...")
    print(f"GUI workflows: {SWARMUI_WORKFLOWS}")
    print(f"API workflows: {API_WORKFLOWS}")
    print()
    
    # Find matching workflow pairs
    matches = find_matching_workflows()
    print(f"Found {len(matches)} matching workflow pairs\n")
    
    # Process each pair
    gui_to_api_count = 0
    api_to_gui_count = 0
    
    for gui_file, api_file in matches:
        print(f"Processing: {gui_file.parent.name}/{gui_file.name}")
        
        try:
            # Load both workflows
            with open(gui_file, 'r', encoding='utf-8') as f:
                gui_workflow = json.load(f)
            
            with open(api_file, 'r', encoding='utf-8') as f:
                api_workflow = json.load(f)
            
            # Extract Note nodes from both
            gui_notes = extract_note_nodes_from_gui(gui_workflow)
            api_notes = extract_note_nodes_from_api(api_workflow)
            
            # Sync GUI -> API (add missing notes to API workflow)
            if gui_notes and not all(title in extract_note_nodes_from_api(api_workflow) for title in gui_notes):
                print(f"  Syncing GUI -> API...")
                api_workflow, added = add_note_nodes_to_api_workflow(api_workflow, gui_notes)
                if added:
                    # Save updated API workflow
                    with open(api_file, 'w', encoding='utf-8') as f:
                        json.dump(api_workflow, f, indent=2, ensure_ascii=False)
                    print(f"  Added to API workflow: {', '.join(added)}")
                    gui_to_api_count += 1
            
            # Sync API -> GUI (add missing notes to GUI workflow)
            if api_notes:
                existing_gui_notes = extract_note_nodes_from_gui(gui_workflow)
                missing_in_gui = [title for title in api_notes if title not in existing_gui_notes]
                
                if missing_in_gui:
                    print(f"  Missing in GUI: {missing_in_gui}")
                    print(f"  Syncing API -> GUI...")
                    gui_workflow, added = add_note_nodes_to_gui_workflow(gui_workflow, api_notes)
                    if added:
                        # Save updated GUI workflow
                        with open(gui_file, 'w', encoding='utf-8') as f:
                            json.dump(gui_workflow, f, indent=2, ensure_ascii=False)
                        print(f"  Added to GUI workflow: {', '.join(added)}")
                        api_to_gui_count += 1
                    else:
                        print(f"  No nodes were added (might already exist)")
            
            # Check if API file needs renaming
            normalized_name = normalize_filename(api_file.name)
            if api_file.name != normalized_name:
                new_api_file = api_file.parent / normalized_name
                print(f"  Renaming API file: {api_file.name} -> {normalized_name}")
                shutil.move(str(api_file), str(new_api_file))
            
            # Check if GUI file needs renaming
            normalized_gui_name = normalize_filename(gui_file.name)
            if gui_file.name != normalized_gui_name:
                new_gui_file = gui_file.parent / normalized_gui_name
                print(f"  Renaming GUI file: {gui_file.name} -> {normalized_gui_name}")
                shutil.move(str(gui_file), str(new_gui_file))
        
        except Exception as e:
            print(f"  ERROR: {e}")
        
        print()
    
    print(f"\nSynchronization complete!")
    print(f"GUI -> API updates: {gui_to_api_count}")
    print(f"API -> GUI updates: {api_to_gui_count}")

def check_unmatched_files():
    """Check for files that don't have matches"""
    print("\nChecking for unmatched files...")
    
    # Check API workflows without GUI counterparts
    print("\nAPI workflows without GUI counterparts:")
    for category in CATEGORIES:
        api_category_path = API_WORKFLOWS / category
        if not api_category_path.exists():
            continue
            
        for api_file in api_category_path.glob("*.json"):
            # Try to find in GUI with both original and denormalized names
            gui_category_path = SWARMUI_WORKFLOWS / category
            if gui_category_path.exists():
                found = False
                # Check exact name
                if (gui_category_path / api_file.name).exists():
                    found = True
                # Check with CAPSLOCK category
                capslock_name = api_file.name.replace("ai4artsed_", f"ai4artsed_{category.upper()}_")
                if (gui_category_path / capslock_name).exists():
                    found = True
                
                if not found:
                    print(f"  {category}/{api_file.name}")

if __name__ == "__main__":
    sync_workflows()
    check_unmatched_files()
