<template>
  <DashboardLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Cumulative Antibiogram</h1>
      
      <!-- Filters -->
      <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Bacterial Species</label>
            <select v-model="selectedSpecies" @change="fetchAntibiogram" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="">All Species</option>
              <option v-for="species in speciesList" :key="species" :value="species">{{ species }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Hospital</label>
            <select v-model="selectedHospital" @change="fetchAntibiogram" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option value="">All Hospitals</option>
              <option v-for="hospital in hospitals" :key="hospital.id" :value="hospital.id">{{ hospital.name }}</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Records</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ antibiogramData.total_records || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Bacterial Species</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ antibiogramData.species_count || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Antibiotics Tested</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ totalAntibiotics }}</p>
        </div>
      </div>

      <!-- Antibiogram Table -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Susceptibility by Species</h2>
        </div>
        
        <div v-if="loading" class="p-8 text-center text-gray-500 dark:text-gray-400">
          Loading...
        </div>
        
        <div v-else-if="antibiogramData.antibiogram && antibiogramData.antibiogram.length > 0" class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Bacterial Species</th>
                <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Antibiotic</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Tested</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Susceptible</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">Resistant</th>
                <th class="px-4 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase">% Susceptible</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="species in antibiogramData.antibiogram" :key="species.bacterial_species">
                <td :rowspan="species.antibiotics.length" class="px-4 py-3 font-medium text-gray-900 dark:text-white border-r border-gray-200 dark:border-gray-700">
                  {{ species.bacterial_species }}
                </td>
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ species.antibiotics[0].antibiotic }}</td>
                <td class="px-4 py-3 text-center text-gray-700 dark:text-gray-300">{{ species.antibiotics[0].total_tested }}</td>
                <td class="px-4 py-3 text-center text-green-600 dark:text-green-400">{{ species.antibiotics[0].susceptible_count }}</td>
                <td class="px-4 py-3 text-center text-red-600 dark:text-red-400">{{ species.antibiotics[0].resistant_count }}</td>
                <td class="px-4 py-3 text-center">
                  <span :class="getSusceptibilityClass(species.antibiotics[0].susceptibility_percentage)" class="px-2 py-1 rounded-full text-sm font-medium">
                    {{ species.antibiotics[0].susceptibility_percentage }}%
                  </span>
                </td>
              </tr>
              <tr v-for="(antibiotic, idx) in species.antibiotics.slice(1)" :key="antibiotic.antibiotic">
                <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ antibiotic.antibiotic }}</td>
                <td class="px-4 py-3 text-center text-gray-700 dark:text-gray-300">{{ antibiotic.total_tested }}</td>
                <td class="px-4 py-3 text-center text-green-600 dark:text-green-400">{{ antibiotic.susceptible_count }}</td>
                <td class="px-4 py-3 text-center text-red-600 dark:text-red-400">{{ antibiotic.resistant_count }}</td>
                <td class="px-4 py-3 text-center">
                  <span :class="getSusceptibilityClass(antibiotic.susceptibility_percentage)" class="px-2 py-1 rounded-full text-sm font-medium">
                    {{ antibiotic.susceptibility_percentage }}%
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-else class="p-8 text-center text-gray-500 dark:text-gray-400">
          No antibiogram data available
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import DashboardLayout from '~/components/DashboardLayout.vue';

const antibiogramData = ref<any>({});
const loading = ref(false);
const selectedSpecies = ref('');
const selectedHospital = ref('');
const speciesList = ref<string[]>([]);
const hospitals = ref<any[]>([]);

const totalAntibiotics = computed(() => {
  if (!antibiogramData.value.antibiogram) return 0;
  return antibiogramData.value.antibiogram.reduce((sum: number, species: any) => sum + species.antibiotics.length, 0);
});

const fetchAntibiogram = async () => {
  loading.value = true;
  try {
    const token = localStorage.getItem('auth_token');
    const params = new URLSearchParams();
    if (selectedSpecies.value) params.append('bacterial_species', selectedSpecies.value);
    if (selectedHospital.value) params.append('hospital_id', selectedHospital.value.toString());
    
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/antibiogram?${params}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    antibiogramData.value = data;
    
    // Extract species list
    if (data.antibiogram) {
      speciesList.value = [...new Set(data.antibiogram.map((s: any) => s.bacterial_species))];
    }
  } catch (error) {
    console.error('Failed to fetch antibiogram:', error);
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

const getSusceptibilityClass = (percentage: number) => {
  if (percentage >= 80) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
  if (percentage >= 50) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
  return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
};

onMounted(() => {
  fetchAntibiogram();
  fetchHospitals();
});
</script>
