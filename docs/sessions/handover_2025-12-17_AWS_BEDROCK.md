# Session Handover: AWS Bedrock Integration (2025-12-17)

## Kontext

User hat Settings-Page mit Anthropic API Key konfiguriert, aber Backend versuchte weiterhin über OpenRouter zu routen (hardcodierte `openrouter/` Präfixe).

## Was implementiert wurde

### 1. Multi-Provider LLM Support

**Neue Provider-Präfixe:**
- `local/model` → Ollama (local inference)
- `bedrock/model` → AWS Bedrock (Anthropic via AWS EU)
- `anthropic/model` → Anthropic Direct API
- `openai/model` → OpenAI Direct API
- `openrouter/provider/model` → OpenRouter Aggregator

**Geänderte Dateien:**
- `devserver/schemas/engine/backend_router.py`
  - BackendType Enum erweitert: ANTHROPIC, OPENAI, AWS_BEDROCK
  - `_detect_backend_from_model()` erkennt alle Präfixe

- `devserver/schemas/engine/prompt_interception_engine.py`
  - `_call_anthropic()` - Direct Anthropic API
  - `_call_openai()` - Direct OpenAI API
  - `_call_aws_bedrock()` - AWS Bedrock via boto3
  - `_get_api_credentials()` - Unified credential loading

- `devserver/schemas/engine/model_selector.py`
  - `strip_prefix()` und `extract_model_name()` für alle Präfixe

- `devserver/my_app/routes/chat_routes.py`
  - Prefix-Handling erweitert

### 2. AWS Bedrock Integration

**Implementation:**
```python
bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="eu-central-1"
)

response = bedrock.invoke_model(
    modelId="eu.anthropic.claude-sonnet-4-5-20250929-v1:0",
    body=json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": prompt}]
    })
)
```

**Credentials:** boto3 nutzt ENV Variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)

**Model-IDs (exakt):**
- Haiku: `bedrock/eu.anthropic.claude-3-5-haiku-20241022-v2:0`
- Sonnet: `bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Opus: `bedrock/eu.anthropic.claude-opus-4-5-20251101-v2:0`

### 3. Settings Page Updates

**Frontend (SettingsView.vue):**
- Provider-Dropdown erweitert: bedrock, anthropic, openai, openrouter
- Hardware Quick-Fill: 3 Tiers (dsgvo_local, dsgvo_cloud, non_dsgvo)
- AWS CSV Upload-Feld
- Obsolete Warnungen entfernt
- Veraltete Modellnamen entfernt (3.5 → 4.5)

**Backend (settings_routes.py):**
- HARDWARE_MATRIX komplett neu: 3 Tiers für alle VRAM-Größen
- POST /api/settings/aws-credentials - CSV Upload Endpoint
- AWS_CREDENTIALS_FILE Path definiert

### 4. Configuration

**config.py:**
```python
REMOTE_FAST_MODEL = "bedrock/eu.anthropic.claude-3-5-haiku-20241022-v2:0"
REMOTE_ADVANCED_MODEL = "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"
REMOTE_EXTREME_MODEL = "bedrock/eu.anthropic.claude-opus-4-5-20251101-v2:0"
```

## 🔴 OFFENES PROBLEM

### Symptom:
```
[BACKEND] ☁️  AWS Bedrock Request: eu.anthropic.claude-sonnet-4-5-20250929-v1:0
ERROR: Unable to locate credentials
```

### Status:
- ✅ Server wurde neu gestartet
- ✅ ENV Variables sind in setup_aws_env.sh gesetzt
- ✅ CSV wurde erfolgreich hochgeladen
- ❌ boto3 findet trotzdem keine Credentials

### Mögliche Ursachen:

1. **ENV Variables nicht im Server-Prozess**
   - Server wurde gestartet OHNE `source setup_aws_env.sh`
   - ENV nur im Shell gesetzt, nicht im Python-Prozess

2. **boto3 nicht installiert**
   - Check: `pip list | grep boto3`

3. **Code-Fehler in _call_aws_bedrock()**
   - boto3.client() wird falsch aufgerufen

4. **Permissions-Problem**
   - AWS IAM User hat keine bedrock:InvokeModel Permission

### Debug-Schritte:

```python
# In _call_aws_bedrock() logging hinzufügen:
import os
logger.info(f"ENV Check: AWS_ACCESS_KEY_ID={os.environ.get('AWS_ACCESS_KEY_ID', 'NOT SET')[:8]}...")
logger.info(f"ENV Check: AWS_SECRET_ACCESS_KEY={'SET' if os.environ.get('AWS_SECRET_ACCESS_KEY') else 'NOT SET'}")
logger.info(f"ENV Check: AWS_DEFAULT_REGION={os.environ.get('AWS_DEFAULT_REGION', 'NOT SET')}")
```

## 🚨 KRITISCHES SECURITY-PROBLEM

**FEHLER in letztem Commit:**
AWS Credentials werden in `aws_credentials.json` gespeichert!

**MUSS SOFORT GEFIXT WERDEN:**
1. aws_credentials.json zu .gitignore hinzufügen
2. Datei löschen
3. Alternative Lösung finden (siehe unten)

## Alternativen für CSV-Upload ohne File-Storage

### Option A: In-Memory Storage (Session-basiert)
```python
# Global variable in settings_routes.py
_aws_credentials_cache = None

