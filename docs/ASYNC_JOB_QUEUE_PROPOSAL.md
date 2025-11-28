# Async Job Queue - Architekturverbesserung für Media-Generierung

> **Status:** Proposal (nicht implementiert)
> **Erstellt:** 2025-11-27, Session 78
> **Priorität:** Hoch (betrifft Production-Stabilität)
> **Aufwand:** ~3-4 Stunden

---

## Problem: Cloudflare 524 Timeouts bei langen Operationen

### Aktuelles Verhalten (Synchron):

```
Frontend → POST /api/run → Backend arbeitet → (100 Sek Cloudflare Timeout) → ❌ Error 524
```

**Was passiert:**
- User startet Media-Generierung (z.B. Wan 2.2 Video)
- Frontend sendet synchronen POST Request
- Backend arbeitet 2-5 Minuten
- **Cloudflare Free Plan Timeout: 100 Sekunden** (hard limit)
- Cloudflare bricht Verbindung ab → Error 524
- Backend arbeitet weiter, aber Frontend bekommt keine Antwort
- User sieht Fehlermeldung, obwohl Generation im Hintergrund läuft

### Betroffene Operationen:

**Aktuell:**
- 🖼️ **Bildgenerierung** (SD3.5 Large): 10-30 Sek
  - ⚠️ Manchmal länger bei komplexen Prompts
  - Risiko: Kann über 100 Sek gehen
- 🎬 **Videogenerierung** (LTX-Video): 1-3 Min
  - ❌ Timeout garantiert
- 🎬 **Videogenerierung** (Wan 2.2): 2-5 Min
  - ❌ Timeout garantiert

**Zukünftig:**
- 🎵 **Audio-Generierung** (Sound Lab)
- 🎞️ **Längere Videos** (wenn erweitert)
- 🎨 **Batch-Generierung** (mehrere Bilder gleichzeitig)

**Alle medienbezogenen Aktionen sind betroffen!**

---

## Lösung: Async Job Queue

### Neue Architektur (Asynchron):

```
1. Job starten:
   Frontend → POST /api/run/start
              ← { job_id: "abc123", status: "queued" }  (sofort!)

2. Status abfragen:
   Frontend → GET /api/run/abc123/status  (alle 2 Sekunden)
              ← {
                  status: "running",
                  progress: 45,
                  message: "Generating frame 15/30"
                }

3. Backend arbeitet im Hintergrund...
   - Job Queue verarbeitet Jobs
   - Progress wird in Redis/Memory gespeichert
   - Frontend pollt Status

4. Job fertig:
   Frontend → GET /api/run/abc123/status
              ← {
                  status: "completed",
                  result: {
                    output_url: "/exports/...",
                    metadata: {...}
                  }
                }

5. Frontend zeigt Ergebnis ✅
```

---

## Vorteile für ALLE Medientypen

1. ✅ **Keine Timeouts** - funktioniert mit Cloudflare Free Plan (100 Sek Limit irrelevant)
2. ✅ **Progress Tracking** - User sieht "Generation 45% fertig"
3. ✅ **Bessere UX** - Frontend bleibt responsive, User kann andere Dinge tun
4. ✅ **Error Handling** - Klare Fehlermeldungen wenn Generation fehlschlägt
5. ✅ **Skalierbar** - Mehrere Jobs parallel verarbeiten
6. ✅ **Future-Proof** - Funktioniert auch mit langsameren/größeren Modellen
7. ✅ **Konsistente API** - Gleicher Flow für alle Medientypen

---

## Implementierungsplan

### Phase 1: Backend Job Queue (2 Stunden)

#### 1.1 Job Queue Service (`devserver/my_app/services/job_queue.py`)

