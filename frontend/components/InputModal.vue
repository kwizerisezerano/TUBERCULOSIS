<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="close"></div>
    <div class="relative bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-6 w-full max-w-md border border-gray-200 dark:border-gray-700">
      <div class="text-center mb-6">
        <div class="h-16 w-16 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mx-auto mb-4">
          <svg class="w-8 h-8 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
        </div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{{ title }}</h3>
        <p class="text-gray-600 dark:text-gray-300">{{ message }}</p>
      </div>
      <div class="mb-4">
        <input
          v-model="inputValue"
          type="text"
          :placeholder="placeholder"
          class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
          @keyup.enter="confirm"
        />
      </div>
      <div class="flex gap-3">
        <button @click="close" class="flex-1 py-3 px-4 rounded-xl bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-semibold transition-colors">
          Cancel
        </button>
        <button @click="confirm" class="flex-1 py-3 px-4 rounded-xl bg-primary-600 hover:bg-primary-700 text-white font-semibold transition-colors">
          Confirm
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  isOpen: boolean;
  title: string;
  message: string;
  placeholder: string;
  initialValue?: string;
}>();

const emit = defineEmits<{
  close: [];
  confirm: [value: string];
}>();

const inputValue = ref(props.initialValue || '');

const close = () => {
  emit('close');
  inputValue.value = '';
};

const confirm = () => {
  emit('confirm', inputValue.value);
  inputValue.value = '';
};

// Reset input when modal opens
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    inputValue.value = props.initialValue || '';
  }
});
</script>