@settings_bp.route('/aws-credentials', methods=['POST'])
def upload_aws_credentials():
    global _aws_credentials_cache
    # Parse CSV
    _aws_credentials_cache = {
        'access_key_id': ...,
        'secret_access_key': ...,
        'region': 'eu-central-1'
    }

# In prompt_interception_engine.py
from my_app.routes.settings_routes import _aws_credentials_cache

async def _call_aws_bedrock(...):
    if _aws_credentials_cache:
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name=_aws_credentials_cache['region'],
            aws_access_key_id=_aws_credentials_cache['access_key_id'],
            aws_secret_access_key=_aws_credentials_cache['secret_access_key']
        )
    else:
        # Fallback to ENV
        bedrock = boto3.client(
            service_name="bedrock-runtime",
            region_name="eu-central-1"
        )
```

**Vorteil:** Keine Datei, nur im RAM
**Nachteil:** Bei Server-Neustart weg (User muss neu uploaden)

### Option B: Nur ENV Variables (empfohlen)

**CSV-Upload entfernen**, stattdessen:
- Dokumentation verbessern
- User setzt ENV einmal manuell
- Für Production: IAM Roles (keine statischen Keys)

## Commits dieser Session

| Commit | Beschreibung |
|--------|--------------|
| 213b972 | Settings page with DSGVO-compliant API key management |
| caac703 | Multi-provider LLM support (anthropic, openai, openrouter) |
| 0b75cac | AWS Bedrock support with boto3 integration |
| d226226 | AWS_BEDROCK_SETUP.md documentation |
| ffa9e80 | Settings Page UI cleanup |
| 1f40879 | AWS CSV upload feature |
| 2d47147 | Remove obsolete data localization warning |
| 48a564a | Robust CSV parsing (BOM handling) |

**LETZTER COMMIT HAT SECURITY-ISSUE:** Credentials in aws_credentials.json!

## Nächste Schritte

1. **SOFORT:** aws_credentials.json zu .gitignore, Datei löschen
2. **Debug:** Warum findet boto3 keine ENV Variables?
3. **Entscheidung:** CSV-Upload behalten (In-Memory) oder entfernen (nur ENV)?
4. **Test:** AWS Bedrock API Call mit korrekten Credentials

## Testing Commands

```bash
# Check ENV
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
echo $AWS_DEFAULT_REGION

# Check boto3
pip list | grep boto3

# Test boto3 manually
python3 -c "import boto3; print(boto3.client('bedrock-runtime', region_name='eu-central-1'))"

# Check if server has ENV (add to _call_aws_bedrock)
import os
logger.info(f"AWS_ACCESS_KEY_ID: {os.environ.get('AWS_ACCESS_KEY_ID', 'NOT SET')[:8]}...")
```

## Architektur-Entscheidungen

### DSGVO Compliance

**3 Stufen implementiert:**
1. **dsgvo_local**: Nur Ollama (lokal)
2. **dsgvo_cloud**: AWS Bedrock EU (DSGVO-compliant!)
3. **non_dsgvo**: OpenRouter US

**WICHTIG:** AWS Bedrock (bedrock/ Präfix) IST DSGVO-compliant wenn eu-central-1 Region genutzt wird!

### Provider-Präfix-System

**Begründung:** Explizit und nachvollziehbar
- Jeder sieht welcher Provider genutzt wird
- Keine versteckten Settings-Dependencies
- Multi-Provider transparent

## Offene Fragen

1. CSV-Upload: In-Memory oder komplett entfernen?
2. Warum findet boto3 die ENV Variables nicht?
3. Sollen wir user_settings.json auch überprüfen ob da alte Werte sind?

## Files die NUR in .gitignore sein dürfen

- ✅ openrouter.key
- ✅ anthropic.key
- ✅ openai.key
- ✅ settings_password.key
- ✅ setup_aws_env.sh
- ⚠️ aws_credentials.json (NEU - MUSS ZU .gitignore!)
- ✅ user_settings.json

---

**Ende des Handovers**
Nächste Session: Debug warum boto3 keine Credentials findet + Security-Fix für aws_credentials.json
