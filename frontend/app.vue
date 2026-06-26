<template>
  <div class="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
useHead({
  title: 'Predictive EHR Analytics Dashboard',
  meta: [
    { name: 'description', content: 'Comprehensive clinical decision support system for tuberculosis care' },
  ],
});
</script>
