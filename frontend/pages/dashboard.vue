<template>
  <DashboardLayout>
    <div class="space-y-6">

      <!-- Summary Cards Row 1 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Patients</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ dashboard.patient_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Diagnoses</p>
          <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ dashboard.diagnosis_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Lab Results</p>
          <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ dashboard.detailed_lab_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Prescriptions</p>
          <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ (dashboard.prescription_stats?.pending || 0) + (dashboard.prescription_stats?.approved || 0) + (dashboard.prescription_stats?.rejected || 0) }}</p>
        </div>
      </div>

      <!-- Summary Cards Row 2 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Antimicrobial Resistance</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ dashboard.antimicrobial_resistance_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">ATC Drugs</p>
          <p class="text-3xl font-bold text-cyan-600 dark:text-cyan-400 mt-1">{{ dashboard.atc_drug_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Treatments</p>
          <p class="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-1">{{ dashboard.treatment_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">High Risk Patients</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-500 mt-1">{{ dashboard.patient_stats?.high_risk || 0 }}</p>
        </div>
      </div>

      <!-- Charts Row 1: Risk + TB Status + Drug Resistance + Gender -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Patient Risk Levels</p>
          <canvas ref="riskChart" height="200"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">TB Status Distribution</p>
          <canvas ref="tbStatusChart" height="200"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Drug Resistance</p>
          <canvas ref="resistanceChart" height="200"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Gender Distribution</p>
          <canvas ref="genderChart" height="200"></canvas>
        </div>
      </div>

      <!-- Charts Row 2: Antibiogram (full width) -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
        <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Cumulative Antibiogram — Resistance Rate per Antibiotic (%)</p>
        <canvas ref="antibiogramChart" height="90"></canvas>
      </div>

      <!-- Charts Row 3: Symptoms + Test Positivity -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Symptom Prevalence (% of patients)</p>
          <canvas ref="symptomsChart" height="180"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Diagnostic Test Positivity (%)</p>
          <canvas ref="testsChart" height="180"></canvas>
        </div>
      </div>

      <!-- Charts Row 4: Bacterial Species + Comorbidities + Prescriptions -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Top Bacterial Species</p>
          <canvas ref="speciesChart" height="220"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Comorbidities (% of patients)</p>
          <canvas ref="comorbidityChart" height="220"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Prescription Status</p>
          <canvas ref="prescriptionChart" height="220"></canvas>
        </div>
      </div>

      <!-- Recent Patients + Alerts -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">Recent Patients</h3>
          <div v-if="patients.length" class="space-y-3">
            <div v-for="patient in patients.slice(0, 5)" :key="patient.id" class="flex items-center gap-3 p-3 rounded-xl bg-gray-100 dark:bg-gray-700/50">
              <div class="h-10 w-10 rounded-full bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 flex items-center justify-center font-bold text-sm">
                {{ patient.first_name?.charAt(0).toUpperCase() || 'P' }}
              </div>
              <div class="flex-1 min-w-0">
                <p class="font-medium text-gray-900 dark:text-white text-sm truncate">{{ patient.first_name }} {{ patient.last_name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ patient.patient_id }} · Age {{ patient.age }}</p>
              </div>
              <span :class="['px-2 py-0.5 rounded-full text-xs font-semibold', getRiskInfo(patient).class]">
                {{ getRiskInfo(patient).text }}
              </span>
            </div>
          </div>
          <p v-else class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">No patients yet</p>
        </div>

        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <h3 class="text-base font-bold text-gray-900 dark:text-white mb-4">
            Recent Alerts
            <span class="ml-2 bg-red-600 text-white text-xs px-2 py-0.5 rounded-full">{{ dashboard.alert_stats?.unread || 0 }} Unread</span>
          </h3>
          <div v-if="alerts.length" class="space-y-3 max-h-72 overflow-y-auto">
            <div v-for="alert in alerts.slice(0, 6)" :key="alert.id"
                 @click="!alert.is_read && handleMarkAlertRead(alert.id)"
                 class="p-3 rounded-xl bg-gray-100 dark:bg-gray-700/50 border-l-4 cursor-pointer"
                 :class="getAlertBorderClass(alert.severity)">
              <p class="text-sm font-medium" :class="getAlertTextClass(alert.severity)">{{ alert.alert_type.replace(/_/g, ' ') }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{{ alert.message }}</p>
            </div>
          </div>
          <p v-else class="text-center py-8 text-gray-500 dark:text-gray-400 text-sm">No alerts yet</p>
        </div>
      </div>

    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

import DashboardLayout from '~/components/DashboardLayout.vue';

const { getPatients, getDashboardStats, getAlerts, markAlertRead, getDashboardCharts } = useApi();

const patients = ref<any[]>([]);
const alerts = ref<any[]>([]);
const dashboard = ref<any>({});
const charts = ref<any>({});

// Canvas refs
const riskChart = ref<HTMLCanvasElement | null>(null);
const tbStatusChart = ref<HTMLCanvasElement | null>(null);
const resistanceChart = ref<HTMLCanvasElement | null>(null);
const genderChart = ref<HTMLCanvasElement | null>(null);
const antibiogramChart = ref<HTMLCanvasElement | null>(null);
const symptomsChart = ref<HTMLCanvasElement | null>(null);
const testsChart = ref<HTMLCanvasElement | null>(null);
const speciesChart = ref<HTMLCanvasElement | null>(null);
const comorbidityChart = ref<HTMLCanvasElement | null>(null);
const prescriptionChart = ref<HTMLCanvasElement | null>(null);

const chartInstances: Chart[] = [];

function destroyCharts() {
  chartInstances.forEach(c => c.destroy());
  chartInstances.length = 0;
}

function gridColor() {
  const isDark = document.documentElement.classList.contains('dark');
  return isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)';
}
function tickColor() {
  const isDark = document.documentElement.classList.contains('dark');
  return isDark ? '#9ca3af' : '#4b5563';
}

function makeBar(canvas: HTMLCanvasElement, labels: string[], data: number[], colors: string[], unit = '') {
  const c = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderRadius: 6, borderSkipped: false }] },
    options: {
      responsive: true, plugins: { legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => ` ${ctx.parsed.y}${unit}` } }
      },
      scales: {
        x: { ticks: { color: tickColor(), font: { size: 11 } }, grid: { color: gridColor() } },
        y: { ticks: { color: tickColor(), font: { size: 11 } }, grid: { color: gridColor() }, beginAtZero: true }
      }
    }
  });
  chartInstances.push(c);
}

