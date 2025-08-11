#!/usr/bin/env python3
"""Populate workflows/metadata.json with placeholder entries.

This script scans workflow JSON files and ensures each has an entry in
metadata.json. For new workflows, a name is derived from the filename and
placeholder description fields are inserted so that the file can be edited
manually later.
"""
import json
import re
from pathlib import Path

def clean_name(workflow_id: str) -> str:
    """Create a human readable name from a workflow id."""
    name = workflow_id
    if name.startswith("ai4artsed_"):
        name = name[len("ai4artsed_"):]
    name = re.sub(r"_[0-9]+$", "", name)
    name = name.replace("_", " ")
    return name.strip()

def main() -> None:
    root = Path(__file__).resolve().parent.parent
    workflows_dir = root / "workflows"
    metadata_path = workflows_dir / "metadata.json"

    if metadata_path.exists():
        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
    else:
        metadata = {"categories": {}, "workflows": {}}

    for category_dir in workflows_dir.iterdir():
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        if category.startswith("."):
            continue
        metadata.setdefault("categories", {})
        if category not in metadata["categories"]:
            metadata["categories"][category] = {"de": category, "en": category}

        for wf_file in category_dir.glob("*.json"):
            workflow_id = wf_file.stem
            if workflow_id in metadata.setdefault("workflows", {}):
                continue

            display_name = clean_name(workflow_id)
            metadata["workflows"][workflow_id] = {
                "category": category,
                "name": {"de": display_name, "en": display_name},
                "description": {"de": "Short description", "en": "Short description"},
                "longDescription": {"de": "Long description", "en": "Long description"},
                "file": f"{category}/{wf_file.name}",
            }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"Updated {metadata_path} with {len(metadata['workflows'])} workflows.")

if __name__ == "__main__":
    main()
