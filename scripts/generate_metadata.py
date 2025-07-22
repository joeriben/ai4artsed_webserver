#!/usr/bin/env python3
"""
Script to generate metadata.json from workflow folder structure and about nodes
"""
import json
from pathlib import Path
import os

def extract_about_info(workflow_data):
    """Extract information from über and about nodes"""
    info = {
        "name": {"de": "", "en": ""},
        "description": {"de": "", "en": ""},
        "longDescription": {"de": "", "en": ""}
    }
    
    # Find über and about nodes (can be Note or PrimitiveStringMultiline)
    for node_id, node in workflow_data.items():
        if isinstance(node, dict):
            class_type = node.get("class_type", "")
            title = node.get("_meta", {}).get("title", "")
            
            # Check if this is a Note or PrimitiveStringMultiline with über/about title
            if (class_type == "Note" and title in ["über", "about"]) or \
               (class_type == "PrimitiveStringMultiline" and title in ["über", "about"]):
                
                # Get text based on node type
                if class_type == "Note":
                    # For Note nodes in API format, text is in inputs.text
                    text = node.get("inputs", {}).get("text", "")
                else:
                    # For PrimitiveStringMultiline, text is in inputs.value
                    text = node.get("inputs", {}).get("value", "")
                
                if title == "über":
                    lines = text.split("\n") if text else []
                    if len(lines) >= 1:
                        info["name"]["de"] = lines[0]
                    if len(lines) >= 2:
                        info["description"]["de"] = lines[1]
                    if len(lines) >= 3:
                        info["longDescription"]["de"] = "\n".join(lines[2:])
                        
                elif title == "about":
                    lines = text.split("\n") if text else []
                    if len(lines) >= 1:
                        info["name"]["en"] = lines[0]
                    if len(lines) >= 2:
                        info["description"]["en"] = lines[1]
                    if len(lines) >= 3:
                        info["longDescription"]["en"] = "\n".join(lines[2:])
    
    return info

def generate_metadata():
    """Generate metadata.json from workflow files"""
    # Get the path relative to the script location
    script_dir = Path(__file__).parent
    workflows_dir = script_dir.parent / "workflows"
    metadata = {"categories": {}, "workflows": {}}
    
    # Define category names
    category_names = {
        "across": {"de": "Medienübergreifend", "en": "Cross-Media"},
        "aesthetics": {"de": "Ästhetik", "en": "Aesthetics"},
        "arts": {"de": "Kunstrichtungen", "en": "Art Movements"},
        "culture": {"de": "Kultur", "en": "Culture"},
        "flow": {"de": "Ablauf", "en": "Flow"},
        "model": {"de": "Modelle", "en": "Models"},
        "semantics": {"de": "Semantik", "en": "Semantics"},
        "sound": {"de": "Klang", "en": "Sound"},
        "vector": {"de": "Vektorräume", "en": "Vector Spaces"}
    }
    
    # Process each category folder
    for category_folder in workflows_dir.iterdir():
        if category_folder.is_dir() and category_folder.name in category_names:
            category = category_folder.name
            
            # Add category metadata
            metadata["categories"][category] = category_names[category]
            
            # Process workflow files in this category
            for workflow_file in category_folder.glob("*.json"):
                workflow_id = workflow_file.stem
                
                try:
                    # Read workflow file
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                    
                    # Extract information from about nodes
                    info = extract_about_info(workflow_data)
                    
                    # Debug output for problematic workflows
                    if workflow_id in ["ai4artsed_OmniGen2ImageEdit_2507171341", "ai4artsed_Comparison_2507191526", "ai4artsed_(((PromptInterception)))_2507101853"]:
                        print(f"\nDEBUG {workflow_id}:")
                        print(f"  Name: {info['name']}")
                        print(f"  Description: {info['description']}")
                        print(f"  Looking for Note/PrimitiveStringMultiline nodes...")
                        for node_id, node_data in workflow_data.items():
                            if isinstance(node_data, dict):
                                class_type = node_data.get("class_type", "")
                                title = node_data.get("_meta", {}).get("title", "")
                                if title in ["über", "about"] and class_type in ["Note", "PrimitiveStringMultiline"]:
                                    if class_type == "Note":
                                        text = node_data.get("inputs", {}).get("text", "")
                                    else:
                                        text = node_data.get("inputs", {}).get("value", "")
                                    print(f"  Found {title} node (ID: {node_id}, type: {class_type}), text length: {len(text)}")
                                    print(f"  First 100 chars: {text[:100]}")
                    
                    # Add to metadata
                    metadata["workflows"][workflow_id] = {
                        "category": category,
                        "name": info["name"],
                        "description": info["description"],
                        "longDescription": info["longDescription"],
                        "file": f"{category}/{workflow_file.name}"
                    }
                    
                except Exception as e:
                    print(f"Error processing {workflow_file}: {e}")
    
    # Write metadata.json
    metadata_path = workflows_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"Generated metadata.json with {len(metadata['workflows'])} workflows in {len(metadata['categories'])} categories")
    return metadata_path

def main():
    metadata_path = generate_metadata()
    
    # Display summary
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    print("\nCategories:")
    for cat_id, cat_names in metadata["categories"].items():
        print(f"  {cat_id}: {cat_names['de']} / {cat_names['en']}")
    
    print(f"\nTotal workflows: {len(metadata['workflows'])}")

if __name__ == "__main__":
    main()
