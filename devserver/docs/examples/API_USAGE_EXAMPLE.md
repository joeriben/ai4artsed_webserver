# Pipeline Config Metadata API - Usage Examples

## Overview

The metadata API provides two endpoints for the Expert Mode workflow selection UI:

1. `/pipeline_configs_metadata` - Get metadata for all configs
2. `/pipeline_config/<config_name>` - Get detailed info for a specific config

**Important**: These endpoints read data **directly from config files** - no data duplication or central registry.

## Endpoint 1: Get All Configs Metadata

### Request
```http
GET /pipeline_configs_metadata
```

### Response
```json
{
  "configs": [
    {
      "id": "jugendsprache",
      "name": {
        "en": "UK Youth Slang",
        "de": "UK-Jugendsprache"
      },
      "description": {
        "en": "Transform text into contemporary UK youth slang",
        "de": "Transformiert Text in zeitgenössische UK-Jugendsprache"
      },
      "category": {
        "en": "Language Transformations",
        "de": "Sprachtransformationen"
      },
      "pipeline": "simple_manipulation",
      "instruction_type": "manipulation.creative",
      "display": {
        "icon": "🗣️",
        "color": "#FF9800",
        "category": "language",
        "difficulty": 2,
        "order": 10
      },
      "tags": {
        "en": ["language", "youth", "slang", "uk"],
        "de": ["sprache", "jugend", "slang", "uk"]
      },
      "audience": {
        "workshop_suitable": true,
        "min_age": 12,
        "complexity": "intermediate"
      },
      "media_preferences": {
        "default_output": "image",
        "supported_types": ["image"]
      }
    },
    // ... 33 more configs
  ],
  "count": 34
}
```

## Endpoint 2: Get Single Config Detail

### Request
```http
GET /pipeline_config/jugendsprache
```

### Response
```json
{
  "success": true,
  "config": {
    "pipeline": "simple_manipulation",
    "name": {
      "en": "UK Youth Slang",
      "de": "UK-Jugendsprache"
    },
    "description": {
      "en": "Transform text into contemporary UK youth slang",
      "de": "Transformiert Text in zeitgenössische UK-Jugendsprache"
    },
    "category": {
      "en": "Language Transformations",
      "de": "Sprachtransformationen"
    },
    "instruction_type": "manipulation.creative",
    "context": "You are a contemporary UK youth... [full context string]",
    "parameters": {
      "temperature": 0.7,
      "top_p": 0.9,
      "max_tokens": 2048
    },
    "media_preferences": {
      "default_output": "image",
      "supported_types": ["image"]
    },
    "meta": {
      "legacy_source": "workflows/language/ai4artsed_jugendsprache_2509251702.json",
      "extracted_date": "2025-10-19",
      "original_model": "local/mistral:7b"
    },
    "display": {
      "icon": "🗣️",
      "color": "#FF9800",
      "category": "language",
      "difficulty": 2,
      "order": 10
    },
    "tags": {
      "en": ["language", "youth", "slang", "uk"],
      "de": ["sprache", "jugend", "slang", "uk"]
    },
    "audience": {
      "workshop_suitable": true,
      "min_age": 12,
      "complexity": "intermediate"
    }
  }
}
```

## Frontend Implementation Example

### Expert Mode: Enhanced Workflow Browser

