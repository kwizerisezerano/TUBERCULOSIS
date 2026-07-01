<template>
  <DashboardLayout>
    <div class="space-y-6">
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Activity Log</h2>
          <div class="text-sm text-gray-500 dark:text-gray-400">
            Total: {{ totalLogs }} records
          </div>
        </div>
        <div v-if="loading" class="text-gray-500 dark:text-gray-400">Loading...</div>
        <div v-else-if="error" class="text-red-500">{{ error }}</div>
        <div v-else>
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Action</th>
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">User</th>
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Role</th>
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Details</th>
                  <th class="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">Timestamp</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="log in auditLogs" :key="log.id" class="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td class="py-3 px-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-300">
                      {{ formatAction(log.action) }}
                    </span>
                  </td>
                  <td class="py-3 px-4 text-sm text-gray-900 dark:text-white">{{ log.user?.username || 'Unknown' }}</td>
                  <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-300">{{ formatRole(log.user?.role) }}</td>
                  <td class="py-3 px-4 text-sm text-gray-600 dark:text-gray-300 max-w-xs truncate">{{ log.details || '-' }}</td>
                  <td class="py-3 px-4 text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">{{ formatDateTime(log.created_at) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="auditLogs.length === 0" class="text-center py-8 text-gray-500 dark:text-gray-400">No activity logs found.</div>
          
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <button 
              @click="loadPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Previous
            </button>
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
            </div>
            <button 
              @click="loadPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';

interface AuditLogUser {
  id?: number;
  username?: string;
  email?: string;
  role?: string;
}

interface AuditLog {
  id: number;
  action: string;
  user?: AuditLogUser;
  details?: string;
  created_at: string;
}

interface AuditLogsResponse {
  audit_logs: AuditLog[];
  pages: number;
  total: number;
}

const auditLogs = ref<AuditLog[]>([]);
const loading = ref(true);
const error = ref('');
const currentPage = ref(1);
const totalPages = ref(1);
const totalLogs = ref(0);

const formatAction = (action: string) => {
  if (!action) return '';
  return action.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase());
};

const formatRole = (role: string | null | undefined) => {
  if (!role) return 'Unknown';
  const roleMap: Record<string, string> = {
    admin: 'System Admin',
    doctor: 'Doctor',
    lab_technician: 'Lab Technician',
    pharmacist: 'Pharmacist',
    hospital_admin: 'Hospital Admin'
  };
  return roleMap[role] || role;
};

const formatDateTime = (timestamp: string) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: true
  });
};

const loadPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  await loadAuditLogs();
};

const loadAuditLogs = async () => {
  loading.value = true;
  try {
    const response = await $fetch<AuditLogsResponse>(`http://127.0.0.1:5000/api/audit-logs?page=${currentPage.value}&per_page=20`, {
      headers: {
        'Authorization': `Bearer ${useCookie('auth_token').value}`
      }
    });
    auditLogs.value = response.audit_logs || [];
    totalPages.value = response.pages || 1;
    totalLogs.value = response.total || 0;
  } catch (e: any) {
    error.value = e.message || 'Failed to load activity logs';
    console.error('Error loading activity logs:', e);
  } finally {
    loading.value = false;
  }
};

onMounted(async () => {
  await loadAuditLogs();
});
</script>
