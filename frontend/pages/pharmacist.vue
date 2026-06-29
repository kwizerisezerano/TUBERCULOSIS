<template>
  <DashboardLayout>
    <div class="space-y-6">
      <!-- Header -->
      <div class="flex justify-between items-center">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Pharmacy Dashboard</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-1">Review prescriptions, check stock, and dispense medications</p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Pending Prescriptions</p>
          <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{{ stats.pending }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Approved Today</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ stats.approved }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Dispensed Today</p>
          <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ stats.dispensed }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Low Stock Alerts</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ stats.lowStock }}</p>
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
              Pending Prescriptions
            </button>
            <button
              @click="activeTab = 'inventory'"
              :class="activeTab === 'inventory' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
              class="px-6 py-4 border-b-2 font-medium text-sm"
            >
              Inventory Management
            </button>
            <button
              @click="activeTab = 'history'"
              :class="activeTab === 'history' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'"
              class="px-6 py-4 border-b-2 font-medium text-sm"
            >
              Dispense History
            </button>
          </nav>
        </div>

        <!-- Pending Prescriptions Tab -->
        <div v-if="activeTab === 'pending'" class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patient</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Medication</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Dosage</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Duration</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Stock</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="presc in pendingPrescriptions" :key="presc.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.patient_name || `Patient #${presc.patient_id}` }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.medication }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.dosage }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.duration_days }} days
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <span v-if="presc.stockCheck" :class="presc.stockCheck.available ? 'text-green-600' : 'text-red-600'">
                      {{ presc.stockCheck?.stock_quantity || 'Checking...' }}
                    </span>
                    <span v-else class="text-gray-500">-</span>
                  </td>
                  <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getStatusColor(presc.status)">
                      {{ presc.status }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm space-x-2">
                    <button
                      v-if="presc.status === 'pending'"
                      @click="checkStock(presc)"
                      class="text-blue-600 hover:text-blue-900 dark:text-blue-400"
                    >
                      Check Stock
                    </button>
                    <button
                      v-if="presc.status === 'pending' && presc.stockCheck?.available"
                      @click="approvePrescription(presc)"
                      class="text-green-600 hover:text-green-900 dark:text-green-400"
                    >
                      Approve
                    </button>
                    <button
                      v-if="presc.status === 'approved'"
                      @click="dispensePrescription(presc)"
                      class="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400"
                    >
                      Dispense
                    </button>
                    <button
                      v-if="presc.status === 'pending'"
                      @click="rejectPrescription(presc)"
                      class="text-red-600 hover:text-red-900 dark:text-red-400"
                    >
                      Reject
                    </button>
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <span v-if="presc.stockCheck" :class="presc.stockCheck.available ? 'text-green-600' : 'text-red-600'">
                      {{ presc.stockCheck.available ? `✓ ${presc.stockCheck.stock_quantity} in stock` : `✗ ${presc.stockCheck.message}` }}
                    </span>
                    <span v-else class="text-gray-400">-</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="pendingPrescriptions.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            No pending prescriptions
          </div>
        </div>

        <!-- Inventory Tab -->
        <div v-if="activeTab === 'inventory'" class="p-6">
          <div class="flex justify-between mb-4">
            <input
              v-model="inventorySearch"
              type="text"
              placeholder="Search inventory..."
              class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
            <button
              @click="showAddInventoryModal = true"
              class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
            >
              Add Inventory
            </button>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Drug</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Stock</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Unit</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Batch</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Expiry</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Location</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="item in filteredInventory" :key="item.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ item.atc_drug?.drug_name || 'Unknown' }}
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <span :class="item.stock_quantity <= item.minimum_stock_level ? 'text-red-600 font-bold' : 'text-gray-900 dark:text-white'">
                      {{ item.stock_quantity }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ item.unit_type }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ item.batch_number || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ item.expiry_date || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ item.location || 'N/A' }}
                  </td>
                  <td class="px-6 py-4 text-sm">
                    <button
                      @click="editInventory(item)"
                      class="text-blue-600 hover:text-blue-900 dark:text-blue-400 mr-3"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- History Tab -->
        <div v-if="activeTab === 'history'" class="p-6">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Patient</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Medication</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Dispensed By</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="presc in dispensedPrescriptions" :key="presc.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(presc.dispensed_at) }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.patient_name || `Patient #${presc.patient_id}` }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ presc.medication }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    Pharmacist #{{ presc.dispensed_by }}
                  </td>
                  <td class="px-6 py-4">
                    <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                      {{ presc.status }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="dispensedPrescriptions.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            No dispense history
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>

  <!-- Rejection Reason Modal -->
  <InputModal
    :is-open="showRejectionModal"
    title="Reject Prescription"
    message="Please enter the reason for rejecting this prescription:"
    placeholder="Enter rejection reason"
    @close="showRejectionModal = false"
    @confirm="confirmRejectPrescription"
  />

  <!-- Edit Inventory Modal -->
  <InputModal
    :is-open="showEditInventoryModal"
    title="Edit Stock Quantity"
    :message="`Enter new stock quantity (current: ${editingInventoryItem?.stock_quantity || 0}):`"
    placeholder="Enter new quantity"
    :initial-value="editingInventoryItem?.stock_quantity?.toString() || ''"
    @close="showEditInventoryModal = false"
    @confirm="confirmEditInventory"
  />

  <!-- Add Inventory Modal -->
  <div v-if="showAddInventoryModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showAddInventoryModal = false"></div>
    <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Add Inventory</h3>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Hospital ID</label>
          <input v-model.number="newInventoryForm.hospital_id" type="number" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ATC Drug ID</label>
          <input v-model.number="newInventoryForm.atc_drug_id" type="number" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Stock Quantity</label>
          <input v-model.number="newInventoryForm.stock_quantity" type="number" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Unit Type</label>
          <select v-model="newInventoryForm.unit_type" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            <option value="tablets">Tablets</option>
            <option value="capsules">Capsules</option>
            <option value="ml">ML</option>
            <option value="vials">Vials</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Batch Number</label>
          <input v-model="newInventoryForm.batch_number" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Expiry Date</label>
          <input v-model="newInventoryForm.expiry_date" type="date" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Location</label>
          <input v-model="newInventoryForm.location" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Minimum Stock Level</label>
          <input v-model.number="newInventoryForm.minimum_stock_level" type="number" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
        </div>
      </div>
      <div class="flex gap-3 mt-6">
        <button @click="showAddInventoryModal = false" class="flex-1 py-3 px-4 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold transition-colors">
          Cancel
        </button>
        <button @click="addInventory" class="flex-1 py-3 px-4 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-semibold transition-colors">
          Add
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '~/composables/useAuth'
import InputModal from '~/components/InputModal.vue'

const { authToken, currentUser } = useAuth()

const activeTab = ref('pending')
const pendingPrescriptions = ref([])
const inventory = ref([])
const dispensedPrescriptions = ref([])
const inventorySearch = ref('')
const showAddInventoryModal = ref(false)
const showRejectionModal = ref(false)
const showEditInventoryModal = ref(false)
const rejectionReason = ref('')
const editInventoryQuantity = ref('')
const editingInventoryItem = ref(null)
const selectedPrescription = ref(null)
const newInventoryForm = ref({
  hospital_id: null,
  atc_drug_id: null,
  stock_quantity: 0,
  unit_type: 'tablets',
  batch_number: '',
  expiry_date: '',
  location: '',
  minimum_stock_level: 10
})

const API_BASE = 'http://127.0.0.1:5000/api'

const stats = computed(() => ({
  pending: pendingPrescriptions.value.filter(p => p.status === 'pending').length,
  approved: pendingPrescriptions.value.filter(p => p.status === 'approved').length,
  dispensed: dispensedPrescriptions.value.length,
  lowStock: inventory.value.filter(i => i.stock_quantity <= i.minimum_stock_level).length
}))

const filteredInventory = computed(() => {
  if (!inventorySearch.value) return inventory.value
  return inventory.value.filter(item => 
    item.atc_drug?.drug_name?.toLowerCase().includes(inventorySearch.value.toLowerCase())
  )
})

const getStatusColor = (status) => {
  const colors = {
    'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    'approved': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'rejected': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    'dispensed': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString()
}

const fetchPendingPrescriptions = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/prescriptions`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    pendingPrescriptions.value = (data.prescriptions || []).filter(p => p.status !== 'dispensed')
  } catch (error) {
    console.error('Error fetching prescriptions:', error)
  }
}

const fetchInventory = async () => {
  try {
    const token = authToken.value
    const response = await fetch('http://127.0.0.1:5000/api/pharmacy-inventory', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    inventory.value = data.inventory || []
  } catch (error) {
    console.error('Error fetching inventory:', error)
  }
}

const fetchDispensedHistory = async () => {
  try {
    const token = authToken.value
    const response = await fetch('http://127.0.0.1:5000/api/prescriptions', {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    dispensedPrescriptions.value = (data.prescriptions || []).filter(p => p.status === 'dispensed')
  } catch (error) {
    console.error('Error fetching history:', error)
  }
}

const checkStock = async (presc) => {
  try {
    const token = authToken.value
    const response = await fetch(`http://127.0.0.1:5000/api/prescriptions/${presc.id}/check-stock`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    presc.stockCheck = data
  } catch (error) {
    console.error('Error checking stock:', error)
  }
}

