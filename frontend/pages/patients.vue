<template>
  <DashboardLayout page-title="Patients">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
        <h2 class="text-xl font-bold text-white">Patient Records</h2>
        <div class="flex flex-col sm:flex-row items-center gap-3">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              v-model="searchQuery"
              @input="debounceLoadResults"
              type="text"
              placeholder="Search patients..."
              class="pl-10 pr-4 py-2 border border-gray-700 rounded-lg bg-gray-800 text-white focus:ring-2 focus:ring-emerald-500"
            />
          </div>
          <button class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            New Patient
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-gray-800 p-4 rounded-xl border border-gray-700">
          <p class="text-sm text-gray-400">Total Patients</p>
          <p class="text-2xl font-bold text-white mt-1">{{ totalPatients }}</p>
        </div>
        <div class="bg-red-900/20 p-4 rounded-xl border border-red-800">
          <p class="text-sm text-red-400">High Risk</p>
          <p class="text-2xl font-bold text-red-400 mt-1">{{ highRiskPatients }}</p>
        </div>
        <div class="bg-yellow-900/20 p-4 rounded-xl border border-yellow-800">
          <p class="text-sm text-yellow-400">Medium Risk</p>
          <p class="text-2xl font-bold text-yellow-400 mt-1">{{ mediumRiskPatients }}</p>
        </div>
        <div class="bg-green-900/20 p-4 rounded-xl border border-green-800">
          <p class="text-sm text-green-400">Low Risk</p>
          <p class="text-2xl font-bold text-green-400 mt-1">{{ lowRiskPatients }}</p>
        </div>
      </div>

      <div class="bg-gray-800 rounded-2xl shadow-sm border border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Age / Gender</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">City</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Symptoms</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-300">Risk Level</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-700">
              <tr
                v-for="patient in patients"
                :key="patient.id"
                class="hover:bg-gray-700/30 cursor-pointer transition"
              >
                <td class="px-6 py-4 text-sm text-gray-300 font-mono">{{ patient.patient_id }}</td>
                <td class="px-6 py-4">
                  <p class="font-medium text-white">{{ patient.first_name }} {{ patient.last_name }}</p>
                </td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ patient.age }} / {{ patient.gender }}</td>
                <td class="px-6 py-4 text-sm text-gray-300">{{ patient.city }}</td>
                <td class="px-6 py-4 text-sm text-gray-300 truncate max-w-xs">{{ patient.symptoms || 'No symptoms' }}</td>
                <td class="px-6 py-4">
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold', getRiskInfo(patient).class]">
                    {{ getRiskInfo(patient).text }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-gray-700/30 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-gray-300">
            Showing <span class="font-semibold">{{ (currentPage - 1) * perPage + 1 }}</span> to <span class="font-semibold">{{ Math.min(currentPage * perPage, totalPatients) }}</span> of <span class="font-semibold">{{ totalPatients }}</span> patients
          </p>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1 rounded border border-gray-700 text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
            >
              Previous
            </button>
            <div class="flex gap-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="currentPage = page"
                :class="['px-3 py-1 rounded text-sm font-medium transition',
                  page === currentPage
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                ]"
              >
                {{ page }}
              </button>
            </div>
            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 rounded border border-gray-700 text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-700"
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
const { getPatients } = useApi();

const patients = ref<any[]>([]);
const searchQuery = ref('');
const currentPage = ref(1);
const perPage = 20;
const totalPatients = ref(0);
const totalPages = ref(1);

function getRiskInfo(patient: any): { class: string; text: string } {
  let score = 0;
  if (patient.tb_status_label === 'Yes') score += 10;
  if (patient.genexpert_test === 'Positive') score += 8;
  if (patient.sputum_smear_test === 'Positive') score += 6;
  if (patient.chest_xray === 'Abnormal') score += 4;
  if (patient.has_fever === 'Yes') score += 1;
  if (patient.has_cough === 'Yes') score += 1;
  if (patient.has_weight_loss === 'Yes') score += 1;
  if (patient.has_night_sweats === 'Yes') score += 1;
  if (patient.has_chest_pain === 'Yes') score += 1;
  if (patient.has_blood === 'Yes') score += 2;

  if (score >= 8) {
    return { class: 'bg-red-900/30 text-red-400', text: 'High Risk' };
  } else if (score >= 4) {
    return { class: 'bg-yellow-900/30 text-yellow-400', text: 'Medium Risk' };
  } else {
    return { class: 'bg-green-900/30 text-green-400', text: 'Low Risk' };
  }
}

const highRiskPatients = computed(() => patients.value.filter(p => getRiskInfo(p).text === 'High Risk').length);
const mediumRiskPatients = computed(() => patients.value.filter(p => getRiskInfo(p).text === 'Medium Risk').length);
const lowRiskPatients = computed(() => patients.value.filter(p => getRiskInfo(p).text === 'Low Risk').length);

const visiblePages = computed(() => {
  const pages = [];
  const startPage = Math.max(1, currentPage.value - 2);
  const endPage = Math.min(totalPages.value, startPage + 4);
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  return pages;
});

let debounceTimer: number;
const debounceLoadResults = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    currentPage.value = 1;
    loadPatients();
  }, 300) as unknown as number;
};

const loadPatients = async () => {
  const res = await getPatients(currentPage.value, perPage, searchQuery.value);
  patients.value = (res as any).patients || [];
  totalPatients.value = (res as any).total || patients.value.length;
  totalPages.value = (res as any).pages || Math.ceil(totalPatients.value / perPage);
};

watch(currentPage, () => loadPatients());

onMounted(async () => {
  await loadPatients();
});
</script>
