#!/usr/bin/env python3
"""
Rename ALL GUI workflows to remove CAPSLOCK category prefixes
Since they are now organized in category folders
"""

import os
from pathlib import Path
import shutil

# Path to SwarmUI workflows
SWARMUI_WORKFLOWS = Path("/home/joerissen/ai/SwarmUI/dlbackend/ComfyUI/user/default/workflows/ai4artsed_comfyui_workflows")

# Categories to process
CATEGORIES = ['across', 'aesthetics', 'arts', 'culture', 'flow', 'model', 'semantics', 'sound', 'vector']

def normalize_filename(filename: str) -> str:
    """
    Normalize filename by removing CAPSLOCK category prefixes
    e.g. ai4artsed_MODEL_Comparison_2507191526.json -> ai4artsed_Comparison_2507191526.json
    Also handles special cases like INTERVENTION, INTERCEPTION, etc.
    """
    # Common prefixes to remove (including categories and special terms)
    # Order matters! More specific patterns first
    prefixes_to_remove = [
        "ai4artsed_SOUND_MODEL_",  # Must come before SOUND_
        "ai4artsed_ACROSS_",
        "ai4artsed_AESTHETICS_",
        "ai4artsed_ARTS_",
        "ai4artsed_CULTURE_",
        "ai4artsed_FLOW_",
        "ai4artsed_MODEL_",
        "ai4artsed_SEMANTICS_",
        "ai4artsed_SOUND_",
        "ai4artsed_VECTOR_",
        "ai4artsed_INTERVENTION_",
        "ai4artsed_INTERCEPTION_"
    ]
    
    for prefix in prefixes_to_remove:
        if filename.startswith(prefix):
            return filename.replace(prefix, "ai4artsed_", 1)
    
    return filename

def rename_workflows_in_category(category_path: Path) -> int:
    """Rename all workflows in a category folder"""
    renamed_count = 0
    
    if not category_path.exists():
        print(f"Category path not found: {category_path}")
        return 0
    
    print(f"\nProcessing category: {category_path.name}")
    
    # Get all JSON files in the category
    for workflow_file in category_path.glob("*.json"):
        normalized_name = normalize_filename(workflow_file.name)
        
        if workflow_file.name != normalized_name:
            new_path = workflow_file.parent / normalized_name
            print(f"  Renaming: {workflow_file.name} -> {normalized_name}")
            
            try:
                shutil.move(str(workflow_file), str(new_path))
                renamed_count += 1
            except Exception as e:
                print(f"    ERROR: {e}")
    
    return renamed_count

def main():
    """Main function to rename all GUI workflows"""
    print("Starting GUI workflow renaming...")
    print(f"GUI workflows directory: {SWARMUI_WORKFLOWS}")
    
    total_renamed = 0
    
    # Process each category
    for category in CATEGORIES:
        category_path = SWARMUI_WORKFLOWS / category
        renamed = rename_workflows_in_category(category_path)
        total_renamed += renamed
    
    # Also check for any workflows in the root directory
    print(f"\nProcessing root directory...")
    for workflow_file in SWARMUI_WORKFLOWS.glob("*.json"):
        normalized_name = normalize_filename(workflow_file.name)
        
        if workflow_file.name != normalized_name:
            new_path = workflow_file.parent / normalized_name
            print(f"  Renaming: {workflow_file.name} -> {normalized_name}")
            
            try:
                shutil.move(str(workflow_file), str(new_path))
                total_renamed += 1
            except Exception as e:
                print(f"    ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"Renaming complete! Total files renamed: {total_renamed}")
    
    # Show summary of remaining files with CAPSLOCK
    print(f"\nChecking for any remaining CAPSLOCK patterns...")
    remaining_capslock = []
    
    for category in CATEGORIES:
        category_path = SWARMUI_WORKFLOWS / category
        if category_path.exists():
            for workflow_file in category_path.glob("*.json"):
                # Check if filename still contains CAPSLOCK patterns
                if any(pattern in workflow_file.name for pattern in ["_ACROSS_", "_AESTHETICS_", "_ARTS_", "_CULTURE_", "_FLOW_", "_MODEL_", "_SEMANTICS_", "_SOUND_", "_VECTOR_", "_INTERVENTION_", "_INTERCEPTION_", "_SOUND_MODEL_"]):
                    remaining_capslock.append(f"{category}/{workflow_file.name}")
    
    if remaining_capslock:
        print(f"Files still containing CAPSLOCK patterns:")
        for file in remaining_capslock:
            print(f"  {file}")
    else:
        print("No files with CAPSLOCK patterns found! ✓")

if __name__ == "__main__":
    main()
