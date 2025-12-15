const API_BASE = '/api/lora';

const elements = {
    projectName: document.getElementById('projectName'),
    triggerToken: document.getElementById('triggerToken'),
    baseModel: document.getElementById('baseModel'),
    datasetSelect: document.getElementById('datasetSelect'),
    refreshDatasets: document.getElementById('refreshDatasets'),
    datasetSummary: document.getElementById('datasetSummary'),
    datasetName: document.getElementById('datasetName'),
    datasetFile: document.getElementById('datasetFile'),
    uploadDataset: document.getElementById('uploadDataset'),
    datasetUploadStatus: document.getElementById('datasetUploadStatus'),
    resolution: document.getElementById('resolution'),
    maxSteps: document.getElementById('maxSteps'),
    batchSize: document.getElementById('batchSize'),
    gradAccum: document.getElementById('gradAccum'),
    learningRate: document.getElementById('learningRate'),
    presetProfiles: document.getElementById('presetProfiles'),
    presetHelp: document.getElementById('presetHelp'),
    scheduler: document.getElementById('scheduler'),
    rank: document.getElementById('rank'),
    alpha: document.getElementById('alpha'),
    seed: document.getElementById('seed'),
    mixedPrecision: document.getElementById('mixedPrecision'),
    trainTextEncoder: document.getElementById('trainTextEncoder'),
    use8bitAdam: document.getElementById('use8bitAdam'),
    validationPrompt: document.getElementById('validationPrompt'),
    commandPreview: document.getElementById('commandPreview'),
    copyCommand: document.getElementById('copyCommand'),
    createJob: document.getElementById('createJob'),
    jobStatus: document.getElementById('jobStatus'),
    jobsTable: document.getElementById('jobsTable'),
};

const numberFormatter = new Intl.NumberFormat('de-DE');
const dateFormatter = new Intl.DateTimeFormat('de-DE', {
    dateStyle: 'medium',
    timeStyle: 'short',
});

async function fetchJson(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
        const text = await response.text();
        throw new Error(text || `Request failed with status ${response.status}`);
    }
    return response.json();
}

function escapeQuotes(value) {
    return String(value ?? '').replace(/"/g, '\\"');
}

function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>"']/g, (match) => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
    }[match]));
}

function buildCommand(config) {
    const parts = [
        'accelerate launch training/train_text_to_image_lora.py',
        `  --pretrained_model_name_or_path="${escapeQuotes(config.baseModel)}"`,
        `  --train_data_dir="${escapeQuotes(config.datasetPath)}"`,
        `  --resolution=${config.resolution}`,
        `  --train_batch_size=${config.batchSize}`,
        `  --gradient_accumulation_steps=${config.gradAccum}`,
        `  --learning_rate=${config.learningRate}`,
        `  --lr_scheduler="${escapeQuotes(config.scheduler)}"`,
        `  --max_train_steps=${config.maxSteps}`,
        `  --output_dir="${escapeQuotes(config.outputDir)}"`,
        `  --rank=${config.rank}`,
        `  --network_alpha=${config.alpha}`,
        `  --mixed_precision=${config.mixedPrecision}`,
        `  --seed=${config.seed}`,
    ];

    if (config.trainTextEncoder) {
        parts.push('  --train_text_encoder');
    }
    if (config.use8bitAdam) {
        parts.push('  --use_8bit_adam');
    }
    if (config.validationPrompt) {
        parts.push(`  --validation_prompt="${escapeQuotes(config.validationPrompt)}"`);
    }

    return parts.join(' \\\n');
}

class LoraUI {
    constructor() {
        this.state = {
            presets: null,
            datasets: [],
            jobs: [],
            command: '',
            selectedPresetId: null,
        };
    }

    async init() {
        try {
            await Promise.all([
                this.loadPresets(),
                this.loadDatasets(),
                this.loadJobs(),
            ]);
            this.registerEvents();
            this.updateCommandPreview();
        } catch (error) {
            console.error(error);
            this.showStatus(`Fehler beim Initialisieren: ${error.message}`, 'error');
        }
    }

