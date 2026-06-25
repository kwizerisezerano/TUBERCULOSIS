<template>
  <DashboardLayout page-title="Dashboard">
    <div class="space-y-6">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Patients</p>
              <p class="text-3xl font-bold text-white mt-1">{{ dashboard.patient_stats?.total || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-emerald-900/30 text-emerald-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Pending Prescriptions</p>
              <p class="text-3xl font-bold text-yellow-400 mt-1">{{ dashboard.prescription_stats?.pending || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-yellow-900/30 text-yellow-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.376c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Completed Lab Results</p>
              <p class="text-3xl font-bold text-blue-400 mt-1">{{ dashboard.lab_test_stats?.completed || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-blue-900/30 text-blue-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Approved Prescriptions</p>
              <p class="text-3xl font-bold text-green-400 mt-1">{{ dashboard.prescription_stats?.approved || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-green-900/30 text-green-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">Recent Patients</h3>
          <div v-if="patients.length" class="space-y-4">
            <div v-for="patient in patients.slice(0, 5)" :key="patient.id" class="flex items-center gap-4 p-4 rounded-xl bg-gray-700/50 hover:bg-gray-700 transition">
              <div class="h-12 w-12 rounded-full bg-emerald-900/30 text-emerald-400 flex items-center justify-center font-bold">
                {{ patient.first_name ? patient.first_name.charAt(0).toUpperCase() : "P" }}
              </div>
              <div class="flex-1">
                <p class="font-medium text-white">{{ patient.first_name }} {{ patient.last_name }}</p>
                <p class="text-sm text-gray-400">ID: {{ patient.patient_id }} · Age: {{ patient.age }}</p>
              </div>
              <div :class="['px-3 py-1 rounded-full text-xs font-semibold', getRiskInfo(patient).class]">
                {{ getRiskInfo(patient).text }}
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-400">
            No patients yet
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <h3 class="text-lg font-bold text-white mb-4">Antimicrobial Resistance Records</h3>
          <div v-if="arRecords.length" class="space-y-4 max-h-96 overflow-y-auto">
            <div v-for="record in arRecords.slice(0, 5)" :key="record.id" class="p-4 rounded-xl bg-gray-700/50 hover:bg-gray-700 transition">
              <div class="flex items-center justify-between mb-2">
                <p class="font-semibold text-white">{{ record.sample_id }}</p>
                <p class="text-xs text-gray-400">{{ record.bacterial_species || 'Unknown' }}</p>
              </div>
              <div class="flex flex-wrap gap-1">
                <span v-if="record.amx_amp === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">AMX/AMP R</span>
                <span v-if="record.cip === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">CIP R</span>
                <span v-if="record.gen === 'R'" class="px-2 py-0.5 text-xs rounded bg-red-900/30 text-red-400">GEN R</span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-400">
            No resistance records yet
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
const { getPatients, getDetailedLabResults, getAntibioticResistanceRecords, getDashboardStats } = useApi();

const patients = ref<any[]>([]);
const labResults = ref<any[]>([]);
const arRecords = ref<any[]>([]);
const dashboard = ref<any>({});

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

onMounted(async () => {
  try {
    const [dashRes, pRes, lRes, arRes] = await Promise.all([
      getDashboardStats(),
      getPatients(1, 100),
      getDetailedLabResults(),
      getAntibioticResistanceRecords(),
    ]);
    dashboard.value = dashRes;
    patients.value = (pRes as any).patients || [];
    labResults.value = (lRes as any)['detailed-lab-results'] || [];
    arRecords.value = (arRes as any)['antibiotic-resistance'] || [];
  } catch (e) {
    console.error('Failed to load data', e);
  }
});
</script>
