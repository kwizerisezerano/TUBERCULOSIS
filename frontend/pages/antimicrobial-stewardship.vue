<template>
  <DashboardLayout page-title="Antimicrobial Stewardship">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Antimicrobial Resistance Records</h2>
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          Total: {{ totalRecords }} records
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Sample ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Patient</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Bacterial Species</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Resistance Profile</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="record in arRecords" :key="record.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ record.sample_id }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ record.patient_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ record.bacterial_species || 'Unknown' }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <span v-if="record.amx_amp === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">AMX/AMP R</span>
                    <span v-if="record.cip === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">CIP R</span>
                    <span v-if="record.gen === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">GEN R</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  <span v-if="isValidDate(record.collection_date)">{{ new Date(record.collection_date).toLocaleDateString() }}</span>
                  <span v-else>{{ record.collection_date || 'Unknown' }}</span>
                </td>
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
const { getAntibioticResistanceRecords } = useApi();

const arRecords = ref<any[]>([]);
const currentPage = ref(1);
const perPage = 20;
const totalRecords = ref(0);
const totalPages = ref(1);

const isValidDate = (dateString: any): boolean => {
  if (!dateString) return false;
  const date = new Date(dateString);
  return !isNaN(date.getTime());
};

const loadRecords = async () => {
  const res = await getAntibioticResistanceRecords(currentPage.value, perPage);
  arRecords.value = (res as any).antibiotic_resistance_records || [];
  totalRecords.value = (res as any).total || 0;
  totalPages.value = (res as any).pages || 1;
};

watch(currentPage, () => loadRecords());

onMounted(async () => {
  await loadRecords();
});
</script>
