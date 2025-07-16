#!/usr/bin/env python3
"""
Test the youth safety filter implementation
"""
import json
from pathlib import Path
import sys

# Add the server directory to the path
sys.path.insert(0, str(Path(__file__).parent / "server"))

from config import SAFETY_NEGATIVE_TERMS
from my_app.services.workflow_logic_service import workflow_logic_service

def test_safety_terms_config():
    """Test that safety terms are properly configured"""
    print("=== Testing Safety Terms Configuration ===")
    
    # Check that both kids and youth terms exist
    assert "kids" in SAFETY_NEGATIVE_TERMS, "Kids safety terms missing"
    assert "youth" in SAFETY_NEGATIVE_TERMS, "Youth safety terms missing"
    
    print(f"✓ Kids terms count: {len(SAFETY_NEGATIVE_TERMS['kids'])}")
    print(f"✓ Youth terms count: {len(SAFETY_NEGATIVE_TERMS['youth'])}")
    
    # Check that they are different
    kids_set = set(SAFETY_NEGATIVE_TERMS['kids'])
    youth_set = set(SAFETY_NEGATIVE_TERMS['youth'])
    
    youth_only = youth_set - kids_set
    print(f"✓ Youth-specific terms: {len(youth_only)}")
    print(f"  Examples: {', '.join(list(youth_only)[:5])}")
    
    return True

def create_test_workflow():
    """Create a minimal workflow for testing"""
    return {
        "1": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "existing negative prompt"}
        },
        "2": {
            "class_type": "KSampler",
            "inputs": {
                "negative": [1, 0],  # Connected to node 1
                "positive": [3, 0],
                "seed": 123
            }
        },
        "3": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": "positive prompt"}
        }
    }

def test_enhance_negative_prompts():
    """Test the enhance_negative_prompts function"""
    print("\n=== Testing Negative Prompt Enhancement ===")
    
    # Test with kids filter
    workflow_kids = create_test_workflow()
    enhanced_count = workflow_logic_service.enhance_negative_prompts(workflow_kids, "kids")
    
    print(f"✓ Kids filter enhanced {enhanced_count} nodes")
    enhanced_text = workflow_kids["1"]["inputs"]["text"]
    print(f"✓ Enhanced text length: {len(enhanced_text)} characters")
    print(f"✓ First 100 chars: {enhanced_text[:100]}...")
    
    # Verify kids terms are present
    kids_terms = ", ".join(SAFETY_NEGATIVE_TERMS["kids"])
    assert kids_terms in enhanced_text, "Kids safety terms not found in enhanced text"
    
    # Test with youth filter
    workflow_youth = create_test_workflow()
    enhanced_count = workflow_logic_service.enhance_negative_prompts(workflow_youth, "youth")
    
    print(f"\n✓ Youth filter enhanced {enhanced_count} nodes")
    enhanced_text = workflow_youth["1"]["inputs"]["text"]
    print(f"✓ Enhanced text length: {len(enhanced_text)} characters")
    print(f"✓ First 100 chars: {enhanced_text[:100]}...")
    
    # Verify youth terms are present
    youth_terms = ", ".join(SAFETY_NEGATIVE_TERMS["youth"])
    assert youth_terms in enhanced_text, "Youth safety terms not found in enhanced text"
    
    # Verify they are different
    assert workflow_kids["1"]["inputs"]["text"] != workflow_youth["1"]["inputs"]["text"], \
        "Kids and youth filters should produce different results"
    
    return True

def test_prepare_workflow():
    """Test the full workflow preparation with safety levels"""
    print("\n=== Testing Full Workflow Preparation ===")
    
    # Find a workflow with safety features
    workflows = workflow_logic_service.list_workflows()
    safety_workflow = None
    
    for wf_name in workflows:
        if "Safe4" in wf_name or "safety" in wf_name.lower():
            safety_workflow = wf_name
            break
    
    if not safety_workflow:
        print("⚠ No safety workflow found for full test")
        return False
    
    print(f"✓ Using workflow: {safety_workflow}")
    
    # Test with youth safety level
    result = workflow_logic_service.prepare_workflow(
        workflow_name=safety_workflow,
        prompt="A creative prompt",
        aspect_ratio="1:1",
        mode="eco",
        seed_mode="standard",
        safety_level="youth"
    )
    
    if result["success"]:
        print("✓ Workflow prepared successfully with youth safety")
        for update in result["status_updates"]:
            if "Jugendschutz" in update:
                print(f"✓ Status update: {update}")
    else:
        print(f"✗ Failed to prepare workflow: {result.get('error')}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("Testing Youth Safety Filter Implementation\n")
    
    tests = [
        test_safety_terms_config,
        test_enhance_negative_prompts,
        test_prepare_workflow
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