    registerEvents() {
        const inputs = [
            elements.projectName,
            elements.triggerToken,
            elements.baseModel,
            elements.datasetSelect,
            elements.resolution,
            elements.maxSteps,
            elements.batchSize,
            elements.gradAccum,
            elements.learningRate,
            elements.scheduler,
            elements.rank,
            elements.alpha,
            elements.seed,
            elements.mixedPrecision,
            elements.validationPrompt,
        ];

        inputs.forEach((input) => {
            if (input) {
                input.addEventListener('input', () => this.updateCommandPreview());
                input.addEventListener('change', () => this.updateCommandPreview());
            }
        });

        elements.trainTextEncoder.addEventListener('change', () => this.updateCommandPreview());
        elements.use8bitAdam.addEventListener('change', () => this.updateCommandPreview());
        if (elements.presetProfiles) {
            elements.presetProfiles.addEventListener('click', (event) => {
                const card = event.target.closest('[data-preset-id]');
                if (card) {
                    this.applyPresetById(card.getAttribute('data-preset-id'));
                }
            });
        }
        elements.datasetSelect.addEventListener('change', () => this.updateDatasetSummary());
        elements.refreshDatasets.addEventListener('click', () => this.loadDatasets());
        elements.uploadDataset.addEventListener('click', () => this.uploadDataset());
        elements.createJob.addEventListener('click', () => this.createJob());
        elements.copyCommand.addEventListener('click', () => this.copyCurrentCommand());
        elements.jobsTable.addEventListener('click', (event) => {
            const target = event.target.closest('[data-command]');
            if (target) {
                const encoded = target.getAttribute('data-command');
                const command = encoded ? decodeURIComponent(encoded) : '';
                navigator.clipboard.writeText(command)
                    .then(() => this.showStatus('Befehl kopiert.', 'success'))
                    .catch((err) => this.showStatus(`Kopieren fehlgeschlagen: ${err.message}`, 'error'));
            }
        });
    }

    async loadPresets() {
        const presets = await fetchJson(`${API_BASE}/presets`);
        this.state.presets = presets;

        elements.baseModel.innerHTML = presets.base_models
            .map((model) => `<option value="${model.id}">${model.label}</option>`)
            .join('');

        elements.scheduler.innerHTML = presets.schedulers
            .map((scheduler) => `<option value="${scheduler}">${scheduler}</option>`)
            .join('');

        this.renderPresets();
        this.applyInitialDefaults();
    }

    renderPresets() {
        if (!elements.presetProfiles) {
            return;
        }

        const profiles = (this.state.presets && this.state.presets.profiles) || [];
        if (!profiles.length) {
            elements.presetProfiles.innerHTML = '';
            elements.presetProfiles.classList.add('is-empty');
            this.showPresetHelp();
            return;
        }

        elements.presetProfiles.classList.remove('is-empty');
        const cards = profiles
            .map((preset) => {
                const notes = Array.isArray(preset.notes) ? preset.notes : [];
                const noteItems = notes
                    .map((note) => `<li>${escapeHtml(note)}</li>`)
                    .join('');
                const noteList = noteItems ? `<ul>${noteItems}</ul>` : '';
                const datasetSize = preset.recommended_dataset_size
                    ? `<p class="preset-range">${escapeHtml(preset.recommended_dataset_size)}</p>`
                    : '';
                return `
                    <article class="preset-card" data-preset-id="${escapeHtml(preset.id)}">
                        <header>
                            <h3>${escapeHtml(preset.label)}</h3>
                            ${datasetSize}
                        </header>
                        <p>${escapeHtml(preset.description)}</p>
                        ${noteList}
                    </article>
                `;
            })
            .join('');

        elements.presetProfiles.innerHTML = cards;
        this.highlightSelectedPreset();
        this.showPresetHelp();
    }

    applyInitialDefaults() {
        const presets = this.state.presets || {};
        const defaultProfileId = presets.defaults && presets.defaults.profile_id;
        if (defaultProfileId && this.applyPresetById(defaultProfileId)) {
            return;
        }
        const baseDefaults = { ...(presets.defaults || {}) };
        delete baseDefaults.profile_id;
        this.applyFormDefaults(baseDefaults);
        this.updateCommandPreview();
    }

