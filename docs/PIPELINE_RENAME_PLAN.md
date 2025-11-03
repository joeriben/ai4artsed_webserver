# Pipeline Rename Migration Plan

**Date:** 2025-11-03
**Status:** PLANNED (Not yet executed)
**Priority:** Medium (do after Stage 4 testing is complete)

---

## Problem: Ambiguous Pipeline Naming

Current pipeline names are confusing because "generation" is ambiguous:

| Current Name | Ambiguous Reading | Actual Meaning |
|--------------|------------------|----------------|
| `single_prompt_generation` | "Generate a single prompt" | "Generate media FROM one prompt" |
| `dual_prompt_generation` | "Generate dual prompts" | "Generate media FROM two prompts" |

This caused confusion leading to Session 15's accidental deprecation of `single_prompt_generation.json`.

---

## Proposed Solution: Input-Type Naming Convention

**New Pattern:** `[INPUT_TYPE(S)]_media_generation`

### Rename Map

| Current Name | New Name | Input Structure | Output |
|--------------|----------|----------------|--------|
| `single_prompt_generation` | `single_text_media_generation` | 1 text | Image/Audio/Video |
| `dual_prompt_generation` | `dual_text_media_generation` | 2 texts | Music (tags + lyrics) |
| `image_plus_text_generation` | `image_text_media_generation` | 1 image + 1 text | Image (inpainting) |

### Future Extensions (Planned)

| New Name | Input Structure | Output | Use Case |
|----------|----------------|--------|----------|
| `image_image_media_generation` | 2 images | Image | Style transfer |
| `video_text_media_generation` | 1 video + 1 text | Video | Video editing |
| `audio_text_media_generation` | 1 audio + 1 text | Audio | Audio manipulation |

---

## Benefits

1. **Unambiguous:** "text" clearly indicates input, "media" clearly indicates output
2. **Scalable:** Easy pattern for future multimodal pipelines
3. **Self-documenting:** Name explicitly describes input structure
4. **Pedagogically clear:** Students immediately understand data flow
5. **Consistent:** All follow same `[INPUT(S)]_media_generation` pattern

---

## Migration Steps

### Phase 1: Identify All References

**1.1 Pipeline Files**
```bash
cd devserver/schemas/pipelines
ls -la single_prompt_generation.json
ls -la dual_prompt_generation.json
ls -la image_plus_text_generation.json
```

**1.2 Config Files Referencing Pipelines**
```bash
cd devserver/schemas/configs
grep -r '"pipeline": "single_prompt_generation"' . -l
grep -r '"pipeline": "dual_prompt_generation"' . -l
grep -r '"pipeline": "image_plus_text_generation"' . -l
```

Expected results:
- `single_prompt_generation`: `output/sd35_large.json`, `output/gpt5_image.json`
- `dual_prompt_generation`: `output/acestep.json` (if exists)
- `image_plus_text_generation`: (not yet implemented)

**1.3 Documentation References**
```bash
cd docs
grep -r "single_prompt_generation" . -l
grep -r "dual_prompt_generation" . -l
```

Expected files:
- `ARCHITECTURE.md`
- `SESSION_HANDOVER.md`
- `DEVELOPMENT_DECISIONS.md`
- `devserver_todos.md`

**1.4 Code References**
```bash
cd devserver
grep -r "single_prompt_generation" . --include="*.py" -l
grep -r "dual_prompt_generation" . --include="*.py" -l
```

Expected files:
- Possibly in tests
- Possibly in hardcoded constants (hopefully not!)

---

### Phase 2: Execute Rename

**2.1 Rename Pipeline Files**
```bash
cd devserver/schemas/pipelines
git mv single_prompt_generation.json single_text_media_generation.json
git mv dual_prompt_generation.json dual_text_media_generation.json
git mv image_plus_text_generation.json image_text_media_generation.json  # if exists
```

**2.2 Update Pipeline Internal Names**

Edit each renamed pipeline file:
```json
{
  "name": "single_text_media_generation",  // ← Update this
  "description": "Single Text to Media Generation Pipeline: Direct media generation from one text prompt",
  ...
}
```

**2.3 Update All Config References**

For each config file found in Phase 1.2:
```json
{
  "pipeline": "single_text_media_generation",  // ← Update this
  ...
}
```

**Example:**
```bash
# In devserver/schemas/configs/output/sd35_large.json
# Change:
"pipeline": "single_prompt_generation"
# To:
"pipeline": "single_text_media_generation"
```

**2.4 Update Documentation**

In `docs/ARCHITECTURE.md`:
- Replace all instances of old names with new names
- Update pipeline comparison tables
- Update example code snippets

In `docs/SESSION_HANDOVER.md`:
- Update pipeline references
- Add note about rename

In `docs/DEVELOPMENT_DECISIONS.md`:
- Add entry documenting the rename decision and rationale

---

### Phase 3: Test Everything

