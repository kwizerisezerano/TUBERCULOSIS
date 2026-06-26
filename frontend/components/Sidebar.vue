<template>
  <aside class="w-64 bg-gray-900 text-white h-full flex flex-col">
    <!-- Header -->
    <div class="p-6 border-b border-gray-700">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-emerald-500 to-emerald-700 flex items-center justify-center shadow-lg shadow-emerald-500/30">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <div>
          <p class="font-bold text-lg">TB Predictive EHR</p>
          <p class="text-xs text-gray-400">Analytics Dashboard</p>
        </div>
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 py-6 space-y-2">
      <template v-for="item in navItems" :key="item.path">
        <router-link
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200"
          :class="isActive(item.path) 
            ? 'bg-gradient-to-r from-emerald-600 to-emerald-700 text-white shadow-lg shadow-emerald-500/30' 
            : 'text-gray-300 hover:bg-gray-800 hover:text-white'
        "
        >
          <span v-html="item.icon"></span>
          <span class="font-medium">{{ item.label }}</span>
        </router-link>
      </template>
    </nav>

    <!-- User Info & Sign Out -->
    <div class="p-4 border-t border-gray-700 space-y-2">
      <div class="px-4 py-2 text-xs text-gray-400">
        <p class="font-semibold text-gray-300">{{ formatRole(userRole) }}</p>
      </div>
      <button
        @click="logout"
        class="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-gray-300 hover:text-red-400 hover:bg-red-900/30 transition-all duration-200"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
        </svg>
        <span class="font-medium">Sign Out</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
const { userRole, logout } = useAuth();
const route = useRoute();

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/');

const formatRole = (role: string | null) => {
    if (!role) return '';
    const roleMap: Record<string, string> = {
        admin: 'System Admin',
        doctor: 'Doctor',
        lab_tech: 'Lab Technician',
        pharmacist: 'Pharmacist',
        hospital_admin: 'Hospital Admin'
    };
    return roleMap[role] || role.charAt(0).toUpperCase() + role.slice(1);
};

const navItems = computed(() => {
  const role = userRole.value;

  const allItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>`,
      roles: ['admin', 'doctor', 'lab_tech', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/patients',
      label: 'Patients',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/diagnose',
      label: 'Diagnose & Predict',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/diagnoses',
      label: 'Diagnoses',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>`,
      roles: ['admin', 'doctor', 'hospital_admin']
    },
    {
      path: '/lab-results',
      label: 'Lab Results',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
      roles: ['admin', 'doctor', 'lab_tech', 'hospital_admin']
    },
    {
      path: '/prescriptions',
      label: 'Prescriptions',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/antimicrobial-stewardship',
      label: 'Antimicrobial Stewardship',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/atc-drugs',
      label: 'ATC Drugs',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>`,
      roles: ['admin', 'doctor', 'pharmacist', 'hospital_admin']
    },
    {
      path: '/admin',
      label: 'Admin',
      icon: `<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>`,
      roles: ['admin', 'hospital_admin']
    }
  ];

  return allItems.filter(item => item.roles.includes(role as any));
});
</script>