```python
"""
Async Job Queue Service for Media Generation

Manages background jobs with progress tracking and status updates.
"""

import uuid
import threading
from queue import Queue
from typing import Dict, Optional, Callable
from datetime import datetime

class JobStatus:
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Job:
    def __init__(self, job_id: str, task_fn: Callable, task_args: dict):
        self.job_id = job_id
        self.task_fn = task_fn
        self.task_args = task_args
        self.status = JobStatus.QUEUED
        self.progress = 0
        self.message = ""
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None

class JobQueue:
    """
    Singleton Job Queue Service

    Usage:
        queue = JobQueue()
        job_id = queue.submit_job(task_function, task_args)
        status = queue.get_job_status(job_id)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._job_queue = Queue()
        self._jobs: Dict[str, Job] = {}
        self._worker_thread = threading.Thread(target=self._worker, daemon=True)
        self._worker_thread.start()

    def submit_job(self, task_fn: Callable, task_args: dict) -> str:
        """
        Submit a new job to the queue

        Args:
            task_fn: Function to execute (must accept progress_callback)
            task_args: Arguments for the function

        Returns:
            job_id: Unique job identifier
        """
        job_id = str(uuid.uuid4())
        job = Job(job_id, task_fn, task_args)
        self._jobs[job_id] = job
        self._job_queue.put(job)
        return job_id

    def get_job_status(self, job_id: str) -> Optional[dict]:
        """
        Get current status of a job

        Returns:
            {
                "job_id": "abc123",
                "status": "running",
                "progress": 45,
                "message": "Processing...",
                "result": {...},  # Only if completed
                "error": "...",   # Only if failed
                "created_at": "2025-11-27T18:00:00",
                "started_at": "2025-11-27T18:00:01",
                "completed_at": "2025-11-27T18:02:30"
            }
        """
        job = self._jobs.get(job_id)
        if not job:
            return None

        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "message": job.message,
            "result": job.result,
            "error": job.error,
            "created_at": job.created_at.isoformat(),
            "started_at": job.started_at.isoformat() if job.started_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

    def _worker(self):
        """
        Background worker thread that processes jobs
        """
        while True:
            job = self._job_queue.get()

            try:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now()

                # Progress callback for task function
                def progress_callback(progress: int, message: str = ""):
                    job.progress = progress
                    job.message = message

                # Execute task with progress callback
                result = job.task_fn(**job.task_args, progress_callback=progress_callback)

                job.status = JobStatus.COMPLETED
                job.result = result
                job.progress = 100
                job.message = "Completed"

            except Exception as e:
                job.status = JobStatus.FAILED
                job.error = str(e)
                job.message = f"Error: {str(e)}"

            finally:
                job.completed_at = datetime.now()
                self._job_queue.task_done()
```

#### 1.2 Adapt Pipeline Executor for Progress Tracking

**File:** `devserver/my_app/engine/pipeline_executor.py`

Add progress callback support to `execute_chunk` and `execute_pipeline`:

```python
def execute_chunk(self, chunk_data: dict, progress_callback: Optional[Callable] = None):
    """
    Execute a single chunk with optional progress tracking

    Args:
        chunk_data: Chunk configuration
        progress_callback: Optional callback(progress: int, message: str)
    """

    # Example: Report progress during execution
    if progress_callback:
        progress_callback(10, f"Starting chunk: {chunk_data['chunk_name']}")

    # ... existing execution logic ...

    if progress_callback:
        progress_callback(50, "Processing with LLM...")

    # ... more execution ...

    if progress_callback:
        progress_callback(90, "Finalizing output...")

    return result
```

#### 1.3 New API Endpoints (`devserver/my_app/routes/job_routes.py`)

