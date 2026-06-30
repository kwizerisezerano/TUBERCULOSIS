<template>
  <DashboardLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Healthcare Facilities</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-1">Manage hospitals, health centers, laboratories, and pharmacies</p>
        </div>
        <button
          v-if="userRole === 'admin' || userRole === 'hospital_admin'"
          @click="showAddModal = true"
          class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Facility
        </button>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Facilities</p>
          <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{{ stats.total }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Hospitals</p>
          <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ stats.hospitals }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Health Centers</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ stats.health_centers }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Laboratories</p>
          <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ stats.laboratories }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Pharmacies</p>
          <p class="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-1">{{ stats.pharmacies }}</p>
        </div>
      </div>

      <!-- Facilities Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="p-5 border-b border-gray-200 dark:border-gray-700">
          <div class="flex gap-4">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search facilities..."
              class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <select
              v-model="filterType"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">All Types</option>
              <option value="Hospital">Hospitals</option>
              <option value="Health Center">Health Centers</option>
              <option value="Laboratory">Laboratories</option>
              <option value="Pharmacy">Pharmacies</option>
            </select>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Facility</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Type</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Location</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Capacity</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patients</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Source</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="hospital in filteredHospitals" :key="hospital.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                <td class="px-6 py-4">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10 bg-indigo-100 dark:bg-indigo-900 rounded-full flex items-center justify-center">
                      <svg class="h-6 w-6 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                      </svg>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900 dark:text-white">{{ hospital.name }}</div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">{{ hospital.hospital_id }}</div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getTypeColor(hospital.facility_type)">
                    {{ hospital.facility_type }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                  {{ hospital.city }}, {{ hospital.region }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                  {{ hospital.bed_capacity || 'N/A' }} beds
                </td>
                <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                  {{ hospital.patient_count || 0 }}
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  {{ hospital.source_dataset }}
                </td>
                <td class="px-6 py-4 text-sm">
                  <button
                    v-if="userRole === 'admin' || userRole === 'hospital_admin'"
                    @click="viewHospital(hospital)"
                    class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300 mr-3"
                  >
                    View
                  </button>
                  <button
                    v-if="userRole === 'admin' || userRole === 'hospital_admin'"
                    @click="editHospital(hospital)"
                    class="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-3"
                  >
                    Edit
                  </button>
                  <button
                    v-if="userRole === 'admin'"
                    @click="deleteHospital(hospital)"
                    class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-if="filteredHospitals.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
          No facilities found
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 w-full max-w-lg mx-4">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
          {{ showEditModal ? 'Edit Facility' : 'Add New Facility' }}
        </h2>
        <form @submit.prevent="saveHospital" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Facility Name</label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Facility Type</label>
            <select
              v-model="formData.facility_type"
              required
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="Hospital">Hospital</option>
              <option value="Health Center">Health Center</option>
              <option value="Laboratory">Laboratory</option>
              <option value="Pharmacy">Pharmacy</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">City</label>
              <input
                v-model="formData.city"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Region</label>
              <input
                v-model="formData.region"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bed Capacity</label>
              <input
                v-model.number="formData.bed_capacity"
                type="number"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ICU Beds</label>
              <input
                v-model.number="formData.icu_beds"
                type="number"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Address</label>
            <textarea
              v-model="formData.address"
              rows="2"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            ></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Phone</label>
              <input
                v-model="formData.phone"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input
                v-model="formData.email"
                type="email"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>
          <div class="flex justify-end gap-3 pt-4">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg"
            >
              {{ showEditModal ? 'Update' : 'Create' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'

const { authToken, currentUser } = useAuth()
const userRole = computed(() => currentUser.value?.role || '')

const API_BASE = 'http://127.0.0.1:5000/api'

const hospitals = ref([])
const searchQuery = ref('')
const filterType = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingHospital = ref(null)

const formData = ref({
  name: '',
  facility_type: 'Hospital',
  city: '',
  region: '',
  address: '',
  phone: '',
  email: '',
  bed_capacity: null,
  icu_beds: null
})

const stats = computed(() => {
  return {
    total: hospitals.value.length,
    hospitals: hospitals.value.filter(h => h.facility_type === 'Hospital').length,
    health_centers: hospitals.value.filter(h => h.facility_type === 'Health Center').length,
    laboratories: hospitals.value.filter(h => h.facility_type === 'Laboratory').length,
    pharmacies: hospitals.value.filter(h => h.facility_type === 'Pharmacy').length
  }
})

const filteredHospitals = computed(() => {
  return hospitals.value.filter(hospital => {
    const matchesSearch = 
      hospital.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      hospital.city.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      hospital.region.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesType = !filterType.value || hospital.facility_type === filterType.value
    return matchesSearch && matchesType
  })
})

const getTypeColor = (type) => {
  const colors = {
    'Hospital': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    'Health Center': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'Laboratory': 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    'Pharmacy': 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300'
  }
  return colors[type] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
}

const fetchHospitals = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/hospitals`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    const data = await response.json()
    hospitals.value = data.hospitals || []
  } catch (error) {
    console.error('Error fetching hospitals:', error)
  }
}

const saveHospital = async () => {
  try {
    const token = authToken.value
    const url = showEditModal.value 
      ? `${API_BASE}/hospitals/${editingHospital.value.id}`
      : `${API_BASE}/hospitals`
    
    const method = showEditModal.value ? 'PUT' : 'POST'
    
    console.log('Saving hospital:', { url, method, formData: formData.value })
    
    const response = await fetch(url, {
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })
    
    console.log('Response status:', response.status)
    
    if (response.ok) {
      closeModal()
      fetchHospitals()
    } else {
      const errorData = await response.json()
      console.error('Error response:', errorData)
      alert(`Error: ${errorData.msg || 'Failed to save hospital'}`)
    }
  } catch (error) {
    console.error('Error saving hospital:', error)
    alert(`Network error: ${error.message}`)
  }
}

const editHospital = (hospital) => {
  editingHospital.value = hospital
  formData.value = {
    name: hospital.name,
    facility_type: hospital.facility_type,
    city: hospital.city,
    region: hospital.region,
    address: hospital.address,
    phone: hospital.phone,
    email: hospital.email,
    bed_capacity: hospital.bed_capacity,
    icu_beds: hospital.icu_beds
  }
  showEditModal.value = true
}

const deleteHospital = async (hospital) => {
  if (!confirm(`Are you sure you want to delete ${hospital.name}?`)) return
  
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/hospitals/${hospital.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.ok) {
      fetchHospitals()
    }
  } catch (error) {
    console.error('Error deleting hospital:', error)
  }
}

const viewHospital = (hospital) => {
  // Navigate to hospital detail view
  console.log('View hospital:', hospital)
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingHospital.value = null
  formData.value = {
    name: '',
    facility_type: 'Hospital',
    city: '',
    region: '',
    address: '',
    phone: '',
    email: '',
    bed_capacity: null,
    icu_beds: null
  }
}

onMounted(() => {
  fetchHospitals()
})
</script>
