<template>
  <DashboardLayout page-title="Admin">
    <div class="space-y-6">
      <h2 class="text-xl font-bold text-gray-900 dark:text-white">Administration Panel</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">User Management</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Add, edit, and remove system users</p>
          <button class="w-full bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm">
            Manage Users
          </button>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">System Settings</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Configure system settings and preferences</p>
          <button class="w-full bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm">
            Settings
          </button>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <p class="font-semibold text-gray-900 dark:text-white mb-2">Model Performance</p>
          <p class="text-gray-600 dark:text-gray-300 text-sm mb-4">Monitor ML model performance metrics</p>
          <button class="w-full bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 rounded-lg text-sm">
            View Metrics
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
</script>
