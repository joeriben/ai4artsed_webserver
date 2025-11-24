# Session 49 - Pipeline Visualization System (Handover)

## Status: PARTIAL IMPLEMENTATION

Implementation was partially completed, then rolled back due to 500 errors and context overflow.

## What Was Completed Successfully

### 1. Backend: Pipeline Visualization Metadata System ✅

**File**: `devserver/my_app/routes/schema_pipeline_routes.py` (Lines 823-905)

Three helper functions added to generate child-friendly pipeline visualizations:

```python
def _get_step_icon(chunk_name: str) -> str:
    """Returns emoji for each chunk type (e.g., 'optimize_t5_prompt' → '📝')"""

def _get_child_friendly_label(chunk_name: str, description: str, language: str) -> dict:
    """Returns 2-3 word labels for kids ages 10-15
    - DE: 'optimize_t5_prompt' → 'Bedeutung verstehen'
    - EN: 'optimize_t5_prompt' → 'Understanding meaning'
    """

def _get_pipeline_visualization_metadata(pipeline_name: str, language: str) -> dict:
    """Reads pipeline structure from schemas/pipelines/*.json files
    Returns visualization metadata with steps, icons, labels
    """
```

**Enhanced `/api/schema/pipeline/execute` response** (Lines 887-905):
- Added `pipeline_visualization`: Structure metadata (steps, icons, labels)
- Added `execution_steps`: Runtime data (status, output, duration per step)

### 2. Frontend: PipelineFlowVisualization Component ✅

**File**: `public/ai4artsed-frontend/src/components/PipelineFlowVisualization.vue`

Complete Vue component (~550 lines) showing horizontal flow:
```
💡 Input → 📝 Understanding → 🎨 Visuals → 🖼️ Image → [Result]
```

Features:
- Status indicators: ⚙️ (running), ✓ (complete), ✗ (failed)
- Clickable steps show details
- Responsive: horizontal (desktop), vertical (mobile)
- Accessibility: high contrast, reduced motion support

### 3. Frontend: i18n Translations ✅

**File**: `public/ai4artsed-frontend/src/i18n.ts` (Lines 137-141, 276-280)

Added pipeline labels in German and English.

### 4. Frontend: TypeScript Types ✅

**File**: `public/ai4artsed-frontend/src/services/api.ts` (Lines 70-122)

```typescript
interface ExecutionStep { ... }
interface PipelineStepDefinition { ... }
interface PipelineVisualization { ... }

// Extended PipelineExecuteResponse with:
pipeline_visualization?: PipelineVisualization
execution_steps?: ExecutionStep[]
```

### 5. Backend: Admin Configuration System ✅

**File**: `devserver/config.py` (Lines 9-80)

**IMPORTANT**: This is the ONLY change that remains after rollback.

Clear ADMIN section at top of file with:

```python
# 1. USER INTERFACE MODE
UI_MODE = "kids"  # Options: "kids", "youth", "expert"

# kids (ages 8-12): Simple interface, separated phases
# youth (ages 13-17): Pipeline visualization, educational flow
# expert: Full debug mode, all metadata visible

# 2. SAFETY LEVEL (Content Filtering)
DEFAULT_SAFETY_LEVEL = "kids"  # Options: "kids", "youth", "adult", "off"

# kids: Maximum filtering (violence, horror, sexual content)
# youth: Moderate filtering (explicit content only)
# adult: Minimal filtering (only §86a StGB illegal content)
# off: No filtering (DEVELOPMENT ONLY)

# 3. SERVER SETTINGS
HOST = "0.0.0.0"
PORT = 17802

# 4. LANGUAGE
DEFAULT_LANGUAGE = "de"
```

**SAFETY_NEGATIVE_TERMS** expanded (Lines 275-308):
- `"kids"`: 49 blocked terms (existing)
- `"youth"`: 17 blocked terms (existing)
- `"adult"`: 11 blocked terms (NEW - only illegal content)
- `"off"`: 0 blocked terms (NEW - for testing)

## What Was Attempted But ROLLED BACK ❌

### 1. userPreferences Store Enhancement
- Added `uiMode` state ("kids"/"youth"/"expert")
- Added `setUiMode()` and `cycleUiMode()` functions
- **Rolled back**: Not needed yet, caused complexity

### 2. Transform API Visualization Extension
- Modified `/api/schema/transform` endpoint to return pipeline_visualization
- **Rolled back**: Caused 500 errors, needs careful testing

### 3. Phase2CreativeFlowView Integration
- Added UI Mode toggle button in top bar
- Added visualization in main layout (not just overlay)
- Captured visualization data in handleTransform()
- **Rolled back**: Too many changes without testing

### 4. TransformResponse TypeScript Extension
- Added pipeline_visualization/execution_steps to TransformResponse
- **Rolled back**: Dependency of other rolled back changes

## Core Problem Identified

