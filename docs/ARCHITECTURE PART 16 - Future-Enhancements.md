# DevServer Architecture

**Part 16: Future Enhancements**

---


### Phase 1: Complete Output-Pipeline System
- [ ] Implement `single_text_media_generation.json` pipeline
- [ ] Implement `dual_text_media_generation.json` pipeline
- [ ] Create standard output configs (sd35_standard, flux1_dev, etc.)
- [ ] Test text→media chains

### Phase 2: Advanced Features
- [ ] `image_text_media_generation` pipeline implementation
  - **Status:** NOT IMPLEMENTED (as of 2025-10-28)
  - **Note:** WorkflowClassifier removed - Config metadata will handle validation
  - **See:** DEVELOPMENT_DECISIONS.md (2025-10-28) for Inpainting implementation plan
- [ ] Inpainting support
  - **Note:** Requires image_text_media_generation pipeline + inpainting config
- [ ] ControlNet support
- [ ] Video generation support

### Phase 3: Additional Backends
- [ ] Replicate API integration
- [ ] Stability AI API
- [ ] Direct OpenAI DALL-E integration

### Phase 4: Optimization
- [ ] Batch processing (multiple prompts → multiple images)
- [ ] Streaming output (real-time generation progress)
- [ ] Cost optimization (choose cheapest model for task)
- [ ] Fallback chains (try model A, if fails try model B)

---