```javascript
// 1. Load all configs on page load
async function loadWorkflowBrowser() {
  const response = await fetch('/pipeline_configs_metadata');
  const data = await response.json();

  // Group configs by category
  const categories = {};
  data.configs.forEach(config => {
    const category = config.category.en;
    if (!categories[category]) {
      categories[category] = [];
    }
    categories[category].push(config);
  });

  // Render categorized grid
  renderCategories(categories);
}

// 2. Render configs as visual cards
function renderCategories(categories) {
  const container = document.getElementById('workflow-browser');

  Object.entries(categories).forEach(([category, configs]) => {
    const categorySection = document.createElement('div');
    categorySection.className = 'category-section';

    // Category header
    const header = document.createElement('h3');
    header.textContent = category;
    categorySection.appendChild(header);

    // Config cards
    const grid = document.createElement('div');
    grid.className = 'config-grid';

    configs.forEach(config => {
      const card = createConfigCard(config);
      grid.appendChild(card);
    });

    categorySection.appendChild(grid);
    container.appendChild(categorySection);
  });
}

// 3. Create visual card for each config
function createConfigCard(config) {
  const card = document.createElement('div');
  card.className = 'config-card';
  card.style.borderColor = config.display.color;

  // Icon and name
  card.innerHTML = `
    <div class="config-icon">${config.display.icon}</div>
    <div class="config-name">${config.name.en}</div>
    <div class="config-description">${config.description.en}</div>
    <div class="config-difficulty">
      ${'⭐'.repeat(config.display.difficulty)}
    </div>
  `;

  // Click handler: select config
  card.addEventListener('click', () => selectConfig(config.id));

  return card;
}

// 4. Load detailed config on selection
async function selectConfig(configId) {
  const response = await fetch(`/pipeline_config/${configId}`);
  const data = await response.json();

  if (data.success) {
    // Show config details in sidebar
    showConfigDetails(data.config);

    // Update selected workflow for execution
    selectedWorkflow = `dev/${configId}`;
  }
}

// 5. Execute workflow
async function executeWorkflow(prompt) {
  const response = await fetch('/run_workflow', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      workflow: selectedWorkflow,  // e.g., "dev/jugendsprache"
      prompt: prompt,
      mode: 'eco'  // or 'fast'
    })
  });

  const result = await response.json();
  // Handle result...
}
```

### CSS Example

```css
.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.config-card {
  border: 2px solid;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.config-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.config-icon {
  font-size: 3rem;
  text-align: center;
  margin-bottom: 0.5rem;
}

.config-name {
  font-weight: bold;
  margin-bottom: 0.5rem;
}

.config-description {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.config-difficulty {
  font-size: 0.8rem;
}
```

## Filtering and Sorting Examples

### Filter by category
```javascript
function filterByCategory(configs, category) {
  return configs.filter(c => c.category.en === category);
}
```

### Filter by difficulty
```javascript
function filterByDifficulty(configs, maxDifficulty) {
  return configs.filter(c => c.display.difficulty <= maxDifficulty);
}
```

### Filter by audience (workshop-suitable)
```javascript
function filterWorkshopSuitable(configs) {
  return configs.filter(c => c.audience.workshop_suitable);
}
```

### Filter by age
```javascript
function filterByAge(configs, userAge) {
  return configs.filter(c => userAge >= c.audience.min_age);
}
```

### Sort by difficulty
```javascript
function sortByDifficulty(configs) {
  return configs.sort((a, b) =>
    a.display.difficulty - b.display.difficulty
  );
}
```

### Search by name or tags
```javascript
function searchConfigs(configs, query, language = 'en') {
  query = query.toLowerCase();
  return configs.filter(c => {
    const name = c.name[language].toLowerCase();
    const tags = c.tags[language] || [];
    return name.includes(query) ||
           tags.some(tag => tag.includes(query));
  });
}
```

## Available Categories

The current configs cover these categories (as of 2025-10-26):

- **Language Transformations** (jugendsprache, piglatin, stillepost, theopposite)
- **Art Movements** (dada)
- **Arts And Heritage** (bauhaus, confucianliterati, expressionism, renaissance, technicaldrawing, yorubaheritage)
- **Aesthetics** (clichéfilter_v1, v2, v3, hunkydoryharmonizer, junkyard, merzscapes)
- **Sound** (acestep_simple, acestep_longnarrativeprompts, acestep_mixedprompts, acestep_shortprompts)
- **Model** ((((promptinterception))), llm-comparison variants, model-comparison)
- **Across** (imageandsound, imagetosound)
- **Llm** (ethicaladvisor)
- **Semantics** (piglatin, stillepost, theopposite)
- **Aesthetic Transformations** (overdrive)
- **Science** (quantumtheory)

## No Data Duplication

These endpoints read **directly from config JSON files** at request time. There is:
- ❌ No central registry
- ❌ No hardcoded defaults
- ❌ No duplicate metadata
- ✅ Single source of truth: config files
- ✅ Changes to config files are immediately reflected in API

If you need to update metadata, edit the config file directly:
```bash
# Example: Update icon for jugendsprache
vim schemas/configs_new/jugendsprache.json
```
