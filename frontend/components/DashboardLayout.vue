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

onMounted(() => {
  const { currentUser } = useAuth();
  if (!currentUser.value) {
    navigateTo('/');
  }
});
</script>
