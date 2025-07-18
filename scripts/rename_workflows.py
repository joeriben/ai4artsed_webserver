#!/usr/bin/env python3
"""
Script to rename workflow files by removing CAPSLOCK categories from filenames
"""
import os
import re
import json
from pathlib import Path

def rename_workflows():
    workflows_dir = Path("../workflows")
    metadata_path = workflows_dir / "metadata.json"
    
    # Load metadata to get the mappings
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata = json.load(f)
    
    # Track renames for updating metadata
    renames = {}
    
    # Process each workflow file
    for old_path in workflows_dir.glob("ai4artsed_*.json"):
        if old_path.name == "metadata.json":
            continue
            
        old_name = old_path.name
        
        # Extract parts of the filename
        # Pattern: ai4artsed_CATEGORY_Name_timestamp.json
        match = re.match(r'^(ai4artsed)_([A-Z]+)_(.+?)(_\d+\.json)$', old_name)
        
        if match:
            prefix = match.group(1)
            category = match.group(2)
            name = match.group(3)
            suffix = match.group(4)
            
            # Create new filename without category
            new_name = f"{prefix}_{name}{suffix}"
            new_path = workflows_dir / new_name
            
            # Only rename if the new name is different
            if old_name != new_name:
                print(f"Renaming: {old_name} -> {new_name}")
                
                # Check if target already exists
                if new_path.exists():
                    print(f"  WARNING: {new_name} already exists, skipping")
                    continue
                
                # Perform the rename
                old_path.rename(new_path)
                renames[old_name] = new_name
        else:
            print(f"Skipping: {old_name} (doesn't match expected pattern)")
    
    # Update metadata.json with new filenames
    if renames:
        print("\nUpdating metadata.json...")
        
        # Update workflow entries
        new_workflows = {}
        for old_name, workflow_data in metadata['workflows'].items():
            new_name = renames.get(old_name, old_name)
            new_workflows[new_name] = workflow_data
        
        metadata['workflows'] = new_workflows
        
        # Write updated metadata
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print("Metadata updated successfully!")
    else:
        print("\nNo files needed renaming.")

if __name__ == "__main__":
    print("Workflow Renaming Script")
    print("========================")
    print("This will remove CAPSLOCK categories from workflow filenames.")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() == 'y':
        rename_workflows()
        print("\nDone!")
    else:
        print("Aborted.")
