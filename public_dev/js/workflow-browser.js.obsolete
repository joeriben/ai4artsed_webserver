// AI4ArtsEd - Expert Mode Workflow Browser
// Visual card-based workflow selection with filtering and categorization

import { getCurrentLanguage } from './simple-translation.js';

let allConfigs = [];
let selectedConfigId = null;
let onSelectionCallback = null;

/**
 * Initialize Expert Mode workflow browser
 * @param {Function} onSelection - Callback when a workflow is selected
 */
export async function initWorkflowBrowser(onSelection) {
    onSelectionCallback = onSelection;

    try {
        // Fetch all pipeline configs metadata
        const response = await fetch('/pipeline_configs_metadata');
        if (!response.ok) {
            throw new Error(`Failed to load configs: ${response.status}`);
        }

        const data = await response.json();
        allConfigs = data.configs || [];

        console.log(`Loaded ${allConfigs.length} pipeline configs`);

        // Render the browser
        renderWorkflowBrowser();

    } catch (error) {
        console.error('Failed to initialize workflow browser:', error);
        throw error;
    }
}

/**
 * Render the complete workflow browser UI
 */
function renderWorkflowBrowser() {
    const container = document.getElementById('workflow-browser-container');
    if (!container) {
        console.error('workflow-browser-container not found');
        return;
    }

    // Clear existing content
    container.innerHTML = '';

    // Create browser structure
    const browser = document.createElement('div');
    browser.className = 'workflow-browser';

    // Add filter controls
    const filters = createFilterControls();
    browser.appendChild(filters);

    // Add categories section
    const categories = createCategoriesView(allConfigs);
    browser.appendChild(categories);

    container.appendChild(browser);
}

/**
 * Create filter controls UI
 */
function createFilterControls() {
    const filters = document.createElement('div');
    filters.className = 'workflow-filters';

    const lang = getCurrentLanguage();

    filters.innerHTML = `
        <div class="filter-group">
            <input type="text"
                   id="workflow-search"
                   class="workflow-search"
                   placeholder="${lang === 'de' ? 'Suche nach Namen oder Tags...' : 'Search by name or tags...'}">
        </div>
        <div class="filter-group">
            <label>${lang === 'de' ? 'Schwierigkeit:' : 'Difficulty:'}</label>
            <select id="difficulty-filter" class="filter-select">
                <option value="all">${lang === 'de' ? 'Alle' : 'All'}</option>
                <option value="1">⭐ ${lang === 'de' ? 'Anfänger' : 'Beginner'}</option>
                <option value="2">⭐⭐ ${lang === 'de' ? 'Einfach' : 'Easy'}</option>
                <option value="3">⭐⭐⭐ ${lang === 'de' ? 'Mittel' : 'Medium'}</option>
                <option value="4">⭐⭐⭐⭐ ${lang === 'de' ? 'Fortgeschritten' : 'Advanced'}</option>
                <option value="5">⭐⭐⭐⭐⭐ ${lang === 'de' ? 'Experte' : 'Expert'}</option>
            </select>
        </div>
        <div class="filter-group">
            <label>
                <input type="checkbox" id="workshop-filter">
                ${lang === 'de' ? 'Nur Workshop-geeignet' : 'Workshop-suitable only'}
            </label>
        </div>
    `;

    // Add event listeners
    filters.querySelector('#workflow-search').addEventListener('input', applyFilters);
    filters.querySelector('#difficulty-filter').addEventListener('change', applyFilters);
    filters.querySelector('#workshop-filter').addEventListener('change', applyFilters);

    return filters;
}

/**
 * Create categories view with config cards
 */
function createCategoriesView(configs) {
    const categoriesContainer = document.createElement('div');
    categoriesContainer.className = 'workflow-categories';
    categoriesContainer.id = 'workflow-categories';

    // Group configs by category
    const categories = groupByCategory(configs);
    const lang = getCurrentLanguage();

    // Render each category
    Object.entries(categories).sort((a, b) => a[0].localeCompare(b[0])).forEach(([categoryName, categoryConfigs]) => {
        const categorySection = document.createElement('div');
        categorySection.className = 'category-section';
        categorySection.dataset.category = categoryName;

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
        categoriesContainer.appendChild(categorySection);
    });

    return categoriesContainer;
}

/**
 * Group configs by category
 */
