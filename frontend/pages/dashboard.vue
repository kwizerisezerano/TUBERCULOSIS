<template>
  <DashboardLayout page-title="Dashboard">
    <div class="space-y-6">
        <!-- First row of cards -->
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
              <p class="text-gray-400 text-sm">Total Diagnoses</p>
              <p class="text-3xl font-bold text-purple-400 mt-1">{{ dashboard.diagnosis_stats?.total || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-purple-900/30 text-purple-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3-7.5H18m-2.25 3H18m-2.25 3H18M4.5 4.5h15a2.25 2.25 0 012.25 2.25v10.5a2.25 2.25 0 01-2.25 2.25h-15A2.25 2.25 0 012.25 17.25V6.75A2.25 2.25 0 014.5 4.5z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Total Lab Results</p>
              <p class="text-3xl font-bold text-blue-400 mt-1">{{ dashboard.detailed_lab_stats?.total || 0 }}</p>
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
              <p class="text-gray-400 text-sm">Total Prescriptions</p>
              <p class="text-3xl font-bold text-green-400 mt-1">{{ (dashboard.prescription_stats?.pending || 0) + (dashboard.prescription_stats?.approved || 0) + (dashboard.prescription_stats?.rejected || 0) }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-green-900/30 text-green-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <!-- Second row of cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Antimicrobial Resistance</p>
              <p class="text-3xl font-bold text-red-400 mt-1">{{ dashboard.antimicrobial_resistance_stats?.total || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-red-900/30 text-red-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">ATC Drugs</p>
              <p class="text-3xl font-bold text-cyan-400 mt-1">{{ dashboard.atc_drug_stats?.total || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-cyan-900/30 text-cyan-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25l-1.875-1.875 1.875-1.875m-3.75 3.75l-1.875-1.875 1.875-1.875m3.75 3.75l-1.875-1.875 1.875-1.875M6 12a6 6 0 1012 0 6 6 0 00-12 0z" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">Treatments</p>
              <p class="text-3xl font-bold text-orange-400 mt-1">{{ dashboard.treatment_stats?.total || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-orange-900/30 text-orange-400 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 4.5l8.25 8.25m0 0l8.25-8.25m-8.25 8.25v8.25" />
              </svg>
            </div>
          </div>
        </div>
        <div class="bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-700">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-gray-400 text-sm">High Risk Patients</p>
              <p class="text-3xl font-bold text-red-500 mt-1">{{ dashboard.patient_stats?.high_risk || 0 }}</p>
            </div>
            <div class="h-14 w-14 rounded-xl bg-red-900/40 text-red-500 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-7 h-7">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
          <h3 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.603V11a6 6 0 10-12 0v3.603a2.032 2.032 0 01-.595 1.405L4 17h5m7z" />
            </svg>
            Alerts
            <span class="ml-auto bg-red-600 text-white text-xs px-2 py-1 rounded-full">{{ dashboard.alert_stats?.unread || 0 }} Unread</span>
          </h3>
          <div v-if="alerts.length" class="space-y-3 max-h-96 overflow-y-auto">
            <div v-for="alert in alerts.slice(0, 5)" :key="alert.id" 
                 @click="!alert.is_read && handleMarkAlertRead(alert.id)" 
                 class="p-4 rounded-xl bg-gray-700/50 hover:bg-gray-700 transition border-l-4 cursor-pointer" 
                 :class="getAlertBorderClass(alert.severity)">
              <div class="flex justify-between items-start">
                <div>
                  <p class="font-medium text-white" :class="getAlertTextClass(alert.severity)">{{ alert.alert_type.replace('_', ' ') }}</p>
                  <p class="text-sm text-gray-400">{{ alert.message }}</p>
                </div>
                <span v-if="!alert.is_read" class="h-2 w-2 rounded-full bg-red-500"></span>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-8 text-gray-400">
            No alerts yet
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
const { getPatients, getDetailedLabResults, getAntibioticResistanceRecords, getDashboardStats, getAlerts, markAlertRead } = useApi();

const patients = ref<any[]>([]);
const labResults = ref<any[]>([]);
const arRecords = ref<any[]>([]);
const alerts = ref<any[]>([]);
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

function getAlertBorderClass(severity: string): string {
  const classes: Record<string, string> = {
    'high': 'border-red-500',
    'medium': 'border-yellow-500',
    'warning': 'border-yellow-500',
    'info': 'border-blue-500'
  };
  return classes[severity] || 'border-gray-500';
}

function getAlertTextClass(severity: string): string {
  const classes: Record<string, string> = {
    'high': 'text-red-400',
    'medium': 'text-yellow-400',
    'warning': 'text-yellow-400',
    'info': 'text-blue-400'
  };
  return classes[severity] || 'text-gray-400';
}

async function handleMarkAlertRead(alertId: number) {
  try {
    await markAlertRead(alertId);
    // Update the local state
    const alertIndex = alerts.value.findIndex(a => a.id === alertId);
    if (alertIndex !== -1) {
      alerts.value[alertIndex].is_read = true;
    }
  } catch (e) {
    console.error('Failed to mark alert as read', e);
  }
}

onMounted(async () => {
  try {
    const [dashRes, pRes, lRes, arRes, alertsRes] = await Promise.all([
      getDashboardStats(),
      getPatients(1, 100),
      getDetailedLabResults(),
      getAntibioticResistanceRecords(),
      getAlerts(1, 50),
    ]);
    dashboard.value = dashRes;
    patients.value = (pRes as any).patients || [];
    labResults.value = (lRes as any).detailed_lab_results || [];
    arRecords.value = (arRes as any).antibiotic_resistance_records || [];
    alerts.value = (alertsRes as any).alerts || [];
  } catch (e) {
    console.error('Failed to load data', e);
  }
});
</script>