```python
"""
Job Queue API Endpoints

Provides async job management for long-running operations.
"""

from flask import Blueprint, jsonify, request
from my_app.services.job_queue import JobQueue
from my_app.engine.pipeline_executor import PipelineExecutor

job_bp = Blueprint('job', __name__, url_prefix='/api/job')
job_queue = JobQueue()

@job_bp.route('/start', methods=['POST'])
def start_job():
    """
    Start a new async job

    POST /api/job/start
    {
        "config_id": "bauhaus",
        "user_input": "A red house",
        "language": "de",
        ...
    }

    Returns:
    {
        "job_id": "abc123",
        "status": "queued"
    }
    """
    data = request.json

    # Create task function for pipeline execution
    def run_pipeline_task(progress_callback=None, **kwargs):
        executor = PipelineExecutor()
        return executor.execute_pipeline(
            config_id=kwargs['config_id'],
            user_input=kwargs['user_input'],
            language=kwargs['language'],
            progress_callback=progress_callback
        )

    # Submit job to queue
    job_id = job_queue.submit_job(run_pipeline_task, data)

    return jsonify({
        "job_id": job_id,
        "status": "queued"
    }), 202

@job_bp.route('/<job_id>/status', methods=['GET'])
def get_job_status(job_id):
    """
    Get job status

    GET /api/job/abc123/status

    Returns:
    {
        "job_id": "abc123",
        "status": "running",
        "progress": 45,
        "message": "Generating image...",
        "result": {...},  // Only if completed
        "error": "..."    // Only if failed
    }
    """
    status = job_queue.get_job_status(job_id)

    if not status:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(status), 200

@job_bp.route('/<job_id>/cancel', methods=['POST'])
def cancel_job(job_id):
    """
    Cancel a running job (optional feature)

    POST /api/job/abc123/cancel
    """
    # TODO: Implement job cancellation
    return jsonify({"message": "Not implemented yet"}), 501
```

**Register blueprint in `devserver/my_app/__init__.py`:**

```python
from my_app.routes.job_routes import job_bp
app.register_blueprint(job_bp)
```

---

### Phase 2: Frontend Integration (1-2 Stunden)

#### 2.1 Job Service (`public/ai4artsed-frontend/src/services/jobService.ts`)

```typescript
/**
 * Async Job Service
 *
 * Manages long-running jobs with progress tracking
 */

import axios from 'axios'

export interface JobStatus {
  job_id: string
  status: 'queued' | 'running' | 'completed' | 'failed'
  progress: number
  message: string
  result?: any
  error?: string
  created_at: string
  started_at?: string
  completed_at?: string
}

export class JobService {
  /**
   * Start a new async job
   */
  static async startJob(configId: string, userInput: string, language: string): Promise<string> {
    const response = await axios.post('/api/job/start', {
      config_id: configId,
      user_input: userInput,
      language: language
    })

    return response.data.job_id
  }

  /**
   * Get job status
   */
  static async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await axios.get(`/api/job/${jobId}/status`)
    return response.data
  }

  /**
   * Poll job status until completion
   *
   * @param jobId Job ID to poll
   * @param onProgress Callback for progress updates
   * @param pollInterval Milliseconds between polls (default: 2000)
   * @returns Final job result
   */
  static async pollJobUntilComplete(
    jobId: string,
    onProgress: (status: JobStatus) => void,
    pollInterval: number = 2000
  ): Promise<any> {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getJobStatus(jobId)
          onProgress(status)

          if (status.status === 'completed') {
            resolve(status.result)
          } else if (status.status === 'failed') {
            reject(new Error(status.error || 'Job failed'))
          } else {
            // Continue polling
            setTimeout(poll, pollInterval)
          }
        } catch (error) {
          reject(error)
        }
      }

      poll()
    })
  }
}
```

#### 2.2 Update Pipeline Execution Component

**File:** `public/ai4artsed-frontend/src/views/text_transformation.vue`

```typescript
import { JobService, JobStatus } from '@/services/jobService'

// Replace synchronous execution with async job
const isGenerating = ref(false)
const jobProgress = ref(0)
const jobMessage = ref('')

async function executeWithAsyncJob() {
  isGenerating.value = true
  jobProgress.value = 0
  jobMessage.value = 'Starting...'

  try {
    // Start job
    const jobId = await JobService.startJob(
      selectedConfig.value.id,
      userInput.value,
      language.value
    )

    console.log('[AsyncJob] Started job:', jobId)

    // Poll until complete
    const result = await JobService.pollJobUntilComplete(
      jobId,
      (status: JobStatus) => {
        // Update UI with progress
        jobProgress.value = status.progress
        jobMessage.value = status.message
        console.log(`[AsyncJob] Progress: ${status.progress}% - ${status.message}`)
      }
    )

    // Show result
    pipelineResult.value = result
    console.log('[AsyncJob] Completed!', result)

  } catch (error) {
    console.error('[AsyncJob] Error:', error)
    alert(`Job failed: ${error.message}`)
  } finally {
    isGenerating.value = false
  }
}
```

