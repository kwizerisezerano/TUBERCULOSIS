<template>
  <DashboardLayout page-title="Antimicrobial Stewardship">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-white">Antimicrobial Resistance Records</h2>
      </div>

      <div class="bg-gray-800 rounded-2xl shadow-sm border border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Sample ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Patient</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Bacterial Species</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Resistance Profile</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              <tr
                v-for="record in arRecords"
                :key="record.id"
                class="hover:bg-gray-700/30 transition"
              >
                <td class="px-6 py-4 text-sm font-medium text-white">{{ record.sample_id }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ record.patient_name }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ record.bacterial_species || 'Unknown' }}</td>
                <td class="px-6 py-4">
                  <div class="flex flex-wrap gap-1">
                    <span v-if="record.amx_amp === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">AMX/AMP R</span>
                    <span v-if="record.cip === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">CIP R</span>
                    <span v-if="record.gen === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">GEN R</span>
                  </div>
                </td>
                <td class="px-6 py-4 text-sm text-gray-400">{{ record.collection_date ? new Date(record.collection_date).toLocaleDateString() : 'Unknown' }}</td>
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
const { getAntibioticResistanceRecords } = useApi();

const arRecords = ref<any[]>([]);

onMounted(async () => {
  const res = await getAntibioticResistanceRecords();
  arRecords.value = (res as any)['antibiotic-resistance'] || [];
});
</script>
