<template>
  <DashboardLayout page-title="Prescriptions">
    <div class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Prescriptions</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ prescriptions.length }}</p>
        </div>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl border border-yellow-200 dark:border-yellow-800">
          <p class="text-sm text-yellow-700 dark:text-yellow-400">Pending</p>
          <p class="text-2xl font-bold text-yellow-700 dark:text-yellow-400 mt-1">{{ pendingCount }}</p>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl border border-green-200 dark:border-green-800">
          <p class="text-sm text-green-700 dark:text-green-400">Approved</p>
          <p class="text-2xl font-bold text-green-700 dark:text-green-400 mt-1">{{ approvedCount }}</p>
        </div>
        <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl border border-red-200 dark:border-red-800">
          <p class="text-sm text-red-700 dark:text-red-400">Rejected</p>
          <p class="text-2xl font-bold text-red-700 dark:text-red-400 mt-1">{{ rejectedCount }}</p>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Patient ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Medication</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Dosage</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Status</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Date</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="presc in prescriptions" :key="presc.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition">
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300 font-mono">{{ presc.id }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ presc.patient_id }}</td>
                <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{{ presc.medication }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ presc.dosage }} ({{ presc.duration }})</td>
                <td class="px-6 py-4">
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold',
                    presc.status === 'approved' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                    presc.status === 'rejected' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                    'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  ]">
                    {{ presc.status.charAt(0).toUpperCase() + presc.status.slice(1) }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">{{ presc.created_at ? new Date(presc.created_at).toLocaleDateString() : 'Unknown' }}</td>
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
const { getPrescriptions } = useApi();

const prescriptions = ref<any[]>([]);

const pendingCount = computed(() => prescriptions.value.filter(p => p.status === 'pending').length);
const approvedCount = computed(() => prescriptions.value.filter(p => p.status === 'approved').length);
const rejectedCount = computed(() => prescriptions.value.filter(p => p.status === 'rejected').length);

onMounted(async () => {
  const res = await getPrescriptions();
  prescriptions.value = (res as any).prescriptions || [];
});
</script>
