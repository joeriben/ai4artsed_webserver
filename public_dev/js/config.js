// AI4ArtsEd - Configuration Module
export let config = {};

export async function loadConfig() {
    try {
        const response = await fetch('/config');
        if (!response.ok) throw new Error('Config fetch failed');
        config = await response.json();
        return config;
    } catch (error) {
        throw new Error('Konfiguration konnte nicht geladen werden: ' + error.message);
    }
}
