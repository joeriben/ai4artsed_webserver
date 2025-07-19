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
    
    # Find über and about nodes
    for node_id, node in workflow_data.items():
        if node.get("_meta", {}).get("title") == "über":
            # For Note nodes, text is in widgets_values
            text = ""
            if "widgets_values" in node and isinstance(node["widgets_values"], list) and len(node["widgets_values"]) > 0:
                text = node["widgets_values"][0]
            else:
                text = node.get("inputs", {}).get("value", "")
            
            lines = text.split("\n") if text else []
            if len(lines) >= 1:
                info["name"]["de"] = lines[0]
            if len(lines) >= 2:
                info["description"]["de"] = lines[1]
            if len(lines) >= 3:
                info["longDescription"]["de"] = "\n".join(lines[2:])
                
        elif node.get("_meta", {}).get("title") == "about":
            # For Note nodes, text is in widgets_values
            text = ""
            if "widgets_values" in node and isinstance(node["widgets_values"], list) and len(node["widgets_values"]) > 0:
                text = node["widgets_values"][0]
            else:
                text = node.get("inputs", {}).get("value", "")
            
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
    workflows_dir = Path("../workflows")
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
                    if workflow_id in ["ai4artsed_MODEL_OmniGen2_2507171527", "ai4artsed_MODEL_Comparison_2507191526"]:
                        print(f"\nDEBUG {workflow_id}:")
                        print(f"  Name: {info['name']}")
                        print(f"  Description: {info['description']}")
                        print(f"  Has 'über' node: {'76' in workflow_data or '77' in workflow_data}")
                        if '76' in workflow_data:
                            print(f"  Node 76: {workflow_data['76']}")
                        if '77' in workflow_data:
                            print(f"  Node 77: {workflow_data['77']}")
                    
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
