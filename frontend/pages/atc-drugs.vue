<template>
  <DashboardLayout page-title="ATC Drugs">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">ATC Drug Directory</h2>
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          Total: {{ totalDrugs }} drugs
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">ATC Code</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Drug Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Level 1</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Level 2</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Level 3</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Level 4</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Level 5</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">DDD</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Unit</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Route</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="drug in atcDrugs" :key="drug.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm font-mono text-emerald-600 dark:text-emerald-400">{{ drug.atc_code }}</td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ drug.drug_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.atc_level_1 }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.atc_level_2 }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.atc_level_3 }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.atc_level_4 }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.atc_level_5 }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.ddd }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.ddd_unit }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ drug.administration_route }}</td>
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
const { getAtcDrugs } = useApi();

const atcDrugs = ref<any[]>([]);
const currentPage = ref(1);
const perPage = 20;
const totalDrugs = ref(0);
const totalPages = ref(1);

const loadDrugs = async () => {
  const res = await getAtcDrugs(currentPage.value, perPage);
  atcDrugs.value = (res as any).atc_drugs || [];
  totalDrugs.value = (res as any).total || 0;
  totalPages.value = (res as any).pages || 1;
};

watch(currentPage, () => loadDrugs());

onMounted(async () => {
  await loadDrugs();
});
</script>