    applyPresetById(presetId) {
        if (!presetId || !this.state.presets || !Array.isArray(this.state.presets.profiles)) {
            return false;
        }
        const preset = this.state.presets.profiles.find((profile) => profile.id === presetId);
        if (!preset) {
            return false;
        }
        const baseDefaults = { ...(this.state.presets.defaults || {}) };
        delete baseDefaults.profile_id;
        const mergedDefaults = { ...baseDefaults, ...(preset.defaults || {}) };
        this.applyFormDefaults(mergedDefaults);
        this.state.selectedPresetId = preset.id;
        this.highlightSelectedPreset();
        this.showPresetHelp(preset);
        this.updateCommandPreview();
        return true;
    }

    applyFormDefaults(defaults = {}) {
        const mapping = {
            resolution: elements.resolution,
            max_train_steps: elements.maxSteps,
            train_batch_size: elements.batchSize,
            gradient_accumulation_steps: elements.gradAccum,
            learning_rate: elements.learningRate,
            scheduler: elements.scheduler,
            network_rank: elements.rank,
            network_alpha: elements.alpha,
            mixed_precision: elements.mixedPrecision,
            seed: elements.seed,
        };

        Object.entries(mapping).forEach(([key, element]) => {
            if (!element || !(key in defaults)) {
                return;
            }
            element.value = defaults[key];
        });

        if ('train_text_encoder' in defaults) {
            elements.trainTextEncoder.checked = Boolean(defaults.train_text_encoder);
        }
        if ('use_8bit_adam' in defaults) {
            elements.use8bitAdam.checked = Boolean(defaults.use_8bit_adam);
        }
    }

    highlightSelectedPreset() {
        if (!elements.presetProfiles) {
            return;
        }
        const cards = elements.presetProfiles.querySelectorAll('[data-preset-id]');
        cards.forEach((card) => {
            const isSelected = card.getAttribute('data-preset-id') === this.state.selectedPresetId;
            card.classList.toggle('is-active', isSelected);
        });
    }

    showPresetHelp(preset = null) {
        if (!elements.presetHelp) {
            return;
        }
        if (!preset) {
            if (this.state.selectedPresetId) {
                preset = (this.state.presets?.profiles || []).find(
                    (profile) => profile.id === this.state.selectedPresetId,
                );
            }
        }

        if (!preset) {
            elements.presetHelp.textContent =
                'Tipp: Wähle eine Voreinstellung, um bewährte Parameter für Foto- und Kunstdatensätze zu laden.';
            return;
        }

        const datasetSize = preset.recommended_dataset_size
            ? ` • ${preset.recommended_dataset_size}`
            : '';
        elements.presetHelp.textContent = `${preset.label}${datasetSize}: ${preset.description}`;
    }

    async loadDatasets(clearStatus = true) {
        try {
            const response = await fetchJson(`${API_BASE}/datasets`);
            this.state.datasets = response.datasets || [];
            this.renderDatasetOptions();
            this.updateDatasetSummary();
            this.updateCommandPreview();
            if (clearStatus) {
                this.showDatasetUploadStatus('', null);
            }
        } catch (error) {
            this.showDatasetUploadStatus(`Fehler beim Laden: ${error.message}`, 'error');
        }
    }

    renderDatasetOptions() {
        const previous = elements.datasetSelect.value;
        if (!this.state.datasets.length) {
            elements.datasetSelect.innerHTML = '<option value="">Kein Datensatz gefunden</option>';
            return;
        }

        const options = this.state.datasets.map((dataset) => `
            <option value="${dataset.id}">${dataset.id} (${dataset.image_count} Dateien)</option>
        `);
        elements.datasetSelect.innerHTML = options.join('');

        const stillExists = this.state.datasets.some((dataset) => dataset.id === previous);
        if (stillExists) {
            elements.datasetSelect.value = previous;
        } else {
            elements.datasetSelect.selectedIndex = 0;
        }
    }

