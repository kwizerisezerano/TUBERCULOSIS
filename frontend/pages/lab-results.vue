<template>
  <DashboardLayout>
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Laboratory Test Results</h2>
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          Total: {{ totalResults }} results
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Test Type</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Result</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Patient ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Completed By</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Completed At</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="result in labResults" :key="result.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ result.test_type }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.results || 'Pending' }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.patient_id }}</td>
                <td class="px-6 py-4">
                  <span :class="['px-2 py-1 text-xs font-medium rounded-full', getStatusClass(result.status)]">
                    {{ result.status }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.completed_by || 'N/A' }}</td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ result.completed_at ? new Date(result.completed_at).toLocaleString() : 'N/A' }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <div class="text-sm text-gray-500 dark:text-gray-400">
            Page {{ currentPage }} of {{ totalPages }}
          </div>
          <div class="flex gap-2">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage <= 1"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-gray-700 dark:text-white transition"
            >
              Previous
            </button>
            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage >= totalPages"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-gray-700 dark:text-white transition"
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
import { useAuth } from '~/composables/useAuth';

const { authToken } = useAuth();

const labResults = ref<any[]>([]);
const currentPage = ref(1);
const perPage = 20;
const totalResults = ref(0);
const totalPages = ref(1);
const config = useRuntimeConfig()
const API_BASE = config.public.apiBase;

const getStatusClass = (status: string) => {
  const classes: Record<string, string> = {
    'requested': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    'in_progress': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    'completed': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
  };
  return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
};

const loadResults = async () => {
  try {
    const response = await fetch(`${API_BASE}/lab-tests?page=${currentPage.value}&per_page=${perPage}&status=completed`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    const data = await response.json();
    console.log('Lab tests response:', data);
    labResults.value = data.lab_tests || [];
    totalResults.value = data.total || 0;
    totalPages.value = data.pages || 1;
  } catch (error) {
    console.error('Error loading lab results:', error);
  }
};

watch(currentPage, () => loadResults());

onMounted(async () => {
  await loadResults();
});
</script>
