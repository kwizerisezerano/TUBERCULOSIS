<template>
  <DashboardLayout>
    <div class="space-y-6">

      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">User Management</h1>
          <p class="text-gray-500 dark:text-gray-400">Users organised by hospital</p>
        </div>
        <button @click="openAddModal" class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl font-medium transition-colors flex items-center gap-2">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
          </svg>
          Add User
        </button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div v-for="stat in stats" :key="stat.label"
          class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 flex items-center gap-3">
          <div :class="stat.bg" class="h-10 w-10 rounded-xl flex items-center justify-center shrink-0">
            <svg class="w-5 h-5" :class="stat.icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.path"/>
            </svg>
          </div>
          <div>
            <p class="text-xl font-bold text-gray-900 dark:text-white">{{ stat.count }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400">{{ stat.label }}</p>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex flex-col sm:flex-row gap-3">
        <input v-model="searchQuery" type="text" placeholder="Search by username or email..."
          class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none text-sm"/>
        <select v-model="selectedRole"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none text-sm">
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="hospital_admin">Hospital Admin</option>
          <option value="doctor">Doctor</option>
          <option value="lab_technician">Lab Technician</option>
          <option value="pharmacist">Pharmacist</option>
        </select>
        <select v-model="selectedHospitalId"
          class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none text-sm">
          <option value="">All Hospitals</option>
          <option v-for="h in hospitalOptions" :key="h.id" :value="h.id">{{ h.name }}</option>
        </select>
      </div>

      <!-- Grouped by Hospital -->
      <div class="space-y-4">
        <div v-if="groupedUsers.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400 text-sm">
          No users found.
        </div>

        <div v-for="group in groupedUsers" :key="group.hospitalId"
          class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">

          <!-- Group header -->
          <div class="flex items-center justify-between px-5 py-3 bg-gray-50 dark:bg-gray-700/40 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center shrink-0">
                <svg class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
                </svg>
              </div>
              <div>
                <p class="font-semibold text-gray-900 dark:text-white text-sm">{{ group.hospitalName }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ group.users.length }} user{{ group.users.length !== 1 ? 's' : '' }}</p>
              </div>
            </div>
            <!-- Role count pills -->
            <div class="flex flex-wrap gap-1.5">
              <span v-for="(count, role) in group.roleCounts" :key="role"
                :class="getRoleBadgeClass(role)"
                class="px-2 py-0.5 rounded-full text-xs font-medium">
                {{ formatRole(role) }}: {{ count }}
              </span>
            </div>
          </div>

          <!-- User rows -->
          <div class="divide-y divide-gray-100 dark:divide-gray-700">
            <div v-for="user in group.users" :key="user.id"
              class="px-5 py-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between hover:bg-gray-50 dark:hover:bg-gray-700/20 transition-colors">

              <div class="flex items-center gap-3">
                <div class="h-9 w-9 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold text-sm shrink-0">
                  {{ user.username.charAt(0).toUpperCase() }}
                </div>
                <div>
                  <p class="font-medium text-gray-900 dark:text-white text-sm">{{ user.username }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ user.email }}</p>
                </div>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <span :class="getRoleBadgeClass(user.role)" class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ formatRole(user.role) }}
                </span>
                <span :class="user.is_active
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                    : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'"
                  class="px-2.5 py-0.5 rounded-full text-xs font-medium">
                  {{ user.is_active ? 'Active' : 'Inactive' }}
                </span>
                <span class="text-xs text-gray-400 dark:text-gray-500">{{ formatDate(user.created_at) }}</span>

                <div class="flex items-center gap-1 ml-1">
                  <button @click="editUser(user)" title="Edit"
                    class="p-1.5 rounded-lg text-primary-600 hover:bg-primary-50 dark:text-primary-400 dark:hover:bg-primary-900/20 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                    </svg>
                  </button>
                  <button @click="toggleUserStatus(user)" :title="user.is_active ? 'Deactivate' : 'Activate'"
                    class="p-1.5 rounded-lg text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"/>
                    </svg>
                  </button>
                  <button @click="confirmDelete(user)" title="Delete"
                    class="p-1.5 rounded-lg text-red-500 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Add / Edit Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-md p-6 space-y-4">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">{{ showEditModal ? 'Edit User' : 'Add User' }}</h2>
        <div class="space-y-3">
          <input v-model="form.username" type="text" placeholder="Username"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm outline-none focus:ring-2 focus:ring-primary-500"/>
          <input v-model="form.email" type="email" placeholder="Email"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm outline-none focus:ring-2 focus:ring-primary-500"/>
          <input v-model="form.password" type="password"
            :placeholder="showEditModal ? 'New password (leave blank to keep)' : 'Password'"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm outline-none focus:ring-2 focus:ring-primary-500"/>
          <select v-model="form.role"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm outline-none focus:ring-2 focus:ring-primary-500">
            <option value="">Select Role</option>
            <option value="admin">Admin</option>
            <option value="hospital_admin">Hospital Admin</option>
            <option value="doctor">Doctor</option>
            <option value="lab_technician">Lab Technician</option>
            <option value="pharmacist">Pharmacist</option>
          </select>
        </div>
        <p v-if="formError" class="text-sm text-red-500">{{ formError }}</p>
        <div class="flex justify-end gap-3 pt-2">
          <button @click="closeModal"
            class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            Cancel
          </button>
          <button @click="saveUser" :disabled="saving"
            class="px-4 py-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium transition-colors disabled:opacity-50">
            {{ saving ? 'Saving...' : (showEditModal ? 'Save Changes' : 'Add User') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirm Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl w-full max-w-sm p-6 space-y-4">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Delete User</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Are you sure you want to delete
          <span class="font-semibold text-gray-900 dark:text-white">{{ deletingUser?.username }}</span>?
          This cannot be undone.
        </p>
        <div class="flex justify-end gap-3">
          <button @click="showDeleteModal = false"
            class="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
            Cancel
          </button>
          <button @click="deleteUser" :disabled="saving"
            class="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-medium transition-colors disabled:opacity-50">
            {{ saving ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>

  </DashboardLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuth } from '~/composables/useAuth'

const { authToken } = useAuth()
const config = useRuntimeConfig()
const API_BASE = config.public.apiBase

const users = ref([])
const searchQuery = ref('')
const selectedRole = ref('')
const selectedHospitalId = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteModal = ref(false)
const editingUser = ref(null)
const deletingUser = ref(null)
const saving = ref(false)
const formError = ref('')
const form = ref({ username: '', email: '', password: '', role: '' })

const ROLE_ORDER = ['admin', 'hospital_admin', 'doctor', 'lab_technician', 'pharmacist']

const stats = computed(() => [
  { label: 'Total Users',  count: users.value.length,                                        bg: 'bg-blue-100 dark:bg-blue-900/30',   icon: 'text-blue-600 dark:text-blue-400',   path: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z' },
  { label: 'Active',       count: users.value.filter(u => u.is_active).length,               bg: 'bg-green-100 dark:bg-green-900/30', icon: 'text-green-600 dark:text-green-400', path: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z' },
  { label: 'Doctors',      count: users.value.filter(u => u.role === 'doctor').length,        bg: 'bg-indigo-100 dark:bg-indigo-900/30', icon: 'text-indigo-600 dark:text-indigo-400', path: 'M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z' },
  { label: 'Lab Techs',    count: users.value.filter(u => u.role === 'lab_technician').length, bg: 'bg-orange-100 dark:bg-orange-900/30', icon: 'text-orange-600 dark:text-orange-400', path: 'M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z' },
  { label: 'Pharmacists',  count: users.value.filter(u => u.role === 'pharmacist').length,    bg: 'bg-pink-100 dark:bg-pink-900/30',   icon: 'text-pink-600 dark:text-pink-400',   path: 'M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4' },
])

const hospitalOptions = computed(() => {
  const seen = new Set()
  return users.value
    .reduce((acc, u) => {
      const id = u.hospital?.id ?? ''
      const name = u.hospital?.name || 'Unassigned'
      if (!seen.has(id)) { seen.add(id); acc.push({ id, name }) }
      return acc
    }, [])
    .sort((a, b) => a.name.localeCompare(b.name))
})

const filteredUsers = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return users.value.filter(u => {
    const matchQ    = !q || u.username.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)
    const matchRole = !selectedRole.value || u.role === selectedRole.value
    const matchHosp = !selectedHospitalId.value || String(u.hospital?.id ?? '') === String(selectedHospitalId.value)
    return matchQ && matchRole && matchHosp
  })
})

const groupedUsers = computed(() => {
  const map = new Map()
  filteredUsers.value.forEach(u => {
    const key  = u.hospital?.id ?? 'unassigned'
    const name = u.hospital?.name || 'Unassigned Hospital'
    if (!map.has(key)) map.set(key, { hospitalId: key, hospitalName: name, users: [], roleCounts: {} })
    const g = map.get(key)
    g.users.push(u)
    g.roleCounts[u.role] = (g.roleCounts[u.role] || 0) + 1
  })
  return [...map.values()]
    .map(g => ({
      ...g,
      users: [...g.users].sort((a, b) =>
        ROLE_ORDER.indexOf(a.role) - ROLE_ORDER.indexOf(b.role) || a.username.localeCompare(b.username)
      ),
      roleCounts: Object.fromEntries(
        ROLE_ORDER.filter(r => g.roleCounts[r]).map(r => [r, g.roleCounts[r]])
      )
    }))
    .sort((a, b) => a.hospitalName.localeCompare(b.hospitalName))
})

const formatDate = d => d ? new Date(d).toLocaleDateString() : 'N/A'

const formatRole = role => ({
  admin: 'Admin', hospital_admin: 'Hosp. Admin', doctor: 'Doctor',
  lab_technician: 'Lab Tech', pharmacist: 'Pharmacist'
}[role] || role)

const getRoleBadgeClass = role => ({
  admin:          'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
  hospital_admin: 'bg-pink-100 text-pink-700 dark:bg-pink-900/30 dark:text-pink-400',
  doctor:         'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  lab_technician: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
  pharmacist:     'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
}[role] || 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300')

const fetchUsers = async () => {
  try {
    const res = await fetch(`${API_BASE}/users`, { headers: { Authorization: `Bearer ${authToken.value}` } })
    users.value = (await res.json()).users || []
  } catch (e) { console.error(e) }
}

const openAddModal = () => {
  form.value = { username: '', email: '', password: '', role: '' }
  formError.value = ''
  showAddModal.value = true
}

const editUser = u => {
  editingUser.value = u
  form.value = { username: u.username, email: u.email, password: '', role: u.role }
  formError.value = ''
  showEditModal.value = true
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingUser.value = null
}

const saveUser = async () => {
  formError.value = ''
  if (!form.value.username || !form.value.email || !form.value.role) {
    formError.value = 'Username, email and role are required.'
    return
  }
  if (showAddModal.value && !form.value.password) {
    formError.value = 'Password is required.'
    return
  }
  saving.value = true
  try {
    const body = { username: form.value.username, email: form.value.email, role: form.value.role }
    if (form.value.password) body.password = form.value.password
    const url    = showEditModal.value ? `${API_BASE}/users/${editingUser.value.id}` : `${API_BASE}/users`
    const method = showEditModal.value ? 'PUT' : 'POST'
    const res = await fetch(url, {
      method,
      headers: { Authorization: `Bearer ${authToken.value}`, 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    })
    if (!res.ok) { formError.value = (await res.json()).msg || 'Failed to save user.'; return }
    await fetchUsers()
    closeModal()
  } catch { formError.value = 'Network error.' } finally { saving.value = false }
}

const toggleUserStatus = async u => {
  try {
    const res = await fetch(`${API_BASE}/users/${u.id}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${authToken.value}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_active: !u.is_active })
    })
    if (res.ok) u.is_active = !u.is_active
  } catch (e) { console.error(e) }
}

const confirmDelete = u => { deletingUser.value = u; showDeleteModal.value = true }

const deleteUser = async () => {
  saving.value = true
  try {
    const res = await fetch(`${API_BASE}/users/${deletingUser.value.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authToken.value}` }
    })
    if (res.ok) {
      users.value = users.value.filter(u => u.id !== deletingUser.value.id)
      showDeleteModal.value = false
    }
  } catch (e) { console.error(e) } finally { saving.value = false }
}

onMounted(fetchUsers)
</script>
