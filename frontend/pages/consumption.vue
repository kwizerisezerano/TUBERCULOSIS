<template>
  <DashboardLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Antimicrobial Consumption Surveillance</h1>
      
      <!-- Filters -->
      <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">ATC Level</label>
            <select v-model="atcLevel" @change="fetchConsumption" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="1">Level 1 (Anatomical)</option>
              <option value="2">Level 2 (Therapeutic)</option>
              <option value="3">Level 3 (Pharmacological)</option>
              <option value="4">Level 4 (Chemical)</option>
              <option value="5">Level 5 (Substance)</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Start Date</label>
            <input type="date" v-model="startDate" @change="fetchConsumption" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">End Date</label>
            <input type="date" v-model="endDate" @change="fetchConsumption" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Hospital</label>
            <select v-model="selectedHospital" @change="fetchConsumption" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="">All Hospitals</option>
              <option v-for="hospital in hospitals" :key="hospital.id" :value="hospital.id">{{ hospital.name }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Prescriptions</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ consumptionData.total_prescriptions || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total DDDs</p>
          <p class="text-3xl font-bold text-primary-600 dark:text-primary-400 mt-1">{{ totalDDDs }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Mg</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ totalMg }}</p>
        </div>
      </div>

      <!-- Consumption Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Consumption by ATC Group</h2>
        </div>
        
        <div v-if="loading" class="p-8 text-center text-gray-500 dark:text-gray-400">
          Loading...
        </div>
        
        <div v-else-if="consumptionData.consumption_data && consumptionData.consumption_data.length > 0" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">ATC Code</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Name</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Prescriptions</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total DDDs</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Total Mg</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Drugs</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="item in consumptionData.consumption_data" :key="item.atc_code">
                <td class="px-4 py-3 font-mono text-sm text-gray-900 dark:text-white">{{ item.atc_code }}</td>
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ item.atc_name }}</td>
                <td class="px-4 py-3 text-center text-gray-700 dark:text-gray-300">{{ item.total_prescriptions }}</td>
                <td class="px-4 py-3 text-center font-bold text-primary-600 dark:text-primary-400">{{ item.total_ddds }}</td>
                <td class="px-4 py-3 text-center text-gray-700 dark:text-gray-300">{{ item.total_mg }}</td>
                <td class="px-4 py-3 text-gray-500 dark:text-gray-400 text-sm">{{ item.drugs.join(', ') }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="p-8 text-center text-gray-500 dark:text-gray-400">
          No consumption data available
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import DashboardLayout from '~/components/DashboardLayout.vue';

const consumptionData = ref<any>({});
const loading = ref(false);
const atcLevel = ref('2');
const startDate = ref('');
const endDate = ref('');
const selectedHospital = ref('');
const hospitals = ref<any[]>([]);

const totalDDDs = computed(() => {
  if (!consumptionData.value.consumption_data) return 0;
  return consumptionData.value.consumption_data.reduce((sum: number, item: any) => sum + item.total_ddds, 0).toFixed(2);
});

const totalMg = computed(() => {
  if (!consumptionData.value.consumption_data) return 0;
  return consumptionData.value.consumption_data.reduce((sum: number, item: any) => sum + item.total_mg, 0).toFixed(2);
});

const fetchConsumption = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('auth_token');
    const params = new URLSearchParams();
    params.append('atc_level', atcLevel.value);
    if (startDate.value) params.append('start_date', startDate.value);
    if (endDate.value) params.append('end_date', endDate.value);
    if (selectedHospital.value) params.append('hospital_id', selectedHospital.value.toString());
    
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/consumption-surveillance?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    consumptionData.value = data;
  } catch (error) {
    console.error('Failed to fetch consumption data:', error);
  } finally {
    loading.value = false;
  }
};

const fetchHospitals = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/hospitals`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    hospitals.value = data.hospitals || [];
  } catch (error) {
    console.error('Failed to fetch hospitals:', error);
  }
};

onMounted(() => {
  fetchConsumption();
  fetchHospitals();
});
</script>
