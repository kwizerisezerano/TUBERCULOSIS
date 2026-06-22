<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="w-full max-w-none px-4 sm:px-6 lg:px-10 2xl:px-12 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-900 text-white shadow-md ring-1 ring-slate-800/10 dark:bg-slate-100 dark:text-slate-900">
              <svg viewBox="0 0 64 64" class="h-9 w-9" fill="none" aria-hidden="true">
                <path d="M31.5 10v17" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
                <path d="M31.5 18c-7 0-13 5-15 12-1.5 5-1 10.5 1.5 15 2.2 4.1 6.2 7.2 11 8.5l2.5-16V18z" fill="rgba(255,255,255,0.92)"/>
                <path d="M32.5 18c7 0 13 5 15 12 1.5 5 1 10.5-1.5 15-2.2 4.1-6.2 7.2-11 8.5l-2.5-16V18z" fill="rgba(236,253,245,0.96)"/>
                <path d="M31.5 14c-1.5-2.5-3.5-4-6-4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <path d="M32.5 14c1.5-2.5 3.5-4 6-4" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
                <path d="M27 25l-5 7m7-4-8 10m12-7-6 9" stroke="#60a5fa" stroke-width="2.5" stroke-linecap="round"/>
                <path d="M37 25l5 7m-7-4 8 10m-12-7 6 9" stroke="#34d399" stroke-width="2.5" stroke-linecap="round"/>
                <circle cx="44.5" cy="44.5" r="2.4" fill="#34d399"/>
                <circle cx="48.5" cy="39.5" r="2" fill="#34d399"/>
                <circle cx="40.5" cy="39.5" r="1.8" fill="#34d399"/>
              </svg>
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">TB Diagnostic System</h1>
              <p class="text-sm text-gray-500 dark:text-gray-400">Comprehensive Patient Analysis & Treatment</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <button
              v-if="isLoggedIn"
              @click="logout"
              class="hidden rounded-xl border border-gray-200 bg-gray-50 px-4 py-2 text-right transition hover:border-emerald-300 hover:bg-emerald-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-emerald-700 dark:hover:bg-emerald-900/20 md:block"
              title="Click your name or role to logout"
            >
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ userDisplayName }}</p>
              <p class="text-xs uppercase tracking-wide text-emerald-600 dark:text-emerald-400">{{ userRoleLabel }}</p>
            </button>
            <!-- Alerts Badge -->
            <button
              v-if="isLoggedIn"
              @click="currentView = 'alerts'"
              class="relative p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              <span class="text-xl">🔔</span>
              <span
                v-if="unreadAlerts > 0"
                class="absolute -top-1 -right-1 bg-red-500 text-white text-xs w-6 h-6 rounded-full flex items-center justify-center"
              >
                {{ unreadAlerts }}
              </span>
            </button>
            <button
              @click="toggleDarkMode"
              class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200"
            >
              {{ isDarkMode ? '☀️' : '🌙' }}
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation -->
    <nav v-if="isLoggedIn" class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="w-full max-w-none px-4 sm:px-6 lg:px-10 2xl:px-12">
        <div class="flex gap-1">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            @click="currentView = tab.id"
            class="px-4 py-3 font-medium border-b-2 transition"
            :class="currentView === tab.id
              ? 'border-emerald-500 text-emerald-600 dark:text-emerald-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 hover:dark:text-gray-200'"
          >
            {{ tab.icon }} {{ tab.label }}
          </button>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="w-full max-w-none px-4 sm:px-6 lg:px-10 2xl:px-12 py-6">
      <div v-if="!isLoggedIn" class="grid grid-cols-1 items-stretch gap-5 xl:min-h-[calc(100vh-11rem)] xl:grid-cols-2">
        <section class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg h-full flex flex-col">
          <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">Clinical Sign-In</p>
          <h2 class="mt-2 text-2xl font-bold text-gray-900 dark:text-white lg:text-[1.9rem]">From patient data to TB decision.</h2>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-gray-600 dark:text-gray-300">
            Open a case, review evidence, generate one guided report.
          </p>
          <div class="mt-4 rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/40">
            <div class="flex items-center justify-between">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">System workflow</h3>
              <p class="text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">Few words</p>
            </div>
            <div class="mt-3 overflow-hidden rounded-xl border border-gray-200 bg-slate-50 p-3 dark:border-gray-700 dark:bg-gray-800/80">
              <svg viewBox="0 0 920 320" class="h-auto w-full" role="img" aria-label="TB system workflow">
                <defs>
                  <filter id="tbCardShadow" x="-20%" y="-20%" width="140%" height="180%">
                    <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#0f172a" flood-opacity="0.08"/>
                  </filter>
                </defs>

                <rect x="18" y="18" width="884" height="284" rx="28" fill="#ffffff" />
                <rect x="42" y="38" width="210" height="244" rx="24" fill="#eff6ff" stroke="#cbd5e1" />
                <rect x="278" y="50" width="602" height="88" rx="22" fill="#ffffff" stroke="#dbeafe" filter="url(#tbCardShadow)" />
                <rect x="278" y="154" width="602" height="112" rx="22" fill="#ffffff" stroke="#e5e7eb" filter="url(#tbCardShadow)" />
                <rect x="292" y="62" width="132" height="64" rx="18" fill="#f0fdf4" stroke="#bbf7d0" />
                <rect x="438" y="62" width="132" height="64" rx="18" fill="#eff6ff" stroke="#bfdbfe" />
                <rect x="584" y="62" width="132" height="64" rx="18" fill="#f5f3ff" stroke="#ddd6fe" />
                <rect x="730" y="62" width="132" height="64" rx="18" fill="#f0fdf4" stroke="#bbf7d0" />

                <g transform="translate(72 64)">
                  <circle cx="74" cy="58" r="48" fill="#0f172a"/>
                  <path d="M74 26v26" stroke="#ffffff" stroke-width="4.5" stroke-linecap="round"/>
                  <path d="M73 39c-6 0-13 5-15 12-2 5-1 10 2 15 3 5 7 8 13 10l2-22V39z" fill="#ffffff"/>
                  <path d="M75 39c6 0 13 5 15 12 2 5 1 10-2 15-3 5-7 8-13 10l-2-22V39z" fill="#d1fae5"/>
                  <path d="M73 32c-3-4-7-6-11-6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
                  <path d="M75 32c3-4 7-6 11-6" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
                  <path d="M60 47l-6 8m9-4-10 13m16-10-7 10" stroke="#60a5fa" stroke-width="2.6" stroke-linecap="round"/>
                  <path d="M88 47l6 8m-9-4 10 13m-16-10 7 10" stroke="#34d399" stroke-width="2.6" stroke-linecap="round"/>
                  <circle cx="95" cy="68" r="2.8" fill="#34d399"/>
                  <circle cx="89" cy="76" r="2.3" fill="#34d399"/>
                  <circle cx="102" cy="75" r="2.3" fill="#34d399"/>
                </g>
                <text x="147" y="205" text-anchor="middle" font-size="20" font-weight="700" fill="#0f172a">TB System</text>
                <text x="147" y="226" text-anchor="middle" font-size="12" fill="#475569">sign in</text>
                <text x="147" y="243" text-anchor="middle" font-size="12" fill="#475569">evaluate</text>
                <text x="147" y="260" text-anchor="middle" font-size="12" fill="#475569">guide care</text>

                <path d="M424 94h14" stroke="#10b981" stroke-width="4" stroke-linecap="round"/>
                <path d="M570 94h14" stroke="#2563eb" stroke-width="4" stroke-linecap="round"/>
                <path d="M716 94h14" stroke="#7c3aed" stroke-width="4" stroke-linecap="round"/>
                <path d="M430 88l8 6-8 6" fill="none" stroke="#10b981" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M576 88l8 6-8 6" fill="none" stroke="#2563eb" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M722 88l8 6-8 6" fill="none" stroke="#7c3aed" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>

                <g>
                  <circle cx="322" cy="94" r="16" fill="#dcfce7"/>
                  <circle cx="468" cy="94" r="16" fill="#dbeafe"/>
                  <circle cx="614" cy="94" r="16" fill="#ede9fe"/>
                  <circle cx="760" cy="94" r="16" fill="#dcfce7"/>
                </g>

                <g fill="none" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="322" cy="90" r="5.5" stroke="#059669" stroke-width="2.5"/>
                  <path d="M312 106c4-6 9-9 15-9 6 0 11 3 15 9" stroke="#059669" stroke-width="2.5"/>
                  <path d="M334 104h8" stroke="#059669" stroke-width="2.5"/>
                  <path d="M338 100v8" stroke="#059669" stroke-width="2.5"/>

                  <path d="M458 103l5-11 5 7 5-11" stroke="#2563eb" stroke-width="3"/>
                  <path d="M454 108h27" stroke="#2563eb" stroke-width="2.6"/>
                  <circle cx="477" cy="82" r="4" stroke="#2563eb" stroke-width="2.5"/>

                  <ellipse cx="614" cy="91" rx="8" ry="10" stroke="#7c3aed" stroke-width="2.5"/>
                  <circle cx="609" cy="87" r="1.6" fill="#7c3aed"/>
                  <circle cx="617" cy="93" r="1.6" fill="#7c3aed"/>
                  <path d="M622 103l6 6" stroke="#7c3aed" stroke-width="2.5"/>

                  <path d="M750 95l6 6 13-14" stroke="#16a34a" stroke-width="4"/>
                  <path d="M760 79v8" stroke="#16a34a" stroke-width="2.5"/>
                </g>

                <g font-family="Inter, Arial, sans-serif">
                  <text x="350" y="84" font-size="9" font-weight="700" fill="#059669">STEP 1</text>
                  <text x="350" y="103" font-size="15" font-weight="700" fill="#065f46">Collect</text>

                  <text x="496" y="84" font-size="9" font-weight="700" fill="#2563eb">STEP 2</text>
                  <text x="496" y="103" font-size="15" font-weight="700" fill="#1d4ed8">Analyze</text>

                  <text x="642" y="84" font-size="9" font-weight="700" fill="#7c3aed">STEP 3</text>
                  <text x="642" y="103" font-size="15" font-weight="700" fill="#6d28d9">Classify</text>

                  <text x="788" y="84" font-size="9" font-weight="700" fill="#16a34a">STEP 4</text>
                  <text x="788" y="103" font-size="15" font-weight="700" fill="#166534">Treat</text>
                </g>

                <g>
                  <rect x="298" y="172" width="176" height="76" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>
                  <rect x="488" y="172" width="176" height="76" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>
                  <rect x="678" y="172" width="170" height="76" rx="18" fill="#f8fafc" stroke="#cbd5e1"/>

                  <rect x="320" y="188" width="40" height="40" rx="12" fill="#ecfdf5"/>
                  <path d="M340 195v26" stroke="#059669" stroke-width="2.6" stroke-linecap="round"/>
                  <path d="M340 201c-5 0-8 4-9 8-1 4 0 8 2 10 2 3 4 5 7 6l1-12v-12z" fill="#ffffff"/>
                  <path d="M340 201c5 0 8 4 9 8 1 4 0 8-2 10-2 3-4 5-7 6l-1-12v-12z" fill="#d1fae5"/>
                  <text x="374" y="201" font-size="12" font-weight="700" fill="#0f172a">Patient</text>
                  <text x="374" y="218" font-size="10" fill="#475569">symptoms</text>
                  <text x="374" y="232" font-size="10" fill="#475569">tests</text>

                  <rect x="508" y="188" width="40" height="40" rx="12" fill="#dbeafe"/>
                  <path d="M519 219h20" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round"/>
                  <path d="M523 214l4-10 4 6 4-12" stroke="#2563eb" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
                  <text x="560" y="201" font-size="12" font-weight="700" fill="#0f172a">TB type</text>
                  <text x="560" y="218" font-size="10" fill="#475569">bacteria</text>
                  <text x="560" y="232" font-size="10" fill="#475569">resistance</text>

                  <rect x="696" y="188" width="40" height="40" rx="12" fill="#ede9fe"/>
                  <path d="M708 196h16l4 4v18h-20z" fill="none" stroke="#7c3aed" stroke-width="2.4" stroke-linejoin="round"/>
                  <path d="M724 196v5h5" stroke="#7c3aed" stroke-width="2.4" stroke-linecap="round"/>
                  <text x="748" y="201" font-size="12" font-weight="700" fill="#0f172a">Report</text>
                  <text x="748" y="218" font-size="10" fill="#475569">treatment</text>
                  <text x="748" y="232" font-size="10" fill="#475569">guidance</text>
                </g>
              </svg>
            </div>
            <div class="mt-3 flex items-center justify-between gap-4 rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-[11px] uppercase tracking-[0.2em] text-slate-500 dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-400">
              <span>New patient</span>
              <span>Existing patient</span>
              <span>Clinical report</span>
            </div>
          </div>
          <div class="mt-4 grid flex-1 content-start gap-3 lg:grid-cols-2">
            <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/30">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">What you can do</h3>
              <ul class="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <li><strong>New:</strong> start a TB case.</li>
                <li><strong>Existing:</strong> reopen a saved record.</li>
                <li><strong>Report:</strong> review guidance.</li>
              </ul>
            </div>
            <div class="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
              <h3 class="text-base font-semibold text-blue-900 dark:text-blue-100">After sign-in</h3>
              <ul class="mt-2 space-y-2 text-sm text-blue-800 dark:text-blue-200">
                <li>`Diagnose` update evidence.</li>
                <li>`Patients` open records.</li>
                <li>`Alerts` review notices.</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg h-full flex flex-col">
          <div class="rounded-2xl border border-emerald-200 bg-white p-4 dark:border-emerald-800 dark:bg-gray-900/30">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">Protected workspace</p>
            <h2 class="mt-2 text-2xl font-bold text-gray-900 dark:text-white lg:text-[1.8rem]">Welcome back</h2>
            <p class="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
              Continue to diagnosis, patients, and alerts.
            </p>
            <div class="mt-3 grid gap-2 sm:grid-cols-3">
              <div class="rounded-xl border border-emerald-100 bg-slate-50 px-3 py-2.5 dark:border-emerald-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">Diagnose</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">Review cases.</p>
              </div>
              <div class="rounded-xl border border-blue-100 bg-slate-50 px-3 py-2.5 dark:border-blue-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">Patients</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">Open records.</p>
              </div>
              <div class="rounded-xl border border-violet-100 bg-slate-50 px-3 py-2.5 dark:border-violet-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-violet-700 dark:text-violet-300">Alerts</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">See notices.</p>
              </div>
            </div>
          </div>
          <form @submit.prevent="login" class="space-y-3 flex-1 flex flex-col">
            <div>
              <label class="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
              <input
                v-model="loginEmail"
                type="email"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label class="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
              <div class="relative">
                <input
                  v-model="loginPassword"
                  :type="showLoginPassword ? 'text' : 'password'"
                  class="w-full rounded-lg border border-gray-300 px-4 py-2.5 pr-12 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  placeholder="Password"
                  required
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  @click="showLoginPassword = !showLoginPassword"
                  :title="showLoginPassword ? 'Hide password' : 'Show password'"
                >
                  {{ showLoginPassword ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-200">
              <p class="text-sm font-semibold">Useful sign-in notes</p>
              <ul class="mt-2 space-y-1 text-xs leading-5">
                <li>Use the eye icon to check the password.</li>
                <li>Email stays after refresh.</li>
                <li>Click your name or role to log out.</li>
              </ul>
            </div>
            <div class="grid gap-2 sm:grid-cols-2">
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
                <p class="text-sm font-semibold text-blue-900 dark:text-blue-100">Diagnose</p>
                <p class="mt-1 text-xs leading-5 text-blue-800 dark:text-blue-200">Enter or continue evidence.</p>
              </div>
              <div class="rounded-xl border border-indigo-200 bg-indigo-50 p-3 dark:border-indigo-800 dark:bg-indigo-900/20">
                <p class="text-sm font-semibold text-indigo-900 dark:text-indigo-100">Patients</p>
                <p class="mt-1 text-xs leading-5 text-indigo-800 dark:text-indigo-200">Open saved records.</p>
              </div>
              <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-900/20">
                <p class="text-sm font-semibold text-amber-900 dark:text-amber-100">Alerts</p>
                <p class="mt-1 text-xs leading-5 text-amber-800 dark:text-amber-200">Review follow-up notices.</p>
              </div>
              <div class="rounded-xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/30">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">Protected</p>
                <p class="mt-1 text-xs leading-5 text-gray-700 dark:text-gray-300">Clinician and admin access only.</p>
              </div>
            </div>
            <p v-if="loginError" class="text-sm font-medium text-red-600 dark:text-red-400">{{ loginError }}</p>
            <div class="mt-auto pt-1">
              <button
                type="submit"
                :disabled="loading"
                class="w-full rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
              >
                {{ loading ? 'Signing in...' : 'Sign in' }}
              </button>
            </div>
          </form>
        </section>
      </div>

      <!-- Diagnose View -->
      <div v-else-if="currentView === 'diagnose'">
        <div class="space-y-5">
          <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">Guided diagnose flow</p>
                <h2 class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">Complete the case in small steps, not one long form.</h2>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                  Move step by step through identity, clinical clues, tests, and DST before generating the report.
                </p>
              </div>
              <div class="grid gap-2 sm:grid-cols-3 lg:min-w-[420px]">
                <div class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 dark:border-emerald-800 dark:bg-emerald-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">Entry</p>
                  <p class="mt-1 text-xs leading-5 text-emerald-800 dark:text-emerald-200">Use guided TB suggestions or type your own evidence.</p>
                </div>
                <div class="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 dark:border-blue-800 dark:bg-blue-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">Order</p>
                  <p class="mt-1 text-xs leading-5 text-blue-800 dark:text-blue-200">Keep the same clinician workflow for new and existing patients.</p>
                </div>
                <div class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 dark:border-amber-800 dark:bg-amber-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700 dark:text-amber-300">Output</p>
                  <p class="mt-1 text-xs leading-5 text-amber-800 dark:text-amber-200">Generate TB type, DST review, and treatment guidance at the end.</p>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 2xl:grid-cols-[minmax(860px,1.45fr)_minmax(560px,0.95fr)] items-start">
          <!-- Patient Form -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg min-w-0">
            <div class="mb-4 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Patient Information</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">Structured evidence entry for TB screening, species estimation, DST review, and treatment planning.</p>
              </div>
              <div class="rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600 dark:bg-gray-700/60 dark:text-gray-300">
                Suggested items are TB-focused. Custom typing is always allowed.
              </div>
            </div>
            <div class="mb-6 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/30">
              <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">Step {{ currentDiagnosisStep }} of {{ diagnosisSteps.length }}</p>
                  <h3 class="mt-1 text-base font-semibold text-gray-900 dark:text-white">{{ currentDiagnosisMeta.title }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ currentDiagnosisMeta.description }}</p>
                </div>
                <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {{ Math.round((currentDiagnosisStep / diagnosisSteps.length) * 100) }}% complete
                </div>
              </div>
              <div class="mt-4 grid gap-2 md:grid-cols-4">
                <button
                  v-for="step in diagnosisSteps"
                  :key="step.id"
                  type="button"
                  @click="goToDiagnosisStep(step.id)"
                  class="rounded-xl border px-3 py-3 text-left transition"
                  :class="currentDiagnosisStep === step.id
                    ? 'border-emerald-400 bg-white shadow-sm dark:border-emerald-500 dark:bg-gray-800'
                    : 'border-gray-200 bg-white/70 hover:border-emerald-200 hover:bg-white dark:border-gray-700 dark:bg-gray-800/60 dark:hover:border-emerald-700'"
                >
                  <div class="flex items-center gap-3">
                    <span
                      class="flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold"
                      :class="currentDiagnosisStep === step.id
                        ? 'bg-emerald-600 text-white'
                        : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200'"
                    >
                      {{ step.id }}
                    </span>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ step.title }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ step.short }}</p>
                    </div>
                  </div>
                </button>
              </div>
            </div>
            <form @submit.prevent="diagnosePatient" class="space-y-5">
              <section v-show="currentDiagnosisStep === 1" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700">
                <div class="mb-4">
                  <h3 class="font-semibold text-gray-900 dark:text-white">1. Patient Identity</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Basic patient details used for record linking and report display.</p>
                </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">First Name</label>
                  <input
                    v-model="patient.first_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    placeholder="First name"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Last Name</label>
                  <input
                    v-model="patient.last_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    placeholder="Last name"
                  />
                </div>
              </div>
              <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Patient ID</label>
                  <input
                    v-model="patient.patient_id"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    placeholder="Unique ID"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Age</label>
                  <input
                    v-model.number="patient.age"
                    type="number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    placeholder="Age"
                  />
                </div>
              </div>
              <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Gender</label>
                  <select
                    v-model="patient.gender"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Male</option>
                    <option>Female</option>
                    <option>Other</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">City</label>
                  <input
                    v-model="patient.city"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    placeholder="City"
                  />
                </div>
              </div>
              </section>

              <section v-show="currentDiagnosisStep === 2" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">2. Clinical Clues</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Add symptoms and exposure history from the guided TB lists, or type your own item if not listed.</p>
                </div>
                <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Symptoms</label>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Type directly in the field. Suggested TB symptoms below can be clicked to append.</p>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">Step 1</span>
                  </div>
                  <textarea
                    v-model="patient.symptoms"
                    class="mt-3 w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    rows="3"
                    placeholder="Describe symptoms or keep the stored patient text as it is"
                  ></textarea>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="option in symptomOptions"
                      :key="option"
                      type="button"
                      class="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-700 hover:bg-emerald-100 dark:border-emerald-700 dark:bg-gray-800 dark:text-emerald-300"
                      @click="appendSuggestedValue('symptoms', option)"
                    >
                      + {{ option }}
                    </button>
                  </div>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Exposure History</label>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Existing patient exposure notes stay unchanged unless the clinician edits them.</p>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">Step 2</span>
                  </div>
                  <textarea
                    v-model="patient.exposure_history"
                    class="mt-3 w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    rows="3"
                    placeholder="Enter or review household, travel, animal, dairy, wildlife, or occupational exposure"
                  ></textarea>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="option in exposureOptions"
                      :key="option"
                      type="button"
                      class="rounded-full border border-blue-200 bg-white px-3 py-1 text-xs text-blue-700 hover:bg-blue-100 dark:border-blue-700 dark:bg-gray-800 dark:text-blue-300"
                      @click="appendSuggestedValue('exposure_history', option)"
                    >
                      + {{ option }}
                    </button>
                  </div>
                </div>
              </section>

              <section v-show="currentDiagnosisStep === 3" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">3. Species And Test Results</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Choose known results or leave bacteria on `Auto-detect` so the system estimates from the patient record.</p>
                </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">TB Bacteria Species</label>
                  <select
                    v-model="patient.bacteria_species"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Auto-detect</option>
                    <option>Mycobacterium tuberculosis</option>
                    <option>Mycobacterium bovis</option>
                    <option>Mycobacterium africanum</option>
                    <option>Mycobacterium canettii</option>
                    <option>Mycobacterium microti</option>
                    <option>Mycobacterium caprae</option>
                    <option>Mycobacterium pinnipedii</option>
                    <option>Mycobacterium orygis</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">TB Culture</label>
                  <select
                    v-model="patient.tb_culture"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Sputum Smear</label>
                  <select
                    v-model="patient.sputum_smear_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">GeneXpert</label>
                  <select
                    v-model="patient.genexpert_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Chest X-ray</label>
                  <select
                    v-model="patient.chest_xray"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Normal</option>
                    <option>Abnormal</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Drug Resistance</label>
                  <select
                    v-model="patient.drug_resistance"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">TST</label>
                  <select
                    v-model="patient.tst"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">IGRA</label>
                  <select
                    v-model="patient.igra"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>Unknown</option>
                    <option>Positive</option>
                    <option>Negative</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">HIV Status</label>
                  <select
                    v-model="patient.hiv"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Diabetes</label>
                  <select
                    v-model="patient.diabetes"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>No</option>
                    <option>Yes</option>
                    <option>Unknown</option>
                  </select>
                </div>
              </div>
              </section>

              <section v-show="currentDiagnosisStep === 4" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">4. DST And Resistance Decision Support</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">Keep these as normal input fields. Suggested TB DST phrases and medicines can be appended when useful.</p>
                </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Antibiogram / DST Summary</label>
                  <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                    <textarea
                      v-model="patient.antibiogram_result"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      rows="3"
                      placeholder="Enter DST summary or keep stored text for an existing patient"
                    ></textarea>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button
                        v-for="option in antibiogramOptions"
                        :key="option"
                        type="button"
                        class="rounded-full border border-rose-200 bg-white px-3 py-1 text-xs text-rose-700 hover:bg-rose-100 dark:border-rose-700 dark:bg-gray-800 dark:text-rose-300"
                        @click="appendSuggestedValue('antibiogram_result', option)"
                      >
                        + {{ option }}
                      </button>
                    </div>
                  </div>
                </div>
                <div class="space-y-4">
                  <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                    <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Resistant To</label>
                    <input
                      v-model="patient.resistant_to"
                      list="tb-drug-options"
                      type="text"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      placeholder="Type resistant medicines or reuse stored patient text"
                    />
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button
                        v-for="option in drugOptions"
                        :key="`res-${option}`"
                        type="button"
                        class="rounded-full border border-rose-200 bg-white px-3 py-1 text-xs text-rose-700 hover:bg-rose-100 dark:border-rose-700 dark:bg-gray-800 dark:text-rose-300"
                        @click="appendSuggestedValue('resistant_to', option)"
                      >
                        + {{ option }}
                      </button>
                    </div>
                  </div>
                  <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                    <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Susceptible To</label>
                    <input
                      v-model="patient.susceptible_to"
                      list="tb-drug-options"
                      type="text"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      placeholder="Type susceptible medicines or reuse stored patient text"
                    />
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button
                        v-for="option in drugOptions"
                        :key="`sus-${option}`"
                        type="button"
                        class="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-700 hover:bg-emerald-100 dark:border-emerald-700 dark:bg-gray-800 dark:text-emerald-300"
                        @click="appendSuggestedValue('susceptible_to', option)"
                      >
                        + {{ option }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              </section>
              <div class="flex flex-col gap-3 rounded-xl border border-gray-200 bg-gray-50 px-4 py-4 dark:border-gray-700 dark:bg-gray-900/30 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ currentDiagnosisMeta.footer }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">You can move between steps without losing typed content.</p>
                </div>
                <div class="flex flex-wrap gap-3">
                  <button
                    v-if="currentDiagnosisStep > 1"
                    type="button"
                    @click="previousDiagnosisStep"
                    class="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                  >
                    Previous step
                  </button>
                  <button
                    v-if="currentDiagnosisStep < diagnosisSteps.length"
                    type="button"
                    @click="nextDiagnosisStep"
                    class="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
                  >
                    Next step
                  </button>
                  <button
                    v-else
                    type="submit"
                    :disabled="loading"
                    class="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {{ loading ? 'Analyzing...' : 'Analyze & Diagnose' }}
                  </button>
                </div>
              </div>
            </form>

            <datalist id="tb-drug-options">
              <option v-for="option in drugOptions" :key="option" :value="option" />
            </datalist>
          </div>

          <!-- Results -->
          <div v-if="diagnosisResult" class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg space-y-6 min-w-0 xl:sticky xl:top-6 xl:max-h-[calc(100vh-7rem)] xl:overflow-y-auto">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Diagnostic Report</h2>
            
            <!-- Patient Info -->
            <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p class="font-medium text-gray-900 dark:text-white">{{ diagnosisResult.patient_name }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">ID: {{ diagnosisResult.patient_id }}</p>
            </div>

            <!-- Symptom Analysis -->
            <div class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">Symptom Analysis</h3>
              <div class="p-4 rounded-lg border" :class="riskColorClass">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-semibold text-lg">{{ diagnosisResult.symptom_analysis.risk_level }}</span>
                  <span class="text-sm px-2 py-1 bg-white/50 dark:bg-gray-800/50 rounded">
                    Score: {{ diagnosisResult.symptom_analysis.risk_score }}
                  </span>
                </div>
                <p class="text-sm">{{ diagnosisResult.symptom_analysis.clinical_advice }}</p>
                <ul v-if="diagnosisResult.symptom_analysis.red_flags.length > 0" class="mt-2 text-sm space-y-1">
                  <li v-for="(flag, i) in diagnosisResult.symptom_analysis.red_flags" :key="i" class="text-red-600 dark:text-red-400">
                    {{ flag }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Test Evaluation -->
            <div class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">Test Evaluation</h3>
              <div class="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
                <p class="text-lg font-medium text-blue-800 dark:text-blue-300">
                  {{ diagnosisResult.test_evaluation.classification }}
                </p>
                <p class="text-sm text-blue-700 dark:text-blue-400 mt-1">
                  Confidence: {{ diagnosisResult.test_evaluation.confidence_percent }}%
                </p>
                <ul class="mt-3 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li v-for="(finding, i) in diagnosisResult.test_evaluation.findings" :key="i">
                    {{ finding }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Bacteria Assessment -->
            <div v-if="diagnosisResult.bacteria_assessment" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">TB Bacteria Assessment</h3>
              <div class="p-4 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-200 dark:border-amber-800">
                <p class="text-lg font-medium text-amber-800 dark:text-amber-300">
                  {{ diagnosisResult.bacteria_assessment.species }}
                </p>
                <p class="mt-1 text-sm text-amber-700 dark:text-amber-400">
                  Method: {{ diagnosisResult.bacteria_assessment.mode }} | Supported species: {{ diagnosisResult.bacteria_assessment.supported_species_count }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  {{ diagnosisResult.bacteria_assessment.description }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  <strong>Reason:</strong> {{ diagnosisResult.bacteria_assessment.reason }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>Typical source:</strong> {{ diagnosisResult.bacteria_assessment.typical_source }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>Lab note:</strong> {{ diagnosisResult.bacteria_assessment.lab_note }}
                </p>
              </div>
            </div>

            <!-- Infection Assessment -->
            <div v-if="diagnosisResult.infection_assessment" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">Infection Assessment</h3>
              <div class="p-4 bg-sky-50 dark:bg-sky-900/30 rounded-lg border border-sky-200 dark:border-sky-800">
                <p class="text-lg font-medium text-sky-800 dark:text-sky-300">
                  {{ diagnosisResult.infection_assessment.primary_infection }}
                </p>
                <ul class="mt-3 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li
                    v-for="(infection, i) in diagnosisResult.infection_assessment.infection_types"
                    :key="i"
                  >
                    {{ infection.label }} - {{ infection.site }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Resistance Profile -->
            <div v-if="diagnosisResult.resistance_profile" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">Resistance / DST Profile</h3>
              <div class="p-4 bg-rose-50 dark:bg-rose-900/30 rounded-lg border border-rose-200 dark:border-rose-800">
                <p class="text-lg font-medium text-rose-800 dark:text-rose-300">
                  {{ diagnosisResult.resistance_profile.classification }}
                </p>
                <p class="mt-1 text-sm text-rose-700 dark:text-rose-400">
                  Regimen level: {{ diagnosisResult.resistance_profile.regimen_level }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  <strong>Antibiogram:</strong> {{ diagnosisResult.resistance_profile.antibiogram_result }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>Resistant to:</strong> {{ diagnosisResult.resistance_profile.resistant_to.join(', ') || 'None provided' }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>Susceptible to:</strong> {{ diagnosisResult.resistance_profile.susceptible_to.join(', ') || 'None provided' }}
                </p>
                <ul class="mt-3 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li v-for="(item, i) in diagnosisResult.resistance_profile.decision_basis" :key="i">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- ML Prediction -->
            <div v-if="diagnosisResult.ml_prediction" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">ML Prediction</h3>
              <div class="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg border border-purple-200 dark:border-purple-800">
                <p class="font-medium text-purple-800 dark:text-purple-300">
                  TB Prediction: {{ formatPredictionLabel(diagnosisResult.ml_prediction.tb_status?.prediction, 'tb') }}
                </p>
                <p v-if="diagnosisResult.ml_prediction.tb_status" class="mt-1 text-sm text-purple-700 dark:text-purple-400">
                  {{ buildConfidenceSummary(diagnosisResult.ml_prediction.tb_status, 'tb') }}
                </p>
                <div class="mt-2 text-sm space-y-1">
                  <p v-if="diagnosisResult.ml_prediction.drug_resistance" class="text-purple-700 dark:text-purple-400">
                    Drug Resistance Prediction: {{ formatPredictionLabel(diagnosisResult.ml_prediction.drug_resistance.prediction, 'resistance') }}
                  </p>
                  <p v-if="diagnosisResult.ml_prediction.drug_resistance" class="text-purple-700 dark:text-purple-400">
                    {{ buildConfidenceSummary(diagnosisResult.ml_prediction.drug_resistance, 'resistance') }}
                  </p>
                  <p
                    v-for="item in formatProbabilityList(diagnosisResult.ml_prediction.tb_status?.probabilities)"
                    :key="item.label"
                    class="text-purple-700 dark:text-purple-400"
                  >
                    {{ item.label }}: {{ item.value }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Treatment Recommendation -->
            <div class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">Treatment Recommendation</h3>
              <div class="p-4 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <div class="flex items-center justify-between mb-2">
                  <p class="font-semibold text-emerald-800 dark:text-emerald-300">
                    {{ diagnosisResult.treatment_recommendation.regimen_name || diagnosisResult.treatment_recommendation.type || diagnosisResult.treatment_recommendation.category || 'Treatment plan' }}
                  </p>
                  <span class="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded font-medium">
                    {{ diagnosisResult.treatment_recommendation.urgency }}
                  </span>
                </div>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Category:</strong> {{ diagnosisResult.treatment_recommendation.category }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Bacteria:</strong> {{ diagnosisResult.treatment_recommendation.bacteria_species || diagnosisResult.bacteria_assessment?.species || 'Not available in this response' }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Infection:</strong> {{ diagnosisResult.treatment_recommendation.infection_type || diagnosisResult.infection_assessment?.primary_infection || diagnosisResult.treatment_recommendation.category || 'Not available in this response' }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Resistance:</strong> {{ diagnosisResult.treatment_recommendation.resistance_class || diagnosisResult.resistance_profile?.classification || diagnosisResult.ml_prediction?.drug_resistance?.prediction || 'Not available in this response' }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Level:</strong> {{ diagnosisResult.treatment_recommendation.regimen_level || diagnosisResult.resistance_profile?.regimen_level || 'WHO rule-based treatment level' }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Duration:</strong> {{ diagnosisResult.treatment_recommendation.duration }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Drugs:</strong> {{ diagnosisResult.treatment_recommendation.drugs }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Dosage:</strong> {{ diagnosisResult.treatment_recommendation.dosage }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Administration:</strong> {{ diagnosisResult.treatment_recommendation.administration }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Monitoring:</strong> {{ diagnosisResult.treatment_recommendation.monitoring }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Guideline:</strong> {{ diagnosisResult.treatment_recommendation.guideline_source || 'WHO-aligned TB treatment guidance' }}
                </p>
                <ul v-if="diagnosisResult.treatment_recommendation.decision_basis?.length" class="mt-3 text-sm text-emerald-700 dark:text-emerald-400 space-y-1">
                  <li v-for="(item, i) in diagnosisResult.treatment_recommendation.decision_basis" :key="i">
                    {{ item }}
                  </li>
                </ul>
                <div v-if="diagnosisResult.treatment_recommendation.treatment_options?.length > 1" class="mt-4">
                  <p class="text-sm font-semibold text-emerald-800 dark:text-emerald-300">Other treatment options</p>
                  <ul class="mt-2 text-sm text-emerald-700 dark:text-emerald-400 space-y-2">
                    <li
                      v-for="(option, i) in diagnosisResult.treatment_recommendation.treatment_options.slice(1)"
                      :key="i"
                    >
                      {{ option.name }} - {{ option.duration }} - {{ option.drugs }}
                    </li>
                  </ul>
                </div>
                <p class="text-xs text-emerald-600 dark:text-emerald-500 mt-2">
                  {{ diagnosisResult.treatment_recommendation.notes }}
                </p>
              </div>
            </div>

            <p class="text-xs text-gray-500 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              Disclaimer: This system is for educational purposes only. Always consult qualified medical professionals.
            </p>
          </div>

          <div v-else class="rounded-xl border border-dashed border-gray-300 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800 xl:sticky xl:top-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Diagnostic Report</h2>
            <p class="mt-3 text-sm text-gray-600 dark:text-gray-300">
              The report will appear here after you complete the guided form and click `Analyze & Diagnose`.
            </p>
            <div class="mt-4 grid gap-3">
              <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700/40">
                <p class="text-sm font-medium text-gray-800 dark:text-gray-200">What the report will show</p>
                <ul class="mt-2 space-y-2 text-sm text-gray-600 dark:text-gray-300">
                  <li>TB risk and red flags</li>
                  <li>Estimated bacteria and infection type</li>
                  <li>DST / resistance interpretation</li>
                  <li>Treatment plan and monitoring guidance</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Patients View -->
      <div v-else-if="currentView === 'patients'">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div class="flex items-center justify-between mb-6">
            <div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Patients</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Showing {{ patientRangeStart }}-{{ patientRangeEnd }} of {{ patientTotal }} records
              </p>
            </div>
            <div class="flex gap-2">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search patients..."
                class="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
              <select
                v-model="patientSort"
                @change="refreshPatients"
                class="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="id_asc">DB Order</option>
                <option value="id_desc">Newest ID</option>
                <option value="created_desc">Newest Created</option>
                <option value="created_asc">Oldest Created</option>
              </select>
              <button
                @click="refreshPatients"
                class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
          
          <div v-if="patients.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            No patients found. Add a patient through the diagnosis page.
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">ID</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Name</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Age</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Gender</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">City</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Created</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="p in patients"
                  :key="p.id"
                  @click="showPatientDetail(p)"
                  class="border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer"
                >
                  <td class="py-3 px-4 text-gray-900 dark:text-white">{{ p.patient_id }}</td>
                  <td class="py-3 px-4 text-gray-900 dark:text-white">{{ p.first_name }} {{ p.last_name }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ p.age }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ p.gender }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ p.city }}</td>
                  <td class="py-3 px-4 text-gray-600 dark:text-gray-400">{{ formatDate(p.created_at) }}</td>
                </tr>
              </tbody>
            </table>

            <div class="mt-4 flex items-center justify-between gap-4">
              <p class="text-sm text-gray-500 dark:text-gray-400">
                Page {{ patientsPage }} of {{ patientPages }}
              </p>
              <div class="flex gap-2">
                <button
                  :disabled="patientsPage <= 1"
                  @click="changePatientsPage(patientsPage - 1)"
                  class="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                >
                  Previous
                </button>
                <button
                  :disabled="patientsPage >= patientPages"
                  @click="changePatientsPage(patientsPage + 1)"
                  class="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Alerts View -->
      <div v-else-if="currentView === 'alerts'">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Alerts</h2>
            <button
              @click="loadAlerts"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
            >
              🔄 Refresh
            </button>
          </div>
          
          <div v-if="alerts.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            No alerts.
          </div>

          <div v-else class="space-y-3">
            <div
              v-for="alert in alerts"
              :key="alert.id"
              @click="markAsRead(alert)"
              class="p-4 rounded-lg border cursor-pointer transition"
              :class="alert.is_read
                ? 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-600'
                : 'bg-white dark:bg-gray-700 border-emerald-200 dark:border-emerald-700'"
            >
              <div class="flex items-start justify-between">
                <div>
                  <p class="font-medium" :class="alert.severity === 'high' ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400'">
                    {{ alert.severity === 'high' ? '🚨' : '⚠️' }} {{ alert.alert_type }}
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ alert.message }}</p>
                  <p class="text-xs text-gray-400 mt-1">{{ formatDate(alert.created_at) }}</p>
                </div>
                <span v-if="!alert.is_read" class="w-2 h-2 bg-emerald-500 rounded-full"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const API_BASE = 'http://localhost:5000/api'

const isDarkMode = ref(false)
const currentView = ref('diagnose')
const loading = ref(false)
const searchQuery = ref('')
const patients = ref([])
const alerts = ref([])
const diagnosisResult = ref(null)
const patientTotal = ref(0)
const patientPages = ref(1)
const patientsPage = ref(1)
const patientPageSize = ref(20)
const patientSort = ref('id_asc')
const currentDiagnosisStep = ref(1)
const currentUser = ref(null)
const token = ref('')
const loginEmail = ref('')
const loginPassword = ref('')
const showLoginPassword = ref(false)
const loginError = ref('')

const isLoggedIn = computed(() => !!token.value)
const userDisplayName = computed(() => {
  if (!currentUser.value) return 'Authenticated user'
  return currentUser.value.username || currentUser.value.email || 'Authenticated user'
})
const userRoleLabel = computed(() => {
  if (!currentUser.value?.role) return 'authorized'
  return String(currentUser.value.role).replace(/_/g, ' ')
})

const tabs = [
  { id: 'diagnose', label: 'Diagnose', icon: '🏥' },
  { id: 'patients', label: 'Patients', icon: '👥' },
  { id: 'alerts', label: 'Alerts', icon: '🔔' }
]

const diagnosisSteps = [
  {
    id: 1,
    title: 'Patient Identity',
    short: 'name and record',
    description: 'Capture the core patient identity used to save, reopen, and display the clinical record.',
    footer: 'Confirm the patient identity details before moving to symptoms.'
  },
  {
    id: 2,
    title: 'Clinical Clues',
    short: 'symptoms and exposure',
    description: 'Document TB symptoms and exposure history using suggested clues or direct typing.',
    footer: 'Review symptoms and exposure history, then continue to laboratory and imaging results.'
  },
  {
    id: 3,
    title: 'Species And Tests',
    short: 'results and evidence',
    description: 'Enter bacteria selection, smear, culture, GeneXpert, x-ray, TST, IGRA, and related evidence.',
    footer: 'Check test results before advancing to DST and resistance evidence.'
  },
  {
    id: 4,
    title: 'DST And Resistance',
    short: 'drug decision support',
    description: 'Complete antibiogram, resistance, and susceptibility details before generating the report.',
    footer: 'Finish the last step and run the TB analysis when the record is ready.'
  }
]

const symptomOptions = [
  'Persistent cough for 2+ weeks',
  'Hemoptysis',
  'Fever',
  'Night sweats',
  'Weight loss',
  'Chest pain',
  'Fatigue',
  'Breathlessness',
  'Loss of appetite',
  'Lymph node swelling',
  'Back pain',
  'Abdominal pain',
  'Neck stiffness',
  'Pleural chest pain'
]

const exposureOptions = [
  'Household TB contact',
  'Close contact with MDR-TB patient',
  'Cattle exposure',
  'Goat or sheep exposure',
  'Unpasteurized milk intake',
  'Rodent exposure',
  'Marine mammal exposure',
  'South Asia travel history',
  'West Africa residence history',
  'Horn of Africa travel history',
  'Prison or crowded living conditions',
  'Healthcare worker exposure',
  'Previous untreated TB episode',
  'Livestock herd exposure'
]

const antibiogramOptions = [
  'Fully susceptible first-line profile',
  'Rifampicin resistance detected',
  'Isoniazid resistance detected',
  'Pyrazinamide resistance suspected',
  'MDR profile confirmed by DST',
  'XDR profile suspected',
  'Fluoroquinolone susceptible',
  'Linezolid active',
  'Clofazimine active',
  'Reference laboratory confirmation recommended'
]

const drugOptions = [
  'isoniazid',
  'rifampicin',
  'pyrazinamide',
  'ethambutol',
  'rifapentine',
  'levofloxacin',
  'moxifloxacin',
  'bedaquiline',
  'linezolid',
  'clofazimine',
  'cycloserine',
  'delamanid',
  'amikacin',
  'kanamycin'
]

const patient = ref({
  patient_id: '',
  first_name: '',
  last_name: '',
  age: 30,
  gender: 'Male',
  city: '',
  symptoms: '',
  exposure_history: '',
  bacteria_species: 'Auto-detect',
  tb_culture: 'Unknown',
  sputum_smear_test: 'Unknown',
  genexpert_test: 'Unknown',
  chest_xray: 'Unknown',
  tst: 'Unknown',
  igra: 'Unknown',
  antibiogram_result: '',
  resistant_to: '',
  susceptible_to: '',
  drug_resistance: 'No',
  hiv: 'No',
  diabetes: 'No'
})

const unreadAlerts = computed(() => alerts.value.filter(a => !a.is_read).length)
const patientRangeStart = computed(() => {
  if (patientTotal.value === 0) return 0
  return (patientsPage.value - 1) * patientPageSize.value + 1
})
const patientRangeEnd = computed(() => {
  if (patientTotal.value === 0) return 0
  return Math.min(patientsPage.value * patientPageSize.value, patientTotal.value)
})
const currentDiagnosisMeta = computed(() => diagnosisSteps.find(step => step.id === currentDiagnosisStep.value) || diagnosisSteps[0])

const riskColorClass = computed(() => {
  if (!diagnosisResult.value) return 'bg-gray-100 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
  const risk = diagnosisResult.value.symptom_analysis.risk_level
  if (risk.includes('HIGH')) return 'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700'
  if (risk.includes('MODERATE')) return 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-700'
  if (risk.includes('LOW')) return 'bg-blue-100 dark:bg-blue-900/30 border-blue-300 dark:border-blue-700'
  return 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700'
})

function canUseBrowserStorage() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined'
}

function readStoredValue(key, fallback = '') {
  if (!canUseBrowserStorage()) return fallback
  return window.localStorage.getItem(key) || fallback
}

function writeStoredValue(key, value) {
  if (!canUseBrowserStorage()) return
  window.localStorage.setItem(key, value)
}

function removeStoredValue(key) {
  if (!canUseBrowserStorage()) return
  window.localStorage.removeItem(key)
}

function applyDarkMode(enabled) {
  if (typeof document === 'undefined') return
  document.documentElement.classList.toggle('dark', enabled)
}

function toggleDarkMode() {
  isDarkMode.value = !isDarkMode.value
  applyDarkMode(isDarkMode.value)
  writeStoredValue('tb_dark_mode', isDarkMode.value ? 'dark' : 'light')
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString()
}

function goToDiagnosisStep(stepId) {
  const nextStep = Number(stepId)
  if (!Number.isInteger(nextStep)) return
  if (nextStep < 1 || nextStep > diagnosisSteps.length) return
  currentDiagnosisStep.value = nextStep
}

function nextDiagnosisStep() {
  if (currentDiagnosisStep.value >= diagnosisSteps.length) return
  currentDiagnosisStep.value += 1
}

function previousDiagnosisStep() {
  if (currentDiagnosisStep.value <= 1) return
  currentDiagnosisStep.value -= 1
}

function appendSuggestedValue(field, suggestion) {
  const value = String(suggestion || '').trim()
  if (!value) return

  const currentText = String(patient.value[field] || '').trim()
  if (!currentText) {
    patient.value[field] = value
    return
  }

  const currentItems = currentText
    .split(/[;,\n]/)
    .map(item => item.trim().toLowerCase())
    .filter(Boolean)

  if (currentItems.includes(value.toLowerCase())) return
  patient.value[field] = `${currentText}, ${value}`
}

function formatPercent(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '-'
  return `${(numeric * 100).toFixed(1)}%`
}

function formatPredictionLabel(value, type = 'tb') {
  const normalized = String(value || '').trim().toLowerCase()
  if (!normalized) return 'Not available'
  if (type === 'tb') {
    if (normalized === 'yes' || normalized === 'positive') return 'TB likely'
    if (normalized === 'no' || normalized === 'negative') return 'TB not likely'
  }
  if (type === 'resistance') {
    if (normalized === 'yes' || normalized === 'positive') return 'Drug resistance likely'
    if (normalized === 'no' || normalized === 'negative') return 'Drug resistance not predicted'
  }
  return value
}

function buildConfidenceSummary(predictionBlock, type = 'tb') {
  if (!predictionBlock) return 'No model confidence available.'
  const predictionLabel = formatPredictionLabel(predictionBlock.prediction, type)
  return `${predictionLabel} with ${formatPercent(predictionBlock.confidence)} model confidence.`
}

function formatProbabilityList(probabilities) {
  if (!probabilities || typeof probabilities !== 'object') return []
  return Object.entries(probabilities).map(([label, value]) => ({
    label,
    value: formatPercent(value)
  }))
}

function clearSession(preserveEmail = true) {
  token.value = ''
  currentUser.value = null
  diagnosisResult.value = null
  patients.value = []
  alerts.value = []
  removeStoredValue('tb_token')
  if (!preserveEmail) removeStoredValue('tb_login_email')
}

async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) }
  if (!headers['Content-Type'] && options.body) headers['Content-Type'] = 'application/json'
  if (token.value) headers.Authorization = `Bearer ${token.value}`

  // #region debug-point A:api-fetch
  fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"A",location:"frontend/app.vue:615",msg:"[DEBUG] apiFetch request",data:{path,hasToken:!!token.value,authorizationHeader:!!headers.Authorization,currentView:currentView.value},ts:Date.now()})}).catch(()=>{})
  // #endregion
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  // #region debug-point B:api-response
  fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"B",location:"frontend/app.vue:621",msg:"[DEBUG] apiFetch response",data:{path,status:response.status,ok:response.ok},ts:Date.now()})}).catch(()=>{})
  // #endregion
  if (response.status === 401) {
    clearSession()
    loginError.value = 'Your session expired. Please sign in again.'
    throw new Error('Unauthorized')
  }
  if (!response.ok) {
    const errorBody = await response.clone().json().catch(() => null)
    throw new Error(errorBody?.msg || errorBody?.error || `Request failed with status ${response.status}`)
  }
  return response
}

async function loadCurrentUser() {
  if (!token.value) {
    currentUser.value = null
    return
  }
  const response = await apiFetch('/auth/me')
  currentUser.value = await response.json()
  // #region debug-point C:auth-me
  fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"C",location:"frontend/app.vue:635",msg:"[DEBUG] auth me loaded",data:{userId:currentUser.value?.id||null,role:currentUser.value?.role||null},ts:Date.now()})}).catch(()=>{})
  // #endregion
}

async function login() {
  loading.value = true
  loginError.value = ''
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: loginEmail.value, password: loginPassword.value })
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      loginError.value = err.msg || 'Invalid email or password'
      return
    }
    const data = await response.json()
    token.value = data.access_token
    currentUser.value = data.user || null
    writeStoredValue('tb_token', token.value)
    writeStoredValue('tb_login_email', loginEmail.value)
    loginPassword.value = ''
    showLoginPassword.value = false
    currentView.value = 'diagnose'
    await loadPatients()
    await loadAlerts()
  } catch (error) {
    loginError.value = 'Login failed. Ensure the backend server is running and your credentials are correct.'
  } finally {
    loading.value = false
  }
}

