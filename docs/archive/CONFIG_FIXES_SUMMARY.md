# Config Fixes Summary - 2025-10-26

## Problem 1: Incorrect or Missing Context Fields

Several configs had incomplete or incorrect `context` fields that didn't match the original legacy workflows.

### Fixed Configs:

#### 1. **piglatin.json**
- **Before**: `"context": "professional translator"`
- **After**: Full Pig Latin rules (1287 characters)
- **Issue**: Missing the complete Pig Latin transformation rules

#### 2. **ethicaladvisor.json**
- **Before**: `"context": "critical friend"`
- **After**: Full ethical reflection prompt (313 characters)
- **Issue**: Missing the complete ethical advisory instructions

#### 3. **stillepost.json**
- **Before**: `"context": "english"`
- **After**: Descriptive context about Chinese Whispers translation chain
- **Issue**: Too minimal, didn't explain the multi-step translation process

## Problem 2: Incorrect media_preferences

Several text-based configs had `"default_output": "image"` which caused automatic image generation instead of text output.

### Fixed Configs:

1. **piglatin.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

2. **ethicaladvisor.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

3. **stillepost.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

4. **theopposite.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

5. **llm-comparison_14b.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

6. **llm-comparison_30b.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

7. **llm-comparison_mistral.json**
   - Changed: `"default_output": "image"` → `"text"`
   - Changed: `"supported_types": ["image"]` → `["text"]`

8. **translation_en.json**
   - Added missing `media_preferences` field
   - Set: `"default_output": "text"`, `"supported_types": ["text"]`

## Impact

### Before Fixes:
- ❌ PigLatin produced poetic transformations instead of Pig Latin
- ❌ EthicalAdvisor produced poetic transformations instead of ethical reflections
- ❌ Text-based workflows automatically generated images
- ❌ Translation workflows generated images

### After Fixes:
- ✅ PigLatin correctly applies Pig Latin rules
- ✅ EthicalAdvisor provides ethical reflections
- ✅ Text-based workflows output text only
- ✅ Translation workflows output translated text

## Testing Recommendations

Test the following configs to verify fixes:

1. **PigLatin**: Input "Hello world" → Should output "Ellohay orldway"
2. **EthicalAdvisor**: Input any prompt → Should output ethical reflection or "approved"
3. **StillePost**: Input any text → Should output transformed text (not image)
4. **TheOpposite**: Input "A happy cat" → Should output "A sad dog" (or similar opposite)
5. **LLM-Comparison**: Input any prompt → Should output text comparison (not image)
6. **Translation_EN**: Input German text → Should output English translation (not image)

## Files Modified

Total: 8 config files

```
schemas/configs_new/piglatin.json
schemas/configs_new/ethicaladvisor.json
schemas/configs_new/stillepost.json
schemas/configs_new/theopposite.json
schemas/configs_new/llm-comparison_14b.json
schemas/configs_new/llm-comparison_30b.json
schemas/configs_new/llm-comparison_mistral.json
schemas/configs_new/translation_en.json
```

## Root Cause

When migrating from legacy workflows to the new config format, the extraction script:

1. **Context Extraction Issue**:
   - Only extracted `input_context` field from legacy workflows
   - Didn't follow node references to get the actual prompt text
   - Result: Some configs got placeholder values ("professional translator", "critical friend", "english") instead of full instructions

2. **Media Preferences Issue**:
   - Default template assumed all configs generate images
   - Didn't differentiate between text-based and image-based workflows
   - Result: Text-based configs inherited incorrect default

## Prevention

To prevent similar issues in future migrations:

1. ✅ Always follow node references in legacy workflows to extract full context
2. ✅ Validate context length (text-based configs should have substantial context)
3. ✅ Check config category and instruction_type to determine correct media_preferences
4. ✅ Test each migrated config with sample input before deployment
5. ✅ Create automated validation script to check:
   - Context length > 100 chars for manipulation configs
   - media_preferences.default_output matches config type
   - Required fields are present and non-empty
