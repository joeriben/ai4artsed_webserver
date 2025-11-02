// AI4ArtsEd - Config Browser (NEW Schema-Pipeline Architecture)
// Simple card-based config selection

import { getCurrentLanguage } from './simple-translation.js';

let allConfigs = [];
let selectedConfigId = null;

/**
 * Initialize config browser
 */
export async function initConfigBrowser() {
    try {
        // Fetch all pipeline configs metadata
        const response = await fetch('/pipeline_configs_metadata');
        if (!response.ok) {
            throw new Error(`Failed to load configs: ${response.status}`);
        }

        const data = await response.json();
        allConfigs = data.configs || [];

        console.log(`[CONFIG-BROWSER] Loaded ${allConfigs.length} configs`);

        // Render the browser
        renderConfigBrowser();

    } catch (error) {
        console.error('[CONFIG-BROWSER] Failed to initialize:', error);
        throw error;
    }
}

/**
 * Render the config browser UI
 */
function renderConfigBrowser() {
    const container = document.getElementById('workflow-browser-container');
    if (!container) {
        console.error('[CONFIG-BROWSER] Container not found');
        return;
    }

    container.innerHTML = '';

    // Group configs by category
    const categories = groupByCategory(allConfigs);
    const lang = getCurrentLanguage();

    Object.entries(categories).sort((a, b) => a[0].localeCompare(b[0])).forEach(([categoryName, categoryConfigs]) => {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section';

        // Category header
        const header = document.createElement('h3');
        header.className = 'category-header';
        header.textContent = categoryName;
        categorySection.appendChild(header);

        // Config cards grid
        const grid = document.createElement('div');
        grid.className = 'config-grid';

        categoryConfigs.forEach(config => {
            const card = createConfigCard(config);
            grid.appendChild(card);
        });

        categorySection.appendChild(grid);
        container.appendChild(categorySection);
    });
}

/**
 * Group configs by category
 */
function groupByCategory(configs) {
    const lang = getCurrentLanguage();
    const categories = {};

    configs.forEach(config => {
        const categoryName = config.category?.[lang] || config.category?.en || 'Andere';

        if (!categories[categoryName]) {
            categories[categoryName] = [];
        }
        categories[categoryName].push(config);
    });

    return categories;
}

/**
 * Create a config card
 */
function createConfigCard(config) {
    const lang = getCurrentLanguage();
    const card = document.createElement('div');
    card.className = 'config-card';
    card.dataset.configId = config.id;

    // Apply color from config
    if (config.display?.color) {
        card.style.borderColor = config.display.color;
    }

    // Icon
    const icon = document.createElement('div');
    icon.className = 'config-icon';
    icon.textContent = config.display?.icon || '🎨';
    card.appendChild(icon);

    // Name
    const name = document.createElement('div');
    name.className = 'config-name';
    name.textContent = config.name?.[lang] || config.name?.en || config.id;
    card.appendChild(name);

    // Description
    const description = document.createElement('div');
    description.className = 'config-description';
    description.textContent = config.description?.[lang] || config.description?.en || '';
    card.appendChild(description);

    // Difficulty stars
    if (config.display?.difficulty) {
        const difficulty = document.createElement('div');
        difficulty.className = 'config-difficulty';
        difficulty.textContent = '⭐'.repeat(config.display.difficulty);
        card.appendChild(difficulty);
    }

    // Click handler
    card.addEventListener('click', () => selectConfig(config.id, card));

    return card;
}

/**
 * Select a config
 */
function selectConfig(configId, cardElement) {
    // Visual feedback
    document.querySelectorAll('.config-card').forEach(card => {
        card.classList.remove('selected');
    });
    cardElement.classList.add('selected');

    selectedConfigId = configId;

    console.log('[CONFIG-BROWSER] Config selected:', configId);

    // Store in hidden input for form submission
    const input = document.getElementById('selected-config');
    if (input) {
        input.value = configId;
    }
}

/**
 * Get currently selected config ID
 */
export function getSelectedConfigId() {
    return selectedConfigId;
}
