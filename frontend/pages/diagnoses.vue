<template>
  <DashboardLayout>
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row gap-4 justify-between items-center">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Diagnosis Records</h2>
        <div class="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          Total: {{ totalDiagnoses }} records
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Patient ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Diagnosis Type</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Risk Level</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Confidence</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="diagnosis in diagnoses" :key="diagnosis.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300 font-mono">{{ diagnosis.id }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ diagnosis.patient_id }}</td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ diagnosis.diagnosis_type }}</td>
                <td class="px-6 py-4">
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold', getRiskLevelClass(diagnosis.risk_level)]">
                    {{ diagnosis.risk_level || 'Unknown' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">
                  {{ diagnosis.confidence_percent ? `${diagnosis.confidence_percent}%` : 'N/A' }}
                </td>
                <td class="px-6 py-4">
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold',
                    diagnosis.status === 'completed'
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                      : 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  ]">
                    {{ diagnosis.status?.charAt(0).toUpperCase() + diagnosis.status?.slice(1) || 'Pending' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ diagnosis.created_at ? new Date(diagnosis.created_at).toLocaleDateString() : 'Unknown' }}</td>
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
const { getDiagnoses } = useApi();

const diagnoses = ref<any[]>([]);
const currentPage = ref(1);
const perPage = 20;
const totalDiagnoses = ref(0);
const totalPages = ref(1);

const getRiskLevelClass = (riskLevel: string | null) => {
  if (!riskLevel) return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
  const level = riskLevel.toLowerCase();
  if (level.includes('high')) return 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400';
  if (level.includes('moderate') || level.includes('medium')) return 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400';
  if (level.includes('low') || level.includes('minimal')) return 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400';
  return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300';
};

const loadDiagnoses = async () => {
  const res = await getDiagnoses(currentPage.value, perPage);
  diagnoses.value = (res as any).diagnoses || [];
  totalDiagnoses.value = (res as any).total || 0;
  totalPages.value = (res as any).pages || 1;
};

watch(currentPage, () => loadDiagnoses());

onMounted(async () => {
  await loadDiagnoses();
});
</script>