**3.1 Verify Config Loading**
```bash
cd devserver
python3 -c "
from schemas.engine.config_loader import ConfigLoader
from pathlib import Path

loader = ConfigLoader()
loader.initialize(Path('schemas'))

print(f'Pipelines loaded: {len(loader.pipelines)}')
print(f'Configs loaded: {len(loader.configs)}')

# Test specific configs
for config_name in ['sd35_large', 'gpt5_image']:
    cfg = loader.get_config(config_name)
    if cfg:
        print(f'✓ {config_name}: pipeline={cfg.pipeline_name}')
    else:
        print(f'✗ {config_name}: NOT FOUND')
"
```

**3.2 Test Pipeline Execution**
```bash
# Test Stage 4 with renamed pipeline
curl -X POST http://localhost:17801/api/schema/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{
    "schema": "dada",
    "input_text": "Eine Blume auf der Wiese",
    "execution_mode": "eco",
    "safety_level": "kids"
  }'
```

Should complete all 4 stages without errors.

**3.3 Run Test Suite**
```bash
cd devserver
python3 test_pipeline_execution.py
python3 test_refactored_system.py
```

---

### Phase 4: Documentation & Commit

**4.1 Update This Plan**
Mark status as "COMPLETED" with execution date

**4.2 Git Commit**
```bash
git add .
git commit -m "refactor: Rename pipelines to input-type naming convention

Old names were ambiguous:
- single_prompt_generation → single_text_media_generation
- dual_prompt_generation → dual_text_media_generation
- image_plus_text_generation → image_text_media_generation

New pattern: [INPUT_TYPE(S)]_media_generation

Benefits:
- Unambiguous: clearly separates input (text/image) from output (media)
- Scalable: easy to add new multimodal combinations
- Self-documenting: name describes input structure
- Pedagogically clear: students understand data flow

Files changed:
- Pipeline files renamed and internal names updated
- All config references updated (sd35_large, gpt5_image, etc.)
- Documentation updated (ARCHITECTURE.md, SESSION_HANDOVER.md)
- All tests passing

Related: docs/PIPELINE_RENAME_PLAN.md
Session: 16 (planning), 17+ (execution)
"

git push origin feature/schema-architecture-v2
```

---

## Backward Compatibility (Optional)

If you want to support old names temporarily, add to `config_loader.py`:

```python
# Pipeline name aliases for backward compatibility
PIPELINE_ALIASES = {
    "single_prompt_generation": "single_text_media_generation",
    "dual_prompt_generation": "dual_text_media_generation",
    "image_plus_text_generation": "image_text_media_generation"
}

def _resolve_pipeline_name(self, pipeline_name: str) -> str:
    """Resolve pipeline name, handling legacy aliases"""
    return PIPELINE_ALIASES.get(pipeline_name, pipeline_name)
```

**Recommendation:** Don't implement aliases. Clean break is better since:
1. No external API consumers yet
2. Only 2-3 configs to update
3. Simpler to maintain

---

## Risk Assessment

**Risk Level:** LOW

**Why:**
- Internal refactor only (no API changes)
- Small number of files to update (~5 configs)
- Easy to test (just load configs and run pipeline)
- Can revert via git if needed

**Potential Issues:**
1. Forgetting to update a config → Config won't load (error is obvious)
2. Forgetting to update docs → Confusing for future sessions
3. Breaking tests → Tests will fail (easy to catch)

**Mitigation:**
- Use grep to find ALL references systematically
- Test before committing
- Update SESSION_HANDOVER.md to warn next session

---

## Estimated Time

- **Phase 1 (Identify):** 10 minutes
- **Phase 2 (Execute):** 20 minutes
- **Phase 3 (Test):** 15 minutes
- **Phase 4 (Document/Commit):** 10 minutes

**Total:** ~55 minutes (less than 1 hour)

---

## When to Execute

**NOT NOW** - Current priority is testing Stage 4 with the restored pipeline.

**BEST TIME:**
- After Stage 4 testing is complete
- After user confirms 4-stage flow works
- Before starting interface design work (cleaner foundation)

**Worst Time:**
- During active debugging
- Right before a demo
- When other critical changes are in progress

---

## Success Criteria

✅ All pipeline files renamed
✅ All config references updated
✅ All documentation updated
✅ ConfigLoader loads all configs successfully
✅ Test pipeline execution completes all stages
✅ All tests passing
✅ Git committed with clear message
✅ No "prompt_generation" strings remain in codebase (except this plan and git history)

---

## Rollback Plan

If something breaks:

```bash
# Revert the commit
git revert HEAD

# Or reset to before rename
git reset --hard <commit-before-rename>

# Or manually restore from git
git checkout HEAD~1 -- devserver/schemas/pipelines/single_prompt_generation.json
git checkout HEAD~1 -- devserver/schemas/configs/output/sd35_large.json
# etc.
```

---

**Created:** 2025-11-03 (Session 16)
**To Execute:** Session 17+ (after Stage 4 testing)
**Status:** PLANNED
**Assignee:** Next Claude Code session or User
