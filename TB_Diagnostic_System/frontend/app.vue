<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center text-white text-xl font-bold">
              TB
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">TB Diagnostic System</h1>
              <p class="text-sm text-gray-500 dark:text-gray-400">Patient Analysis & Treatment Management</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <!-- Alerts Badge -->
            <button
              @click="currentView = 'alerts'"
              class="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <span class="text-xl">🔔</span>
              <span
                v-if="unreadAlerts > 0"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-5 h-5 rounded-full flex items-center justify-center"
              >
                {{ unreadAlerts }}
              </span>
            </button>
            <button
              @click="toggleDarkMode"
              class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              {{ isDarkMode ? '☀️' : '🌙' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex gap-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentView = tab.id"
            class="px-4 py-3 font-medium border-b-2 transition"
            :class="currentView === tab.id
              ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 hover:dark:text-gray-200'"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Diagnose View -->
      <div v-if="currentView === 'diagnose'">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Patient Form -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Patient Diagnosis</h2>
            <form @submit.prevent="diagnosePatient" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">First Name</label>
                  <input
                    v-model="patient.first_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Last Name</label>
                  <input
                    v-model="patient.last_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Patient ID</label>
                  <input
                    v-model="patient.patient_id"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Age</label>
                  <input
                    v-model.number="patient.age"
                    type="number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Gender</label>
                  <select
                    v-model="patient.gender"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">City</label>
                  <input
                    v-model="patient.city"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  />
                </div>
              </div>
              <div>
                <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Symptoms</label>
                <textarea
                  v-model="patient.symptoms"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  rows="2"
                  placeholder="Fever, Cough, Night sweats, Weight loss..."
                ></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Sputum Smear</label>
                  <select
                    v-model="patient.sputum_smear_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">GeneXpert</label>
                  <select
                    v-model="patient.genexpert_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Chest X-ray</label>
                  <select
                    v-model="patient.chest_xray"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Normal</option>
                    <option>Abnormal</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Drug Resistance</label>
                  <select
                    v-model="patient.drug_resistance"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">HIV Status</label>
                  <select
                    v-model="patient.hiv"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Diabetes</label>
                  <select
                    v-model="patient.diabetes"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
              </div>
              <button
                type="submit"
                :disabled="loading"
                class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition"
              >
                {{ loading ? 'Analyzing...' : 'Analyze & Diagnose' }}
              </button>
            </form>
          </div>

          <!-- Results -->
          <div v-if="diagnosisResult" class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 class="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Diagnostic Report</h2>
            
            <!-- Patient Info -->
            <div class="mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p class="font-medium text-gray-900 dark:text-white">{{ diagnosisResult.patient_name }}</p>
            </div>

            <!-- Symptom Analysis -->
            <div class="mb-6 p-4 rounded-lg" :class="riskColorClass">
              <h3 class="font-semibold mb-2">{{ diagnosisResult.symptom_analysis.risk_level }}</h3>
              <p class="text-sm mb-2">{{ diagnosisResult.symptom_analysis.clinical_advice }}</p>
              <ul v-if="diagnosisResult.symptom_analysis.red_flags.length > 0" class="text-sm">
                <li v-for="(flag, i) in diagnosisResult.symptom_analysis.red_flags" :key="i" class="text-red-600 dark:text-red-400">
                  ⚠️ {{ flag }}
                </li>
              </ul>
            </div>

            <!-- Test Evaluation -->
            <div class="mb-6">
              <h3 class="font-semibold mb-2 text-gray-800 dark:text-gray-200">Test Evaluation</h3>
              <p class="text-lg font-medium text-gray-900 dark:text-white mb-2">{{ diagnosisResult.test_evaluation.diagnosis }}</p>
              <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                <p v-for="(finding, i) in diagnosisResult.test_evaluation.findings" :key="i">{{ finding }}</p>
              </div>
              <p class="text-sm mt-2 font-medium">Confidence: {{ diagnosisResult.test_evaluation.confidence_percent }}%</p>
            </div>

            <!-- ML Prediction -->
            <div v-if="diagnosisResult.ml_prediction" class="mb-6 p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
              <h3 class="font-semibold mb-2 text-blue-800 dark:text-blue-300">ML Prediction</h3>
              <p class="text-sm text-blue-700 dark:text-blue-400">Prediction: {{ diagnosisResult.ml_prediction.prediction }}</p>
              <p class="text-sm text-blue-700 dark:text-blue-400">
                Drug Sensitive: {{ diagnosisResult.ml_prediction.probability_sensitive }}% | 
                Drug Resistant: {{ diagnosisResult.ml_prediction.probability_drug_resistant }}%
              </p>
            </div>

            <!-- Treatment -->
            <div class="mb-4">
              <h3 class="font-semibold mb-2 text-gray-800 dark:text-gray-200">Treatment Recommendation</h3>
              <div class="bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 rounded-lg p-4">
                <p class="font-medium text-emerald-700 dark:text-emerald-300 mb-1">{{ diagnosisResult.treatment_recommendation.type }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Category:</strong> {{ diagnosisResult.treatment_recommendation.category }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Drugs:</strong> {{ diagnosisResult.treatment_recommendation.drugs }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Duration:</strong> {{ diagnosisResult.treatment_recommendation.duration }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Dosage:</strong> {{ diagnosisResult.treatment_recommendation.dosage }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Administration:</strong> {{ diagnosisResult.treatment_recommendation.administration }}</p>
                <p class="text-sm text-emerald-600 dark:text-emerald-400 mb-1"><strong>Monitoring:</strong> {{ diagnosisResult.treatment_recommendation.monitoring }}</p>
                <p class="text-xs text-emerald-500 dark:text-emerald-500 mt-2">{{ diagnosisResult.treatment_recommendation.notes }}</p>
              </div>
            </div>

            <p class="text-xs text-gray-500 mt-4">
              Disclaimer: This system is for educational purposes only. Always consult with qualified medical professionals.
            </p>
          </div>
        </div>
      </div>

      <!-- Patients View -->
      <div v-if="currentView === 'patients'">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Patients</h2>
            <div class="flex gap-2">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search patients..."
                class="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
              <button
                @click="loadPatients"
                class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
              >
                🔄
              </button>
            </div>
          </div>
          
          <div v-if="patients.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No patients found. Add a patient through the diagnosis page.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">ID</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Name</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Age</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Gender</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">City</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Date</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="patient in patients"
                  :key="patient.id"
                  @click="showPatientDetail(patient)"
                  class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                >
                  <td class="py-3 px-4 text-gray-900 dark:text-white">{{ patient.patient_id }}</td>
                  <td class="py-3 px-4 text-gray-900 dark:text-white">{{ patient.first_name }} {{ patient.last_name }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ patient.age }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ patient.gender }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ patient.city }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ formatDate(patient.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Alerts View -->
      <div v-if="currentView === 'alerts'">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Alerts</h2>
            <button
              @click="loadAlerts"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
            >
              🔄 Refresh
            </button>
          </div>
          
          <div v-if="alerts.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">
            No alerts.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="alert in alerts"
              :key="alert.id"
              @click="markAsRead(alert)"
              class="p-4 rounded-lg border cursor-pointer transition"
              :class="alert.is_read
                ? 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-600'
                : 'bg-white dark:bg-gray-700 border-emerald-200 dark:border-emerald-700'"
            >
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-medium" :class="alert.severity === 'high' ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'">
                    {{ alert.severity === 'high' ? '🚨' : '⚠️' }} {{ alert.alert_type }}
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ alert.message }}</p>
                  <p class="text-xs text-gray-400 mt-1">{{ formatDate(alert.created_at) }}</p>
                </div>
                <span v-if="!alert.is_read" class="w-2 h-2 bg-emerald-500 rounded-full"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = 'http://localhost:5000/api'

const isDarkMode = ref(false)
const currentView = ref('diagnose')
const loading = ref(false)
const searchQuery = ref('')
const patients = ref([])
const alerts = ref([])
const diagnosisResult = ref(null)

const tabs = [
  { id: 'diagnose', label: 'Diagnose', icon: '🏥' },
  { id: 'patients', label: 'Patients', icon: '👥' },
  { id: 'alerts', label: 'Alerts', icon: '🔔' }
]

const patient = ref({
  patient_id: '',
  first_name: '',
  last_name: '',
  age: 30,
  gender: 'Male',
  city: '',
  symptoms: '',
  sputum_smear_test: 'Unknown',
  genexpert_test: 'Unknown',
  chest_xray: 'Unknown',
  drug_resistance: 'No',
  hiv: 'No',
  diabetes: 'No'
})

const unreadAlerts = computed(() => alerts.value.filter(a => !a.is_read).length)

const riskColorClass = computed(() => {
  if (!diagnosisResult.value) return 'bg-gray-100 dark:bg-gray-700'
  const risk = diagnosisResult.value.symptom_analysis.risk_level
  if (risk.includes('High')) return 'bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-700'
  if (risk.includes('Moderate')) return 'bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-300 dark:border-yellow-700'
  return 'bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-700'
})

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

async function diagnosePatient() {
  loading.value = true
  try {
    const response = await fetch(`${API_BASE}/diagnose`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient: patient.value })
    })
    diagnosisResult.value = await response.json()
    
    // Save patient first if needed
    if (patient.value.patient_id) {
      await fetch(`${API_BASE}/patients`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(patient.value)
      })
      await loadPatients()
      await loadAlerts()
    }
  } catch (error) {
    console.error('Diagnosis error:', error)
  } finally {
    loading.value = false
  }
}

async function loadPatients() {
  try {
    const response = await fetch(`${API_BASE}/patients?search=${searchQuery.value}`)
    const data = await response.json()
    patients.value = data.patients || []
  } catch (error) {
    console.error('Load patients error:', error)
  }
}

async function loadAlerts() {
  try {
    const response = await fetch(`${API_BASE}/alerts`)
    const data = await response.json()
    alerts.value = data.alerts || []
  } catch (error) {
    console.error('Load alerts error:', error)
  }
}

async function markAsRead(alert) {
  if (alert.is_read) return
  try {
    await fetch(`${API_BASE}/alerts/${alert.id}/read`, { method: 'PUT' })
    alert.is_read = true
  } catch (error) {
    console.error('Mark read error:', error)
  }
}

function showPatientDetail(patientData) {
  patient.value = { ...patient.value, ...patientData }
  currentView.value = 'diagnose'
}

onMounted(() => {
  loadPatients()
  loadAlerts()
})
</script>
