<template>
  <DashboardLayout>
    <div class="space-y-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Administration Panel</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">User Management</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Add, edit, and remove system users</p>
          <button @click="showUserManagement = true" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition">
            Manage Users
          </button>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">System Settings</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Configure system settings and preferences</p>
          <button @click="showSettings = true" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition">
            Settings
          </button>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">Model Performance</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Monitor ML model performance metrics</p>
          <button @click="showMetrics = true" class="w-full bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-sm transition">
            View Metrics
          </button>
        </div>
      </div>

      <!-- User Management Modal -->
      <div v-if="showUserManagement" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showUserManagement = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-4xl border border-gray-200 dark:border-gray-700 max-h-[90vh] overflow-y-auto">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">User Management</h3>
            <button @click="showUserManagement = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div class="mb-4">
            <button @click="showAddUserModal = true" class="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm">
              Add New User
            </button>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ID</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Username</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Email</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Role</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Status</th>
                  <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ user.id }}</td>
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ user.username }}</td>
                  <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ user.email }}</td>
                  <td class="px-4 py-3 text-sm">
                    <span class="px-2 py-1 text-xs font-medium rounded-full" :class="getRoleColor(user.role)">
                      {{ user.role }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm">
                    <span class="px-2 py-1 text-xs font-medium rounded-full" :class="user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-sm space-x-2">
                    <button @click="editUser(user)" class="text-blue-600 hover:text-blue-900 text-xs">
                      Edit
                    </button>
                    <button @click="toggleUserStatus(user)" :class="user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'" class="text-xs">
                      {{ user.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                    <button @click="deleteUser(user)" class="text-red-600 hover:text-red-900 text-xs">
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="users.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
            Loading users...
          </div>
        </div>
      </div>

      <!-- Add User Modal -->
      <div v-if="showAddUserModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showAddUserModal = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Add New User</h3>
            <button @click="showAddUserModal = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
              <input v-model="newUserForm.username" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input v-model="newUserForm.email" type="email" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
              <input v-model="newUserForm.password" type="password" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
              <select v-model="newUserForm.role" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="doctor">Doctor</option>
                <option value="lab_technician">Lab Technician</option>
                <option value="pharmacist">Pharmacist</option>
                <option value="hospital_admin">Hospital Admin</option>
                <option value="admin">Admin</option>
              </select>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showAddUserModal = false" class="flex-1 py-3 px-4 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold transition-colors">
              Cancel
            </button>
            <button @click="addUser" class="flex-1 py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold transition-colors">
              Add User
            </button>
          </div>
        </div>
      </div>

      <!-- Edit User Modal -->
      <div v-if="showEditUserModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showEditUserModal = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Edit User</h3>
            <button @click="showEditUserModal = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
              <input v-model="editUserForm.username" type="text" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input v-model="editUserForm.email" type="email" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
              <select v-model="editUserForm.role" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option value="doctor">Doctor</option>
                <option value="lab_technician">Lab Technician</option>
                <option value="pharmacist">Pharmacist</option>
                <option value="hospital_admin">Hospital Admin</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
              <select v-model="editUserForm.is_active" class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option :value="true">Active</option>
                <option :value="false">Inactive</option>
              </select>
            </div>
          </div>
          <div class="flex gap-3 mt-6">
            <button @click="showEditUserModal = false" class="flex-1 py-3 px-4 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold transition-colors">
              Cancel
            </button>
            <button @click="saveUserEdit" class="flex-1 py-3 px-4 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-semibold transition-colors">
              Save Changes
            </button>
          </div>
        </div>
      </div>

      <!-- Settings Modal -->
      <div v-if="showSettings" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showSettings = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">System Settings</h3>
            <button @click="showSettings = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <p class="text-gray-600 dark:text-gray-300">System settings are not yet implemented.</p>
        </div>
      </div>

      <!-- Metrics Modal -->
      <div v-if="showMetrics" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showMetrics = false"></div>
        <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">Model Performance</h3>
            <button @click="showMetrics = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          <p class="text-gray-600 dark:text-gray-300">Model performance metrics are not yet implemented.</p>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'
import DashboardLayout from '~/components/DashboardLayout.vue'

const { authToken } = useAuth()

const showUserManagement = ref(false)
const showSettings = ref(false)
const showMetrics = ref(false)
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const users = ref<any[]>([])
const editingUserId = ref<number | null>(null)

const API_BASE = 'http://127.0.0.1:5000/api'

const newUserForm = ref({
  username: '',
  email: '',
  password: '',
  role: 'doctor'
})

const editUserForm = ref({
  username: '',
  email: '',
  role: 'doctor',
  is_active: true
})

const fetchUsers = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/users`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await response.json()
    users.value = data.users || []
  } catch (error) {
    console.error('Error fetching users:', error)
  }
}

const addUser = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/users`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(newUserForm.value)
    })
    if (response.ok) {
      showAddUserModal.value = false
      newUserForm.value = {
        username: '',
        email: '',
        password: '',
        role: 'doctor'
      }
      fetchUsers()
    } else {
      const data = await response.json()
      alert(data.msg || 'Failed to add user')
    }
  } catch (error) {
    console.error('Error adding user:', error)
  }
}

const editUser = (user: any) => {
  editingUserId.value = user.id
  editUserForm.value = {
    username: user.username,
    email: user.email,
    role: user.role,
    is_active: user.is_active
  }
  showEditUserModal.value = true
}

const saveUserEdit = async () => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/users/${editingUserId.value}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(editUserForm.value)
    })
    if (response.ok) {
      showEditUserModal.value = false
      editingUserId.value = null
      fetchUsers()
    } else {
      alert('Failed to update user')
    }
  } catch (error) {
    console.error('Error updating user:', error)
  }
}

const toggleUserStatus = async (user: any) => {
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/users/${user.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ is_active: !user.is_active })
    })
    if (response.ok) {
      user.is_active = !user.is_active
    }
  } catch (error) {
    console.error('Error toggling user status:', error)
  }
}

const deleteUser = async (user: any) => {
  if (!confirm(`Are you sure you want to delete user ${user.username}?`)) return
  
  try {
    const token = authToken.value
    const response = await fetch(`${API_BASE}/users/${user.id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    if (response.ok) {
      users.value = users.value.filter(u => u.id !== user.id)
    } else {
      alert('Failed to delete user')
    }
  } catch (error) {
    console.error('Error deleting user:', error)
  }
}

const getRoleColor = (role: string) => {
  const colors: Record<string, string> = {
    'admin': 'bg-purple-100 text-purple-800',
    'doctor': 'bg-blue-100 text-blue-800',
    'lab_technician': 'bg-green-100 text-green-800',
    'pharmacist': 'bg-yellow-100 text-yellow-800',
    'hospital_admin': 'bg-orange-100 text-orange-800'
  }
  return colors[role] || 'bg-gray-100 text-gray-800'
}

onMounted(() => {
  fetchUsers()
})
</script>
