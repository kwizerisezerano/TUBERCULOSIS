<template>
  <div class="flex min-h-screen bg-gray-900">
    <Sidebar />
    <div class="flex-1 bg-gray-900">
      <header class="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-white">{{ pageTitle }}</h1>
          </div>
          <div class="flex items-center gap-4">
            <button class="p-2 rounded-lg hover:bg-gray-700">
              <svg class="w-6 h-6 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.603V11a6 6 0 10-12 0v3.603a2.032 2.032 0 01-.595 1.405L4 17h5m7z"></path>
              </svg>
            </button>
            <div class="flex items-center gap-3">
              <div class="text-right">
                <p class="text-sm font-semibold text-white">{{ currentUser?.email }}</p>
                <p class="text-xs text-gray-400 uppercase">{{ currentUser?.role }}</p>
              </div>
              <div class="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-500 to-emerald-700 text-white flex items-center justify-center font-bold shadow-lg shadow-emerald-500/30">
                {{ currentUser?.username.charAt(0).toUpperCase() }}
              </div>
            </div>
          </div>
        </div>
      </header>
      <main class="p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue';
const { currentUser } = useAuth();

defineProps<{
  pageTitle: string;
}>();

onMounted(() => {
  if (!currentUser.value) {
    navigateTo('/');
  }
});
</script>
