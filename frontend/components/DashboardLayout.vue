<template>
  <div class="flex min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
    <!-- Mobile Menu Button -->
    <button @click="showMobileMenu = !showMobileMenu" class="lg:hidden fixed top-4 left-4 z-50 p-3 rounded-xl bg-primary-600 text-white shadow-lg">
      <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
      </svg>
      <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
      </svg>
    </button>

    <!-- Alert Notification Bell -->
    <button @click="showAlerts = !showAlerts" class="fixed top-4 right-4 z-50 p-3 rounded-xl bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 shadow-lg relative hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
      </svg>
      <span v-if="unreadCount > 0" class="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
        {{ unreadCount > 9 ? '9+' : unreadCount }}
      </span>
    </button>

    <!-- Alerts Dropdown -->
    <div v-if="showAlerts" class="fixed top-16 right-4 z-50 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-xl border border-gray-200 dark:border-gray-700 max-h-96 overflow-y-auto">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 class="font-semibold text-gray-900 dark:text-white">Alerts</h3>
        <button @click="showAlerts = false" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      <div v-if="alerts.length === 0" class="p-4 text-center text-gray-500 dark:text-gray-400">
        No alerts
      </div>
      <div v-else>
        <div v-for="alert in alerts" :key="alert.id" @click="markAsRead(alert.id)" class="p-4 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors" :class="{ 'bg-blue-50 dark:bg-blue-900/20': !alert.is_read }">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0">
              <span v-if="alert.severity === 'critical'" class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-300">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </span>
              <span v-else class="inline-flex items-center justify-center w-8 h-8 rounded-full bg-yellow-100 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </span>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{{ alert.message }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ formatDate(alert.created_at) }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Sidebar Overlay -->
    <div v-if="showMobileMenu" @click="showMobileMenu = false" class="lg:hidden fixed inset-0 bg-black/50 z-40"></div>

    <!-- Sidebar -->
    <Sidebar :is-mobile="showMobileMenu" @close="showMobileMenu = false" />

    <div class="flex-1 bg-white dark:bg-gray-950">
      <main class="p-4 sm:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue';

const showMobileMenu = ref(false);
const showAlerts = ref(false);
const unreadCount = ref(0);
const alerts = ref<any[]>([]);

const { currentUser, authToken, isLoggedIn } = useAuth();

const fetchAlerts = async () => {
  try {
    if (!authToken.value) return;
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/alerts?unread_only=true&per_page=5`, {
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      }
    });
    const data = await response.json();
    alerts.value = data.alerts || [];
  } catch (error) {
    console.error('Error fetching alerts:', error);
  }
};

const fetchUnreadCount = async () => {
  try {
    if (!authToken.value) return;
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/alerts/unread-count`, {
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      }
    });
    const data = await response.json();
    unreadCount.value = data.unread_count || 0;
  } catch (error) {
    console.error('Error fetching unread count:', error);
  }
};

const markAsRead = async (alertId: number) => {
  try {
    if (!authToken.value) return;
    const config = useRuntimeConfig()
    await fetch(`${config.public.apiBase}/alerts/${alertId}/read`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      }
    });
    await fetchAlerts();
    await fetchUnreadCount();
  } catch (error) {
    console.error('Error marking alert as read:', error);
  }
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  
  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return date.toLocaleDateString();
};

onMounted(async () => {
  if (!isLoggedIn.value) {
    navigateTo('/');
    return;
  }
  if (currentUser.value?.role !== 'patient') {
    fetchUnreadCount();
    fetchAlerts();
    setInterval(() => {
      fetchUnreadCount();
      fetchAlerts();
    }, 30000);
  }
});
</script>
