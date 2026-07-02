<template>
  <aside :class="[
    'w-64 bg-white dark:bg-gray-900 text-gray-900 dark:text-white h-full flex flex-col border-r border-gray-200 dark:border-gray-800',
    'lg:flex',
    isMobile ? 'fixed inset-y-0 left-0 z-50' : ''
  ]">
    <!-- Header with Logo -->
    <div class="p-6 border-b border-gray-200 dark:border-gray-800">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-primary-600 flex items-center justify-center shadow-sm">
          <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            <circle cx="12" cy="12" r="2" fill="currentColor"></circle>
          </svg>
        </div>
        <div>
          <p class="font-bold text-lg">Predictive EHR</p>
          <p class="text-xs text-gray-500 dark:text-gray-400">Analytics Dashboard</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-6 space-y-2">
      <template v-for="item in navItems" :key="item.path">
        <router-link
          :to="item.path"
          @click="closeMobileMenu"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :class="isActive(item.path)
            ? 'bg-primary-600 text-white shadow-sm'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-white'
          "
        >
          <span v-html="item.icon"></span>
          <span class="font-medium">{{ item.label }}</span>
          <span v-if="item.badge && item.badge > 0" class="ml-auto bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{{ item.badge }}</span>
        </router-link>
      </template>
    </nav>

    <!-- User Info Card -->
    <div class="p-4 border-t border-gray-200 dark:border-gray-800 space-y-3">
      <button @click="showLogoutModal = true" class="w-full p-4 rounded-xl bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors text-left">
        <div class="flex items-center gap-3">
          <div class="h-10 w-10 rounded-full bg-primary-600 text-white flex items-center justify-center font-bold shadow-sm shrink-0">
            {{ userInitial }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-semibold text-gray-900 dark:text-white text-sm truncate">{{ userDisplayName }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ userSubtext }}</p>
          </div>
          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
          </svg>
        </div>
      </button>
      <!-- Theme Toggle -->
      <button @click="$colorMode.preference = $colorMode.preference === 'dark' ? 'light' : 'dark'" class="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all duration-200">
        <svg v-if="$colorMode.preference === 'dark'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12 a4 4 0 11-8 0 4 4 0 018 0z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
        </svg>
        <span class="font-medium">{{ $colorMode.preference === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
      </button>
      <div class="px-4 py-2 text-xs text-gray-500 dark:text-gray-400">
        <p class="font-semibold text-gray-900 dark:text-gray-300">{{ formatRole(userRole) }}</p>
      </div>
    </div>

    <!-- Logout Modal -->
    <LogoutModal 
      :is-open="showLogoutModal" 
      @close="showLogoutModal = false" 
      @confirm="handleLogout" 
    />
  </aside>
</template>

<script setup lang="ts">
import LogoutModal from './LogoutModal.vue';

const props = defineProps<{
  isMobile?: boolean;
}>();

const emit = defineEmits<{
  close: [];
}>();

const { userRole, currentUser, logout, authToken } = useAuth();
const route = useRoute();

const showLogoutModal = ref(false);
const unreadAlertCount = ref(0);

const userInitial = computed(() => {
  if (userRole.value === 'patient') {
    return currentUser.value?.first_name?.charAt(0).toUpperCase() || 'P';
  } else {
    return currentUser.value?.username?.charAt(0).toUpperCase() || 'U';
  }
});

const userDisplayName = computed(() => {
  if (userRole.value === 'patient') {
    return `${currentUser.value?.first_name || ''} ${currentUser.value?.last_name || ''}`.trim() || 'Patient';
  } else {
    return currentUser.value?.username || 'User';
  }
});

const userSubtext = computed(() => {
  if (userRole.value === 'patient') {
    return currentUser.value?.patient_id || '';
  } else {
    return currentUser.value?.email || '';
  }
});

// Fetch unread alert count
const fetchAlertCount = async () => {
  try {
    if (!authToken.value || userRole.value === 'patient') {
      return;
    }
    const config = useRuntimeConfig()
    const response = await fetch(`${config.public.apiBase}/alerts/unread-count`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    const data = await response.json();
    unreadAlertCount.value = data.unread_count || 0;
  } catch (error) {
    console.error('Failed to fetch alert count:', error);
  }
};

// Fetch alert count on mount and periodically
onMounted(() => {
  if (userRole.value !== 'patient') {
    fetchAlertCount();
    const interval = setInterval(fetchAlertCount, 30000); // Refresh every 30 seconds
    onUnmounted(() => clearInterval(interval));
  }
});

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/');

const closeMobileMenu = () => {
  if (props.isMobile) {
    emit('close');
  }
};

const handleLogout = () => {
  showLogoutModal.value = false;
  logout();
};

const formatRole = (role: string | null) => {
  if (!role) return '';
  const roleMap: Record<string, string> = {
      admin: 'System Admin',
      doctor: 'Doctor',
      lab_technician: 'Lab Technician',
      pharmacist: 'Pharmacist',
      hospital_admin: 'Hospital Admin',
      patient: 'Patient'
  };
  return roleMap[role] || role.charAt(0).toUpperCase() + role.slice(1);
};

const navItems = computed(() => {
  const role = userRole.value;

  const allItems = [
    {
      path: '/patient-portal',
      label: 'Patient Portal',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`,
      roles: ['patient']
    },
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>`,
      roles: ['admin', 'doctor', 'lab_technician', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/patients',
      label: 'Patients',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/diagnose',
      label: 'Diagnose & Predict',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/diagnoses',
      label: 'Diagnoses',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/lab-technician',
      label: 'Lab Dashboard',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      roles: ['admin', 'lab_technician', 'hospital_admin']
    },
    {
      path: '/lab-results',
      label: 'Lab Results',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      roles: ['admin', 'doctor', 'lab_technician', 'hospital_admin']
    },
    {
      path: '/pharmacist',
      label: 'Pharmacy',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>`,
      roles: ['admin', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/prescriptions',
      label: 'Prescriptions',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/antimicrobial-stewardship',
      label: 'Antimicrobial Stewardship',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/atc-drugs',
      label: 'ATC Drugs',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/alerts',
      label: 'Alerts',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin'],
      badge: unreadAlertCount.value
    },
    {
      path: '/hospitals',
      label: 'Facilities',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>`,
      roles: ['admin', 'hospital_admin']
    },
    {
      path: '/activity-log',
      label: 'Activity',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      roles: ['admin', 'hospital_admin']
    },
    {
      path: '/user-management',
      label: 'Users',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>`,
      roles: ['admin']
    },
    {
      path: '/system-settings',
      label: 'Settings',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`,
      roles: ['admin']
    }
  ];

  return allItems.filter(item => item.roles.includes(role as any));
});
</script>