function logout() {
  clearSession()
}

async function diagnosePatient() {
  loading.value = true
  loginError.value = ''
  try {
    const response = await apiFetch('/diagnose', {
      method: 'POST',
      body: JSON.stringify({ patient: patient.value })
    })
    diagnosisResult.value = await response.json()
    await loadPatients()
    await loadAlerts()
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? 'Please sign in again.' : 'Unable to complete the diagnosis request.'
  } finally {
    loading.value = false
  }
}

async function loadPatients() {
  try {
    if (!isLoggedIn.value) return
    const response = await apiFetch(`/patients?page=${patientsPage.value}&per_page=${patientPageSize.value}&sort=${encodeURIComponent(patientSort.value)}&search=${encodeURIComponent(searchQuery.value)}`)
    const data = await response.json()
    patients.value = data.patients || []
    patientTotal.value = data.total || 0
    patientPages.value = data.pages || 1
    patientsPage.value = data.current_page || 1
    patientSort.value = data.sort || patientSort.value
    // #region debug-point D:patients-loaded
    fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"D",location:"frontend/app.vue:695",msg:"[DEBUG] patients loaded",data:{count:patients.value.length,total:data.total||null,page:data.current_page||null,pages:data.pages||null,sort:data.sort||null,search:searchQuery.value},ts:Date.now()})}).catch(()=>{})
    // #endregion
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? 'Please sign in again.' : 'Unable to load patients.'
  }
}

