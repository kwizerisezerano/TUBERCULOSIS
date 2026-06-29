<template>
  <DashboardLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Laboratory Dashboard</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-1">Review test requests and submit lab results</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Pending Tests</p>
          <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{{ stats.pending }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Completed Today</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ stats.completed }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">In Progress</p>
          <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ stats.inProgress }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Tests</p>
          <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ stats.total }}</p>
        </div>
      </div>

      <!-- Tabs -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="flex -mb-px">
            <button
              @click="activeTab = 'pending'"
              :class="activeTab === 'pending' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
              class="px-6 py-4 border-b-2 font-medium text-sm"
            >
              Pending Requests
            </button>
            <button
              @click="activeTab = 'in-progress'"
              :class="activeTab === 'in-progress' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
              class="px-6 py-4 border-b-2 font-medium text-sm"
            >
              In Progress
            </button>
            <button
              @click="activeTab = 'completed'"
              :class="activeTab === 'completed' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
              class="px-6 py-4 border-b-2 font-medium text-sm"
            >
              Completed
            </button>
          </nav>
        </div>

        <!-- Pending Requests Tab -->
        <div v-if="activeTab === 'pending'" class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patient</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Test Type</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Requested By</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Requested At</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Priority</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="test in pendingTests" :key="test.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Patient #{{ test.patient_id }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ test.test_type }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Doctor #{{ test.requested_by }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(test.created_at) }}
                  </td>
                  <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300">
                      Normal
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm space-x-2">
                    <button
                      @click="startTest(test)"
                      class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    >
                      Start
                    </button>
                    <button
                      @click="submitResult(test)"
                      class="text-green-600 hover:text-green-900 dark:text-green-400"
                    >
                      Submit Result
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="pendingTests.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            No pending test requests
          </div>
        </div>

        <!-- In Progress Tab -->
        <div v-if="activeTab === 'in-progress'" class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patient</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Test Type</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Started At</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="test in inProgressTests" :key="test.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Patient #{{ test.patient_id }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ test.test_type }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(test.updated_at) }}
                  </td>
                  <td class="px-6 py-4 text-sm space-x-2">
                    <button
                      @click="submitResult(test)"
                      class="text-green-600 hover:text-green-900 dark:text-green-400"
                    >
                      Submit Result
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="inProgressTests.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            No tests in progress
          </div>
        </div>

        <!-- Completed Tab -->
        <div v-if="activeTab === 'completed'" class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patient</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Test Type</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Result</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Completed At</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Completed By</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="test in completedTests" :key="test.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Patient #{{ test.patient_id }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ test.test_type }}
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <span :class="getResultColor(test.results)">
                      {{ test.results || 'Pending' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(test.completed_at) }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Tech #{{ test.completed_by }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="completedTests.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            No completed tests
          </div>
        </div>
      </div>

      <!-- Submit Result Modal -->
      <div v-if="showResultModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-lg mx-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Submit Test Result</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Test Type</label>
              <input
                :value="selectedTest?.test_type"
                type="text"
                disabled
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Result</label>
              <select
                v-model="resultForm.results"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="">Select result...</option>
                <option value="Positive">Positive</option>
                <option value="Negative">Negative</option>
                <option value="Abnormal">Abnormal</option>
                <option value="Normal">Normal</option>
                <option value="Inconclusive">Inconclusive</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Notes</label>
              <textarea
                v-model="resultForm.notes"
                rows="3"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Additional notes about the test result..."
              ></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-3 mt-6">
            <button
              @click="showResultModal = false"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              @click="confirmSubmitResult"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg"
            >
              Submit
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'

const { authToken, currentUser } = useAuth()

const API_BASE = 'http://127.0.0.1:5000/api'

const activeTab = ref('pending')
const pendingTests = ref([])
const inProgressTests = ref([])
const completedTests = ref([])
const showResultModal = ref(false)
const selectedTest = ref(null)
const resultForm = ref({
  results: '',
  notes: ''
})

const stats = computed(() => ({
  pending: pendingTests.value.length,
  completed: completedTests.value.filter(t => isToday(t.completed_at)).length,
  inProgress: inProgressTests.value.length,
  total: pendingTests.value.length + inProgressTests.value.length + completedTests.value.length
}))

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

const isToday = (dateStr) => {
  if (!dateStr) return false
  const date = new Date(dateStr)
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

const getResultColor = (result) => {
  if (!result) return 'text-gray-500'
  const colors = {
    'Positive': 'text-red-600 font-bold',
    'Negative': 'text-green-600',
    'Abnormal': 'text-yellow-600',
    'Normal': 'text-blue-600',
    'Inconclusive': 'text-gray-600'
  }
  return colors[result] || 'text-gray-600'
}

const fetchPendingTests = async () => {
  try {
    const token = authToken.value
    const response = await fetch('http://127.0.0.1:5000/api/lab-tests/pending', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    pendingTests.value = data.pending_tests || []
  } catch (error) {
    console.error('Error fetching pending tests:', error)
  }
}

const fetchAllTests = async () => {
  try {
    const token = authToken.value
    const response = await fetch('http://127.0.0.1:5000/api/lab-tests', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    const allTests = data.lab_tests || []
    
    inProgressTests.value = allTests.filter(t => t.status === 'in_progress')
    completedTests.value = allTests.filter(t => t.status === 'completed')
  } catch (error) {
    console.error('Error fetching tests:', error)
  }
}

const startTest = async (test) => {
  try {
    const token = authToken.value
    const response = await fetch(`http://127.0.0.1:5000/api/lab-tests/${test.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'in_progress' })
    })
    if (response.ok) {
      test.status = 'in_progress'
      fetchPendingTests()
      fetchAllTests()
    }
  } catch (error) {
    console.error('Error starting test:', error)
  }
}

const submitResult = (test) => {
  selectedTest.value = test
  resultForm.value = { results: '', notes: '' }
  showResultModal.value = true
}

const confirmSubmitResult = async () => {
  if (!resultForm.value.results) {
    return
  }
  
  try {
    const token = authToken.value
    const response = await fetch(`http://127.0.0.1:5000/api/lab-tests/${selectedTest.value.id}/submit-result`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(resultForm.value)
    })
    if (response.ok) {
      showResultModal.value = false
      selectedTest.value = null
      fetchPendingTests()
      fetchAllTests()
    }
  } catch (error) {
    console.error('Error submitting result:', error)
  }
}

onMounted(() => {
  fetchPendingTests()
  fetchAllTests()
})
</script>
