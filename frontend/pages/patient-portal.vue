<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <DashboardLayout>
      <template #sidebar>
        <Sidebar />
      </template>

      <div class="p-6">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white">Patient Portal</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-2">Manage your health information and consent preferences</p>
        </div>

        <!-- Patient Info Card -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Your Information</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Patient ID</label>
              <p class="text-gray-900 dark:text-white">{{ patient?.patient_id }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Name</label>
              <p class="text-gray-900 dark:text-white">{{ patient?.first_name }} {{ patient?.last_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Primary Hospital</label>
              <p class="text-gray-900 dark:text-white">{{ patient?.hospital?.name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">All Hospitals</label>
              <p class="text-gray-900 dark:text-white">{{ patient?.hospitals?.map((h: any) => h.name).join(', ') }}</p>
            </div>
          </div>
        </div>

        <!-- Consent Management Card -->
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6 mb-6">
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Data Sharing Consent</h2>
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            Control whether your medical data can be shared with other healthcare facilities for interoperability purposes.
          </p>
          
          <div class="flex items-center gap-4 mb-4">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Current Status:</span>
            <span
              :class="{
                'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200': patient?.data_sharing_consent === 'granted',
                'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200': patient?.data_sharing_consent === 'pending',
                'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200': patient?.data_sharing_consent === 'denied'
              }"
              class="px-3 py-1 rounded-full text-sm font-medium"
            >
              {{ patient?.data_sharing_consent?.toUpperCase() || 'PENDING' }}
            </span>
          </div>

          <div class="flex gap-3">
            <button
              @click="updateConsent('granted')"
              :disabled="isLoading || patient?.data_sharing_consent === 'granted'"
              class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              Grant Consent
            </button>
            <button
              @click="updateConsent('denied')"
              :disabled="isLoading || patient?.data_sharing_consent === 'denied'"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              Deny Consent
            </button>
          </div>

          <div v-if="patient?.consent_granted_at" class="mt-4 text-sm text-gray-600 dark:text-gray-400">
            <p>Consent granted: {{ new Date(patient.consent_granted_at).toLocaleDateString() }}</p>
            <p v-if="patient.consent_expires_at">Expires: {{ new Date(patient.consent_expires_at).toLocaleDateString() }}</p>
          </div>
        </div>

        <!-- Password Change Card - Hidden for now since we're skipping passwords
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-sm p-6">
      <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">Change Password</h2>
      <form @submit.prevent="changePassword" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Current Password</label>
          <input
            v-model="currentPassword"
            type="password"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">New Password</label>
          <input
            v-model="newPassword"
            type="password"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Confirm New Password</label>
          <input
            v-model="confirmPassword"
            type="password"
            class="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
          />
        </div>
        <button
          type="submit"
          :disabled="isLoading"
          class="px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
        >
          {{ isLoading ? 'Updating...' : 'Update Password' }}
        </button>
      </form>
      <p v-if="passwordMessage" :class="passwordError ? 'text-red-600' : 'text-green-600'" class="mt-2 text-sm">
        {{ passwordMessage }}
      </p>
    </div>
    -->
      </div>
    </DashboardLayout>
  </div>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue'
import Sidebar from '~/components/Sidebar.vue'

const { currentUser, authToken } = useAuth()
const router = useRouter()

const patient = ref<any>(null)
const isLoading = ref(false)
const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordMessage = ref('')
const passwordError = ref(false)

onMounted(async () => {
  if (!authToken.value) {
    router.push('/')
    return
  }
  
  // Fetch patient data
  try {
    const config = useRuntimeConfig()
    const data = await $fetch(`${config.public.apiBase}/patients/${currentUser.value?.id}`, {
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      }
    })
    patient.value = data.patient
  } catch (e) {
    console.error('Failed to fetch patient data:', e)
  }
})

const updateConsent = async (status: string) => {
  isLoading.value = true
  try {
    const config = useRuntimeConfig()
    await $fetch(`${config.public.apiBase}/patients/${patient.value?.id}/consent`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      },
      body: {
        data_sharing_consent: status
      }
    })
    // Refresh patient data
    const data = await $fetch(`${config.public.apiBase}/patients/${patient.value?.id}`, {
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      }
    })
    patient.value = data.patient
  } catch (e) {
    console.error('Failed to update consent:', e)
  }
  isLoading.value = false
}

const changePassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    passwordMessage.value = 'Passwords do not match'
    passwordError.value = true
    return
  }
  
  if (newPassword.value.length < 8) {
    passwordMessage.value = 'Password must be at least 8 characters'
    passwordError.value = true
    return
  }

  isLoading.value = true
  passwordMessage.value = ''
  
  try {
    const config = useRuntimeConfig()
    await $fetch(`${config.public.apiBase}/patients/${patient.value?.id}/password`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      },
      body: {
        current_password: currentPassword.value,
        new_password: newPassword.value
      }
    })
    passwordMessage.value = 'Password updated successfully'
    passwordError.value = false
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
  } catch (e) {
    passwordMessage.value = (e as any).data?.msg || 'Failed to update password'
    passwordError.value = true
  }
  
  isLoading.value = false
}
</script>