#### 2.3 Progress UI Component

```vue
<template>
  <div v-if="isGenerating" class="progress-overlay">
    <div class="progress-card">
      <h3>Generierung läuft...</h3>
      <div class="progress-bar">
        <div
          class="progress-fill"
          :style="{ width: `${jobProgress}%` }"
        ></div>
      </div>
      <p class="progress-text">{{ jobProgress }}% - {{ jobMessage }}</p>
    </div>
  </div>
</template>

<style scoped>
.progress-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.progress-card {
  background: #1a1a1a;
  padding: 2rem;
  border-radius: 12px;
  min-width: 400px;
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 24px;
  background: #333;
  border-radius: 12px;
  overflow: hidden;
  margin: 1rem 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #4CAF50, #8BC34A);
  transition: width 0.3s ease;
}

.progress-text {
  color: #aaa;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}
</style>
```

---

## Migration Strategy

### Option 1: Gradual Migration (Empfohlen)
1. Implementiere Job Queue parallel zu synchronem System
2. Neue Endpoint: `/api/job/start` (async)
3. Alter Endpoint: `/api/run` (synchron, bleibt vorerst)
4. Frontend: Feature Flag für Async Mode
5. Teste ausgiebig mit Async Mode
6. Wenn stabil: Migriere alle Komponenten
7. Entferne alten synchronen Endpoint

### Option 2: Big Bang Migration
1. Implementiere Job Queue
2. Ersetze `/api/run` komplett
3. Update alle Frontend-Komponenten
4. Deploy und teste

**Empfehlung: Option 1** - weniger Risiko, besseres Testing

---

## Testing Strategy

### Backend Tests
```python
# tests/test_job_queue.py

def test_job_submission():
    queue = JobQueue()

    def dummy_task(progress_callback=None):
        if progress_callback:
            progress_callback(50, "Half done")
        return {"result": "success"}

    job_id = queue.submit_job(dummy_task, {})

    # Wait for completion
    time.sleep(1)

    status = queue.get_job_status(job_id)
    assert status['status'] == 'completed'
    assert status['result'] == {"result": "success"}
```

### Frontend Tests
```typescript
// tests/jobService.test.ts

describe('JobService', () => {
  it('should start job and poll until complete', async () => {
    const jobId = await JobService.startJob('bauhaus', 'test', 'de')

    const result = await JobService.pollJobUntilComplete(
      jobId,
      (status) => {
        console.log('Progress:', status.progress)
      }
    )

    expect(result).toBeDefined()
  })
})
```

### Manual Testing
1. Start lange Video-Generierung (Wan 2.2)
2. Beobachte Progress Updates im Frontend
3. Verifiziere dass kein 524 Timeout auftritt
4. Checke dass Result korrekt angezeigt wird
5. Teste Error-Handling bei fehlgeschlagener Generation

---

## Performance Considerations

### Memory Management
- **Problem:** Jobs in Memory können bei vielen Usern explodieren
- **Lösung:** Job Cleanup nach X Stunden
- **Implementierung:**
```python
def cleanup_old_jobs(self, max_age_hours: int = 24):
    """Remove completed/failed jobs older than max_age_hours"""
    cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

    for job_id, job in list(self._jobs.items()):
        if job.completed_at and job.completed_at < cutoff_time:
            del self._jobs[job_id]
```

