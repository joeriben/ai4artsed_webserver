# Legacy ComfyUI Workflows

⚠️ **These are LEGACY workflows from the original Flask server**

## Purpose

These JSON files contain **original ComfyUI workflows** that used the `ai4artsed_prompt_interception` Custom Node. They serve as:

- **Historical reference** for the migration to DevServer
- **Documentation** of original pedagogical implementations
- **Source material** for DevServer config creation

## Structure

Each workflow file contains:
- ComfyUI node graph with `ai4artsed_prompt_interception` node
- Original metaprompts (now called "context" in DevServer)
- Model settings and parameters
- Pedagogical instructions

## DevServer Migration

DevServer configs reference these workflows via `legacy_source` field:

```json
{
  "name": "dada",
  "legacy_source": "workflows_legacy/arts_and_heritage/ai4artsed_Dada_2506220140.json",
  ...
}
```

## Why Keep These?

1. **Architecture documentation** - Shows how Legacy Server worked
2. **Pedagogical preservation** - Original instructions and concepts
3. **Migration validation** - Verify DevServer implementation is correct
4. **Historical record** - Document the evolution of the system

## Do Not Use Directly

These workflows:
- ❌ Do NOT work with DevServer
- ❌ Require the Legacy Flask server + ComfyUI Custom Node
- ✅ Are for REFERENCE ONLY

For working implementations, see:
- DevServer: `/devserver/schemas/configs/`
- Legacy Server: https://github.com/joeriben/ai4artsed_webserver_legacy

---

**Created:** 2025-10-30
**Status:** Archive/Reference only
