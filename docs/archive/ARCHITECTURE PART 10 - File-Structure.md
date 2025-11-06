# DevServer Architecture

**Part 10: File Structure**

---


```
devserver/
├── schemas/
│   ├── chunks/
│   │   ├── manipulate.json                    # Universal text transformation
│   │   ├── comfyui_image_generation.json      # Image generation
│   │   └── comfyui_audio_generation.json      # Audio/Music generation
│   │
│   ├── pipelines/
│   │   ├── text_transformation.json           # Text → Text (30 configs)
│   │   ├── single_text_media_generation.json      # Text → Media (SD3.5, Flux1, etc.)
│   │   ├── dual_text_media_generation.json        # 2 Texts → Music (AceStep)
│   │   └── image_text_media_generation.json    # Image+Text → Image (future)
│   │
│   ├── configs/
│   │   ├── dada.json                          # Text transformation configs
│   │   ├── bauhaus.json
│   │   ├── overdrive.json
│   │   ├── ...                                # (30 total)
│   │   ├── sd35_standard.json                 # Output generation configs
│   │   ├── flux1_dev.json
│   │   ├── acestep_standard.json
│   │   └── stableaudio.json
│   │
│   └── engine/
│       ├── config_loader.py                   # Load configs + pipelines
│       ├── chunk_builder.py                   # Build chunks
│       ├── pipeline_executor.py               # Execute pipelines
│       ├── backend_router.py                  # Route to backends
│       ├── model_selector.py                  # Task-based model selection
│       └── comfyui_workflow_generator.py      # DEPRECATED (workflows in chunks now)
│
├── my_app/
│   ├── routes/
│   │   ├── schema_pipeline_routes.py          # Main API endpoint (NEW)
│   │   ├── workflow_streaming_routes.py       # SSE streaming endpoints
│   │   ├── export_routes.py                   # Export management
│   │   ├── media_routes.py                    # Media file serving
│   │   └── workflow_routes.py.obsolete        # DEPRECATED (removed 2025-10-28)
│   ├── services/
│   │   ├── ollama_service.py                  # Ollama integration
│   │   ├── comfyui_service.py                 # ComfyUI integration
│   │   └── translator_service.py              # Pre-translation
│   └── utils/
│       └── helpers.py                         # Helper functions
│
├── docs/
│   ├── ARCHITECTURE.md                        # This file
│   ├── OUTPUT_PIPELINE_ARCHITECTURE.md        # Output pipeline design
│   ├── DEVELOPMENT_DECISIONS.md               # Decision log
│   ├── devserver_todos.md                     # Implementation TODOs
│   └── tmp/
│       ├── CHUNK_ANALYSIS.md                  # Chunk analysis
│       ├── PLACEHOLDER_ANALYSIS.md            # Placeholder analysis
│       └── PIPELINE_ANALYSIS.md               # Pipeline analysis
│
├── test_refactored_system.py                  # Architecture tests
├── test_pipeline_execution.py                 # Execution tests
└── config.py                                  # Server configuration
```

---