async function loadAlerts() {
  try {
    if (!isLoggedIn.value) return
    const response = await apiFetch('/alerts')
    const data = await response.json()
    alerts.value = data.alerts || []
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? 'Please sign in again.' : 'Unable to load alerts.'
  }
}

async function markAsRead(alert) {
  if (alert.is_read) return
  try {
    await apiFetch(`/alerts/${alert.id}/read`, { method: 'PUT' })
    alert.is_read = true
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? 'Please sign in again.' : 'Unable to mark alert as read.'
  }
}

function showPatientDetail(p) {
  patient.value = { ...patient.value, ...p }
  currentDiagnosisStep.value = 1
  currentView.value = 'diagnose'
}

function refreshPatients() {
  patientsPage.value = 1
  loadPatients()
}

function changePatientsPage(page) {
  if (page < 1 || page > patientPages.value) return
  patientsPage.value = page
  loadPatients()
}

onMounted(() => {
  token.value = readStoredValue('tb_token')
  loginEmail.value = readStoredValue('tb_login_email')
  isDarkMode.value = readStoredValue('tb_dark_mode', 'light') === 'dark'
  applyDarkMode(isDarkMode.value)

  if (token.value) {
    loadCurrentUser().catch(() => clearSession())
  }

  if (isLoggedIn.value) {
    loadPatients()
    loadAlerts()
  }
})
</script>