    updateDatasetSummary() {
        const selectedId = elements.datasetSelect.value;
        const dataset = this.state.datasets.find((item) => item.id === selectedId);
        if (!dataset) {
            elements.datasetSummary.textContent = 'Bitte Datensatz auswählen oder hochladen.';
            return;
        }
        const metadataInfo = dataset.has_metadata ? 'metadata.jsonl ✓' : 'metadata.jsonl fehlt';
        const imageInfo = dataset.image_count ? `${numberFormatter.format(dataset.image_count)} Dateien` : 'keine Bilder gezählt';
        elements.datasetSummary.textContent = `${imageInfo} • ${metadataInfo}`;
    }

    async uploadDataset() {
        if (!elements.datasetFile.files.length) {
            this.showDatasetUploadStatus('Bitte ZIP-Datei auswählen.', 'error');
            return;
        }

        const name = (elements.datasetName.value || elements.datasetFile.files[0].name.replace(/\.zip$/i, '')).trim();
        if (!name) {
            this.showDatasetUploadStatus('Bitte einen Datensatz-Namen angeben.', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('dataset', elements.datasetFile.files[0]);
        formData.append('dataset_name', name);

        this.toggleUploadButton(true);
        this.showDatasetUploadStatus('Upload läuft…', null);
        try {
            const response = await fetch(`${API_BASE}/datasets`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) {
                const text = await response.text();
                throw new Error(text || 'Upload fehlgeschlagen');
            }
            const data = await response.json();
            this.showDatasetUploadStatus(`Datensatz "${data.dataset.id}" gespeichert.`, 'success');
            elements.datasetFile.value = '';
            elements.datasetName.value = '';
            await this.loadDatasets(false);
            elements.datasetSelect.value = data.dataset.id;
            this.updateDatasetSummary();
            this.updateCommandPreview();
        } catch (error) {
            this.showDatasetUploadStatus(error.message, 'error');
        } finally {
            this.toggleUploadButton(false);
        }
    }

    toggleUploadButton(disabled) {
        elements.uploadDataset.disabled = disabled;
        elements.uploadDataset.textContent = disabled ? 'Upload…' : 'Upload starten';
    }

    showDatasetUploadStatus(message, type) {
        elements.datasetUploadStatus.textContent = message;
        elements.datasetUploadStatus.classList.remove('status-error', 'status-success');
        if (type === 'error') {
            elements.datasetUploadStatus.classList.add('status-error');
        } else if (type === 'success') {
            elements.datasetUploadStatus.classList.add('status-success');
        }
    }

    updateCommandPreview() {
        const datasetId = elements.datasetSelect.value;
        const dataset = this.state.datasets.find((item) => item.id === datasetId);
        const baseModel = elements.baseModel.value;
        const project = elements.projectName.value.trim();
        const projectSlug = project
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, '_')
            .replace(/^_+|_+$/g, '');

        if (!dataset || !baseModel || !project || !projectSlug) {
            elements.commandPreview.textContent = 'Bitte Projektname, Basis-Modell und Datensatz auswählen.';
            this.state.command = '';
            return;
        }

        const config = {
            baseModel,
            datasetPath: dataset.path,
            resolution: Number(elements.resolution.value),
            maxSteps: Number(elements.maxSteps.value),
            batchSize: Number(elements.batchSize.value),
            gradAccum: Number(elements.gradAccum.value),
            learningRate: Number(elements.learningRate.value),
            scheduler: elements.scheduler.value,
            rank: Number(elements.rank.value),
            alpha: Number(elements.alpha.value),
            mixedPrecision: elements.mixedPrecision.value,
            seed: Number(elements.seed.value),
            trainTextEncoder: elements.trainTextEncoder.checked,
            use8bitAdam: elements.use8bitAdam.checked,
            validationPrompt: elements.validationPrompt.value.trim(),
            outputDir: `/workspace/ai4artsed_webserver/lora/outputs/${projectSlug}`,
        };

        const command = buildCommand(config);
        this.state.command = command;
        elements.commandPreview.textContent = command;
    }

    async createJob() {
        if (!this.state.command) {
            this.showStatus('Bitte erst alle Pflichtfelder ausfüllen.', 'error');
            return;
        }

        const datasetId = elements.datasetSelect.value;
        const payload = {
            project_name: elements.projectName.value.trim(),
            base_model: elements.baseModel.value,
            dataset_id: datasetId,
            resolution: Number(elements.resolution.value),
            max_train_steps: Number(elements.maxSteps.value),
            train_batch_size: Number(elements.batchSize.value),
            gradient_accumulation_steps: Number(elements.gradAccum.value),
            learning_rate: Number(elements.learningRate.value),
            scheduler: elements.scheduler.value,
            network_rank: Number(elements.rank.value),
            network_alpha: Number(elements.alpha.value),
            mixed_precision: elements.mixedPrecision.value,
            seed: Number(elements.seed.value),
            train_text_encoder: elements.trainTextEncoder.checked,
            use_8bit_adam: elements.use8bitAdam.checked,
            validation_prompt: elements.validationPrompt.value.trim(),
            instance_token: elements.triggerToken.value.trim(),
        };

        try {
            const response = await fetchJson(`${API_BASE}/jobs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });
            this.showStatus(`Job "${response.job.display_name}" gespeichert.`, 'success');
            await this.loadJobs();
        } catch (error) {
            this.showStatus(`Job konnte nicht angelegt werden: ${error.message}`, 'error');
        }
    }

    async loadJobs() {
        try {
            const response = await fetchJson(`${API_BASE}/jobs`);
            this.state.jobs = response.jobs || [];
            this.renderJobs();
        } catch (error) {
            this.showStatus(`Jobs konnten nicht geladen werden: ${error.message}`, 'error');
        }
    }

    renderJobs() {
        const tbody = elements.jobsTable.querySelector('tbody');
        tbody.innerHTML = '';

        if (!this.state.jobs.length) {
            const row = document.createElement('tr');
            const cell = document.createElement('td');
            cell.colSpan = 7;
            cell.textContent = 'Noch keine Trainingsjobs gespeichert.';
            row.appendChild(cell);
            tbody.appendChild(row);
            return;
        }

        this.state.jobs.forEach((job) => {
            const row = document.createElement('tr');

            const tokenTag = job.instance_token ? `<span class="tag">${job.instance_token}</span>` : '';

            const parameterTags = `
                <span class="tag">${job.resolution}px</span>
                <span class="tag">${job.max_train_steps} Steps</span>
                <span class="tag">bs ${job.train_batch_size} × ${job.gradient_accumulation_steps}</span>
                <span class="tag">rank ${job.network_rank}</span>
                <span class="tag">α ${job.network_alpha}</span>
                <span class="tag">lr ${job.learning_rate}</span>
                <span class="tag">${job.scheduler}</span>
            `;

            row.innerHTML = `
                <td>
                    <strong>${job.display_name}</strong><br>
                    <span class="hint">${job.project_name}</span>
                </td>
                <td>${job.base_model}</td>
                <td><code>${job.dataset?.id || ''}</code></td>
                <td>${parameterTags} ${tokenTag}</td>
                <td><span class="tag">${job.status}</span></td>
                <td>${job.created_at ? dateFormatter.format(new Date(job.created_at)) : '-'}</td>
                <td><button class="button-secondary" data-command="${encodeURIComponent(job.command)}">Kopieren</button></td>
            `;

            tbody.appendChild(row);
        });
    }

    copyCurrentCommand() {
        if (!this.state.command) {
            this.showStatus('Kein Befehl verfügbar.', 'error');
            return;
        }
        navigator.clipboard.writeText(this.state.command)
            .then(() => this.showStatus('Befehl kopiert.', 'success'))
            .catch((error) => this.showStatus(`Kopieren fehlgeschlagen: ${error.message}`, 'error'));
    }

    showStatus(message, type) {
        elements.jobStatus.textContent = message;
        elements.jobStatus.classList.remove('status-error', 'status-success');
        if (type === 'error') {
            elements.jobStatus.classList.add('status-error');
        } else if (type === 'success') {
            elements.jobStatus.classList.add('status-success');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const ui = new LoraUI();
    ui.init();
});
