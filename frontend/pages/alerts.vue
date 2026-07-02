<template>
  <DashboardLayout>
    <div class="space-y-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Alerts</h1>
      
      <!-- Alert Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Total Alerts</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white mt-1">{{ dashboard.alert_stats?.total || alerts.length }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Unread</p>
          <p class="text-3xl font-bold text-red-600 dark:text-red-400 mt-1">{{ dashboard.alert_stats?.unread || unreadCount }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-5 rounded-2xl border border-gray-200 dark:border-gray-700">
          <p class="text-gray-500 dark:text-gray-400 text-sm">Critical</p>
          <p class="text-3xl font-bold text-orange-600 dark:text-orange-400 mt-1">{{ dashboard.alert_stats?.critical || criticalCount }}</p>
        </div>
      </div>

      <!-- Alerts List -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">All Alerts</h2>
          <button 
            @click="markAllRead" 
            v-if="(dashboard.alert_stats?.unread || unreadCount) > 0"
            class="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition"
          >
            Mark All as Read
          </button>
        </div>
        
        <div v-if="alerts.length === 0" class="p-8 text-center text-gray-500 dark:text-gray-400">
          No alerts found
        </div>
        
        <div v-else class="divide-y divide-gray-200 dark:divide-gray-700">
          <div 
            v-for="alert in alerts" 
            :key="alert.id"
            class="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition cursor-pointer"
            :class="{ 'bg-blue-50 dark:bg-blue-900/10': !alert.is_read }"
            @click="markAsRead(alert)"
          >
            <div class="flex items-start gap-3">
              <div class="mt-1">
                <svg v-if="alert.severity === 'critical'" class="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                <svg v-else class="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
              </div>
              <div class="flex-1">
                <p class="font-medium text-gray-900 dark:text-white" :class="{ 'font-semibold': !alert.is_read }">
                  {{ alert.message }}
                </p>
                <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
                  {{ formatDate(alert.created_at) }}
                </p>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                  Patient ID: {{ alert.patient_id }} | Type: {{ alert.alert_type }}
                </p>
              </div>
              <div v-if="!alert.is_read" class="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="p-4 border-t border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <p class="text-sm text-gray-500 dark:text-gray-400">
            Page {{ currentPage }} of {{ totalPages }} ({{ totalAlerts }} total)
          </p>
          <div class="flex gap-2">
            <button
              @click="goToPage(currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >Previous</button>
            <button
              v-for="p in pageNumbers"
              :key="p"
              @click="goToPage(p)"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border transition"
              :class="p === currentPage
                ? 'bg-primary-600 text-white border-primary-600'
                : 'border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700'"
            >{{ p }}</button>
            <button
              @click="goToPage(currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700 transition"
            >Next</button>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import DashboardLayout from '~/components/DashboardLayout.vue';

const { getAlerts, markAlertRead, getDashboardStats } = useApi();
const { unreadAlertCount, refresh: refreshAlertCount } = useAlertCount();

const alerts = ref<any[]>([]);
const dashboard = ref<any>({});
const loading = ref(false);
const currentPage = ref(1);
const perPage = 10;
const totalAlerts = ref(0);

const totalPages = computed(() => Math.ceil(totalAlerts.value / perPage));
const pageNumbers = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, start + 4);
  for (let i = start; i <= end; i++) pages.push(i);
  return pages;
});

const unreadCount = computed(() => alerts.value.filter(a => !a.is_read).length);
const criticalCount = computed(() => alerts.value.filter(a => a.severity === 'critical').length);

const fetchAlerts = async () => {
  loading.value = true;
  try {
    const [alertsRes, dashboardRes] = await Promise.all([
      getAlerts(currentPage.value, perPage, false),
      getDashboardStats()
    ]);
    alerts.value = alertsRes.alerts || [];
    totalAlerts.value = alertsRes.total || 0;
    dashboard.value = dashboardRes;
  } catch (error) {
    console.error('Failed to fetch alerts:', error);
  } finally {
    loading.value = false;
  }
};

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchAlerts();
};

const markAsRead = async (alert: any) => {
  if (alert.is_read) return;
  try {
    await markAlertRead(alert.id);
    alert.is_read = true;
    dashboard.value.alert_stats && dashboard.value.alert_stats.unread--;
    refreshAlertCount();
  } catch (error) {
    console.error('Failed to mark alert as read:', error);
  }
};

const markAllRead = async () => {
  try {
    await Promise.all(alerts.value.filter(a => !a.is_read).map(a => markAlertRead(a.id)));
    alerts.value.forEach(a => a.is_read = true);
    if (dashboard.value.alert_stats) dashboard.value.alert_stats.unread = 0;
    refreshAlertCount();
  } catch (error) {
    console.error('Failed to mark all alerts as read:', error);
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleString();
};

onMounted(() => {
  fetchAlerts();
});
</script>
