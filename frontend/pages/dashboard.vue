<template>
  <DashboardLayout>
    <div class="space-y-6">

      <!-- Pharmacist Dashboard -->
      <div v-if="userRole === 'pharmacist'">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Pharmacy Dashboard</h1>
        
        <!-- Pharmacist Stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Pending Prescriptions</p>
            <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{{ dashboard.prescription_stats?.pending || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Approved Today</p>
            <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ dashboard.prescription_stats?.approved || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Dispensed Today</p>
            <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ dashboard.prescription_stats?.dispensed || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Low Stock Alerts</p>
            <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ dashboard.inventory_stats?.low_stock || 0 }}</p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link to="/pharmacist" class="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-center font-medium transition">
                Manage Prescriptions
              </router-link>
              <router-link to="/prescriptions" class="block w-full py-3 px-4 bg-gray-600 hover:bg-gray-700 text-white rounded-xl text-center font-medium transition">
                View All Prescriptions
              </router-link>
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Inventory Summary</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">Total Drugs in Stock</span>
                <span class="text-gray-900 dark:text-white font-medium">{{ dashboard.inventory_stats?.total_drugs || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">Below Minimum Stock</span>
                <span class="text-red-600 font-medium">{{ dashboard.inventory_stats?.low_stock || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Lab Technician Dashboard -->
      <div v-else-if="userRole === 'lab_technician'">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Laboratory Dashboard</h1>
        
        <!-- Lab Tech Stats -->
        <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Pending Tests</p>
            <p class="text-3xl font-bold text-yellow-600 dark:text-yellow-400 mt-1">{{ dashboard.lab_stats?.pending || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Completed Today</p>
            <p class="text-3xl font-bold text-green-600 dark:text-green-400 mt-1">{{ dashboard.lab_stats?.completed_today || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">In Progress</p>
            <p class="text-3xl font-bold text-blue-600 dark:text-blue-400 mt-1">{{ dashboard.lab_stats?.in_progress || 0 }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Total This Week</p>
            <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ dashboard.lab_stats?.total_week || 0 }}</p>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Quick Actions</h3>
            <div class="space-y-3">
              <router-link to="/lab-technician" class="block w-full py-3 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-center font-medium transition">
                Manage Lab Tests
              </router-link>
              <router-link to="/lab-results" class="block w-full py-3 px-4 bg-gray-600 hover:bg-gray-700 text-white rounded-xl text-center font-medium transition">
                View All Results
              </router-link>
            </div>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Test Types Summary</h3>
            <div class="space-y-2 text-sm">
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">Sputum Smear</span>
                <span class="text-gray-900 dark:text-white font-medium">{{ dashboard.lab_stats?.sputum_tests || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">GeneXpert</span>
                <span class="text-gray-900 dark:text-white font-medium">{{ dashboard.lab_stats?.genexpert_tests || 0 }}</span>
              </div>
              <div class="flex justify-between">
                <span class="text-gray-500 dark:text-gray-400">Chest X-ray</span>
                <span class="text-gray-900 dark:text-white font-medium">{{ dashboard.lab_stats?.xray_tests || 0 }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin/Doctor/Hospital Admin Dashboard -->
      <div v-else>
      <!-- Summary Cards Row 1 -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Patients</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ dashboard.patient_stats?.total || 0 }}</p>
          <p v-if="userRole === 'admin'" class="text-xs text-gray-400 dark:text-gray-500 mt-1">System-wide view</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Healthcare Facilities</p>
          <p class="text-3xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">{{ dashboard.hospital_stats?.total || 0 }}</p>
          <p v-if="userRole === 'admin'" class="text-xs text-gray-400 dark:text-gray-500 mt-1">System-wide view</p>
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
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Diagnoses</p>
          <p class="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-1">{{ dashboard.diagnosis_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Antimicrobial Resistance</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ dashboard.antimicrobial_resistance_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">ATC Drugs</p>
          <p class="text-3xl font-bold text-cyan-600 dark:text-cyan-400 mt-1">{{ dashboard.atc_drug_stats?.total || 0 }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">High Risk Patients</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-500 mt-1">{{ dashboard.patient_stats?.high_risk || 0 }}</p>
          <p v-if="userRole === 'admin'" class="text-xs text-gray-400 dark:text-gray-500 mt-1">System-wide view</p>
        </div>
      </div>

      <!-- Charts Row 1: Patient Overview (Risk, TB Status, Gender) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Patient Risk Levels</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="riskChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">TB Status Distribution</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="tbStatusChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Gender Distribution</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="genderChart" height="150"></canvas>
        </div>
      </div>

      <!-- Charts Row 2: Clinical Indicators (Drug Resistance, Symptoms, Test Positivity) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Drug Resistance</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="resistanceChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Symptom Prevalence (%)</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="symptomsChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Test Positivity (%)</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="testsChart" height="150"></canvas>
        </div>
      </div>

      <!-- Charts Row 3: Treatment & Reference (Prescription, Antibiogram, Comorbidities) -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Prescription Status</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="prescriptionChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Comorbidities (%)</p>
            <span v-if="userRole === 'admin'" class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="comorbidityChart" height="150"></canvas>
        </div>
        <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <p class="text-sm font-semibold text-gray-900 dark:text-white">Top Bacterial Species</p>
            <span class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
              System-wide
            </span>
          </div>
          <canvas ref="speciesChart" height="150"></canvas>
        </div>
      </div>

      <!-- Charts Row 4: Antibiogram (full width, compact) -->
      <div class="bg-white dark:bg-gray-800 p-4 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-2">
          <p class="text-sm font-semibold text-gray-900 dark:text-white">Antibiogram — Resistance Rate per Antibiotic (%)</p>
          <span class="text-xs px-2 py-1 rounded-full bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-400">
            System-wide
          </span>
        </div>
        <canvas ref="antibiogramChart" height="80"></canvas>
      </div>
      </div>

      <!-- Recent Patients + Alerts -->
      <div v-if="userRole !== 'pharmacist' && userRole !== 'lab_technician'" class="grid grid-cols-1 lg:grid-cols-2 gap-4">
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
const { userRole } = useAuth();

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
    getAlerts(1, 20, false),
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