### Scaling
- **Single Server:** Python Queue + Threading (current proposal)
- **Multi-Server:** Migrate to Redis + Celery
- **Cloud:** Use AWS SQS or Google Cloud Tasks

---

## Future Enhancements

### Phase 3: Advanced Features (Optional)
1. **Job Cancellation** - User can abort running jobs
2. **Job History** - User can see past generations
3. **Batch Processing** - Generate multiple variants at once
4. **Priority Queue** - Premium users get higher priority
5. **Webhook Notifications** - Email/Push when job completes
6. **Job Scheduling** - Schedule generation for later time

---

## Success Metrics

Nach Implementierung sollten folgende Metriken besser sein:

1. ✅ **Cloudflare 524 Errors: 0** (aktuell: häufig bei Videos)
2. ✅ **User Satisfaction:** Positive Feedback zu Progress Tracking
3. ✅ **Completion Rate:** 100% für alle Medientypen
4. ✅ **System Stability:** Kein Memory-Leak, keine Crashes
5. ✅ **Response Time:** Frontend bleibt responsive während Generation

---

## Risks & Mitigation

### Risk 1: Memory Leak bei vielen Jobs
- **Mitigation:** Automatic job cleanup after 24 hours
- **Monitoring:** Track jobs count in memory

### Risk 2: Worker Thread crashes
- **Mitigation:** Proper exception handling in worker
- **Monitoring:** Health check endpoint `/api/health/queue`

### Risk 3: Frontend polling overload
- **Mitigation:** Exponential backoff if server overloaded
- **Implementation:**
```typescript
let pollInterval = 2000 // Start with 2 sec
const maxInterval = 10000 // Max 10 sec

function adaptivePoll() {
  // If server returns 429 (Too Many Requests), increase interval
  if (response.status === 429) {
    pollInterval = Math.min(pollInterval * 1.5, maxInterval)
  }
}
```

---

## Deployment Checklist

- [ ] Backend: Implement `JobQueue` service
- [ ] Backend: Add progress tracking to `PipelineExecutor`
- [ ] Backend: Implement `/api/job/*` endpoints
- [ ] Backend: Register job blueprint
- [ ] Backend: Write tests
- [ ] Frontend: Implement `JobService`
- [ ] Frontend: Add progress UI component
- [ ] Frontend: Update all pipeline execution components
- [ ] Frontend: Write tests
- [ ] Testing: Manual test all media types
- [ ] Testing: Load testing with multiple concurrent jobs
- [ ] Documentation: Update API docs
- [ ] Deployment: Deploy to production
- [ ] Monitoring: Track 524 errors (should be 0)
- [ ] Cleanup: Remove old synchronous endpoint (after validation)

---

## Estimated Timeline

- **Phase 1 (Backend):** 2 hours
  - Job Queue Service: 1 hour
  - Pipeline Executor updates: 30 min
  - API Endpoints: 30 min

- **Phase 2 (Frontend):** 1-2 hours
  - Job Service: 30 min
  - Progress UI: 30 min
  - Component updates: 30-60 min

- **Testing & Refinement:** 30-60 min

**Total: 3-4 hours** for full implementation

---

## References

- **Current Implementation:** `devserver/my_app/routes/schema_pipeline_routes.py` (synchronous execution)
- **Pipeline Executor:** `devserver/my_app/engine/pipeline_executor.py`
- **Frontend Execution:** `public/ai4artsed-frontend/src/views/*.vue`
- **Cloudflare 524 Docs:** https://developers.cloudflare.com/support/troubleshooting/cloudflare-errors/troubleshooting-cloudflare-524-errors/

---

## Questions for Next Session

1. Prefer Python Queue + Threading or migrate to Redis + Celery?
2. Should we implement job cancellation in Phase 1 or later?
3. What should be the job cleanup interval (24 hours ok?)
4. Do we want email notifications when long jobs complete?

---

**Status:** Ready for implementation
**Next Step:** Schedule dedicated session (3-4 hours) for implementation
**Priority:** High - affects production stability and user experience
