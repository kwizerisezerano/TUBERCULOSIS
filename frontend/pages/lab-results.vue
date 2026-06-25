<template>
  <DashboardLayout page-title="Lab Results">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-white">Laboratory Results</h2>
      </div>

      <div class="bg-gray-800 rounded-2xl shadow-sm border border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Test Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Value</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Reference Range</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Hospital</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              <tr
                v-for="result in labResults"
                :key="result.id"
                class="hover:bg-gray-700/30 transition"
              >
                <td class="px-6 py-4 text-sm font-medium text-white">{{ result.test_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ result.test_value }} {{ result.unit }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ result.reference_range }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ result.hospital }}</td>
                <td class="px-6 py-4 text-sm text-gray-400">{{ result.collection_date ? new Date(result.collection_date).toLocaleDateString() : 'Unknown' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
const { getDetailedLabResults } = useApi();

const labResults = ref<any[]>([]);

onMounted(async () => {
  const res = await getDetailedLabResults();
  labResults.value = (res as any)['detailed-lab-results'] || [];
});
</script>