const approvePrescription = async (presc) => {
  try {
    const token = authToken.value
    const response = await fetch(`http://127.0.0.1:5000/api/prescriptions/${presc.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'approved' })
    })
    if (response.ok) {
      presc.status = 'approved'
      fetchPendingPrescriptions()
    }
  } catch (error) {
    console.error('Error approving prescription:', error)
  }
}

const dispensePrescription = async (presc) => {
  try {
    const token = authToken.value
    const response = await fetch(`http://127.0.0.1:5000/api/prescriptions/${presc.id}/dispense`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      presc.status = 'dispensed'
      fetchPendingPrescriptions()
      fetchDispensedHistory()
      fetchInventory()
    }
  } catch (error) {
    console.error('Error dispensing prescription:', error)
  }
}

const rejectPrescription = (presc) => {
  selectedPrescription.value = presc
  showRejectionModal.value = true
}

const confirmRejectPrescription = async () => {
  if (!rejectionReason.value) return
  
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/prescriptions/${selectedPrescription.value.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ status: 'rejected', rejection_reason: rejectionReason.value })
    })
    if (response.ok) {
      selectedPrescription.value.status = 'rejected'
      showRejectionModal.value = false
      rejectionReason.value = ''
      fetchPendingPrescriptions()
    }
  } catch (error) {
    console.error('Error rejecting prescription:', error)
  }
}

const editInventory = (item) => {
  editingInventoryItem.value = item
  showEditInventoryModal.value = true
}

const confirmEditInventory = async (value) => {
  if (!editingInventoryItem.value) return
  
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/pharmacy-inventory/${editingInventoryItem.value.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ stock_quantity: parseInt(value) })
    })
    if (response.ok) {
      editingInventoryItem.value.stock_quantity = parseInt(value)
      showEditInventoryModal.value = false
      editInventoryQuantity.value = ''
      fetchInventory()
    }
  } catch (error) {
    console.error('Error updating inventory:', error)
  }
}

const addInventory = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/pharmacy-inventory`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newInventoryForm.value)
    })
    if (response.ok) {
      showAddInventoryModal.value = false
      newInventoryForm.value = {
        hospital_id: null,
        atc_drug_id: null,
        stock_quantity: 0,
        unit_type: 'tablets',
        batch_number: '',
        expiry_date: '',
        location: '',
        minimum_stock_level: 10
      }
      fetchInventory()
    }
  } catch (error) {
    console.error('Error adding inventory:', error)
  }
}

onMounted(() => {
  fetchPendingPrescriptions()
  fetchInventory()
  fetchDispensedHistory()
})
</script>