function makeDoughnut(canvas: HTMLCanvasElement, labels: string[], data: number[], colors: string[]) {
  const c = new Chart(canvas, {
    type: 'doughnut',
    data: { labels, datasets: [{ data, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }] },
    options: {
      responsive: true, cutout: '65%',
      plugins: { legend: { position: 'bottom', labels: { color: tickColor(), boxWidth: 12, font: { size: 11 } } } }
    }
  });
  chartInstances.push(c);
}

function makeHorizontalBar(canvas: HTMLCanvasElement, labels: string[], data: number[], color: string, unit = '') {
  const c = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets: [{ data, backgroundColor: color, borderRadius: 4 }] },
    options: {
      indexAxis: 'y', responsive: true,
      plugins: { legend: { display: false },
        tooltip: { callbacks: { label: (ctx) => ` ${ctx.parsed.x}${unit}` } }
      },
      scales: {
        x: { ticks: { color: tickColor(), font: { size: 11 } }, grid: { color: gridColor() }, beginAtZero: true },
        y: { ticks: { color: tickColor(), font: { size: 11 } }, grid: { display: false } }
      }
    }
  });
  chartInstances.push(c);
}

function buildCharts(d: any) {
  destroyCharts();
  if (!d) return;

  if (riskChart.value && d.risk_distribution)
    makeBar(riskChart.value, d.risk_distribution.labels, d.risk_distribution.data, d.risk_distribution.colors);

  if (tbStatusChart.value && d.tb_status)
    makeDoughnut(tbStatusChart.value, d.tb_status.labels, d.tb_status.data, d.tb_status.colors);

  if (resistanceChart.value && d.drug_resistance)
    makeBar(resistanceChart.value, d.drug_resistance.labels, d.drug_resistance.data, d.drug_resistance.colors);

  if (genderChart.value && d.gender_distribution)
    makeDoughnut(genderChart.value, d.gender_distribution.labels, d.gender_distribution.data, d.gender_distribution.colors);

  if (antibiogramChart.value && d.antibiogram?.labels?.length)
    makeBar(antibiogramChart.value, d.antibiogram.labels, d.antibiogram.data,
      d.antibiogram.labels.map((_: string, i: number) => `hsl(${(i * 28) % 360},70%,55%)`), '%');

  if (symptomsChart.value && d.symptom_prevalence)
    makeHorizontalBar(symptomsChart.value, d.symptom_prevalence.labels, d.symptom_prevalence.data, '#6366f1', '%');

  if (testsChart.value && d.test_positivity)
    makeBar(testsChart.value, d.test_positivity.labels, d.test_positivity.data, d.test_positivity.colors, '%');

  if (speciesChart.value && d.bacterial_species?.labels?.length)
    makeHorizontalBar(speciesChart.value, d.bacterial_species.labels, d.bacterial_species.data, '#8b5cf6');

  if (comorbidityChart.value && d.comorbidities)
    makeBar(comorbidityChart.value, d.comorbidities.labels, d.comorbidities.data, d.comorbidities.colors, '%');

  if (prescriptionChart.value && d.prescription_status)
    makeDoughnut(prescriptionChart.value, d.prescription_status.labels, d.prescription_status.data, d.prescription_status.colors);
}

function getRiskInfo(patient: any) {
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
  if (score >= 8) return { class: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400', text: 'High' };
  if (score >= 4) return { class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400', text: 'Medium' };
  return { class: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400', text: 'Low' };
}

function getAlertBorderClass(s: string) {
  return ({ high: 'border-red-500', medium: 'border-yellow-500', warning: 'border-yellow-500', info: 'border-blue-500' } as any)[s] || 'border-gray-500';
}
function getAlertTextClass(s: string) {
  const isDark = document.documentElement.classList.contains('dark');
  if (isDark) {
    return ({ high: 'text-red-400', medium: 'text-yellow-400', warning: 'text-yellow-400', info: 'text-blue-400' } as any)[s] || 'text-gray-300';
  }
  return ({ high: 'text-red-700', medium: 'text-yellow-700', warning: 'text-yellow-700', info: 'text-blue-700' } as any)[s] || 'text-gray-700';
}

async function handleMarkAlertRead(id: number) {
  await markAlertRead(id);
  const a = alerts.value.find(x => x.id === id);
  if (a) a.is_read = true;
}

onMounted(async () => {
  const [dashRes, pRes, alertsRes, chartsRes] = await Promise.all([
    getDashboardStats(),
    getPatients(1, 20),
    getAlerts(1, 20),
    getDashboardCharts(),
  ]);
  dashboard.value = dashRes;
  patients.value = (pRes as any).patients || [];
  alerts.value = (alertsRes as any).alerts || [];
  charts.value = chartsRes;

  await nextTick();
  buildCharts(chartsRes);
});

onUnmounted(() => destroyCharts());
</script>
