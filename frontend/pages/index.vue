<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <div class="max-w-6xl mx-auto px-4 py-12">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="flex flex-col gap-6">
          <div class="flex items-center gap-3">
            <div class="flex h-16 w-16 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-lg">
              <span class="text-2xl font-bold">TB</span>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
                Predictive EHR Analytics Dashboard
              </h1>
              <p class="text-sm text-gray-600 dark:text-gray-300">
                Tuberculosis Risk Prediction & Antimicrobial Stewardship
              </p>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
            <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Welcome to the System
            </h2>
            <p class="text-gray-600 dark:text-gray-300 mb-4">
              This system helps clinicians predict TB risk, monitor antimicrobial usage, and manage patient care.
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div class="bg-emerald-50 dark:bg-emerald-900/30 p-4 rounded-xl">
                <p class="font-semibold text-emerald-800 dark:text-emerald-200">🎯 Risk Prediction</p>
                <p class="text-sm text-emerald-700 dark:text-emerald-300">ML-driven TB risk scoring</p>
              </div>
              <div class="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-xl">
                <p class="font-semibold text-blue-800 dark:text-blue-200">💊 Antimicrobial Stewardship</p>
                <p class="text-sm text-blue-700 dark:text-blue-300">Track and optimize antibiotic use</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Sign In
          </h2>
          <form @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Email Address
              </label>
              <input
                v-model="loginEmail"
                type="email"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-emerald-500 outline-none"
                placeholder="your-email@example.com"
                required
              />
            </div>
            <div>
              <label class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Password
              </label>
              <input
                v-model="loginPassword"
                :type="showPassword ? 'text' : 'password'"
                class="w-full px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-emerald-500 outline-none"
                placeholder="••••••••"
                required
              />
              <button type="button" class="mt-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200" @click="showPassword = !showPassword">
                {{ showPassword ? 'Hide password' : 'Show password' }}
              </button>
            </div>
            <div v-if="loginError" class="bg-red-50 dark:bg-red-900/30 p-3 rounded-lg text-red-700 dark:text-red-300 text-sm">
              {{ loginError }}
            </div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition"
            >
              {{ loading ? 'Signing in...' : 'Sign in' }}
            </button>
          </form>

          <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-3">Test Credentials:</p>
            <div class="grid grid-cols-1 gap-2 text-xs">
              <div class="p-2 rounded bg-gray-50 dark:bg-gray-700/50">
                <span class="font-semibold text-gray-700 dark:text-gray-200">Doctor:</span> igiranezac459@gmail.com / Doctor123!
              </div>
              <div class="p-2 rounded bg-gray-50 dark:bg-gray-700/50">
                <span class="font-semibold text-gray-700 dark:text-gray-200">Lab Tech:</span> clarisseigiraneza56@gmail.com / LabTech123!
              </div>
              <div class="p-2 rounded bg-gray-50 dark:bg-gray-700/50">
                <span class="font-semibold text-gray-700 dark:text-gray-200">Pharmacist:</span> clarisseigiraneza915@gmail.com / Pharm123!
              </div>
              <div class="p-2 rounded bg-gray-50 dark:bg-gray-700/50">
                <span class="font-semibold text-gray-700 dark:text-gray-200">Admin:</span> divinekageruka@gmail.com / Admin123!
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { login, isLoggedIn } = useAuth();
const router = useRouter();

const loginEmail = ref('');
const loginPassword = ref('');
const showPassword = ref(false);
const loading = ref(false);
const loginError = ref('');

if (isLoggedIn.value) {
  router.push('/dashboard');
}

const handleLogin = async () => {
  loading.value = true;
  loginError.value = '';

  const result = await login(loginEmail.value, loginPassword.value);

  if (result.success) {
    router.push('/dashboard');
  } else {
    loginError.value = result.error;
  }
  loading.value = false;
};
</script>
