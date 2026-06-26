<template>
  <DashboardLayout page-title="Lab Results">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Laboratory Results</h2>
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          Total: {{ totalResults }} results
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Test Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Value</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Reference Range</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Hospital</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="result in labResults" :key="result.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ result.test_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.test_value }} {{ result.unit }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.reference_range }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ result.hospital }}</td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ result.collection_date ? new Date(result.collection_date).toLocaleDateString() : 'Unknown' }}</td>
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
const { getDetailedLabResults } = useApi();

const labResults = ref<any[]>([]);
const currentPage = ref(1);
const perPage = 20;
const totalResults = ref(0);
const totalPages = ref(1);

const loadResults = async () => {
  const res = await getDetailedLabResults(currentPage.value, perPage);
  labResults.value = (res as any).detailed_lab_results || [];
  totalResults.value = (res as any).total || 0;
  totalPages.value = (res as any).pages || 1;
};

watch(currentPage, () => loadResults());

onMounted(async () => {
  await loadResults();
});
</script>
