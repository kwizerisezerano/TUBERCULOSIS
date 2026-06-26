<template>
  <div class="flex min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
    <Sidebar />
    <div class="flex-1 bg-white dark:bg-gray-950">
      <header class="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 px-6 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ pageTitle }}</h1>
          </div>
          <div class="flex items-center gap-4">
            <!-- Header content can be added here if needed -->
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
const { currentUser, logout } = useAuth();

defineProps<{
  pageTitle: string;
}>();

onMounted(() => {
  if (!currentUser.value) {
    navigateTo('/');
  }
});
</script>