The visualization was initially placed ONLY in the Media Generation Overlay:
```vue
<div v-if="isGenerating || previewImage" class="generation-overlay">
  <PipelineFlowVisualization ... />
</div>
```

**Problem**: Transform-only configs (dada, bauhaus, surrealization) never trigger `isGenerating`, so visualization never appears!

**Solution needed**: Visualization must also appear during transformation (handleTransform), not just media generation.

## Architecture Clarification

### Frontend Phase System (User's Correction):
- **Phase 1**: Property Selection
- **Phase 2**: Creative Flow
  - **Phase 2a**: Transform (`/api/schema/transform` - Stage 1+2)
  - **Phase 2b**: Media Selection (user chooses output type)
  - **Phase 3/4**: Media Generation (`/api/schema/pipeline/execute` - Stage 3+4)

### Backend Stage System (Always 4 Stages):
All executions go through 4-stage orchestration:
1. Stage 1: Translation + Safety
2. Stage 2: Interception/Transformation
3. Stage 3: Pre-Output Safety
4. Stage 4: Media Generation (may be skipped if no output_config)

### Key Insight:
"Stage 2 Pipelines" don't exist - ALL pipelines run through all 4 stages. The difference is:
- Text-only configs: No output_config → Stage 4 skipped
- Media configs: Have output_config → Stage 4 executes

Frontend splits this into TWO API calls for UX reasons (kids mode simplicity).

## Next Steps for Future Implementation

### Youth Mode Implementation Plan:

1. **Add uiMode to userPreferences store**
   - State: `uiMode` ("kids"/"youth"/"expert")
   - Functions: `setUiMode()`, `cycleUiMode()`
   - Persisted in localStorage

2. **Add UI Mode toggle**
   - Button in top bar of Phase2CreativeFlowView
   - Cycles through modes: kids → youth → expert

3. **Extend Transform API** (CAREFULLY!)
   - Add pipeline_visualization to `/api/schema/transform` response
   - Test thoroughly before deploying
   - Check for attribute errors on `config.pipeline_name`

4. **Show visualization in main layout**
   - After result panel, conditional: `v-if="pipelineVisualization && uiMode !== 'kids'"`
   - During transform AND after completion
   - Separate from media generation overlay

5. **Youth Mode Flow** (Future):
   - Consider combining Phase 2a+2b+3/4 into single continuous flow
   - Show visualization throughout entire process
   - Auto-proceed to media generation (optional)

## Modified Files (Current State)

**Kept**:
- `devserver/config.py`: ADMIN section with UI_MODE and complete SAFETY_NEGATIVE_TERMS

**Reverted** (working state restored):
- `devserver/my_app/routes/schema_pipeline_routes.py`: Transform endpoint changes removed
- `public/ai4artsed-frontend/src/services/api.ts`: TransformResponse back to original
- `public/ai4artsed-frontend/src/stores/userPreferences.ts`: uiMode system removed
- `public/ai4artsed-frontend/src/views/Phase2CreativeFlowView.vue`: UI toggle and main layout viz removed

**Unchanged** (from previous session, working):
- `public/ai4artsed-frontend/src/components/PipelineFlowVisualization.vue`: Component exists and works
- `public/ai4artsed-frontend/src/i18n.ts`: Pipeline translations exist

## Critical Lessons Learned

1. **Test Incrementally**: Each change should be tested before adding more
2. **Understand Architecture First**: Transform API vs Execute API distinction is crucial
3. **Check Existing Code**: System reminders about file modifications must be heeded
4. **Use Thinking Mode**: Complex architectural changes need careful planning
5. **Kids vs Youth UI**: Separation of phases is intentional for kids (8-12), youth mode is for ages 13-17

## Technical Debt

1. **surrealization.json deleted**: Moved to deactivated/ folder - check if this was intentional
2. **Multiple background bash shells**: Many old test servers still running - cleanup needed
3. **UI_MODE not used**: config.py has UI_MODE but it's not consumed anywhere yet
4. **DEFAULT_SAFETY_LEVEL not used**: config.py has it but system still uses request-level safety_level

## Safe Next Session Start

To continue this work safely:

1. Read this handover document
2. Read Session 48 documentation about dual-encoder pipelines
3. Test current visualization (only works in media generation overlay for now)
4. Plan youth mode implementation carefully with user approval
5. Implement ONE change at a time, test each change
6. Don't modify Transform API without understanding error implications

## Current Working State

✅ Backend: Serves pipeline visualization metadata for `/api/schema/pipeline/execute`
✅ Frontend: Shows visualization in media generation overlay (Phase 3/4)
✅ Config: Admin can configure UI_MODE and SAFETY_LEVEL in config.py
❌ Transform visualization: Not yet working (needs Transform API enhancement)
❌ Youth mode: Not yet implemented (needs uiMode store + conditional rendering)
