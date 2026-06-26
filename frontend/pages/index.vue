<template>
  <div class="min-h-screen bg-white dark:bg-gray-950 transition-colors duration-300">
    <!-- Top bar -->
    <header class="flex items-center justify-between px-4 sm:px-6 md:px-10 py-3 sm:py-4 border-b border-gray-200 dark:border-gray-800">
      <div class="flex items-center gap-2 sm:gap-3">
        <div class="flex h-8 w-8 sm:h-10 sm:w-10 items-center justify-center rounded-xl bg-primary-600 shadow-sm">
          <svg class="w-5 h-5 sm:w-6 sm:h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            <circle cx="12" cy="12" r="2" fill="currentColor"></circle>
          </svg>
        </div>
        <span class="text-gray-900 dark:text-white font-bold text-base sm:text-lg">Predictive EHR Analytics</span>
      </div>
      <button @click="$colorMode.preference = $colorMode.preference === 'dark' ? 'light' : 'dark'" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors">
        <svg v-if="$colorMode.preference === 'dark'" class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
        </svg>
        <svg v-else class="w-5 h-5 text-gray-700 dark:text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
        </svg>
      </button>
    </header>

    <!-- Main content -->
    <main class="flex-1 px-4 sm:px-6 md:px-10 py-6 sm:py-10 lg:py-16">
      <div class="w-full grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8 lg:gap-16 items-start lg:items-stretch">
        <!-- Left: Info Section -->
        <div class="space-y-6 sm:space-y-8 flex flex-col lg:flex-col lg:h-full">
          <div>
            <h1 class="text-2xl sm:text-3xl md:text-4xl lg:text-5xl xl:text-6xl font-extrabold text-gray-900 dark:text-white leading-tight">
              Predictive EHR Analytics
              <span class="block text-primary-600">Dashboard</span>
            </h1>
            <p class="mt-4 sm:mt-6 text-sm sm:text-base md:text-lg lg:text-xl text-gray-600 dark:text-gray-300 leading-relaxed">
              A comprehensive clinical decision support system combining machine learning, WHO treatment guidelines, and real-time antimicrobial stewardship to improve patient outcomes for tuberculosis care.
            </p>
          </div>

          <!-- Features Grid -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5 flex-1">
            <div v-for="feature in features" :key="feature.title" class="group p-5 sm:p-6 rounded-2xl bg-gradient-to-br from-white to-gray-50 dark:from-gray-800 dark:to-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div class="w-12 h-12 sm:w-14 sm:h-14 rounded-xl flex items-center justify-center mb-4 shrink-0" :class="feature.color">
                <span class="w-6 h-6 sm:w-7 sm:h-7 text-white" v-html="feature.icon"></span>
              </div>
              <h3 class="font-semibold text-gray-900 dark:text-white mb-2" :class="feature.title.length > 20 ? 'text-sm sm:text-base' : 'text-base sm:text-lg'">{{ feature.title }}</h3>
              <p class="text-gray-600 dark:text-gray-400 leading-relaxed" :class="feature.desc.length > 50 ? 'text-xs sm:text-sm' : 'text-sm sm:text-base'">{{ feature.desc }}</p>
            </div>
          </div>

          <!-- Stats -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4">
            <div v-for="stat in stats" :key="stat.label" class="text-center p-4 sm:p-5 rounded-xl bg-gradient-to-br from-primary-50 to-white dark:from-primary-950/30 dark:to-gray-800 border border-primary-100 dark:border-primary-900/30">
              <p class="font-bold text-primary-600 dark:text-primary-400" :class="stat.value.length > 5 ? 'text-xl sm:text-2xl md:text-3xl' : 'text-2xl sm:text-3xl md:text-4xl'">{{ stat.value }}</p>
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400 mt-1 font-medium">{{ stat.label }}</p>
            </div>
          </div>
        </div>

        <!-- Right: Login Card -->
        <div class="bg-white dark:bg-gray-800 rounded-3xl border border-gray-200 dark:border-gray-700 shadow-xl p-4 sm:p-6 md:p-8 lg:p-10 flex flex-col lg:h-full">
          <div class="flex items-center gap-3 sm:gap-4 mb-6 sm:mb-8">
            <div class="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-primary-600 flex items-center justify-center shadow-sm shrink-0">
              <svg class="w-6 h-6 sm:w-7 sm:h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                <circle cx="12" cy="12" r="2" fill="currentColor"></circle>
              </svg>
            </div>
            <div>
              <h2 class="text-lg sm:text-xl md:text-2xl font-bold text-gray-900 dark:text-white">Welcome Back</h2>
              <p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">Sign in to access your dashboard</p>
            </div>
          </div>

          <form @submit.prevent="handleLogin" class="space-y-4 sm:space-y-5">
            <div>
              <label for="email" class="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Email Address</label>
              <input
                id="email"
                v-model="email"
                type="email"
                required
                autocomplete="email"
                class="w-full px-3 sm:px-4 py-2 sm:py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-sm sm:text-base"
                placeholder="you@hospital.com"
              />
            </div>
            <div>
              <label for="password" class="block text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300 mb-1 sm:mb-2">Password</label>
              <div class="relative">
                <input
                  id="password"
                  v-model="password"
                  :type="showPwd ? 'text' : 'password'"
                  required
                  autocomplete="current-password"
                  class="w-full px-3 sm:px-4 py-2 sm:py-3 pr-10 sm:pr-12 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition-all text-sm sm:text-base"
                  placeholder="••••••••"
                />
                <button type="button" @click="showPwd = !showPwd" class="absolute right-2 sm:right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
                  <svg v-if="!showPwd" class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="error" class="flex items-center gap-2 p-2 sm:p-3 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-xs sm:text-sm">
              <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              <span>{{ error }}</span>
            </div>

            <button type="submit" :disabled="isLoading" class="w-full py-2 sm:py-3 rounded-xl bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-xs sm:text-sm transition-all shadow-sm flex items-center justify-center gap-2">
              <svg v-if="isLoading" class="animate-spin w-4 h-4 sm:w-5 sm:h-5" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
              </svg>
              {{ isLoading ? 'Signing in...' : 'Sign In' }}
            </button>
          </form>

          <!-- Quick Credentials -->
          <div class="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-gray-200 dark:border-gray-700">
            <p class="text-[10px] sm:text-xs text-gray-500 dark:text-gray-400 mb-3 sm:mb-4 font-semibold uppercase tracking-wide">Demo Credentials</p>
            <div class="space-y-1.5 sm:space-y-2">
              <button v-for="cred in credentials" :key="cred.role" @click="email = cred.email; password = cred.pwd; showPwd = true" class="w-full flex items-center gap-2 px-3 sm:px-4 py-2 sm:py-3 rounded-xl bg-gray-50 dark:bg-gray-900 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors text-xs sm:text-sm overflow-hidden">
                <div class="text-left min-w-0 flex-1 overflow-hidden">
                  <span class="font-semibold text-gray-700 dark:text-gray-300 block truncate">{{ cred.role }}</span>
                  <span class="text-gray-400 dark:text-gray-500 text-[10px] sm:text-xs truncate block">{{ cred.email }}</span>
                </div>
                <span class="text-primary-600 dark:text-primary-400 font-mono text-[10px] sm:text-xs shrink-0">{{ cred.pwd }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="text-center py-4 sm:py-6 text-[10px] sm:text-xs text-gray-500 dark:text-gray-500 border-t border-gray-200 dark:border-gray-800">
      Predictive EHR Analytics Dashboard · WHO-Aligned Guidelines · Built for Healthcare Professionals
    </footer>
  </div>
</template>

<script setup lang="ts">
const { login, isLoggedIn } = useAuth();
const router = useRouter();

if (isLoggedIn.value) router.push('/dashboard');

const email = ref('');
const password = ref('');
const showPwd = ref(false);
const isLoading = ref(false);
const error = ref('');

const features = [
  {
    title: 'ML Risk Prediction',
    desc: 'Random Forest models predict TB status and drug resistance',
    icon: '<svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>',
    color: 'bg-primary-600'
  },
  {
    title: 'Antimicrobial Stewardship',
    desc: 'Real-time alerts for antibiotic misuse',
    icon: '<svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path></svg>',
    color: 'bg-primary-700'
  },
  {
    title: 'Interactive Dashboard',
    desc: 'Real-time charts for antibiograms and resistance trends',
    icon: '<svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>',
    color: 'bg-primary-500'
  },
  {
    title: 'Lab Integration',
    desc: 'GeneXpert, sputum smear, and culture results linked',
    icon: '<svg class="w-full h-full" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
    color: 'bg-primary-800'
  }
];

const stats = [
  { value: '28K+', label: 'Patients' },
  { value: '2 ML', label: 'Models' },
  { value: 'ATC', label: 'Drugs DB' },
  { value: '4 Roles', label: 'Access' }
];

const credentials = [
  { role: 'System Admin', email: 'divinekageruka@gmail.com', pwd: 'Admin123!' },
  { role: 'Hospital Admin', email: 'igiclarisse10@gmail.com', pwd: 'Admin123!' },
  { role: 'Doctor', email: 'igiranezac459@gmail.com', pwd: 'Doctor123!' },
  { role: 'Lab Technician', email: 'clarisseigiraneza56@gmail.com', pwd: 'LabTech123!' },
  { role: 'Pharmacist', email: 'clarisseigiraneza915@gmail.com', pwd: 'Pharm123!' }
];

const handleLogin = async () => {
  isLoading.value = true;
  error.value = '';
  const result = await login(email.value, password.value);
  if (result.success) {
    router.push('/dashboard');
  } else {
    error.value = result.error || 'Invalid email or password';
  }
  isLoading.value = false;
};
</script>
