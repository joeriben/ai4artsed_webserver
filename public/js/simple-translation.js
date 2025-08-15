// Simple translation module for static UI elements
// This module is completely independent from workflow.js

const translations = {
    de: {
        'execution-mode-label': 'Ausführungsmodus',
        'seed-control-label': 'Seed-Kontrolle',
        'safety-level-label': 'Sicherheitsstufe',
        'privacy-hint': 'Hinweis: Generierte Inhalte werden zu Forschungszwecken auf dem Server gespeichert. Es werden keine User- oder IP-Daten erfasst. Hochgeladene Bilder werden nicht gespeichert.',
        // Radio button labels
        'seed-random': 'Zufall',
        'seed-standard': '123456789',
        'seed-fixed': 'letzter Seed',
        'eco-mode': 'Eco (Lokal)',
        'fast-mode': 'Schnell (Cloud)',
        'safety-off': 'Aus',
        'safety-youth': 'Youth',
        'safety-kids': 'Kids',
        // Workflow selection texts
        'workflow-random-option': 'Zufallsauswahl oder WORKFLOW auswählen',
        'workflow-fixed-mode': 'Fixed Modus:',
        'workflow-fixed-description': 'Der Server verwendet automatisch diesen Workflow.',
        'workflow-fixed-label': 'Workflow (Fest konfiguriert)',
        'workflow-system-mode': 'System Modus:',
        'workflow-system-random': 'Zufallsauswahl',
        'workflow-system-description': 'Das System wählt zufällig einen Workflow aus den Kategorien:',
        'workflow-system-label': 'Workflow (Automatische Auswahl)'
    },
    en: {
        'execution-mode-label': 'Execution Mode',
        'seed-control-label': 'Seed Control',
        'safety-level-label': 'Safety Level',
        'privacy-hint': 'Note: Generated content is saved on the server for research purposes. No user or IP data is collected. Uploaded images are not saved.',
        // Radio button labels
        'seed-random': 'Random',
        'seed-standard': '123456789',
        'seed-fixed': 'last seed',
        'eco-mode': 'Eco (Local)',
        'fast-mode': 'Fast (Cloud)',
        'safety-off': 'Off',
        'safety-youth': 'Youth',
        'safety-kids': 'Kids',
        // Workflow selection texts
        'workflow-random-option': 'Random selection or choose WORKFLOW',
        'workflow-fixed-mode': 'Fixed Mode:',
        'workflow-fixed-description': 'The server automatically uses this workflow.',
        'workflow-fixed-label': 'Workflow (Fixed Configuration)',
        'workflow-system-mode': 'System Mode:',
        'workflow-system-random': 'Random Selection',
        'workflow-system-description': 'The system randomly selects a workflow from categories:',
        'workflow-system-label': 'Workflow (Automatic Selection)'
    }
};

let currentLanguage = 'de';

function updateTexts() {
    const trans = translations[currentLanguage];
    
    // Update the 4 static text elements
    const executionModeLabel = document.getElementById('execution-mode-label');
    if (executionModeLabel) {
        executionModeLabel.childNodes[0].textContent = trans['execution-mode-label'];
    }
    
    const seedControlLabel = document.getElementById('seed-control-label');
    if (seedControlLabel) {
        seedControlLabel.textContent = trans['seed-control-label'];
    }
    
    const safetyLevelLabel = document.getElementById('safety-level-label');
    if (safetyLevelLabel) {
        // Preserve the Safety+ indicator
        const safetyIndicator = document.getElementById('safety-plus-indicator');
        safetyLevelLabel.textContent = trans['safety-level-label'] + ' ';
        if (safetyIndicator) {
            safetyLevelLabel.appendChild(safetyIndicator);
        }
    }
    
    const privacyHint = document.getElementById('privacy-hint');
    if (privacyHint) {
        privacyHint.textContent = trans['privacy-hint'];
    }
    
    // Update radio button labels
    const radioLabels = [
        'seed-random', 'seed-standard', 'seed-fixed',
        'eco-mode', 'fast-mode',
        'safety-off', 'safety-youth', 'safety-kids'
    ];
    
    radioLabels.forEach(id => {
        const label = document.querySelector(`label[for="${id}"]`);
        if (label && trans[id]) {
            label.textContent = trans[id];
        }
    });
}

export function initSimpleTranslation() {
    // Check localStorage for saved language preference
    const savedLang = localStorage.getItem('selectedLanguage');
    if (savedLang && (savedLang === 'de' || savedLang === 'en')) {
        currentLanguage = savedLang;
    }
    
    // Update button states
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        if (btn.dataset.lang === currentLanguage) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Add click listeners to language buttons
    langButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const newLang = e.target.dataset.lang;
            if (newLang !== currentLanguage && (newLang === 'de' || newLang === 'en')) {
                currentLanguage = newLang;
                localStorage.setItem('selectedLanguage', newLang);
                
                // Update button states
                langButtons.forEach(b => {
                    if (b.dataset.lang === currentLanguage) {
                        b.classList.add('active');
                    } else {
                        b.classList.remove('active');
                    }
                });
                
                // Update texts
                updateTexts();
            }
        });
    });
    
    // Initial text update
    updateTexts();
}

// Export translation function for other modules
export function t(key) {
    return translations[currentLanguage]?.[key] || translations['de'][key] || key;
}

// Export current language getter
export function getCurrentLanguage() {
    return currentLanguage;
}