function groupByCategory(configs) {
    const lang = getCurrentLanguage();
    const categories = {};

    configs.forEach(config => {
        const categoryName = config.category?.[lang] || config.category?.en || 'Other';

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

    // Workshop badge
    if (config.audience?.workshop_suitable) {
        const badge = document.createElement('div');
        badge.className = 'config-badge workshop-badge';
        badge.textContent = lang === 'de' ? 'Workshop' : 'Workshop';
        badge.title = lang === 'de' ? 'Workshop-geeignet' : 'Workshop-suitable';
        card.appendChild(badge);
    }

    // Click handler
    card.addEventListener('click', () => selectConfig(config.id, card));

    return card;
}

/**
 * Select a config
 */
async function selectConfig(configId, cardElement) {
    // Visual feedback
    document.querySelectorAll('.config-card').forEach(card => {
        card.classList.remove('selected');
    });
    cardElement.classList.add('selected');

    selectedConfigId = configId;

    console.log('[WORKFLOW-BROWSER] Config selected:', configId);

    // Load full config details
    try {
        const response = await fetch(`/pipeline_config/${configId}`);
        if (!response.ok) {
            throw new Error(`Failed to load config: ${response.status}`);
        }

        const data = await response.json();
        const config = data.config;

        console.log('[WORKFLOW-BROWSER] Config loaded:', config);

        // Show config details in sidebar (if exists)
        showConfigDetails(config);

        // Notify callback with correct workflow path
        const workflowPath = `dev/${configId}`;
        console.log('[WORKFLOW-BROWSER] Calling callback with workflow path:', workflowPath);

        if (onSelectionCallback) {
            onSelectionCallback(workflowPath, config);
        }

    } catch (error) {
        console.error('Failed to load config details:', error);
    }
}

/**
 * Show config details in sidebar
 */
function showConfigDetails(config) {
    const sidebar = document.getElementById('workflow-details-sidebar');
    if (!sidebar) return;

    const lang = getCurrentLanguage();

    sidebar.innerHTML = `
        <div class="workflow-details">
            <div class="detail-icon">${config.display?.icon || '🎨'}</div>
            <h3>${config.name?.[lang] || config.name?.en || config.id}</h3>
            <p class="detail-description">${config.description?.[lang] || config.description?.en || ''}</p>

            <div class="detail-section">
                <h4>${lang === 'de' ? 'Kategorie' : 'Category'}</h4>
                <p>${config.category?.[lang] || config.category?.en || 'N/A'}</p>
            </div>

            <div class="detail-section">
                <h4>${lang === 'de' ? 'Schwierigkeit' : 'Difficulty'}</h4>
                <p>${'⭐'.repeat(config.display?.difficulty || 1)}</p>
            </div>

            ${config.audience?.min_age ? `
            <div class="detail-section">
                <h4>${lang === 'de' ? 'Mindestalter' : 'Minimum Age'}</h4>
                <p>${config.audience.min_age}+</p>
            </div>
            ` : ''}

            <div class="detail-section">
                <h4>${lang === 'de' ? 'Pipeline' : 'Pipeline'}</h4>
                <p><code>${config.pipeline}</code></p>
            </div>

            ${config.tags && (config.tags[lang]?.length > 0 || config.tags.en?.length > 0) ? `
            <div class="detail-section">
                <h4>${lang === 'de' ? 'Tags' : 'Tags'}</h4>
                <div class="detail-tags">
                    ${(config.tags[lang] || config.tags.en || []).map(tag =>
                        `<span class="tag">${tag}</span>`
                    ).join('')}
                </div>
            </div>
            ` : ''}
        </div>
    `;

    sidebar.style.display = 'block';
}

/**
 * Apply filters to config cards
 */
function applyFilters() {
    const searchTerm = document.getElementById('workflow-search')?.value.toLowerCase() || '';
    const difficultyFilter = document.getElementById('difficulty-filter')?.value || 'all';
    const workshopOnly = document.getElementById('workshop-filter')?.checked || false;

    const lang = getCurrentLanguage();
    let visibleCount = 0;
    const categoryVisibility = {};

    // Filter each card
    document.querySelectorAll('.config-card').forEach(card => {
        const configId = card.dataset.configId;
        const config = allConfigs.find(c => c.id === configId);

        if (!config) return;

        let visible = true;

        // Search filter
        if (searchTerm) {
            const name = (config.name?.[lang] || config.name?.en || '').toLowerCase();
            const tags = (config.tags?.[lang] || config.tags?.en || []).map(t => t.toLowerCase());
            const description = (config.description?.[lang] || config.description?.en || '').toLowerCase();

            visible = visible && (
                name.includes(searchTerm) ||
                tags.some(tag => tag.includes(searchTerm)) ||
                description.includes(searchTerm)
            );
        }

        // Difficulty filter
        if (difficultyFilter !== 'all') {
            visible = visible && (config.display?.difficulty === parseInt(difficultyFilter));
        }

        // Workshop filter
        if (workshopOnly) {
            visible = visible && config.audience?.workshop_suitable;
        }

        // Update visibility
        card.style.display = visible ? 'block' : 'none';

        if (visible) {
            visibleCount++;
            const categoryName = config.category?.[lang] || config.category?.en || 'Other';
            categoryVisibility[categoryName] = true;
        }
    });

    // Hide empty categories
    document.querySelectorAll('.category-section').forEach(section => {
        const categoryName = section.querySelector('.category-header')?.textContent;
        section.style.display = categoryVisibility[categoryName] ? 'block' : 'none';
    });

    console.log(`Filters applied: ${visibleCount} configs visible`);
}

/**
 * Get currently selected config ID
 */
export function getSelectedConfig() {
    return selectedConfigId;
}

/**
 * Reset browser (clear selection, reset filters)
 */
export function resetBrowser() {
    selectedConfigId = null;
    document.querySelectorAll('.config-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Reset filters
    const searchInput = document.getElementById('workflow-search');
    if (searchInput) searchInput.value = '';

    const difficultySelect = document.getElementById('difficulty-filter');
    if (difficultySelect) difficultySelect.value = 'all';

    const workshopCheckbox = document.getElementById('workshop-filter');
    if (workshopCheckbox) workshopCheckbox.checked = false;

    applyFilters();
}
