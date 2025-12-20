<template>
  <div class="session-export-container">
    <div class="export-header">
      <h2>Session Data Export</h2>
      <p class="help">View and export research data from generated sessions</p>
    </div>

    <!-- Statistics -->
    <div class="stats-container" v-if="!loading && !error">
      <div class="stat-card">
        <div class="stat-number">{{ stats.total }}</div>
        <div class="stat-label">Total Sessions</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.users }}</div>
        <div class="stat-label">Users</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.configs }}</div>
        <div class="stat-label">Configs</div>
      </div>
      <div class="stat-card">
        <div class="stat-number">{{ stats.media }}</div>
        <div class="stat-label">Media Files</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters-container" v-if="!loading && !error">
      <div class="filter-row">
        <div class="filter-group">
          <button @click="exportFilteredSessions" class="export-csv-btn" :disabled="loading || sessions.length === 0">
            Export Filtered to CSV
          </button>
        </div>

        <div class="filter-group">
          <label>Date Range</label>
          <div class="date-range">
            <input type="date" v-model="filters.date_from" @change="applyFilters" placeholder="From" />
            <span class="date-separator">→</span>
            <input type="date" v-model="filters.date_to" @change="applyFilters" placeholder="To" />
          </div>
        </div>

        <div class="filter-group available-dates-group">
          <label>Available Dates (click to select)</label>
          <div class="available-dates">
            <button
              v-for="dateInfo in availableDates.slice(0, 10)"
              :key="dateInfo.date"
              @click="selectDate(dateInfo.date)"
              :class="['date-btn', { active: isDateSelected(dateInfo.date) }]"
              :title="`${dateInfo.count} sessions`"
            >
              {{ formatShortDate(dateInfo.date) }}
              <span class="date-count">{{ dateInfo.count }}</span>
            </button>
            <button
              v-if="availableDates.length > 10"
              @click="showAllDates = !showAllDates"
              class="date-btn more-dates"
            >
              {{ showAllDates ? 'Less' : `+${availableDates.length - 10} more` }}
            </button>
          </div>
          <div v-if="showAllDates" class="available-dates">
            <button
              v-for="dateInfo in availableDates.slice(10)"
              :key="dateInfo.date"
              @click="selectDate(dateInfo.date)"
              :class="['date-btn', { active: isDateSelected(dateInfo.date) }]"
              :title="`${dateInfo.count} sessions`"
            >
              {{ formatShortDate(dateInfo.date) }}
              <span class="date-count">{{ dateInfo.count }}</span>
            </button>
          </div>
        </div>

        <div class="filter-group">
          <label>User</label>
          <select v-model="filters.user_id" @change="applyFilters">
            <option value="">All Users</option>
            <option v-for="user in availableFilters.users" :key="user" :value="user">
              {{ user }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Config</label>
          <select v-model="filters.config_name" @change="applyFilters">
            <option value="">All Configs</option>
            <option v-for="config in availableFilters.configs" :key="config" :value="config">
              {{ config }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Safety Level</label>
          <select v-model="filters.safety_level" @change="applyFilters">
            <option value="">All Levels</option>
            <option v-for="level in availableFilters.safety_levels" :key="level" :value="level">
              {{ level }}
            </option>
          </select>
        </div>

        <div class="filter-group">
          <label>Search</label>
          <input
            type="text"
            v-model="filters.search"
            @input="debouncedSearch"
            placeholder="Session ID..."
          />
        </div>

        <div class="filter-group">
          <button @click="clearFilters" class="clear-btn">Clear Filters</button>
        </div>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading sessions...</p>
    </div>

    <div v-if="error" class="error-state">
      <p>Error: {{ error }}</p>
    </div>

    <!-- Sessions Table -->
    <div v-if="!loading && !error && sessions.length > 0" class="table-container">
      <table class="sessions-table">
        <thead>
          <tr>
            <th>Preview</th>
            <th @click="sortBy('timestamp')" class="sortable">
              Timestamp
              <span v-if="sortField === 'timestamp'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('user_id')" class="sortable">
              User
              <span v-if="sortField === 'user_id'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th @click="sortBy('config_name')" class="sortable">
              Config
              <span v-if="sortField === 'config_name'">{{ sortOrder === 'asc' ? '↑' : '↓' }}</span>
            </th>
            <th>Safety Level</th>
            <th>Stage</th>
            <th>Entities</th>
            <th>Media</th>
            <th>Session ID</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="session in sessions" :key="session.run_id">
            <td>
              <div v-if="session.thumbnail" class="thumbnail-container">
                <img :src="session.thumbnail" class="thumbnail" @error="handleImageError" />
              </div>
              <div v-else class="no-thumbnail">
                <span>No Image</span>
              </div>
            </td>
            <td>{{ formatTimestamp(session.timestamp) }}</td>
            <td>{{ session.user_id }}</td>
            <td><span class="config-badge">{{ session.config_name }}</span></td>
            <td><span class="safety-badge" :class="`safety-${session.safety_level}`">{{ session.safety_level }}</span></td>
            <td>{{ session.stage }} / {{ session.step }}</td>
            <td>{{ session.entity_count }}</td>
            <td>{{ session.media_count }}</td>
            <td><code class="run-id">{{ session.run_id.substring(0, 8) }}...</code></td>
            <td>
              <button @click="viewSession(session.run_id)" class="action-btn view-btn">View</button>
              <button @click="downloadSession(session.run_id)" class="action-btn download-btn">JSON</button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Pagination -->
      <div class="pagination">
        <button
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage <= 1"
          class="page-btn"
        >
          Previous
        </button>

        <span class="page-info">
          Page {{ currentPage }} of {{ totalPages }} ({{ stats.total }} total)
        </span>

        <button
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage >= totalPages"
          class="page-btn"
        >
          Next
        </button>

        <select v-model.number="perPage" @change="applyFilters" class="per-page-select">
          <option :value="25">25 per page</option>
          <option :value="50">50 per page</option>
          <option :value="100">100 per page</option>
          <option :value="250">250 per page</option>
        </select>
      </div>
    </div>

    <!-- No Data -->
    <div v-if="!loading && !error && sessions.length === 0" class="no-data">
      <p>No sessions found for the selected filters.</p>
    </div>

    <!-- Session Detail Modal -->
    <div v-if="showModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Session Details</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingDetail" class="loading-state">
            <div class="spinner"></div>
            <p>Loading session details...</p>
          </div>
          <div v-else-if="selectedSession">
            <div class="detail-section">
              <h4>Metadata</h4>
              <table class="detail-table">
                <tr>
                  <td><strong>Session ID:</strong></td>
                  <td><code>{{ selectedSession.run_id }}</code></td>
                </tr>
                <tr>
                  <td><strong>Timestamp:</strong></td>
                  <td>{{ formatTimestamp(selectedSession.timestamp) }}</td>
                </tr>
                <tr>
                  <td><strong>Config:</strong></td>
                  <td>{{ selectedSession.config_name }}</td>
                </tr>
                <tr>
                  <td><strong>User:</strong></td>
                  <td>{{ selectedSession.user_id }}</td>
                </tr>
                <tr>
                  <td><strong>Safety Level:</strong></td>
                  <td>{{ selectedSession.safety_level }}</td>
                </tr>
                <tr>
                  <td><strong>Stage:</strong></td>
                  <td>{{ selectedSession.current_state?.stage }} / {{ selectedSession.current_state?.step }}</td>
                </tr>
              </table>
            </div>

            <div class="detail-section">
              <h4>Entities ({{ selectedSession.entities?.length || 0 }})</h4>
              <div v-for="entity in selectedSession.entities" :key="entity.sequence" class="entity-item">
                <div class="entity-header">
                  <span class="entity-type">{{ entity.type }}</span>
                  <span class="entity-filename">{{ entity.filename }}</span>
                  <span class="entity-time">{{ formatTime(entity.timestamp) }}</span>
                </div>
                <div v-if="entity.image_url" class="entity-image">
                  <img :src="entity.image_url" :alt="entity.filename" class="detail-image" />
                </div>
                <div v-else-if="entity.content" class="entity-content">
                  <pre>{{ entity.content }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const loading = ref(false)
const error = ref(null)
const sessions = ref([])
const currentPage = ref(1)
const perPage = ref(50)
const totalPages = ref(0)
const sortField = ref('timestamp')
const sortOrder = ref('desc')

const filters = ref({
  date_from: new Date().toISOString().split('T')[0], // Today by default
  date_to: new Date().toISOString().split('T')[0],   // Today by default
  user_id: '',
  config_name: '',
  safety_level: '',
  search: ''
})

const availableDates = ref([])
const showAllDates = ref(false)

const availableFilters = ref({
  users: [],
  configs: [],
  safety_levels: []
})

const stats = ref({
  total: 0,
  users: 0,
  configs: 0,
  media: 0
})

const showModal = ref(false)
const selectedSession = ref(null)
const loadingDetail = ref(false)

let searchTimeout = null

async function loadAvailableDates() {
  try {
    const response = await fetch('/api/settings/sessions/available-dates', {
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    availableDates.value = data.dates
  } catch (e) {
    console.error('Failed to load available dates:', e)
  }
}

async function loadSessions() {
  try {
    loading.value = true
    error.value = null

    const params = new URLSearchParams({
      page: currentPage.value,
      per_page: perPage.value,
      sort: sortField.value,
      order: sortOrder.value,
      ...(filters.value.date_from && { date_from: filters.value.date_from }),
      ...(filters.value.date_to && { date_to: filters.value.date_to }),
      ...(filters.value.user_id && { user_id: filters.value.user_id }),
      ...(filters.value.config_name && { config_name: filters.value.config_name }),
      ...(filters.value.safety_level && { safety_level: filters.value.safety_level }),
      ...(filters.value.search && { search: filters.value.search })
    })

    const response = await fetch(`/api/settings/sessions?${params}`, {
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    sessions.value = data.sessions
    totalPages.value = data.total_pages
    stats.value.total = data.total

    // Update available filters
    availableFilters.value = data.filters
    stats.value.users = data.filters.users.length
    stats.value.configs = data.filters.configs.length
    stats.value.media = data.sessions.reduce((sum, s) => sum + s.media_count, 0)

  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  currentPage.value = 1
  loadSessions()
}

function debouncedSearch() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    applyFilters()
  }, 500)
}

function clearFilters() {
  const today = new Date().toISOString().split('T')[0]
  filters.value = {
    date_from: today,
    date_to: today,
    user_id: '',
    config_name: '',
    safety_level: '',
    search: ''
  }
  applyFilters()
}

function selectDate(dateStr) {
  filters.value.date_from = dateStr
  filters.value.date_to = dateStr
  applyFilters()
}

function isDateSelected(dateStr) {
  return filters.value.date_from === dateStr && filters.value.date_to === dateStr
}

function formatShortDate(dateStr) {
  try {
    const dt = new Date(dateStr)
    return dt.toLocaleDateString('de-DE', { month: 'short', day: 'numeric' })
  } catch {
    return dateStr
  }
}

function sortBy(field) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'desc'
  }
  loadSessions()
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadSessions()
  }
}

async function viewSession(runId) {
  try {
    showModal.value = true
    loadingDetail.value = true
    selectedSession.value = null

    const response = await fetch(`/api/settings/sessions/${runId}`, {
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    selectedSession.value = await response.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loadingDetail.value = false
  }
}

function closeModal() {
  showModal.value = false
  selectedSession.value = null
}

async function downloadSession(runId) {
  try {
    const response = await fetch(`/api/settings/sessions/${runId}`, {
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }

    const data = await response.json()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `session_${runId}.json`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  }
}

function exportFilteredSessions() {
  try {
    // Create CSV header
    const headers = [
      'Session ID',
      'Timestamp',
      'User ID',
      'Config Name',
      'Safety Level',
      'Execution Mode',
      'Stage',
      'Step',
      'Entity Count',
      'Media Count'
    ]

    // Create CSV rows
    const rows = sessions.value.map(session => [
      session.run_id,
      formatTimestamp(session.timestamp),
      session.user_id,
      session.config_name,
      session.safety_level,
      session.execution_mode,
      session.stage,
      session.step,
      session.entity_count,
      session.media_count
    ])

    // Combine header and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => {
        // Escape quotes and wrap in quotes if contains comma or quote
        const cellStr = String(cell || '')
        if (cellStr.includes(',') || cellStr.includes('"') || cellStr.includes('\n')) {
          return `"${cellStr.replace(/"/g, '""')}"`
        }
        return cellStr
      }).join(','))
    ].join('\n')

    // Create and download blob
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    const timestamp = new Date().toISOString().split('T')[0]
    a.download = `ai4artsed_sessions_${timestamp}.csv`
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    error.value = e.message
  }
}

function formatTimestamp(timestamp) {
  try {
    const dt = new Date(timestamp)
    return dt.toLocaleString('de-DE')
  } catch {
    return timestamp
  }
}

function formatTime(timestamp) {
  try {
    const dt = new Date(timestamp)
    return dt.toLocaleTimeString('de-DE')
  } catch {
    return timestamp
  }
}

function handleImageError(event) {
  // Hide broken image icon
  event.target.style.display = 'none'
}

onMounted(() => {
  loadAvailableDates()
  loadSessions()
})
</script>

<style scoped>
.session-export-container {
  padding: 20px;
  background: #000;
  color: #fff;
  min-height: 100vh;
}

.export-header {
  background: #fff;
  padding: 15px;
  border: 1px solid #ccc;
  margin-bottom: 20px;
}

.export-header h2 {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.export-header .help {
  margin: 0;
  font-size: 13px;
  color: #666;
}

/* Statistics */
.stats-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #fff;
  border: 1px solid #ccc;
  padding: 15px;
  text-align: center;
}

.stat-number {
  font-size: 28px;
  font-weight: bold;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Filters */
.filters-container {
  background: #fff;
  border: 1px solid #ccc;
  padding: 15px;
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 150px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #333;
}

.filter-group input,
.filter-group select {
  padding: 6px 8px;
  border: 1px solid #ccc;
  font-size: 13px;
  background: #fff;
  color: #000;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-range input {
  flex: 1;
  min-width: 140px;
}

.date-separator {
  color: #666;
  font-weight: bold;
}

.available-dates-group {
  min-width: 100%;
  flex-basis: 100%;
}

.available-dates {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 5px;
}

.date-btn {
  padding: 6px 10px;
  background: #f0f0f0;
  border: 1px solid #ccc;
  cursor: pointer;
  font-size: 12px;
  color: #333;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.date-btn:hover {
  background: #e0e0e0;
  border-color: #999;
}

.date-btn.active {
  background: #007bff;
  color: #fff;
  border-color: #0056b3;
  font-weight: 600;
}

.date-btn.active .date-count {
  background: rgba(255, 255, 255, 0.3);
}

.date-count {
  background: #ddd;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
}

.date-btn.more-dates {
  background: #e9ecef;
  color: #666;
  font-style: italic;
}

.clear-btn {
  padding: 6px 12px;
  background: #6c757d;
  color: #fff;
  border: 1px solid #999;
  cursor: pointer;
  font-size: 13px;
}

.clear-btn:hover {
  background: #888;
}

.export-csv-btn {
  padding: 6px 12px;
  background: #28a745;
  color: #fff;
  border: 1px solid #1e7e34;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
}

.export-csv-btn:hover:not(:disabled) {
  background: #218838;
}

.export-csv-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Loading / Error */
.loading-state,
.error-state,
.no-data {
  background: #fff;
  border: 1px solid #ccc;
  padding: 40px;
  text-align: center;
  color: #333;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #c00;
}

/* Table */
.table-container {
  background: #fff;
  border: 1px solid #ccc;
  overflow-x: auto;
}

.sessions-table {
  width: 100%;
  border-collapse: collapse;
}

.sessions-table th,
.sessions-table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
  color: #000;
  font-size: 13px;
}

.sessions-table th {
  background: #f0f0f0;
  font-weight: 600;
  color: #333;
}

.sessions-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.sessions-table th.sortable:hover {
  background: #e0e0e0;
}

.sessions-table tbody tr:hover {
  background: #f8f9fa;
}

.config-badge {
  background: #e7f3ff;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
  font-family: monospace;
}

.safety-badge {
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.safety-kids {
  background: #d4edda;
  color: #155724;
}

.safety-youth {
  background: #fff3cd;
  color: #856404;
}

.safety-adult,
.safety-open {
  background: #f8d7da;
  color: #721c24;
}

.run-id {
  font-family: monospace;
  font-size: 11px;
  background: #f1f3f4;
  padding: 2px 4px;
  border-radius: 2px;
}

.action-btn {
  padding: 4px 10px;
  font-size: 12px;
  border: 1px solid #ccc;
  cursor: pointer;
  margin-right: 5px;
}

.view-btn {
  background: #007bff;
  color: #fff;
}

.view-btn:hover {
  background: #0056b3;
}

.download-btn {
  background: #28a745;
  color: #fff;
}

.download-btn:hover {
  background: #218838;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #ddd;
}

.page-btn {
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #ccc;
  cursor: pointer;
  font-size: 13px;
  color: #000;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: #e0e0e0;
}

.page-info {
  font-size: 13px;
  color: #333;
}

.per-page-select {
  padding: 6px 8px;
  border: 1px solid #ccc;
  font-size: 13px;
  background: #fff;
  color: #000;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border: 1px solid #ccc;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #ddd;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #666;
  line-height: 1;
  padding: 0;
  width: 30px;
  height: 30px;
}

.close-btn:hover {
  color: #000;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
  color: #000;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 5px;
}

.detail-table {
  width: 100%;
  border-collapse: collapse;
}

.detail-table td {
  padding: 8px 10px;
  border-bottom: 1px solid #eee;
}

.detail-table code {
  background: #f1f3f4;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  font-size: 12px;
}

.entity-item {
  border: 1px solid #ddd;
  margin-bottom: 10px;
  border-radius: 4px;
  overflow: hidden;
}

.entity-header {
  background: #f8f9fa;
  padding: 8px 12px;
  display: flex;
  gap: 15px;
  align-items: center;
  font-size: 12px;
}

.entity-type {
  font-weight: 600;
  color: #007bff;
}

.entity-filename {
  font-family: monospace;
  color: #666;
}

.entity-time {
  color: #999;
  margin-left: auto;
}

.entity-content {
  padding: 12px;
  background: #fff;
  border-top: 1px solid #ddd;
}

.entity-content pre {
  margin: 0;
  font-size: 12px;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #333;
}

.entity-image {
  padding: 12px;
  background: #fff;
  border-top: 1px solid #ddd;
  text-align: center;
}

.detail-image {
  max-width: 100%;
  max-height: 600px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Thumbnails */
.thumbnail-container {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail {
  max-width: 60px;
  max-height: 60px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.no-thumbnail {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.no-thumbnail span {
  font-size: 10px;
  color: #999;
  text-align: center;
}
</style>
