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
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">{{ t(TEXT.indexKicker) }}</h1>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.headerSubtitle) }}</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div class="relative">
              <button
                type="button"
                class="flex items-center gap-2 rounded-xl border border-gray-200 bg-white px-2.5 py-2 text-gray-700 shadow-sm transition hover:border-emerald-300 hover:bg-emerald-50 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-200 dark:hover:border-emerald-700 dark:hover:bg-gray-700"
                :aria-label="t(TEXT.languageLabel)"
                :aria-expanded="languageMenuOpen ? 'true' : 'false'"
                @click="languageMenuOpen = !languageMenuOpen"
              >
                <img
                  :src="selectedLanguageOption.flagSrc"
                  :alt="t(selectedLanguageOption.label)"
                  class="h-4 w-6 rounded-sm object-cover ring-1 ring-black/10"
                />
                <span class="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-semibold uppercase tracking-wide text-gray-700 dark:bg-gray-700 dark:text-gray-200">
                  {{ selectedLanguageOption.code }}
                </span>
                <svg viewBox="0 0 20 20" class="h-4 w-4 text-gray-500 dark:text-gray-300" fill="none" aria-hidden="true">
                  <path d="m5 7 5 5 5-5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
              <div
                v-if="languageMenuOpen"
                class="absolute right-0 z-20 mt-2 w-52 rounded-2xl border border-slate-200 bg-slate-900/95 p-2 text-white shadow-2xl ring-1 ring-black/10 backdrop-blur dark:border-slate-700"
              >
                <div class="mb-1 px-2 py-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">
                  {{ t(TEXT.langShort) }}
                </div>
                <button
                  v-for="lang in languageOptions"
                  :key="lang.code"
                  type="button"
                  class="flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm transition"
                  :class="uiLanguage === lang.code ? 'bg-emerald-500/15 text-emerald-300' : 'text-slate-100 hover:bg-white/5'"
                  @click="setLanguage(lang.code)"
                >
                  <img
                    :src="lang.flagSrc"
                    :alt="t(lang.label)"
                    class="h-4 w-6 rounded-sm object-cover ring-1 ring-black/10"
                  />
                  <span class="min-w-[2rem] text-xs font-semibold uppercase tracking-wide text-slate-400" :class="uiLanguage === lang.code ? 'text-emerald-300' : 'text-slate-400'">{{ lang.code }}</span>
                  <span class="font-medium">{{ t(lang.label) }}</span>
                  <span v-if="uiLanguage === lang.code" class="ml-auto text-emerald-300">•</span>
                </button>
              </div>
            </div>
            <button
              v-if="isLoggedIn"
              @click="logout"
              class="hidden rounded-xl border border-gray-200 bg-gray-50 px-4 py-2 text-right transition hover:border-emerald-300 hover:bg-emerald-50 dark:border-gray-700 dark:bg-gray-800 dark:hover:border-emerald-700 dark:hover:bg-emerald-900/20 md:block"
              :title="t(TEXT.signInNote3)"
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
      <div v-if="!isLoggedIn">
        <div class="mb-5 flex flex-col gap-3 rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">{{ t(TEXT.publicAreaLabel) }}</p>
            <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">{{ t(TEXT.publicAreaHint) }}</p>
          </div>
          <div class="flex rounded-xl bg-gray-100 p-1 dark:bg-gray-700/60">
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm font-semibold transition"
              :class="publicView === 'index' ? 'bg-white text-gray-900 shadow-sm dark:bg-gray-900/40 dark:text-white' : 'text-gray-700 hover:text-gray-900 dark:text-gray-200 dark:hover:text-white'"
              @click="publicView = 'index'"
            >
              {{ t(TEXT.homeTitle) }}
            </button>
            <button
              type="button"
              class="rounded-lg px-4 py-2 text-sm font-semibold transition"
              :class="publicView === 'login' ? 'bg-white text-gray-900 shadow-sm dark:bg-gray-900/40 dark:text-white' : 'text-gray-700 hover:text-gray-900 dark:text-gray-200 dark:hover:text-white'"
              @click="publicView = 'login'"
            >
              {{ t(TEXT.loginTitle) }}
            </button>
          </div>
        </div>

        <div v-if="publicView === 'index'" class="space-y-5">
          <section class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div class="max-w-3xl">
                <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">{{ t(TEXT.indexKicker) }}</p>
                <h2 class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{{ t(TEXT.indexHeadline) }}</h2>
                <p class="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">{{ t(TEXT.indexSubhead) }}</p>
              </div>
              <div class="flex flex-col gap-2 sm:flex-row">
                <button
                  type="button"
                  class="rounded-lg bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                  @click="publicView = 'login'"
                >
                  {{ t(TEXT.goToLogin) }}
                </button>
                <button
                  type="button"
                  class="rounded-lg border border-gray-200 bg-white px-5 py-3 text-sm font-semibold text-gray-800 transition hover:bg-gray-50 dark:border-gray-700 dark:bg-gray-900/30 dark:text-gray-100 dark:hover:bg-gray-900/50"
                  @click="fieldGuideOpen = !fieldGuideOpen"
                >
                  {{ fieldGuideOpen ? t(TEXT.hideDetails) : t(TEXT.showDetails) }}
                </button>
              </div>
            </div>
          </section>

          <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div
              v-for="card in indexSectionCards"
              :key="card.id"
              class="flex h-full flex-col rounded-xl border border-gray-200 bg-white p-5 shadow-sm dark:border-gray-700 dark:bg-gray-800"
            >
              <p class="text-xs font-semibold uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">{{ t(card.kicker) }}</p>
              <p class="mt-2 text-base font-semibold text-gray-900 dark:text-white">{{ t(card.title) }}</p>
              <p class="mt-1 flex-1 text-sm leading-6 text-gray-600 dark:text-gray-300">{{ t(card.body) }}</p>
              <button
                type="button"
                class="mt-4 mt-auto inline-flex w-full items-center justify-center rounded-lg bg-gray-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"
                @click="selectIndexSection(card.id)"
              >
                {{ t(TEXT.showThisSection) }}
              </button>
            </div>
          </section>

          <section class="rounded-xl border border-emerald-200 bg-emerald-50 p-6 dark:border-emerald-800 dark:bg-emerald-900/20">
            <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
              <div>
                <p class="text-sm font-semibold text-emerald-900 dark:text-emerald-100">{{ t(TEXT.fieldGuideTitle) }}</p>
                <p class="mt-1 text-xs leading-5 text-emerald-800 dark:text-emerald-200">{{ t(TEXT.fieldGuideSubtitle) }}</p>
              </div>
              <button
                type="button"
                class="inline-flex items-center justify-center rounded-lg bg-white px-3 py-2 text-xs font-semibold text-emerald-800 shadow-sm ring-1 ring-emerald-200 transition hover:bg-emerald-100 dark:bg-gray-900/40 dark:text-emerald-100 dark:ring-emerald-800 dark:hover:bg-emerald-900/30"
                @click="fieldGuideOpen = !fieldGuideOpen"
              >
                {{ fieldGuideOpen ? t(TEXT.hideDetails) : t(TEXT.showDetails) }}
              </button>
            </div>

            <div v-show="fieldGuideOpen" class="mt-4 space-y-3">
              <div class="flex flex-col gap-3 rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60 md:flex-row md:items-center md:justify-between">
                <div>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.filterTitle) }}</p>
                  <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">{{ t(TEXT.filterSubtitle) }}</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <button
                    type="button"
                    class="rounded-full px-3 py-2 text-xs font-semibold transition"
                    :class="indexSelectedSection === 'all'
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-900/30 dark:text-gray-200 dark:hover:bg-gray-900/50'"
                    @click="selectIndexSection('all')"
                  >
                    {{ t(TEXT.showAllSections) }}
                  </button>
                  <button
                    v-for="card in indexSectionCards"
                    :key="`filter-${card.id}`"
                    type="button"
                    class="rounded-full px-3 py-2 text-xs font-semibold transition"
                    :class="indexSelectedSection === card.id
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-900/30 dark:text-gray-200 dark:hover:bg-gray-900/50'"
                    @click="selectIndexSection(card.id)"
                  >
                    {{ t(card.title) }}
                  </button>
                </div>
              </div>
              <div
                v-for="group in visibleIndexFieldGroups"
                :key="group.id"
                class="rounded-2xl border border-emerald-100 bg-white p-5 dark:border-emerald-900/50 dark:bg-gray-800/60"
              >
                <div class="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(group.title) }}</p>
                    <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">{{ t(group.description) }}</p>
                  </div>
                </div>

                <div class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
                  <div
                    v-for="item in group.items"
                    :key="`${group.id}-${item.id}`"
                    class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/30"
                  >
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(item.title) }}</p>
                    <ul class="mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-200">
                      <li v-for="(line, idx) in t(item.lines)" :key="`${group.id}-${item.id}-${idx}`">
                        {{ line }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.aiUseTitle) }}</p>
                <div class="mt-2 grid gap-2 md:grid-cols-2">
                  <div
                    v-for="row in aiUseRows"
                    :key="`public-${row.id}`"
                    class="rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-700 dark:bg-gray-900/30 dark:text-gray-200"
                  >
                    <p class="font-semibold">{{ t(row.field) }}</p>
                    <p class="text-xs text-gray-600 dark:text-gray-300">{{ t(row.purpose) }}</p>
                  </div>
                </div>
              </div>

              <div class="rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.additionalDataTitle) }}</p>
                <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">{{ t(TEXT.additionalDataSubtitle) }}</p>
                <ul class="mt-3 grid gap-2 text-sm text-gray-700 dark:text-gray-200 sm:grid-cols-2">
                  <li v-for="(line, idx) in t(TEXT.additionalDataList)" :key="`public-add-${idx}`" class="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-900/30">
                    {{ line }}
                  </li>
                </ul>
              </div>
            </div>
          </section>
        </div>

      <div v-else class="grid grid-cols-1 items-stretch gap-5 xl:min-h-[calc(100vh-11rem)] xl:grid-cols-2">
        <section class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg h-full flex flex-col">
          <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">{{ t(TEXT.loginTitle) }}</p>
          <h2 class="mt-2 text-2xl font-bold text-gray-900 dark:text-white lg:text-[1.9rem]">{{ t(TEXT.loginHeroHeadline) }}</h2>
          <p class="mt-2 max-w-3xl text-sm leading-6 text-gray-600 dark:text-gray-300">
            {{ t(TEXT.loginHeroSubtitle) }}
          </p>
          <div class="mt-4 rounded-2xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-900/40">
            <div class="flex items-center justify-between">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t(TEXT.systemWorkflowTitle) }}</h3>
              <p class="text-xs uppercase tracking-[0.2em] text-gray-500 dark:text-gray-400">{{ t(TEXT.systemWorkflowHint) }}</p>
            </div>
            <div class="mt-3 rounded-xl border border-gray-200 bg-slate-50 p-4 dark:border-gray-700 dark:bg-gray-800/80">
              <div class="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
                <div class="rounded-2xl border border-slate-200 bg-white p-4 text-center shadow-sm dark:border-slate-700 dark:bg-gray-900/40">
                  <div class="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900">
                    <span class="text-3xl">TB</span>
                  </div>
                  <p class="mt-4 text-lg font-bold text-slate-900 dark:text-white">{{ t(TEXT.workflowSystemTitle) }}</p>
                  <div class="mt-2 space-y-1 text-sm text-slate-500 dark:text-slate-400">
                    <p>{{ t(TEXT.workflowLogin) }}</p>
                    <p>{{ t(TEXT.workflowEvaluate) }}</p>
                    <p>{{ t(TEXT.workflowGuideCare) }}</p>
                  </div>
                </div>
                <div class="space-y-4">
                  <div class="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                    <div
                      v-for="step in loginWorkflowSteps"
                      :key="step.id"
                      class="rounded-2xl border bg-white p-4 shadow-sm dark:bg-gray-900/30"
                      :class="step.accent"
                    >
                      <p class="text-[11px] font-semibold uppercase tracking-[0.2em]" :class="step.kickerClass">{{ t(step.stepLabel) }}</p>
                      <p class="mt-2 text-base font-semibold text-gray-900 dark:text-white break-words">{{ t(step.title) }}</p>
                    </div>
                  </div>
                  <div class="grid gap-3 lg:grid-cols-3">
                    <div
                      v-for="card in loginWorkflowSummaryCards"
                      :key="card.id"
                      class="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-700 dark:bg-gray-900/30"
                    >
                      <p class="text-sm font-semibold text-slate-900 dark:text-white break-words">{{ t(card.title) }}</p>
                      <div class="mt-2 space-y-1 text-sm text-slate-500 dark:text-slate-400">
                        <p v-for="line in card.lines" :key="line">{{ t(line) }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="mt-3 grid gap-2 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-[11px] uppercase tracking-[0.2em] text-slate-500 dark:border-slate-700 dark:bg-slate-900/40 dark:text-slate-400 sm:grid-cols-3">
              <span>{{ t(TEXT.newPatient) }}</span>
              <span>{{ t(TEXT.existingPatient) }}</span>
              <span>{{ t(TEXT.clinicalReport) }}</span>
            </div>
          </div>
          <div class="mt-4 grid flex-1 content-start gap-3 lg:grid-cols-2">
            <div class="rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/30">
              <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ t(TEXT.whatYouCanDo) }}</h3>
              <ul class="mt-2 space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <li>{{ t(TEXT.whatNew) }}</li>
                <li>{{ t(TEXT.whatExisting) }}</li>
                <li>{{ t(TEXT.whatReport) }}</li>
              </ul>
            </div>
            <div class="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
              <h3 class="text-base font-semibold text-blue-900 dark:text-blue-100">{{ t(TEXT.afterSignIn) }}</h3>
              <ul class="mt-2 space-y-2 text-sm text-blue-800 dark:text-blue-200">
                <li>{{ t(TEXT.afterDiagnose) }}</li>
                <li>{{ t(TEXT.afterPatients) }}</li>
                <li>{{ t(TEXT.afterAlerts) }}</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="bg-white dark:bg-gray-800 rounded-xl p-5 shadow-lg h-full flex flex-col">
          <div class="rounded-2xl border border-emerald-200 bg-white p-4 dark:border-emerald-800 dark:bg-gray-900/30">
            <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">{{ t(TEXT.protectedWorkspace) }}</p>
            <h2 class="mt-2 text-2xl font-bold text-gray-900 dark:text-white lg:text-[1.8rem]">{{ t(TEXT.welcomeBack) }}</h2>
            <p class="mt-2 text-sm leading-6 text-gray-600 dark:text-gray-300">
              {{ t(TEXT.continueToTabs) }}
            </p>
            <div class="mt-3 grid gap-2 sm:grid-cols-3">
              <div class="rounded-xl border border-emerald-100 bg-slate-50 px-3 py-2.5 dark:border-emerald-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">{{ t(TEXT.tabDiagnose) }}</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">{{ t(TEXT.reviewCases) }}</p>
              </div>
              <div class="rounded-xl border border-blue-100 bg-slate-50 px-3 py-2.5 dark:border-blue-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">{{ t(TEXT.tabPatients) }}</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">{{ t(TEXT.openRecords) }}</p>
              </div>
              <div class="rounded-xl border border-violet-100 bg-slate-50 px-3 py-2.5 dark:border-violet-900/40 dark:bg-gray-900/40">
                <p class="text-xs font-semibold uppercase tracking-[0.18em] text-violet-700 dark:text-violet-300">{{ t(TEXT.tabAlerts) }}</p>
                <p class="mt-1 text-xs font-medium text-gray-900 dark:text-white">{{ t(TEXT.seeNotices) }}</p>
              </div>
            </div>
          </div>
          <form @submit.prevent="login" class="space-y-3 flex-1 flex flex-col">
            <div>
              <label class="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.emailLabel) }}</label>
              <input
                v-model="loginEmail"
                type="email"
                class="w-full rounded-lg border border-gray-300 px-4 py-2.5 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                :placeholder="t(TEXT.emailPlaceholder)"
                required
              />
            </div>
            <div>
              <label class="block mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.passwordLabel) }}</label>
              <div class="relative">
                <input
                  v-model="loginPassword"
                  :type="showLoginPassword ? 'text' : 'password'"
                  class="w-full rounded-lg border border-gray-300 px-4 py-2.5 pr-12 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  :placeholder="t(TEXT.passwordPlaceholder)"
                  required
                />
                <button
                  type="button"
                  class="absolute inset-y-0 right-0 flex items-center px-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                  @click="showLoginPassword = !showLoginPassword"
                  :title="showLoginPassword ? t(TEXT.hidePasswordTitle) : t(TEXT.showPasswordTitle)"
                >
                  {{ showLoginPassword ? '🙈' : '👁️' }}
                </button>
              </div>
            </div>
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-800 dark:bg-emerald-900/20 dark:text-emerald-200">
              <p class="text-sm font-semibold">{{ t(TEXT.signInNotesTitle) }}</p>
              <ul class="mt-2 space-y-1 text-xs leading-5">
                <li>{{ t(TEXT.signInNote1) }}</li>
                <li>{{ t(TEXT.signInNote2) }}</li>
                <li>{{ t(TEXT.signInNote3) }}</li>
              </ul>
            </div>
            <div class="grid gap-2 sm:grid-cols-2">
              <div class="rounded-xl border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
                <p class="text-sm font-semibold text-blue-900 dark:text-blue-100">{{ t(TEXT.tabDiagnose) }}</p>
                <p class="mt-1 text-xs leading-5 text-blue-800 dark:text-blue-200">{{ t(TEXT.enterContinueEvidence) }}</p>
              </div>
              <div class="rounded-xl border border-indigo-200 bg-indigo-50 p-3 dark:border-indigo-800 dark:bg-indigo-900/20">
                <p class="text-sm font-semibold text-indigo-900 dark:text-indigo-100">{{ t(TEXT.tabPatients) }}</p>
                <p class="mt-1 text-xs leading-5 text-indigo-800 dark:text-indigo-200">{{ t(TEXT.openSavedRecords) }}</p>
              </div>
              <div class="rounded-xl border border-amber-200 bg-amber-50 p-3 dark:border-amber-800 dark:bg-amber-900/20">
                <p class="text-sm font-semibold text-amber-900 dark:text-amber-100">{{ t(TEXT.tabAlerts) }}</p>
                <p class="mt-1 text-xs leading-5 text-amber-800 dark:text-amber-200">{{ t(TEXT.reviewNotices) }}</p>
              </div>
              <div class="rounded-xl border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-900/30">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.protected) }}</p>
                <p class="mt-1 text-xs leading-5 text-gray-700 dark:text-gray-300">{{ t(TEXT.clinicianAdminOnly) }}</p>
              </div>
            </div>
            <p v-if="loginError" class="text-sm font-medium text-red-600 dark:text-red-400">{{ loginError }}</p>
            <div class="mt-auto pt-1">
              <button
                type="submit"
                :disabled="loading"
                class="w-full rounded-lg bg-emerald-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
              >
                {{ loading ? t(TEXT.signingIn) : t(TEXT.signIn) }}
              </button>
            </div>
          </form>
        </section>
      </div>
      </div>

      <!-- Diagnose View -->
      <div v-else-if="currentView === 'diagnose'">
        <div class="space-y-5">
          <div class="rounded-xl border border-gray-200 bg-white p-4 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">{{ t(TEXT.guidedFlowTitle) }}</p>
                <h2 class="mt-1 text-lg font-semibold text-gray-900 dark:text-white">{{ t(TEXT.guidedFlowHeadline) }}</h2>
                <p class="mt-1 text-sm text-gray-600 dark:text-gray-300">
                  {{ t(TEXT.guidedFlowBody) }}
                </p>
              </div>
              <div class="grid gap-2 sm:grid-cols-3 lg:min-w-[420px]">
                <div class="rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2 dark:border-emerald-800 dark:bg-emerald-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700 dark:text-emerald-300">{{ t(TEXT.flowEntryTitle) }}</p>
                  <p class="mt-1 text-xs leading-5 text-emerald-800 dark:text-emerald-200">{{ t(TEXT.flowEntryBody) }}</p>
                </div>
                <div class="rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 dark:border-blue-800 dark:bg-blue-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-blue-700 dark:text-blue-300">{{ t(TEXT.flowOrderTitle) }}</p>
                  <p class="mt-1 text-xs leading-5 text-blue-800 dark:text-blue-200">{{ t(TEXT.flowOrderBody) }}</p>
                </div>
                <div class="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 dark:border-amber-800 dark:bg-amber-900/20">
                  <p class="text-xs font-semibold uppercase tracking-[0.18em] text-amber-700 dark:text-amber-300">{{ t(TEXT.flowOutputTitle) }}</p>
                  <p class="mt-1 text-xs leading-5 text-amber-800 dark:text-amber-200">{{ t(TEXT.flowOutputBody) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 gap-6 2xl:grid-cols-[minmax(860px,1.45fr)_minmax(560px,0.95fr)] items-start">
          <!-- Patient Form -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg min-w-0">
            <div class="mb-4 flex flex-col gap-2 md:flex-row md:items-end md:justify-between">
              <div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t(TEXT.patientInfoTitle) }}</h2>
                <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.patientInfoSubtitle) }}</p>
              </div>
              <div class="rounded-lg bg-gray-50 px-3 py-2 text-xs text-gray-600 dark:bg-gray-700/60 dark:text-gray-300">
                {{ t(TEXT.suggestedItemsHint) }}
              </div>
            </div>
            <div class="mb-6 rounded-xl border border-gray-200 bg-gray-50 p-4 dark:border-gray-700 dark:bg-gray-900/30">
              <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 dark:text-emerald-300">{{ tf(TEXT.stepOf, { current: currentDiagnosisStep, total: diagnosisSteps.length }) }}</p>
                  <h3 class="mt-1 text-base font-semibold text-gray-900 dark:text-white">{{ currentDiagnosisMeta.title }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ currentDiagnosisMeta.description }}</p>
                </div>
                <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
                  {{ tf(TEXT.percentComplete, { percent: Math.round((currentDiagnosisStep / diagnosisSteps.length) * 100) }) }}
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
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ t(TEXT.step1Title) }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.step1Intro) }}</p>
                </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.firstNameLabel) }}</label>
                  <input
                    v-model="patient.first_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    :placeholder="t(TEXT.firstNamePlaceholder)"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.lastNameLabel) }}</label>
                  <input
                    v-model="patient.last_name"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    :placeholder="t(TEXT.lastNamePlaceholder)"
                  />
                </div>
              </div>
              <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.patientIdLabel) }}</label>
                  <input
                    v-model="patient.patient_id"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    :placeholder="t(TEXT.uniqueIdPlaceholder)"
                  />
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.ageLabel) }}</label>
                  <input
                    v-model.number="patient.age"
                    type="number"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    :placeholder="t(TEXT.agePlaceholder)"
                  />
                </div>
              </div>
              <div class="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.genderLabel) }}</label>
                  <select
                    v-model="patient.gender"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option>{{ t(TEXT.genderMale) }}</option>
                    <option>{{ t(TEXT.genderFemale) }}</option>
                    <option>{{ t(TEXT.genderOther) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.cityLabel) }}</label>
                  <input
                    v-model="patient.city"
                    type="text"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    :placeholder="t(TEXT.cityPlaceholder)"
                  />
                </div>
              </div>
              </section>

              <section v-show="currentDiagnosisStep === 2" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ t(TEXT.step2Title) }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.clinicalCluesIntro) }}</p>
                </div>
                <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.symptomsLabel) }}</label>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ t(TEXT.symptomsHint) }}</p>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ t(TEXT.miniStep1) }}</span>
                  </div>
                  <textarea
                    v-model="patient.symptoms"
                    class="mt-3 w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    rows="3"
                    :placeholder="t(TEXT.symptomsPlaceholder)"
                  ></textarea>
                  <div class="mt-3">
                    <button
                      v-if="!openCustomCommaInputs.symptoms"
                      type="button"
                      class="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50 dark:border-emerald-700 dark:bg-gray-800 dark:text-emerald-300 dark:hover:bg-gray-700"
                      @click="openCustomListInput('symptoms')"
                    >
                      <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
                        <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                      </svg>
                      {{ t(TEXT.addSymptom) }}
                    </button>
                    <div v-else class="flex flex-col gap-2 sm:flex-row">
                      <input
                        v-model="customCommaInputs.symptoms"
                        type="text"
                        class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                        :placeholder="t(TEXT.addOneSymptom)"
                        @keydown.enter.prevent="addCustomListValue('symptoms')"
                      />
                      <button
                        type="button"
                        class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
                        @click="addCustomListValue('symptoms')"
                      >
                        {{ t(TEXT.add) }}
                      </button>
                      <button
                        type="button"
                        class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                        @click="closeCustomListInput('symptoms')"
                      >
                        {{ t(TEXT.cancel) }}
                      </button>
                    </div>
                  </div>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="option in symptomOptions"
                      :key="option.value"
                      type="button"
                      class="rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs text-emerald-700 hover:bg-emerald-100 dark:border-emerald-700 dark:bg-gray-800 dark:text-emerald-300"
                      @click="appendSuggestedValue('symptoms', option.value)"
                    >
                      + {{ t(option.label) }}
                    </button>
                  </div>
                </div>

                <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                  <div class="flex items-center justify-between gap-3">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.exposureHistoryLabel) }}</label>
                      <p class="text-xs text-gray-500 dark:text-gray-400">{{ t(TEXT.exposureHint) }}</p>
                    </div>
                    <span class="text-xs text-gray-500 dark:text-gray-400">{{ t(TEXT.miniStep2) }}</span>
                  </div>
                  <textarea
                    v-model="patient.exposure_history"
                    class="mt-3 w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                    rows="3"
                    :placeholder="t(TEXT.exposurePlaceholder)"
                  ></textarea>
                  <div class="mt-3">
                    <button
                      v-if="!openCustomCommaInputs.exposure_history"
                      type="button"
                      class="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-white px-3 py-2 text-xs font-semibold text-blue-700 transition hover:bg-blue-50 dark:border-blue-700 dark:bg-gray-800 dark:text-blue-300 dark:hover:bg-gray-700"
                      @click="openCustomListInput('exposure_history')"
                    >
                      <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
                        <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                      </svg>
                      {{ t(TEXT.addExposure) }}
                    </button>
                    <div v-else class="flex flex-col gap-2 sm:flex-row">
                      <input
                        v-model="customCommaInputs.exposure_history"
                        type="text"
                        class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                        :placeholder="t(TEXT.addOneExposure)"
                        @keydown.enter.prevent="addCustomListValue('exposure_history')"
                      />
                      <button
                        type="button"
                        class="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                        @click="addCustomListValue('exposure_history')"
                      >
                        {{ t(TEXT.add) }}
                      </button>
                      <button
                        type="button"
                        class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                        @click="closeCustomListInput('exposure_history')"
                      >
                        {{ t(TEXT.cancel) }}
                      </button>
                    </div>
                  </div>
                  <div class="mt-3 flex flex-wrap gap-2">
                    <button
                      v-for="option in exposureOptions"
                      :key="option.value"
                      type="button"
                      class="rounded-full border border-blue-200 bg-white px-3 py-1 text-xs text-blue-700 hover:bg-blue-100 dark:border-blue-700 dark:bg-gray-800 dark:text-blue-300"
                      @click="appendSuggestedValue('exposure_history', option.value)"
                    >
                      + {{ t(option.label) }}
                    </button>
                  </div>
                </div>
              </section>

              <section v-show="currentDiagnosisStep === 3" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ t(TEXT.step3Title) }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.testsIntro) }}</p>
                </div>
              <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-900/20">
                <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p class="text-sm font-semibold text-emerald-900 dark:text-emerald-100">{{ t(TEXT.fieldGuideTitle) }}</p>
                    <p class="mt-1 text-xs leading-5 text-emerald-800 dark:text-emerald-200">{{ t(TEXT.fieldGuideSubtitle) }}</p>
                  </div>
                  <button
                    type="button"
                    class="inline-flex items-center justify-center rounded-lg bg-white px-3 py-2 text-xs font-semibold text-emerald-800 shadow-sm ring-1 ring-emerald-200 transition hover:bg-emerald-100 dark:bg-gray-900/40 dark:text-emerald-100 dark:ring-emerald-800 dark:hover:bg-emerald-900/30"
                    @click="fieldGuideOpen = !fieldGuideOpen"
                  >
                    {{ fieldGuideOpen ? t(TEXT.hideDetails) : t(TEXT.showDetails) }}
                  </button>
                </div>

                <div v-show="fieldGuideOpen" class="mt-4 space-y-3">
                  <div
                    v-for="item in fieldGuideItems"
                    :key="item.id"
                    class="rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60"
                  >
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(item.title) }}</p>
                    <ul class="mt-2 space-y-1 text-sm text-gray-700 dark:text-gray-200">
                      <li v-for="(line, idx) in t(item.lines)" :key="`${item.id}-${idx}`">
                        {{ line }}
                      </li>
                    </ul>
                  </div>

                  <div class="rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.aiUseTitle) }}</p>
                    <div class="mt-2 grid gap-2 md:grid-cols-2">
                      <div
                        v-for="row in aiUseRows"
                        :key="row.id"
                        class="rounded-lg bg-gray-50 px-3 py-2 text-sm text-gray-700 dark:bg-gray-900/30 dark:text-gray-200"
                      >
                        <p class="font-semibold">{{ t(row.field) }}</p>
                        <p class="text-xs text-gray-600 dark:text-gray-300">{{ t(row.purpose) }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="rounded-xl border border-emerald-100 bg-white p-4 dark:border-emerald-900/50 dark:bg-gray-800/60">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ t(TEXT.additionalDataTitle) }}</p>
                    <p class="mt-1 text-xs leading-5 text-gray-600 dark:text-gray-300">{{ t(TEXT.additionalDataSubtitle) }}</p>
                    <ul class="mt-3 grid gap-2 text-sm text-gray-700 dark:text-gray-200 sm:grid-cols-2">
                      <li v-for="(line, idx) in t(TEXT.additionalDataList)" :key="`add-${idx}`" class="rounded-lg bg-gray-50 px-3 py-2 dark:bg-gray-900/30">
                        {{ line }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('bacteria_species') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('bacteria_species') }}</p>
                  <select
                    v-model="patient.bacteria_species"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Auto-detect">{{ t(TEXT.autoDetectLabel) }}</option>
                    <option value="Mycobacterium tuberculosis">{{ t(TEXT.speciesTuberculosis) }}</option>
                    <option value="Mycobacterium bovis">{{ t(TEXT.speciesBovis) }}</option>
                    <option value="Mycobacterium africanum">{{ t(TEXT.speciesAfricanum) }}</option>
                    <option value="Mycobacterium canettii">{{ t(TEXT.speciesCanettii) }}</option>
                    <option value="Mycobacterium microti">{{ t(TEXT.speciesMicroti) }}</option>
                    <option value="Mycobacterium caprae">{{ t(TEXT.speciesCaprae) }}</option>
                    <option value="Mycobacterium pinnipedii">{{ t(TEXT.speciesPinnipedii) }}</option>
                    <option value="Mycobacterium orygis">{{ t(TEXT.speciesOrygis) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('tb_culture') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('tb_culture') }}</p>
                  <select
                    v-model="patient.tb_culture"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Positive">{{ t(TEXT.statusPositive) }}</option>
                    <option value="Negative">{{ t(TEXT.statusNegative) }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('sputum_smear_test') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('sputum_smear_test') }}</p>
                  <select
                    v-model="patient.sputum_smear_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Positive">{{ t(TEXT.statusPositive) }}</option>
                    <option value="Negative">{{ t(TEXT.statusNegative) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('genexpert_test') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('genexpert_test') }}</p>
                  <select
                    v-model="patient.genexpert_test"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Positive">{{ t(TEXT.statusPositive) }}</option>
                    <option value="Negative">{{ t(TEXT.statusNegative) }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('chest_xray') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('chest_xray') }}</p>
                  <select
                    v-model="patient.chest_xray"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Normal">{{ t(TEXT.statusNormal) }}</option>
                    <option value="Abnormal">{{ t(TEXT.statusAbnormal) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('drug_resistance') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('drug_resistance') }}</p>
                  <select
                    v-model="patient.drug_resistance"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="No">{{ t(TEXT.statusNo) }}</option>
                    <option value="Yes">{{ t(TEXT.statusYes) }}</option>
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('tst') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('tst') }}</p>
                  <select
                    v-model="patient.tst"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Positive">{{ t(TEXT.statusPositive) }}</option>
                    <option value="Negative">{{ t(TEXT.statusNegative) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('igra') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('igra') }}</p>
                  <select
                    v-model="patient.igra"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                    <option value="Positive">{{ t(TEXT.statusPositive) }}</option>
                    <option value="Negative">{{ t(TEXT.statusNegative) }}</option>
                  </select>
                </div>
              </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('hiv') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('hiv') }}</p>
                  <select
                    v-model="patient.hiv"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="No">{{ t(TEXT.statusNo) }}</option>
                    <option value="Yes">{{ t(TEXT.statusYes) }}</option>
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                  </select>
                </div>
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ fieldLabel('diabetes') }}</label>
                  <p class="mb-2 text-xs leading-5 text-gray-500 dark:text-gray-400">{{ fieldHelp('diabetes') }}</p>
                  <select
                    v-model="patient.diabetes"
                    class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  >
                    <option value="No">{{ t(TEXT.statusNo) }}</option>
                    <option value="Yes">{{ t(TEXT.statusYes) }}</option>
                    <option value="Unknown">{{ t(TEXT.statusUnknown) }}</option>
                  </select>
                </div>
              </div>
              </section>

              <section v-show="currentDiagnosisStep === 4" class="rounded-xl border border-gray-200 p-4 dark:border-gray-700 space-y-4">
                <div>
                  <h3 class="font-semibold text-gray-900 dark:text-white">{{ t(TEXT.step4Title) }}</h3>
                  <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.dstIntro) }}</p>
                </div>
              <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.antibiogramSummaryLabel) }}</label>
                  <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                    <textarea
                      v-model="patient.antibiogram_result"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      rows="3"
                      :placeholder="t(TEXT.dstSummaryPlaceholder)"
                    ></textarea>
                    <div class="mt-3">
                      <button
                        v-if="!openCustomCommaInputs.antibiogram_result"
                        type="button"
                        class="inline-flex items-center gap-2 rounded-full border border-rose-200 bg-white px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-50 dark:border-rose-700 dark:bg-gray-800 dark:text-rose-300 dark:hover:bg-gray-700"
                        @click="openCustomListInput('antibiogram_result')"
                      >
                        <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
                          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                        {{ t(TEXT.addDstItem) }}
                      </button>
                      <div v-else class="flex flex-col gap-2 sm:flex-row">
                        <input
                          v-model="customCommaInputs.antibiogram_result"
                          type="text"
                          class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                          :placeholder="t(TEXT.addOneDstItem)"
                          @keydown.enter.prevent="addCustomListValue('antibiogram_result')"
                        />
                        <button
                          type="button"
                          class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-700"
                          @click="addCustomListValue('antibiogram_result')"
                        >
                          {{ t(TEXT.add) }}
                        </button>
                        <button
                          type="button"
                          class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                          @click="closeCustomListInput('antibiogram_result')"
                        >
                          {{ t(TEXT.cancel) }}
                        </button>
                      </div>
                    </div>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button
                        v-for="option in antibiogramOptions"
                        :key="option.value"
                        type="button"
                        class="rounded-full border border-rose-200 bg-white px-3 py-1 text-xs text-rose-700 hover:bg-rose-100 dark:border-rose-700 dark:bg-gray-800 dark:text-rose-300"
                        @click="appendSuggestedValue('antibiogram_result', option.value)"
                      >
                        + {{ t(option.label) }}
                      </button>
                    </div>
                  </div>
                </div>
                <div class="space-y-4">
                  <div class="rounded-xl bg-gray-50 p-4 dark:bg-gray-900/30">
                    <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.resistantToLabel) }}</label>
                    <input
                      v-model="patient.resistant_to"
                      list="tb-drug-options"
                      type="text"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      :placeholder="t(TEXT.resistantToPlaceholder)"
                    />
                    <div class="mt-3">
                      <button
                        v-if="!openCustomCommaInputs.resistant_to"
                        type="button"
                        class="inline-flex items-center gap-2 rounded-full border border-rose-200 bg-white px-3 py-2 text-xs font-semibold text-rose-700 transition hover:bg-rose-50 dark:border-rose-700 dark:bg-gray-800 dark:text-rose-300 dark:hover:bg-gray-700"
                        @click="openCustomListInput('resistant_to')"
                      >
                        <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
                          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                        {{ t(TEXT.addResistantMedicine) }}
                      </button>
                      <div v-else class="flex flex-col gap-2 sm:flex-row">
                        <input
                          v-model="customCommaInputs.resistant_to"
                          list="tb-drug-options"
                          type="text"
                          class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                          :placeholder="t(TEXT.addOneResistantMedicine)"
                          @keydown.enter.prevent="addCustomListValue('resistant_to')"
                        />
                        <button
                          type="button"
                          class="rounded-lg bg-rose-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-rose-700"
                          @click="addCustomListValue('resistant_to')"
                        >
                          {{ t(TEXT.add) }}
                        </button>
                        <button
                          type="button"
                          class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                          @click="closeCustomListInput('resistant_to')"
                        >
                          {{ t(TEXT.cancel) }}
                        </button>
                      </div>
                    </div>
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
                    <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.susceptibleToLabel) }}</label>
                    <input
                      v-model="patient.susceptible_to"
                      list="tb-drug-options"
                      type="text"
                      class="w-full rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                      :placeholder="t(TEXT.susceptibleToPlaceholder)"
                    />
                    <div class="mt-3">
                      <button
                        v-if="!openCustomCommaInputs.susceptible_to"
                        type="button"
                        class="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-2 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-50 dark:border-emerald-700 dark:bg-gray-800 dark:text-emerald-300 dark:hover:bg-gray-700"
                        @click="openCustomListInput('susceptible_to')"
                      >
                        <svg viewBox="0 0 16 16" class="h-4 w-4" fill="none" aria-hidden="true">
                          <path d="M8 3v10M3 8h10" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
                        </svg>
                        {{ t(TEXT.addSusceptibleMedicine) }}
                      </button>
                      <div v-else class="flex flex-col gap-2 sm:flex-row">
                        <input
                          v-model="customCommaInputs.susceptible_to"
                          list="tb-drug-options"
                          type="text"
                          class="flex-1 rounded-lg border border-gray-300 px-4 py-2 text-sm dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                          :placeholder="t(TEXT.addOneSusceptibleMedicine)"
                          @keydown.enter.prevent="addCustomListValue('susceptible_to')"
                        />
                        <button
                          type="button"
                          class="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
                          @click="addCustomListValue('susceptible_to')"
                        >
                          {{ t(TEXT.add) }}
                        </button>
                        <button
                          type="button"
                          class="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                          @click="closeCustomListInput('susceptible_to')"
                        >
                          {{ t(TEXT.cancel) }}
                        </button>
                      </div>
                    </div>
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
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ t(TEXT.stepHint) }}</p>
                </div>
                <div class="flex flex-wrap gap-3">
                  <button
                    v-if="currentDiagnosisStep > 1"
                    type="button"
                    @click="previousDiagnosisStep"
                    class="rounded-lg border border-gray-300 px-5 py-2.5 text-sm font-medium text-gray-700 transition hover:bg-gray-100 dark:border-gray-600 dark:text-gray-200 dark:hover:bg-gray-700"
                  >
                    {{ t(TEXT.previousStep) }}
                  </button>
                  <button
                    v-if="currentDiagnosisStep < diagnosisSteps.length"
                    type="button"
                    @click="nextDiagnosisStep"
                    class="rounded-lg bg-slate-900 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
                  >
                    {{ t(TEXT.nextStep) }}
                  </button>
                  <button
                    v-else
                    type="submit"
                    :disabled="loading"
                    class="rounded-lg bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:opacity-50"
                  >
                    {{ loading ? t(TEXT.analyzing) : t(TEXT.analyzeDiagnose) }}
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
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t(TEXT.diagnosticReport) }}</h2>
            
            <!-- Patient Info -->
            <div class="p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <p class="font-medium text-gray-900 dark:text-white">{{ diagnosisResult.patient_name }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ t(TEXT.idLabel) }}: {{ diagnosisResult.patient_id }}</p>
            </div>

            <!-- Symptom Analysis -->
            <div class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.symptomAnalysis) }}</h3>
              <div class="p-4 rounded-lg border" :class="riskColorClass">
                <div class="flex items-center justify-between mb-2">
                  <span class="font-semibold text-lg">{{ diagnosisResult.symptom_analysis.risk_level_display || diagnosisResult.symptom_analysis.risk_level }}</span>
                  <span class="text-sm px-2 py-1 bg-white/50 dark:bg-gray-800/50 rounded">
                    {{ t(TEXT.scoreLabel) }}: {{ diagnosisResult.symptom_analysis.risk_score }}
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
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.testEvaluation) }}</h3>
              <div class="p-4 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-200 dark:border-blue-800">
                <p class="text-lg font-medium text-blue-800 dark:text-blue-300">
                  {{ translateBackendText(diagnosisResult.test_evaluation.classification) }}
                </p>
                <p class="text-sm text-blue-700 dark:text-blue-400 mt-1">
                  {{ t(TEXT.confidenceLabel) }}: {{ diagnosisResult.test_evaluation.confidence_percent }}%
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
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.tbBacteriaAssessment) }}</h3>
              <div class="p-4 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-200 dark:border-amber-800">
                <p class="text-lg font-medium text-amber-800 dark:text-amber-300">
                  {{ translateBackendText(diagnosisResult.bacteria_assessment.species) }}
                </p>
                <p class="mt-1 text-sm text-amber-700 dark:text-amber-400">
                  {{ t(TEXT.methodLabel) }}: {{ translateBackendText(diagnosisResult.bacteria_assessment.mode) }} | {{ t(TEXT.supportedSpeciesLabel) }}: {{ diagnosisResult.bacteria_assessment.supported_species_count }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  {{ translateBackendText(diagnosisResult.bacteria_assessment.description) }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.reasonLabel) }}:</strong> {{ translateBackendText(diagnosisResult.bacteria_assessment.reason) }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.typicalSourceLabel) }}:</strong> {{ translateBackendText(diagnosisResult.bacteria_assessment.typical_source) }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.labNoteLabel) }}:</strong> {{ translateBackendText(diagnosisResult.bacteria_assessment.lab_note) }}
                </p>
              </div>
            </div>

            <!-- Infection Assessment -->
            <div v-if="diagnosisResult.infection_assessment" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.infectionAssessment) }}</h3>
              <div class="p-4 bg-sky-50 dark:bg-sky-900/30 rounded-lg border border-sky-200 dark:border-sky-800">
                <p class="text-lg font-medium text-sky-800 dark:text-sky-300">
                  {{ translateBackendText(diagnosisResult.infection_assessment.primary_infection) }}
                </p>
                <ul class="mt-3 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li
                    v-for="(infection, i) in diagnosisResult.infection_assessment.infection_types"
                    :key="i"
                  >
                    {{ translateBackendText(infection.label) }} - {{ translateBackendText(infection.site) }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- Resistance Profile -->
            <div v-if="diagnosisResult.resistance_profile" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.resistanceDstProfile) }}</h3>
              <div class="p-4 bg-rose-50 dark:bg-rose-900/30 rounded-lg border border-rose-200 dark:border-rose-800">
                <p class="text-lg font-medium text-rose-800 dark:text-rose-300">
                  {{ translateBackendText(diagnosisResult.resistance_profile.classification) }}
                </p>
                <p class="mt-1 text-sm text-rose-700 dark:text-rose-400">
                  {{ t(TEXT.regimenLevelLabel) }}: {{ translateBackendText(diagnosisResult.resistance_profile.regimen_level) }}
                </p>
                <p class="mt-2 text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.antibiogramLabel) }}:</strong> {{ translateBackendText(diagnosisResult.resistance_profile.antibiogram_result) }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.resistantToLabel) }}:</strong> {{ diagnosisResult.resistance_profile.resistant_to.join(', ') || t(TEXT.noneProvided) }}
                </p>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                  <strong>{{ t(TEXT.susceptibleToLabel) }}:</strong> {{ diagnosisResult.resistance_profile.susceptible_to.join(', ') || t(TEXT.noneProvided) }}
                </p>
                <ul class="mt-3 text-sm text-gray-700 dark:text-gray-300 space-y-1">
                  <li v-for="(item, i) in diagnosisResult.resistance_profile.decision_basis" :key="i">
                    {{ translateBackendText(item) }}
                  </li>
                </ul>
              </div>
            </div>

            <!-- ML Prediction -->
            <div v-if="diagnosisResult.ml_prediction" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.mlPrediction) }}</h3>
              <div class="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg border border-purple-200 dark:border-purple-800">
                <p class="font-medium text-purple-800 dark:text-purple-300">
                  {{ t(TEXT.tbPredictionLabel) }}: {{ formatPredictionLabel(diagnosisResult.ml_prediction.tb_status?.prediction, 'tb') }}
                </p>
                <p v-if="diagnosisResult.ml_prediction.tb_status" class="mt-1 text-sm text-purple-700 dark:text-purple-400">
                    {{ buildConfidenceSummary(diagnosisResult.ml_prediction.tb_status, 'tb') }}
                </p>
                <div class="mt-2 text-sm space-y-1">
                  <p v-if="diagnosisResult.ml_prediction.drug_resistance" class="text-purple-700 dark:text-purple-400">
                    {{ t(TEXT.drugResistancePredictionLabel) }}: {{ formatPredictionLabel(diagnosisResult.ml_prediction.drug_resistance.prediction, 'resistance') }}
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
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">{{ t(TEXT.treatmentRecommendation) }}</h3>
              <div class="p-4 bg-emerald-50 dark:bg-emerald-900/30 rounded-lg border border-emerald-200 dark:border-emerald-800">
                <div class="flex items-center justify-between mb-2">
                  <p class="font-semibold text-emerald-800 dark:text-emerald-300">
                    {{ translateBackendText(diagnosisResult.treatment_recommendation.regimen_name || diagnosisResult.treatment_recommendation.type || diagnosisResult.treatment_recommendation.category || t(TEXT.treatmentPlanFallback)) }}
                  </p>
                  <span class="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded font-medium">
                    {{ translateBackendText(diagnosisResult.treatment_recommendation.urgency) }}
                  </span>
                </div>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.categoryLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.category) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.bacteriaLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.bacteria_species || diagnosisResult.bacteria_assessment?.species || t(TEXT.notAvailableInResponse)) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.infectionLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.infection_type || diagnosisResult.infection_assessment?.primary_infection || diagnosisResult.treatment_recommendation.category || t(TEXT.notAvailableInResponse)) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.resistanceLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.resistance_class || diagnosisResult.resistance_profile?.classification || diagnosisResult.ml_prediction?.drug_resistance?.prediction || t(TEXT.notAvailableInResponse)) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.levelLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.regimen_level || diagnosisResult.resistance_profile?.regimen_level || t(TEXT.whoRuleBasedLevel)) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.durationLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.duration) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.drugsLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.drugs) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.dosageLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.dosage) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.administrationLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.administration) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.monitoringLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.monitoring) }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>{{ t(TEXT.guidelineLabel) }}:</strong> {{ translateBackendText(diagnosisResult.treatment_recommendation.guideline_source || t(TEXT.whoTreatmentGuidance)) }}
                </p>
                <ul v-if="diagnosisResult.treatment_recommendation.decision_basis?.length" class="mt-3 text-sm text-emerald-700 dark:text-emerald-400 space-y-1">
                  <li v-for="(item, i) in diagnosisResult.treatment_recommendation.decision_basis" :key="i">
                    {{ translateBackendText(item) }}
                  </li>
                </ul>
                <div v-if="diagnosisResult.treatment_recommendation.treatment_options?.length > 1" class="mt-4">
                  <p class="text-sm font-semibold text-emerald-800 dark:text-emerald-300">{{ t(TEXT.otherTreatmentOptions) }}</p>
                  <ul class="mt-2 text-sm text-emerald-700 dark:text-emerald-400 space-y-2">
                    <li
                      v-for="(option, i) in diagnosisResult.treatment_recommendation.treatment_options.slice(1)"
                      :key="i"
                    >
                      {{ translateBackendText(option.name) }} - {{ translateBackendText(option.duration) }} - {{ translateBackendText(option.drugs) }}
                    </li>
                  </ul>
                </div>
                <p class="text-xs text-emerald-600 dark:text-emerald-500 mt-2">
                  {{ translateBackendText(diagnosisResult.treatment_recommendation.notes) }}
                </p>
              </div>
            </div>

            <p class="text-xs text-gray-500 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              {{ t(TEXT.disclaimer) }}
            </p>
          </div>

          <div v-else class="rounded-xl border border-dashed border-gray-300 bg-white p-6 shadow-lg dark:border-gray-700 dark:bg-gray-800 xl:sticky xl:top-6">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t(TEXT.diagnosticReport) }}</h2>
            <p class="mt-3 text-sm text-gray-600 dark:text-gray-300">
              {{ t(TEXT.reportPlaceholder) }}
            </p>
            <div class="mt-4 grid gap-3">
              <div class="rounded-lg bg-gray-50 p-4 dark:bg-gray-700/40">
                <p class="text-sm font-medium text-gray-800 dark:text-gray-200">{{ t(TEXT.reportWillShow) }}</p>
                <ul class="mt-2 space-y-2 text-sm text-gray-600 dark:text-gray-300">
                  <li>{{ t(TEXT.reportItemRisk) }}</li>
                  <li>{{ t(TEXT.reportItemBacteria) }}</li>
                  <li>{{ t(TEXT.reportItemDst) }}</li>
                  <li>{{ t(TEXT.reportItemTreatment) }}</li>
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
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t(TEXT.tabPatients) }}</h2>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                {{ tf(TEXT.showingRecords, { start: patientRangeStart, end: patientRangeEnd, total: patientTotal }) }}
              </p>
            </div>
            <div class="flex gap-2">
              <input
                v-model="searchQuery"
                type="text"
                :placeholder="t(TEXT.searchPatients)"
                class="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              />
              <select
                v-model="patientSort"
                @change="refreshPatients"
                class="px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
              >
                <option value="id_asc">{{ t(TEXT.sortDbOrder) }}</option>
                <option value="id_desc">{{ t(TEXT.sortNewestId) }}</option>
                <option value="created_desc">{{ t(TEXT.sortNewestCreated) }}</option>
                <option value="created_asc">{{ t(TEXT.sortOldestCreated) }}</option>
              </select>
            <button
                @click="refreshPatients"
                class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
              >
              🔄 {{ t(TEXT.refresh) }}
              </button>
            </div>
          </div>
          
          <div v-if="patients.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            {{ t(TEXT.noPatientsFound) }}
          </div>

          <div v-else class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b border-gray-200 dark:border-gray-700">
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colId) }}</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colName) }}</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colAge) }}</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colGender) }}</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colCity) }}</th>
                  <th class="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">{{ t(TEXT.colCreated) }}</th>
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
                {{ tf(TEXT.pageOf, { page: patientsPage, pages: patientPages }) }}
              </p>
              <div class="flex gap-2">
                <button
                  :disabled="patientsPage <= 1"
                  @click="changePatientsPage(patientsPage - 1)"
                  class="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                >
                  {{ t(TEXT.previous) }}
                </button>
                <button
                  :disabled="patientsPage >= patientPages"
                  @click="changePatientsPage(patientsPage + 1)"
                  class="px-4 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 disabled:opacity-50"
                >
                  {{ t(TEXT.next) }}
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
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">{{ t(TEXT.tabAlerts) }}</h2>
            <button
              @click="loadAlerts"
              class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg"
            >
              🔄 {{ t(TEXT.refresh) }}
            </button>
          </div>
          
          <div v-if="alerts.length === 0" class="text-center py-12 text-gray-500 dark:text-gray-400">
            {{ t(TEXT.noAlerts) }}
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
                    {{ alert.severity === 'high' ? '🚨' : '⚠️' }} {{ translateBackendText(alert.alert_type) }}
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ translateBackendText(alert.message) }}</p>
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
import { ref, computed, onMounted, watch } from 'vue'

const API_BASE = 'http://localhost:5000/api'

function makeFlagDataUri(svg) {
  return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const languageOptions = [
  {
    code: 'EN',
    flagSrc: makeFlagDataUri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40"><rect width="60" height="40" fill="#1f4aa8"/><path d="M0 0l60 40M60 0L0 40" stroke="#fff" stroke-width="8"/><path d="M0 0l60 40M60 0L0 40" stroke="#d62828" stroke-width="4"/><path d="M30 0v40M0 20h60" stroke="#fff" stroke-width="14"/><path d="M30 0v40M0 20h60" stroke="#d62828" stroke-width="8"/></svg>'),
    label: { EN: 'English', FR: 'Anglais', SW: 'Kiingereza', RW: 'Icyongereza' }
  },
  {
    code: 'FR',
    flagSrc: makeFlagDataUri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40"><rect width="20" height="40" fill="#1f4aa8"/><rect x="20" width="20" height="40" fill="#ffffff"/><rect x="40" width="20" height="40" fill="#d62828"/></svg>'),
    label: { EN: 'French', FR: 'Français', SW: 'Kifaransa', RW: 'Igifaransa' }
  },
  {
    code: 'SW',
    flagSrc: makeFlagDataUri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40"><rect width="60" height="40" fill="#1eb53a"/><path d="M-8 34L16 -6h52L44 46z" fill="#00a3dd"/><path d="M-10 32L14 -8h8L-2 32zm40 16L70 8h-8L22 48z" fill="#fcd116"/><path d="M-6 36L18 -4h24L18 44z" fill="#000"/></svg>'),
    label: { EN: 'Swahili', FR: 'Swahili', SW: 'Kiswahili', RW: 'Igiswahili' }
  },
  {
    code: 'RW',
    flagSrc: makeFlagDataUri('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40"><rect width="60" height="20" fill="#00a1de"/><rect y="20" width="60" height="10" fill="#fad201"/><rect y="30" width="60" height="10" fill="#20603d"/><circle cx="48" cy="10" r="4.5" fill="#fad201"/><g stroke="#fad201" stroke-width="1.4" stroke-linecap="round"><path d="M48 2v3"/><path d="M48 15v3"/><path d="M40 10h3"/><path d="M53 10h3"/><path d="m42.7 4.7 2.2 2.2"/><path d="m51.1 13.1 2.2 2.2"/><path d="m53.3 4.7-2.2 2.2"/><path d="m44.9 13.1-2.2 2.2"/></g></svg>'),
    label: { EN: 'Kinyarwanda', FR: 'Kinyarwanda', SW: 'Kinyarwanda', RW: 'Ikinyarwanda' }
  }
]

const TEXT = {
  langShort: { EN: 'Lang', FR: 'Langue', SW: 'Lugha', RW: 'Ururimi' },
  publicAreaLabel: { EN: 'Public area', FR: 'Espace public', SW: 'Eneo la umma', RW: 'Aho bose babona' },
  publicAreaHint: {
    EN: 'Read the home page explanation, then go to Login to access the protected workspace.',
    FR: "Lisez l'explication de la page d'accueil, puis allez à Connexion pour accéder à l'espace protégé.",
    SW: 'Soma maelezo ya ukurasa wa mwanzo, kisha nenda kwenye kuingia ili ufungue sehemu iliyolindwa.',
    RW: "Soma ibisobanuro byo ku rupapuro rubanza, hanyuma ujye ku kwinjira kugirango winjire ahakingiwe."
  },
  homeTitle: { EN: 'Home', FR: 'Accueil', SW: 'Mwanzo', RW: 'Ahabanza' },
  loginTitle: { EN: 'Login', FR: 'Connexion', SW: 'Ingia', RW: 'Kwinjira' },
  authenticatedUser: { EN: 'Authenticated user', FR: 'Utilisateur connecté', SW: 'Mtumiaji ameidhinishwa', RW: 'Umukoresha wemerewe' },
  authorizedRole: { EN: 'authorized', FR: 'autorisé', SW: 'ameidhinishwa', RW: 'yemewe' },
  tabDiagnose: { EN: 'Diagnose', FR: 'Diagnostic', SW: 'Uchunguzi', RW: 'Isuzuma' },
  tabPatients: { EN: 'Patients', FR: 'Patients', SW: 'Wagonjwa', RW: 'Abarwayi' },
  tabAlerts: { EN: 'Alerts', FR: 'Alertes', SW: 'Tahadhari', RW: 'Amatangazo' },
  sessionExpired: {
    EN: 'Your session expired. Please sign in again.',
    FR: 'Votre session a expiré. Veuillez vous reconnecter.',
    SW: 'Kipindi chako kimeisha. Tafadhali ingia tena.',
    RW: 'Igihe cyo kwinjira cyarangiye. Ongera winjire.'
  },
  invalidEmailOrPassword: {
    EN: 'Invalid email or password',
    FR: 'Email ou mot de passe invalide',
    SW: 'Barua pepe au nenosiri si sahihi',
    RW: 'Email cyangwa ijambo-banga si byo'
  },
  loginFailed: {
    EN: 'Login failed. Ensure the backend server is running and your credentials are correct.',
    FR: 'La connexion a échoué. Vérifiez que le serveur backend fonctionne et que vos identifiants sont corrects.',
    SW: 'Kuingia kumeshindikana. Hakikisha seva ya backend inafanya kazi na taarifa zako ni sahihi.',
    RW: 'Kwinjira byanze. Reba ko seriveri ya backend iri gukora kandi amakuru winjije ari yo.'
  },
  headerSubtitle: {
    EN: 'Comprehensive Patient Analysis & Treatment',
    FR: 'Analyse complète du patient et traitement',
    SW: 'Uchambuzi kamili wa mgonjwa na matibabu',
    RW: 'Isesengura ry’umurwayi n’ubuvuzi'
  },
  emailLabel: { EN: 'Email', FR: 'Email', SW: 'Barua pepe', RW: 'Email' },
  emailPlaceholder: { EN: 'you@example.com', FR: 'vous@exemple.com', SW: 'wewe@mfano.com', RW: 'wowe@urugero.com' },
  passwordLabel: { EN: 'Password', FR: 'Mot de passe', SW: 'Nenosiri', RW: 'Ijambo-banga' },
  passwordPlaceholder: { EN: 'Password', FR: 'Mot de passe', SW: 'Nenosiri', RW: 'Ijambo-banga' },
  showPasswordTitle: { EN: 'Show password', FR: 'Afficher le mot de passe', SW: 'Onyesha nenosiri', RW: 'Erekana ijambo-banga' },
  hidePasswordTitle: { EN: 'Hide password', FR: 'Masquer le mot de passe', SW: 'Ficha nenosiri', RW: 'Hisha ijambo-banga' },
  signInNotesTitle: { EN: 'Useful sign-in notes', FR: 'Notes utiles', SW: 'Vidokezo vya kuingia', RW: 'Inama zo kwinjira' },
  signInNote1: {
    EN: 'Use the eye icon to check the password.',
    FR: "Utilisez l'icône œil pour voir le mot de passe.",
    SW: 'Tumia alama ya jicho kuona nenosiri.',
    RW: 'Koresha akamenyetso k’ijisho urebe ijambo-banga.'
  },
  signInNote2: {
    EN: 'Email stays after refresh.',
    FR: "L'email reste après actualisation.",
    SW: 'Barua pepe inabaki baada ya kurefusha ukurasa.',
    RW: 'Email iguma ihari na nyuma yo kongera gufungura.'
  },
  signInNote3: {
    EN: 'Click your name or role to log out.',
    FR: 'Cliquez votre nom ou rôle pour vous déconnecter.',
    SW: 'Bofya jina au nafasi yako ili utoke.',
    RW: 'Kanda izina cyangwa umwanya wawe kugira ngo usohoke.'
  },
  languageLabel: {
    EN: 'Language',
    FR: 'Langue',
    SW: 'Lugha',
    RW: 'Ururimi'
  },
  diagnosisRequestFailed: {
    EN: 'Unable to complete the diagnosis request.',
    FR: "Impossible de terminer la demande de diagnostic.",
    SW: 'Imeshindikana kukamilisha ombi la uchunguzi.',
    RW: "Ntibishobotse kurangiza ubusabe bw'isuzuma."
  },
  patientsLoadFailed: {
    EN: 'Unable to load patients.',
    FR: 'Impossible de charger les patients.',
    SW: 'Imeshindikana kupakia wagonjwa.',
    RW: 'Ntibishobotse gupakira abarwayi.'
  },
  alertsLoadFailed: {
    EN: 'Unable to load alerts.',
    FR: 'Impossible de charger les alertes.',
    SW: 'Imeshindikana kupakia tahadhari.',
    RW: 'Ntibishobotse gupakira amatangazo.'
  },
  alertLabel: {
    EN: 'TB alert',
    FR: 'Alerte TB',
    SW: 'Tahadhari ya TB',
    RW: 'Itangazo rya TB'
  },
  alertMarkReadFailed: {
    EN: 'Unable to mark alert as read.',
    FR: "Impossible de marquer l'alerte comme lue.",
    SW: 'Imeshindikana kuashiria tahadhari kuwa imesomwa.',
    RW: 'Ntibishobotse gushyira itangazo ku rwego rw\'iryasomwe.'
  },
  backendAlertTemplate: {
    EN: 'Patient {patientName} (ID: {patientId}) classified as {category} with estimated bacteria {species}. {recommendation}',
    FR: 'Patient {patientName} (ID : {patientId}) classé {category} avec bactérie estimée {species}. {recommendation}',
    SW: 'Mgonjwa {patientName} (ID: {patientId}) ameainishwa kama {category} na bakteria anayekadiriwa kuwa {species}. {recommendation}',
    RW: "Umurwayi {patientName} (ID: {patientId}) yashyizwe mu rwego rwa {category} n'udukoko twagereranijwe ko ari {species}. {recommendation}"
  },
  signIn: { EN: 'Sign in', FR: 'Se connecter', SW: 'Ingia', RW: 'Injira' },
  signingIn: { EN: 'Signing in...', FR: 'Connexion...', SW: 'Inaingia...', RW: 'Birimo kwinjira...' },
  add: { EN: 'Add', FR: 'Ajouter', SW: 'Ongeza', RW: 'Ongeraho' },
  cancel: { EN: 'Cancel', FR: 'Annuler', SW: 'Ghairi', RW: 'Hagarika' },
  addSymptom: { EN: 'Add symptom', FR: 'Ajouter symptôme', SW: 'Ongeza dalili', RW: 'Ongeraho ikimenyetso' },
  addOneSymptom: { EN: 'Add one symptom', FR: 'Ajouter un symptôme', SW: 'Ongeza dalili moja', RW: 'Ongeraho ikimenyetso kimwe' },
  addExposure: { EN: 'Add exposure', FR: 'Ajouter exposition', SW: 'Ongeza exposure', RW: 'Ongeraho aho yandurira' },
  addOneExposure: {
    EN: 'Add one exposure item',
    FR: "Ajouter un élément d'exposition",
    SW: 'Ongeza kipengele kimoja cha exposure',
    RW: "Ongeraho ikintu kimwe cy'aho yandurira"
  },
  guidedFlowTitle: { EN: 'Guided diagnosis flow', FR: 'Flux de diagnostic guidé', SW: 'Mtiririko wa uchunguzi unaoongozwa', RW: 'Uko isuzuma rikurikirana' },
  loginHeroHeadline: {
    EN: 'From patient data to TB decision.',
    FR: 'Des données du patient à la décision TB.',
    SW: 'Kutoka taarifa za mgonjwa hadi uamuzi wa TB.',
    RW: "Kuva ku makuru y’umurwayi kugera ku mwanzuro wa TB."
  },
  loginHeroSubtitle: {
    EN: 'Open a case, review evidence, generate one guided report.',
    FR: 'Ouvrez un dossier, revoyez les preuves, générez un rapport guidé.',
    SW: 'Fungua kesi, kagua ushahidi, toa ripoti iliyoongozwa.',
    RW: 'Fungura dosiye, suzuma ibimenyetso, ukore raporo iyobowe.'
  },
  systemWorkflowTitle: { EN: 'System workflow', FR: 'Flux du système', SW: 'Utaratibu wa mfumo', RW: 'Uko sisitemu ikora' },
  systemWorkflowHint: { EN: 'Few words', FR: 'En bref', SW: 'Kwa kifupi', RW: 'Muri make' },
  workflowSystemTitle: { EN: 'TB System', FR: 'Système TB', SW: 'Mfumo wa TB', RW: 'Sisitemu ya TB' },
  workflowLogin: { EN: 'login', FR: 'connexion', SW: 'ingia', RW: 'kwinjira' },
  workflowEvaluate: { EN: 'evaluate', FR: 'évaluer', SW: 'tathmini', RW: 'gusuzuma' },
  workflowGuideCare: { EN: 'guide care', FR: 'guider soins', SW: 'ongoza matibabu', RW: 'kuyobora ubuvuzi' },
  workflowStep1: { EN: 'STEP 1', FR: 'ÉTAPE 1', SW: 'HATUA 1', RW: 'INTAMBWE 1' },
  workflowStep2: { EN: 'STEP 2', FR: 'ÉTAPE 2', SW: 'HATUA 2', RW: 'INTAMBWE 2' },
  workflowStep3: { EN: 'STEP 3', FR: 'ÉTAPE 3', SW: 'HATUA 3', RW: 'INTAMBWE 3' },
  workflowStep4: { EN: 'STEP 4', FR: 'ÉTAPE 4', SW: 'HATUA 4', RW: 'INTAMBWE 4' },
  workflowCollect: { EN: 'Collect', FR: 'Collecter', SW: 'Kusanya', RW: 'Kwegeranya' },
  workflowAnalyze: { EN: 'Analyze', FR: 'Analyser', SW: 'Chambua', RW: 'Sesengura' },
  workflowClassify: { EN: 'Classify', FR: 'Classer', SW: 'Ainisha', RW: 'Shyira mu rwego' },
  workflowTreat: { EN: 'Treat', FR: 'Traiter', SW: 'Tibu', RW: 'Vura' },
  workflowPatient: { EN: 'Patient', FR: 'Patient', SW: 'Mgonjwa', RW: 'Umurwayi' },
  workflowSymptoms: { EN: 'symptoms', FR: 'symptômes', SW: 'dalili', RW: 'ibimenyetso' },
  workflowTests: { EN: 'tests', FR: 'tests', SW: 'vipimo', RW: 'ibizamini' },
  workflowTbType: { EN: 'TB type', FR: 'Type TB', SW: 'Aina ya TB', RW: 'Ubwoko bwa TB' },
  workflowBacteria: { EN: 'bacteria', FR: 'bactérie', SW: 'bakteria', RW: 'udukoko' },
  workflowResistance: { EN: 'resistance', FR: 'résistance', SW: 'usugu', RW: 'resistance' },
  workflowReport: { EN: 'Report', FR: 'Rapport', SW: 'Ripoti', RW: 'Raporo' },
  workflowTreatment: { EN: 'treatment', FR: 'traitement', SW: 'matibabu', RW: 'ubuvuzi' },
  workflowGuidance: { EN: 'guidance', FR: 'conseils', SW: 'mwongozo', RW: 'ubuyobozi' },
  newPatient: { EN: 'New patient', FR: 'Nouveau patient', SW: 'Mgonjwa mpya', RW: 'Umurwayi mushya' },
  existingPatient: { EN: 'Existing patient', FR: 'Patient existant', SW: 'Mgonjwa aliyepo', RW: 'Umurwayi usanzwe' },
  clinicalReport: { EN: 'Clinical report', FR: 'Rapport clinique', SW: 'Ripoti ya kliniki', RW: 'Raporo ya kliniki' },
  whatYouCanDo: { EN: 'What you can do', FR: 'Ce que vous pouvez faire', SW: 'Unachoweza kufanya', RW: 'Ibyo ushobora gukora' },
  step1Title: { EN: '1. Patient identity', FR: '1. Identité du patient', SW: '1. Utambulisho wa mgonjwa', RW: "1. Amakuru y'umurwayi" },
  step1Intro: {
    EN: 'Basic patient details used for record linking and report display.',
    FR: 'Détails de base pour relier le dossier et afficher le rapport.',
    SW: 'Taarifa za msingi za mgonjwa kwa kuunganisha rekodi na kuonyesha ripoti.',
    RW: "Amakuru y'ibanze afasha guhuza dosiye no kwerekana raporo."
  },
  step2Title: { EN: '2. Clinical clues', FR: '2. Indices cliniques', SW: '2. Dalili', RW: '2. Ibimenyetso' },
  step3Title: { EN: '3. Species and test results', FR: '3. Espèce et résultats', SW: '3. Aina na majibu ya vipimo', RW: '3. Ubwoko n’ibisubizo' },
  step4Title: { EN: '4. DST and resistance', FR: '4. DST et résistance', SW: '4. DST na usugu', RW: '4. DST na resistance' },
  firstNameLabel: { EN: 'First name', FR: 'Prénom', SW: 'Jina la kwanza', RW: 'Izina rya mbere' },
  firstNamePlaceholder: { EN: 'First name', FR: 'Prénom', SW: 'Jina la kwanza', RW: 'Izina rya mbere' },
  lastNameLabel: { EN: 'Last name', FR: 'Nom', SW: 'Jina la mwisho', RW: 'Izina rya nyuma' },
  lastNamePlaceholder: { EN: 'Last name', FR: 'Nom', SW: 'Jina la mwisho', RW: 'Izina rya nyuma' },
  patientIdLabel: { EN: 'Patient ID', FR: 'ID patient', SW: 'ID ya mgonjwa', RW: "ID y'umurwayi" },
  uniqueIdPlaceholder: { EN: 'Unique ID', FR: 'ID unique', SW: 'ID ya kipekee', RW: 'ID yihariye' },
  ageLabel: { EN: 'Age', FR: 'Âge', SW: 'Umri', RW: 'Imyaka' },
  agePlaceholder: { EN: 'Age', FR: 'Âge', SW: 'Umri', RW: 'Imyaka' },
  genderLabel: { EN: 'Gender', FR: 'Sexe', SW: 'Jinsia', RW: 'Igitsina' },
  genderMale: { EN: 'Male', FR: 'Masculin', SW: 'Mwanaume', RW: 'Gabo' },
  genderFemale: { EN: 'Female', FR: 'Féminin', SW: 'Mwanamke', RW: 'Gore' },
  genderOther: { EN: 'Other', FR: 'Autre', SW: 'Nyingine', RW: 'Ikindi' },
  autoDetectLabel: { EN: 'Auto-detect', FR: 'Détection auto', SW: 'Mfumo ujichagulie', RW: 'Sisitemu yihitiremo' },
  speciesTuberculosis: { EN: 'Mycobacterium tuberculosis', FR: 'Mycobacterium tuberculosis', SW: 'Mycobacterium tuberculosis', RW: 'Mycobacterium tuberculosis' },
  speciesBovis: { EN: 'Mycobacterium bovis', FR: 'Mycobacterium bovis', SW: 'Mycobacterium bovis', RW: 'Mycobacterium bovis' },
  speciesAfricanum: { EN: 'Mycobacterium africanum', FR: 'Mycobacterium africanum', SW: 'Mycobacterium africanum', RW: 'Mycobacterium africanum' },
  speciesCanettii: { EN: 'Mycobacterium canettii', FR: 'Mycobacterium canettii', SW: 'Mycobacterium canettii', RW: 'Mycobacterium canettii' },
  speciesMicroti: { EN: 'Mycobacterium microti', FR: 'Mycobacterium microti', SW: 'Mycobacterium microti', RW: 'Mycobacterium microti' },
  speciesCaprae: { EN: 'Mycobacterium caprae', FR: 'Mycobacterium caprae', SW: 'Mycobacterium caprae', RW: 'Mycobacterium caprae' },
  speciesPinnipedii: { EN: 'Mycobacterium pinnipedii', FR: 'Mycobacterium pinnipedii', SW: 'Mycobacterium pinnipedii', RW: 'Mycobacterium pinnipedii' },
  speciesOrygis: { EN: 'Mycobacterium orygis', FR: 'Mycobacterium orygis', SW: 'Mycobacterium orygis', RW: 'Mycobacterium orygis' },
  statusUnknown: { EN: 'Unknown', FR: 'Inconnu', SW: 'Haijulikani', RW: 'Ntibizwi' },
  statusPositive: { EN: 'Positive', FR: 'Positif', SW: 'Kimeonekana', RW: 'Cyagaragaye' },
  statusNegative: { EN: 'Negative', FR: 'Négatif', SW: 'Hakitaonekana', RW: 'Nticyagaragaye' },
  statusNormal: { EN: 'Normal', FR: 'Normal', SW: 'Kawaida', RW: 'Bisanzwe' },
  statusAbnormal: { EN: 'Abnormal', FR: 'Anormal', SW: 'Isiyo ya kawaida', RW: 'Ntibisanzwe' },
  statusYes: { EN: 'Yes', FR: 'Oui', SW: 'Ndiyo', RW: 'Yego' },
  statusNo: { EN: 'No', FR: 'Non', SW: 'Hapana', RW: 'Oya' },
  cityLabel: { EN: 'City', FR: 'Ville', SW: 'Mji', RW: 'Umujyi' },
  cityPlaceholder: { EN: 'City', FR: 'Ville', SW: 'Mji', RW: 'Umujyi' },
  antibiogramSummaryLabel: { EN: 'Antibiogram / DST summary', FR: 'Résumé antibiogramme / DST', SW: 'Muhtasari wa antibiogram / DST', RW: 'Incamake ya antibiogram / DST' },
  addDstItem: { EN: 'Add DST item', FR: 'Ajouter élément DST', SW: 'Ongeza kipengele cha DST', RW: 'Ongeraho ikintu cya DST' },
  addOneDstItem: { EN: 'Add one DST item', FR: 'Ajouter un élément DST', SW: 'Ongeza kipengele kimoja cha DST', RW: 'Ongeraho ikintu kimwe cya DST' },
  resistantToLabel: { EN: 'Resistant to', FR: 'Résistant à', SW: 'Imiti isiyofataho', RW: 'Imiti idafataho' },
  susceptibleToLabel: { EN: 'Susceptible to', FR: 'Sensible à', SW: 'Imiti ifataho', RW: 'Imiti ifataho' },
  addResistantMedicine: { EN: 'Add resistant medicine', FR: 'Ajouter médicament résistant', SW: 'Ongeza umuti usiyofataho', RW: 'Ongeraho umuti udafataho' },
  addOneResistantMedicine: { EN: 'Add one resistant medicine', FR: 'Ajouter un médicament résistant', SW: 'Ongeza umuti umwe usiyofataho', RW: 'Ongeraho umuti umwe udafataho' },
  addSusceptibleMedicine: { EN: 'Add susceptible medicine', FR: 'Ajouter médicament sensible', SW: 'Ongeza umuti ufataho', RW: 'Ongeraho umuti ufataho' },
  addOneSusceptibleMedicine: { EN: 'Add one susceptible medicine', FR: 'Ajouter un médicament sensible', SW: 'Ongeza umuti umwe ufataho', RW: 'Ongeraho umuti umwe ufataho' },
  stepOf: {
    EN: 'Step {current} of {total}',
    FR: 'Étape {current} sur {total}',
    SW: 'Hatua {current} kati ya {total}',
    RW: 'Intambwe {current} kuri {total}'
  },
  percentComplete: {
    EN: '{percent}% complete',
    FR: '{percent}% terminé',
    SW: '{percent}% imekamilika',
    RW: '{percent}% birarangiye'
  },
  symptomsLabel: { EN: 'Symptoms', FR: 'Symptômes', SW: 'Dalili', RW: 'Ibimenyetso' },
  exposureHistoryLabel: { EN: 'Exposure history', FR: "Historique d'exposition", SW: 'Historia ya kuambukizwa', RW: "Amateka y'aho yandurira" },
  clinicalCluesIntro: {
    EN: 'Add symptoms and exposure history from the guided TB lists, or type your own item if not listed.',
    FR: "Ajoutez symptômes et exposition via les listes TB, ou saisissez un élément si non listé.",
    SW: 'Ongeza dalili na historia ya kuambukizwa kutoka kwenye orodha, au andika ikiwa haipo.',
    RW: "Ongeraho ibimenyetso n'aho yandurira ukoresheje urutonde, cyangwa wandike ibitanditse."
  },
  symptomsHint: {
    EN: 'Type directly in the field. Suggested TB symptoms below can be clicked to append.',
    FR: "Saisissez directement. Les symptômes suggérés ci‑dessous peuvent être ajoutés en un clic.",
    SW: 'Andika moja kwa moja. Dalili ziri hapa chini ushobora kuzikanda zikiyongeramo.',
    RW: "Andika mu mwanya wabugenewe. Ibimenyetso biri hasi ushobora kubikanda bikiyongeramo."
  },
  exposureHint: {
    EN: 'Existing patient exposure notes stay unchanged unless the clinician edits them.',
    FR: "Les notes d'exposition restent inchangées sauf modification par le clinicien.",
    SW: 'Amakuru y’aho mgonjwa ashobora kuba yaranduriye aguma uko ari kugeza muganga ayahinduye.',
    RW: "Amakuru y’aho umurwayi ashobora kuba yaranduriye aguma uko ari keretse muganga ayahinduye."
  },
  exposurePlaceholder: {
    EN: 'Enter or review household, travel, animal, dairy, wildlife, or occupational exposure',
    FR: "Saisir ou revoir exposition : domicile, voyage, animaux, lait, faune, profession",
    SW: 'Andika cyangwa usubiremo aho ashobora kuba yaranduriye: nyumbani, safari, wanyama, maziwa, wanyamapori, kazi',
    RW: "Andika cyangwa usubiremo aho ashobora kuba yaranduriye: mu rugo, ingendo, amatungo, amata, inyamaswa, akazi"
  },
  testsIntro: {
    EN: 'Choose known results or leave bacteria on `Auto-detect` so the system estimates from the patient record.',
    FR: "Choisissez les résultats connus ou laissez `Auto-detect` pour estimer selon le dossier.",
    SW: 'Hitamo ibisubizo uziko cyangwa usige `Mfumo ujichagulie` sisitemu ibigereranye ishingiye kuri rekodi.',
    RW: "Hitamo ibisubizo uziko cyangwa usige `Sisitemu yihitiremo` kugira ngo ibigereranye ishingiye kuri dosiye."
  },
  dstIntro: {
    EN: 'Keep these as normal input fields. Suggested TB DST phrases and medicines can be appended when useful.',
    FR: "Gardez ces champs comme saisie normale. Les suggestions DST/médicaments peuvent être ajoutées.",
    SW: 'Hizi ni sehemu za kawaida. Mapendekezo ya DST/dawa yanaweza kuongezwa ukihitaji.',
    RW: "Ibi ni ibyo wandika bisanzwe. Ushobora kongeramo DST/dawa byatanzwe iyo bikenewe."
  },
  dstSummaryPlaceholder: {
    EN: 'Enter DST summary or keep stored text for an existing patient',
    FR: 'Saisir le résumé DST ou garder le texte existant',
    SW: 'Ingiza muhtasari wa DST au acha maandishi yaliyopo',
    RW: 'Andika incamake ya DST cyangwa ugumane ibyari bihari'
  },
  resistantToPlaceholder: {
    EN: 'Type resistant medicines or reuse stored patient text',
    FR: 'Saisir médicaments résistants ou réutiliser le texte existant',
    SW: 'Andika imiti isiyofataho cyangwa ukoreshe ibisanzwe byabitswe',
    RW: 'Andika imiti idafataho cyangwa ukoreshe ibisanzwe byabitswe'
  },
  susceptibleToPlaceholder: {
    EN: 'Type susceptible medicines or reuse stored patient text',
    FR: 'Saisir médicaments sensibles ou réutiliser le texte existant',
    SW: 'Andika imiti ifataho cyangwa ukoreshe ibisanzwe byabitswe',
    RW: 'Andika imiti ifataho cyangwa ukoreshe ibisanzwe byabitswe'
  },
  reportWillShow: { EN: 'What the report will show', FR: 'Ce que montre le rapport', SW: 'Ripoti itaonyesha nini', RW: 'Ibyo raporo izerekana' },
  reportItemRisk: { EN: 'TB risk and red flags', FR: 'Risque TB et signaux rouges', SW: 'Hatari ya TB na dalili hatari', RW: 'Ibyago bya TB n’ibimenyetso bikomeye' },
  reportItemBacteria: { EN: 'Estimated bacteria and infection type', FR: "Bactérie estimée et type d'infection", SW: 'Bakteria anayekadiriwa na aina ya maambukizi', RW: 'Udukoko twagereranijwe n’ubwoko bw’infection' },
  confidenceLabel: { EN: 'Confidence', FR: 'Confiance', SW: 'Uhakika', RW: 'Icyizere' },
  tbBacteriaAssessment: { EN: 'TB bacteria assessment', FR: 'Évaluation des bactéries TB', SW: 'Tathmini ya bakteria wa TB', RW: 'Isuzuma ry’udukoko twa TB' },
  methodLabel: { EN: 'Method', FR: 'Méthode', SW: 'Njia', RW: 'Uburyo' },
  supportedSpeciesLabel: { EN: 'Supported species', FR: 'Espèces prises en charge', SW: 'Aina zinazotambuliwa', RW: 'Ubwoko bushyigikiwe' },
  reasonLabel: { EN: 'Reason', FR: 'Raison', SW: 'Sababu', RW: 'Impamvu' },
  typicalSourceLabel: { EN: 'Typical source', FR: 'Source habituelle', SW: 'Chanzo cha kawaida', RW: 'Aho bikunze guturuka' },
  labNoteLabel: { EN: 'Lab note', FR: 'Note labo', SW: 'Maelezo ya maabara', RW: 'Icyitonderwa cya labo' },
  infectionAssessment: { EN: 'Infection assessment', FR: "Évaluation de l'infection", SW: 'Tathmini ya maambukizi', RW: 'Isuzuma ry’ubwandu' },
  resistanceDstProfile: { EN: 'Resistance / DST profile', FR: 'Profil résistance / DST', SW: 'Muhtasari wa usugu / DST', RW: 'Umwirondoro w’ukudafata kw’imiti / DST' },
  regimenLevelLabel: { EN: 'Regimen level', FR: 'Niveau du schéma', SW: 'Urwego rw’imiti', RW: 'Urwego rw’imiti' },
  antibiogramLabel: { EN: 'Antibiogram', FR: 'Antibiogramme', SW: 'Antibiogram', RW: 'Antibiogram' },
  noneProvided: { EN: 'None provided', FR: 'Aucun fourni', SW: 'Hakuna kilichotolewa', RW: 'Nta byatanzwe' },
  mlPrediction: { EN: 'ML prediction', FR: 'Prédiction ML', SW: 'Utabiri wa porogaramu', RW: 'Ihanura rya porogaramu' },
  tbPredictionLabel: { EN: 'TB prediction', FR: 'Prédiction TB', SW: 'Utabiri wa TB', RW: 'Ihanura rya TB' },
  drugResistancePredictionLabel: { EN: 'Drug resistance prediction', FR: 'Prédiction de résistance', SW: 'Utabiri wa usugu wa dawa', RW: 'Ihanura rya resistance y’imiti' },
  treatmentRecommendation: { EN: 'Treatment recommendation', FR: 'Recommandation de traitement', SW: 'Pendekezo la matibabu', RW: 'Inama y’ubuvuzi' },
  treatmentPlanFallback: { EN: 'Treatment plan', FR: 'Plan de traitement', SW: 'Mpango wa matibabu', RW: 'Gahunda y’ubuvuzi' },
  categoryLabel: { EN: 'Category', FR: 'Catégorie', SW: 'Kategoria', RW: 'Icyiciro' },
  bacteriaLabel: { EN: 'Bacteria', FR: 'Bactérie', SW: 'Bakteria', RW: 'Udukoko' },
  infectionLabel: { EN: 'Infection', FR: 'Infection', SW: 'Maambukizi', RW: 'Ubwandu' },
  resistanceLabel: { EN: 'Resistance', FR: 'Résistance', SW: 'Usugu', RW: 'Ukudafata kw’imiti' },
  levelLabel: { EN: 'Level', FR: 'Niveau', SW: 'Kiwango', RW: 'Urwego' },
  durationLabel: { EN: 'Duration', FR: 'Durée', SW: 'Muda', RW: 'Igihe' },
  drugsLabel: { EN: 'Drugs', FR: 'Médicaments', SW: 'Dawa', RW: 'Imiti' },
  dosageLabel: { EN: 'Dosage', FR: 'Posologie', SW: 'Dozi', RW: 'Igipimo' },
  administrationLabel: { EN: 'Administration', FR: 'Administration', SW: 'Utoaji', RW: 'Uko itangwa' },
  monitoringLabel: { EN: 'Monitoring', FR: 'Surveillance', SW: 'Ufuatiliaji', RW: 'Gukurikirana' },
  guidelineLabel: { EN: 'Guideline', FR: 'Directive', SW: 'Mwongozo', RW: 'Amabwiriza' },
  otherTreatmentOptions: { EN: 'Other treatment options', FR: 'Autres options de traitement', SW: 'Chaguo nyingine za matibabu', RW: 'Ubundi buryo bw’ubuvuzi' },
  notAvailableInResponse: { EN: 'Not available in this response', FR: 'Non disponible dans cette réponse', SW: 'Haipatikani kwenye jibu hili', RW: 'Ntiboneka muri iki gisubizo' },
  whoRuleBasedLevel: { EN: 'WHO rule-based treatment level', FR: 'Niveau de traitement basé sur les règles OMS', SW: 'Kiwango cha matibabu kulingana na sheria za WHO', RW: 'Urwego rw’ubuvuzi rushingiye ku mabwiriza ya WHO' },
  whoTreatmentGuidance: { EN: 'WHO-aligned TB treatment guidance', FR: "Guide de traitement TB aligné sur l'OMS", SW: 'Mwongozo wa matibabu ya TB unaolingana na WHO', RW: 'Ubuyobozi bw’ubuvuzi bwa TB bujyanye na WHO' },
  notAvailable: { EN: 'Not available', FR: 'Non disponible', SW: 'Haipatikani', RW: 'Ntibihari' },
  tbLikely: { EN: 'TB likely', FR: 'TB probable', SW: 'Birakekwa ko ari TB', RW: 'Birakekwa ko ari TB' },
  tbNotLikely: { EN: 'TB not likely', FR: 'TB peu probable', SW: 'Biragoye ko yaba ari TB', RW: 'Biragoye ko yaba ari TB' },
  drugResistanceLikely: { EN: 'Drug resistance likely', FR: 'Résistance probable', SW: 'Birashoboka ko imiti itafataho', RW: 'Birashoboka ko imiti idafataho' },
  drugResistanceNotPredicted: { EN: 'Drug resistance not predicted', FR: 'Résistance non prédite', SW: 'Nta kimenyetso kigaragaza ko imiti itafataho', RW: 'Nta kimenyetso kigaragaza ko imiti idafataho' },
  noModelConfidence: { EN: 'No model confidence available.', FR: 'Aucune confiance du modèle disponible.', SW: 'Nta rugero rw’icyizere cya porogaramu rubonetse.', RW: 'Nta rugero rw’icyizere cya porogaramu rubonetse.' },
  modelConfidenceSummary: {
    EN: '{label} with {confidence} model confidence.',
    FR: '{label} avec {confidence} de confiance du modèle.',
    SW: '{label} ku rugero rw’icyizere cya porogaramu rungana na {confidence}.',
    RW: '{label} ku rugero rw’icyizere cya porogaramu rungana na {confidence}.'
  },
  modeDefault: { EN: 'default', FR: 'défaut', SW: 'byahiswemo mbere', RW: 'byahiswemo mbere' },
  regimenFirstLine: { EN: 'first-line', FR: 'première ligne', SW: 'dawa za kwanza', RW: 'umurongo wa mbere' },
  regimenSecondLine: { EN: 'second-line', FR: 'deuxième ligne', SW: 'dawa za pili', RW: 'umurongo wa kabiri' },
  regimenModifiedFirstLine: { EN: 'modified first-line', FR: 'première ligne modifiée', SW: 'dawa za kwanza zilizahindurwa', RW: 'umurongo wa mbere wahinduwe' },
  regimenIndividualizedSecondLine: { EN: 'individualized second-line', FR: 'deuxième ligne individualisée', SW: 'dawa za pili zilizabinafsishwa', RW: 'umurongo wa kabiri wabugenewe' },
  regimenPreventiveTherapy: { EN: 'preventive therapy', FR: 'thérapie préventive', SW: 'tiba ya kinga', RW: 'ubuvuzi bwo kwirinda' },
  urgencyHigh: { EN: 'HIGH', FR: 'ÉLEVÉ', SW: 'KUBWA', RW: 'HEJURU' },
  urgencyUrgent: { EN: 'URGENT', FR: 'URGENT', SW: 'HARAKA', RW: 'BYIHUTIRWA' },
  urgencyCritical: { EN: 'CRITICAL - LIFE THREATENING', FR: 'CRITIQUE - MENACE VITALE', SW: 'HATARI KUBWA KWA MAISHA', RW: 'BIREMEREYE - BISHYIRA UBUZIMA MU KAGA' },
  pulmonaryTb: { EN: 'Pulmonary TB', FR: 'TB pulmonaire', SW: 'TB ya mapafu', RW: 'TB yo mu bihaha' },
  lungsLabel: { EN: 'Lungs', FR: 'Poumons', SW: 'Mapafu', RW: 'Ibihaha' },
  lymphNodeTb: { EN: 'Lymph Node TB', FR: 'TB ganglionnaire', SW: 'TB ya vifuko vya limfu', RW: 'TB yo mu dusabo twa lympho' },
  lymphNodesLabel: { EN: 'Lymph nodes', FR: 'Ganglions lymphatiques', SW: 'Vifuko vya limfu', RW: 'Udusabo twa lympho' },
  boneJointTb: { EN: 'Bone and Joint TB', FR: 'TB osseuse et articulaire', SW: "TB y'amagufa n'ingingo", RW: "TB yo mu magufa n'ingingo" },
  bonesJointsSite: { EN: 'Spine, bones, or joints', FR: 'Colonne, os ou articulations', SW: "Uti wa mgongo, amagufa cyangwa ingingo", RW: "Urutirigongo, amagufa cyangwa ingingo" },
  tbMeningitis: { EN: 'TB Meningitis', FR: 'Méningite tuberculeuse', SW: 'TB yo mu bwonko', RW: 'TB yo mu bwonko' },
  centralNervousSystem: { EN: 'Central nervous system', FR: 'Système nerveux central', SW: "Sisitemu yo hagati y'imyakura", RW: "Sisitemu yo hagati y'imyakura" },
  genitourinaryTb: { EN: 'Genitourinary TB', FR: 'TB génito-urinaire', SW: "TB yo mu myanya ndangagitsina n'inkari", RW: "TB yo mu myanya ndangagitsina n'inkari" },
  genitourinaryTract: { EN: 'Genitourinary tract', FR: 'Voies génito-urinaires', SW: "Imiyoboro y'inkari n'imyanya ndangagitsina", RW: "Imiyoboro y'inkari n'imyanya ndangagitsina" },
  abdominalTb: { EN: 'Abdominal TB', FR: 'TB abdominale', SW: 'TB yo mu nda', RW: 'TB yo mu nda' },
  abdomenPeritoneum: { EN: 'Abdomen/peritoneum', FR: 'Abdomen/péritoine', SW: 'Mu nda/peritoneum', RW: 'Mu nda/peritoneum' },
  pleuralTb: { EN: 'Pleural TB', FR: 'TB pleurale', SW: "TB yo ku gihu cy'ibihaha", RW: "TB yo ku gihu cy'ibihaha" },
  pleuraLabel: { EN: 'Pleura', FR: 'Plèvre', SW: "Igihu cy'ibihaha", RW: "Igihu cy'ibihaha" },
  miliaryTb: { EN: 'Miliary TB', FR: 'TB miliaire', SW: "TB yakwirakwiriye umubiri wose", RW: "TB yakwirakwiriye umubiri wose" },
  disseminatedSite: { EN: 'Disseminated / whole body spread', FR: 'Disséminée / propagation dans tout le corps', SW: "Byakwirakwiriye mu mubiri wose", RW: "Byakwirakwiriye mu mubiri wose" },
  latentTbInfection: { EN: 'Latent TB Infection', FR: 'Infection tuberculeuse latente', SW: 'Ubwandu bwa TB butaragaragara', RW: 'Ubwandu bwa TB butaragaragara' },
  noActiveOrganDisease: { EN: 'No active organ disease', FR: "Aucune atteinte active d'organe", SW: "Nta gice cy'umubiri cyarwaye ku buryo bugaragara", RW: "Nta gice cy'umubiri cyarwaye ku buryo bugaragara" },
  tbHivCoinfection: { EN: 'TB/HIV Co-infection', FR: 'Co-infection TB/VIH', SW: 'Ubwandu bwa TB na HIV icyarimwe', RW: 'Ubwandu bwa TB na VIH icyarimwe' },
  systemicComorbidity: { EN: 'Systemic comorbidity', FR: 'Comorbidité systémique', SW: "Indi ndwara ikorana na yo mu mubiri", RW: "Indi ndwara ijyana na yo mu mubiri" },
  backendSpeciesDescMtuberculosis: {
    EN: 'The most common cause of human tuberculosis worldwide.',
    FR: 'La cause la plus fréquente de tuberculose humaine dans le monde.',
    SW: 'Hiki ndicho chanzo kinachoonekana zaidi cha TB kwa binadamu duniani.',
    RW: 'Ubu ni bwo bwoko bukunze gutera igituntu ku bantu ku isi.'
  },
  backendSpeciesReasonDefault: {
    EN: 'Defaulted to the most common human TB species because the patient record did not contain enough species-specific evidence.',
    FR: "Choix par défaut de l'espèce humaine la plus fréquente car le dossier ne contenait pas assez d'éléments spécifiques.",
    SW: 'Mfumo umechagua aina ya kawaida zaidi ya TB ya binadamu kwa sababu rekodi ya mgonjwa haina ushahidi wa kutosha wa aina mahususi.',
    RW: "Sisitemu yahisemo ubwoko bwa TB busanzwe buboneka ku bantu kuko dosiye y'umurwayi itari ifite ibimenyetso bihagije byihariye ku bwoko."
  },
  backendTypicalSourceHuman: {
    EN: 'Human-to-human airborne transmission.',
    FR: 'Transmission aérienne d’une personne à une autre.',
    SW: 'Maambukizi ya hewani kutoka mtu mmoja kwenda kwa mwingine.',
    RW: 'Yandurira mu mwuka iva ku muntu umwe ujya ku wundi.'
  },
  backendLabNoteRoutineMtbc: {
    EN: 'Routine TB molecular tests and culture commonly target this species within the MTBC.',
    FR: 'Les tests moléculaires TB de routine et la culture ciblent souvent cette espèce dans le MTBC.',
    SW: 'Vipimo vya kawaida vya TB vya molekuli na culture mara nyingi hulenga aina hii ndani ya MTBC.',
    RW: 'Ibizamini bya TB bisanzwe bya molekuli na culture bikunze kwibanda kuri ubu bwoko muri MTBC.'
  },
  backendGuidelineWhoEngine: {
    EN: 'WHO-aligned TB rule engine with species notes, infection-site classification, and DST-aware regimen escalation.',
    FR: "Moteur de règles TB aligné sur l'OMS avec notes d'espèce, classification du site d'infection et escalade guidée par DST.",
    SW: 'Mfumo wa miongozo ya TB unaolingana na WHO ufite maelezo y’ubwoko, aho maambukizi ari, na uteuzi w’imiti ushingiye kuri DST.',
    RW: 'Sisitemu y’amabwiriza ya TB ihuje na WHO, ifite ibisobanuro by’ubwoko, aho ubwandu buri, n’igenamigambi ry’imiti rishingiye kuri DST.'
  },
  primaryTbClassification: { EN: 'Primary TB classification', FR: 'Classification TB principale', SW: 'Uainishaji mkuu wa TB', RW: 'Icyiciro nyamukuru cya TB' },
  bacteriaEstimate: { EN: 'Bacteria estimate', FR: 'Estimation de la bactérie', SW: 'Makadirio ya bakteria', RW: 'Ikigereranyo cy’udukoko' },
  resistanceClassLabel: { EN: 'Resistance class', FR: 'Classe de résistance', SW: 'Icyiciro cy’usugu', RW: 'Icyiciro cy’ukudafata kw’imiti' },
  antibiogramDstSummary: { EN: 'Antibiogram/DST summary', FR: 'Résumé antibiogramme/DST', SW: 'Muhtasari wa antibiogram/DST', RW: 'Incamake ya antibiogram/DST' },
  backendChosenMdr: {
    EN: 'Chosen because rifampicin and isoniazid resistance is present or strongly suspected.',
    FR: "Choisi car une résistance à la rifampicine et à l'isoniazide est présente ou fortement suspectée.",
    SW: 'Byahiswemo kwa sababu usugu wa rifampicin na isoniazid urahari cyangwa ukekwa cyane.',
    RW: 'Byahiswemo kuko kudafata kwa rifampicin na isoniazid kuboneka cyangwa gukekwa cyane.'
  },
  duration18to24Months: { EN: '18-24 months', FR: '18-24 mois', SW: 'miezi 18-24', RW: 'amezi 18-24' },
  duration18to24MonthsTotal: { EN: '18-24 months total', FR: '18-24 mois zose', SW: 'jumla ya miezi 18-24', RW: 'amezi 18-24 yose hamwe' },
  whoMdrRegimen: { EN: 'WHO MDR-TB second-line regimen', FR: 'Schéma OMS MDR-TB de deuxième ligne', SW: 'Gahunda ya WHO ya MDR-TB yo ku murongo wa pili', RW: 'Gahunda ya WHO ya MDR-TB yo ku murongo wa kabiri' },
  confirmedPulmonaryTb: {
    EN: 'CONFIRMED PULMONARY TB (PTB)',
    FR: 'TB PULMONAIRE CONFIRMÉE (PTB)',
    SW: 'TB YA MAPAFU ILIYOTHIBITISHWA (PTB)',
    RW: 'TB Y’IBIHAHA YEMEJWE (PTB)'
  },
  clinicallyDiagnosedPulmonaryTb: {
    EN: 'CLINICALLY DIAGNOSED PULMONARY TB (PTB)',
    FR: 'TB PULMONAIRE DIAGNOSTIQUÉE CLINIQUEMENT (PTB)',
    SW: 'TB YA MAPAFU ILIYOGUNDULIWA KIKLINIKI (PTB)',
    RW: 'TB Y’IBIHAHA YASUZUMWE NA MUGANGA (PTB)'
  },
  presumptivePulmonaryTb: { EN: 'PRESUMPTIVE PULMONARY TB (PTB)', FR: 'TB PULMONAIRE PRÉSUMÉE (PTB)', SW: 'TB YA MAPAFU INAYOSHUKIWA (PTB)', RW: 'TB Y’IBIHAHA IKEKWA (PTB)' },
  noSpecificTbPattern: {
    EN: 'No specific TB infection pattern confirmed',
    FR: "Aucun profil spécifique d'infection TB confirmé",
    SW: 'Nta bwandu bwa TB bwihariye bwemejwe',
    RW: 'Nta bwandu bwa TB bwihariye bwemejwe'
  },
  unspecifiedLabel: { EN: 'Unspecified', FR: 'Non précisé', SW: 'Bitasobanuwe neza', RW: 'Bitasobanuwe neza' },
  dsTbLabel: { EN: 'Drug-sensitive TB (DS-TB)', FR: 'TB sensible aux médicaments (DS-TB)', SW: 'TB yumva imiti (DS-TB)', RW: 'TB yumva imiti (DS-TB)' },
  notProvided: { EN: 'Not provided', FR: 'Non fourni', SW: 'Nta byatanzwe', RW: 'Nta byatanzwe' },
  observationFurtherTesting: {
    EN: 'OBSERVATION AND FURTHER TESTING',
    FR: 'OBSERVATION ET EXAMENS COMPLÉMENTAIRES',
    SW: 'GUKURIKIRANA NO GUKORA IBINDI BIZAMINI',
    RW: 'GUKURIKIRANA NO GUKORA IBINDI BIZAMINI'
  },
  moderateLabel: { EN: 'MODERATE', FR: 'MODÉRÉ', SW: 'HAGATI', RW: 'BIRINGANIYE' },
  noEvidenceOfTb: { EN: 'NO EVIDENCE OF TB', FR: 'AUCUNE PREUVE DE TB', SW: 'NTA BIMENYETSO BYA TB', RW: 'NTA BIMENYETSO BYA TB' },
  durationNa: { EN: 'N/A', FR: 'N/A', SW: 'Nta gihe cyagenwe', RW: 'Nta gihe cyagenwe' },
  noAntiTbTreatmentHighSuspicion: {
    EN: 'No anti-TB treatment unless clinical suspicion remains high',
    FR: "Pas de traitement anti-TB sauf si la suspicion clinique reste élevée",
    SW: 'Nta miti ya TB itangwa keretse ibimenyetso bikomeje gukekwa cyane',
    RW: 'Nta miti ya TB itangwa keretse gukeka indwara bikomeje kuba byinshi'
  },
  dosageNa: {
    EN: 'Intensive: N/A, Continuation: N/A',
    FR: 'Phase intensive : N/A, continuation : N/A',
    SW: 'Icyiciro cya mbere: nta cyagenwe, gukomeza: nta cyagenwe',
    RW: 'Icyiciro cya mbere: nta cyagenwe, gukomeza: nta cyagenwe'
  },
  administrationNa: {
    EN: 'Intensive phase: N/A; continuation phase: N/A; daily DOTS/supervised dosing where feasible.',
    FR: 'Phase intensive : N/A ; phase de continuation : N/A ; DOTS/itangwa rikurikiranwa buri munsi igihe bishoboka.',
    SW: 'Icyiciro cya mbere: nta cyagenwe; gukomeza: nta cyagenwe; DOTS/itangwa rikurikiranwa buri munsi aho bishoboka.',
    RW: 'Icyiciro cya mbere: nta cyagenwe; gukomeza: nta cyagenwe; DOTS/itangwa rikurikiranwa buri munsi aho bishoboka.'
  },
  monitorSymptomsAlternativeDx: {
    EN: 'Monitor symptoms, consider other diagnoses',
    FR: 'Surveiller les symptômes, envisager d’autres diagnostics',
    SW: 'Komeza gukurikirana ibimenyetso no gusuzuma izindi ndwara',
    RW: 'Komeza gukurikirana ibimenyetso no gusuzuma izindi ndwara'
  },
  monitorCloselyRepeatTests: {
    EN: 'Monitor closely, repeat tests as indicated, evaluate for alternative diagnoses',
    FR: 'Surveiller étroitement, répéter les tests si nécessaire et rechercher d’autres diagnostics',
    SW: 'Komeza gukurikiranwa neza, usubiremo ibizamini igihe bikenewe, kandi usuzume izindi ndwara',
    RW: 'Komeza gukurikiranwa neza, usubiremo ibizamini igihe bikenewe, kandi usuzume izindi ndwara'
  },
  whoRecommendationStartTreatment: {
    EN: 'Initiate treatment promptly according to national guidelines; ensure airborne precautions',
    FR: 'Commencer rapidement le traitement selon les directives nationales; assurer les précautions aériennes',
    SW: 'Anza matibabu haraka kulingana na miongozo ya taifa; hakikisha tahadhari za hewani',
    RW: "Tangira ubuvuzi vuba ukurikije amabwiriza y’igihugu; hubahirizwe kwirinda ubwandu bwo mu mwuka"
  },
  dstFullySusceptible: {
    EN: 'Fully susceptible first-line profile',
    FR: 'Profil complètement sensible de première ligne',
    SW: 'Muundo wa mazingira yote ya kwanza yenye uwezo wa kukabiliwa na dawa',
    RW: 'Incamake y’umurongo wa mbere yumva imiti yose'
  },
  dstRifampicinResistance: {
    EN: 'Rifampicin resistance detected',
    FR: 'Résistance à la rifampicine détectée',
    SW: 'Usugu wa rifampicin umeonekana',
    RW: 'Resistance ya rifampicin yagaragaye'
  },
  dstPyrazinamideSuspected: {
    EN: 'Pyrazinamide resistance suspected',
    FR: 'Résistance à la pyrazinamide suspectée',
    SW: 'Usugu wa pyrazinamide unashukiwa',
    RW: 'Resistance ya pyrazinamide inekewa'
  },
  dstIsoniazidResistance: {
    EN: 'Isoniazid resistance detected',
    FR: 'Résistance à l’isoniazide détectée',
    SW: 'Usugu wa isoniazid umeonekana',
    RW: 'Resistance ya isoniazid yagaragaye'
  },
  dstMdrConfirmed: {
    EN: 'MDR profile confirmed by DST',
    FR: 'Profil MDR confirmé par DST',
    SW: 'Muundo wa MDR umethibitishwa na DST',
    RW: 'Incamake ya MDR yemejwe na DST'
  },
  dstXdrSuspected: {
    EN: 'XDR profile suspected',
    FR: 'Profil XDR suspecté',
    SW: 'Muundo wa XDR unashukiwa',
    RW: 'Incamake ya XDR inekewa'
  },
  tbCultureLabel: { EN: 'TB culture', FR: 'Culture TB', SW: 'Culture ya TB', RW: 'Culture ya TB' },
  tstShortLabel: { EN: 'TST', FR: 'TST', SW: 'TST', RW: 'TST' },
  igraShortLabel: { EN: 'IGRA', FR: 'IGRA', SW: 'IGRA', RW: 'IGRA' },
  reportItemDst: {
    EN: 'DST / resistance interpretation',
    FR: 'Interprétation DST / résistance',
    SW: 'Tafsiri ya DST / usugu',
    RW: 'Gusobanura DST / resistance'
  },
  reportItemTreatment: { EN: 'Treatment plan and monitoring guidance', FR: 'Plan de traitement et suivi', SW: 'Mpango wa matibabu na ufuatiliaji', RW: 'Gahunda y’ubuvuzi n’uko gukurikirana' },
  miniStep1: { EN: 'Step 1', FR: 'Étape 1', SW: 'Hatua 1', RW: 'Intambwe 1' },
  miniStep2: { EN: 'Step 2', FR: 'Étape 2', SW: 'Hatua 2', RW: 'Intambwe 2' },
  symptomsPlaceholder: {
    EN: 'Describe symptoms or keep the stored patient text as it is',
    FR: 'Décrivez les symptômes ou gardez le texte existant',
    SW: 'Eleza dalili au acha maandishi yaliyopo',
    RW: 'Sobanura ibimenyetso cyangwa ugumane ibyari bihari'
  },
  reportPlaceholder: {
    EN: 'The report will appear here after you complete the guided form and click `Analyze & Diagnose`.',
    FR: "Le rapport apparaîtra ici après avoir complété le formulaire et cliqué sur `Analyser & Diagnostiquer`.",
    SW: 'Ripoti itaonekana hapa baada ya kukamilisha fomu na kubofya `Chambua & Gundiua`.',
    RW: 'Raporo izagaragara hano umaze kuzuza form hanyuma ugakanda `Sesengura & Sobanura`.'
  },
  disclaimer: {
    EN: 'Disclaimer: This system is for educational purposes only. Always consult qualified medical professionals.',
    FR: 'Avertissement : ce système est destiné à des fins éducatives uniquement. Consultez toujours des professionnels de santé qualifiés.',
    SW: 'Kanusho: Mfumo huu ni kwa madhumuni ya elimu tu. Daima wasiliana na wataalamu wa afya wenye sifa.',
    RW: 'Iburira: Iyi sisitemu igenewe kwigisha gusa. Buri gihe baza abajyanama b’ubuzima babifitiye ubumenyi.'
  },
  refresh: { EN: 'Refresh', FR: 'Actualiser', SW: 'Onyesha upya', RW: 'Ongera urekane' },
  previous: { EN: 'Previous', FR: 'Précédent', SW: 'Iliyopita', RW: 'Ibanziriza' },
  next: { EN: 'Next', FR: 'Suivant', SW: 'Inayofuata', RW: 'Ikurikira' },
  showingRecords: {
    EN: 'Showing {start}-{end} of {total} records',
    FR: 'Affichage {start}-{end} sur {total} dossiers',
    SW: 'Inaonyesha {start}-{end} kati ya rekodi {total}',
    RW: 'Kwerekana {start}-{end} kuri {total} records'
  },
  pageOf: {
    EN: 'Page {page} of {pages}',
    FR: 'Page {page} sur {pages}',
    SW: 'Ukurasa {page} kati ya {pages}',
    RW: 'Urupapuro {page} kuri {pages}'
  },
  searchPatients: { EN: 'Search patients...', FR: 'Rechercher patients...', SW: 'Tafuta wagonjwa...', RW: 'Shakisha abarwayi...' },
  sortDbOrder: { EN: 'DB order', FR: 'Ordre DB', SW: 'Mpangilio DB', RW: 'Uko DB itondetse' },
  sortNewestId: { EN: 'Newest ID', FR: 'ID le plus récent', SW: 'ID mpya', RW: 'ID nshya' },
  sortNewestCreated: { EN: 'Newest created', FR: 'Créés récemment', SW: 'Zilizoundwa karibuni', RW: 'Zashizweho vuba' },
  sortOldestCreated: { EN: 'Oldest created', FR: 'Plus anciens', SW: 'Za zamani', RW: 'Zishaje' },
  colId: { EN: 'ID', FR: 'ID', SW: 'ID', RW: 'ID' },
  colName: { EN: 'Name', FR: 'Nom', SW: 'Jina', RW: 'Amazina' },
  colAge: { EN: 'Age', FR: 'Âge', SW: 'Umri', RW: 'Imyaka' },
  colGender: { EN: 'Gender', FR: 'Sexe', SW: 'Jinsia', RW: 'Igitsina' },
  colCity: { EN: 'City', FR: 'Ville', SW: 'Mji', RW: 'Umujyi' },
  colCreated: { EN: 'Created', FR: 'Créé', SW: 'Imeundwa', RW: 'Yakozwe' },
  noPatientsFound: {
    EN: 'No patients found. Add a patient through the diagnosis page.',
    FR: "Aucun patient trouvé. Ajoutez un patient via la page de diagnostic.",
    SW: 'Hakuna wagonjwa waliopatikana. Ongeza mgonjwa kupitia ukurasa wa uchunguzi.',
    RW: "Nta barwayi babonetse. Ongeraho umurwayi unyuze ku rupapuro rw'isuzuma."
  },
  noAlerts: { EN: 'No alerts.', FR: 'Aucune alerte.', SW: 'Hakuna tahadhari.', RW: 'Nta matangazo.' },
  whatNew: {
    EN: 'New: start a TB case.',
    FR: 'Nouveau : démarrer un dossier TB.',
    SW: 'Mpya: anza kesi ya TB.',
    RW: 'Mushya: tangira dosiye ya TB.'
  },
  whatExisting: {
    EN: 'Existing: reopen a saved record.',
    FR: 'Existant : rouvrir un dossier enregistré.',
    SW: 'Aliyepo: fungua rekodi iliyohifadhiwa.',
    RW: 'Usanzwe: fungura dosiye yabitswe.'
  },
  whatReport: {
    EN: 'Report: review guidance.',
    FR: 'Rapport : revoir les conseils.',
    SW: 'Ripoti: kagua mwongozo.',
    RW: 'Raporo: subiramo ubuyobozi.'
  },
  afterSignIn: { EN: 'After sign-in', FR: 'Après connexion', SW: 'Baada ya kuingia', RW: 'Nyuma yo kwinjira' },
  afterDiagnose: {
    EN: '`Diagnose` update evidence.',
    FR: '`Diagnostic` mettre à jour les preuves.',
    SW: '`Uchunguzi` sasisha ushahidi.',
    RW: '`Isuzuma` vugurura ibimenyetso.'
  },
  afterPatients: {
    EN: '`Patients` open records.',
    FR: '`Patients` ouvrir les dossiers.',
    SW: '`Wagonjwa` fungua rekodi.',
    RW: '`Abarwayi` fungura dosiye.'
  },
  afterAlerts: {
    EN: '`Alerts` review notices.',
    FR: '`Alertes` consulter les notifications.',
    SW: '`Tahadhari` kagua taarifa.',
    RW: '`Amatangazo` reba amatangazo.'
  },
  protectedWorkspace: { EN: 'Protected workspace', FR: 'Espace protégé', SW: 'Sehemu iliyolindwa', RW: 'Ahakingiwe' },
  welcomeBack: { EN: 'Welcome back', FR: 'Bon retour', SW: 'Karibu tena', RW: 'Murakaza neza' },
  continueToTabs: {
    EN: 'Continue to diagnosis, patients, and alerts.',
    FR: 'Continuez vers diagnostic, patients et alertes.',
    SW: 'Endelea kwenye uchunguzi, wagonjwa, na tahadhari.',
    RW: 'Komeza ku isuzuma, abarwayi, n’amatangazo.'
  },
  reviewCases: { EN: 'Review cases.', FR: 'Revoir les dossiers.', SW: 'Kagua kesi.', RW: 'Subiramo dosiye.' },
  openRecords: { EN: 'Open records.', FR: 'Ouvrir les dossiers.', SW: 'Fungua rekodi.', RW: 'Fungura dosiye.' },
  seeNotices: { EN: 'See notices.', FR: 'Voir notifications.', SW: 'Angalia taarifa.', RW: 'Reba amatangazo.' },
  enterContinueEvidence: {
    EN: 'Enter or continue evidence.',
    FR: 'Saisir ou continuer les éléments.',
    SW: 'Ingiza au endelea na ushahidi.',
    RW: 'Injiza cyangwa ukomeze ibimenyetso.'
  },
  openSavedRecords: {
    EN: 'Open saved records.',
    FR: 'Ouvrir les dossiers enregistrés.',
    SW: 'Fungua rekodi zilizohifadhiwa.',
    RW: 'Fungura dosiye zabitswe.'
  },
  reviewNotices: {
    EN: 'Review follow-up notices.',
    FR: 'Consulter les notifications de suivi.',
    SW: 'Kagua tahadhari za ufuatiliaji.',
    RW: 'Reba amatangazo yo gukurikirana.'
  },
  protected: { EN: 'Protected', FR: 'Protégé', SW: 'Imelindwa', RW: 'Birinzwe' },
  clinicianAdminOnly: {
    EN: 'Clinician and admin access only.',
    FR: 'Accès réservé aux cliniciens et admins.',
    SW: 'Ni kwa daktari na msimamizi tu.',
    RW: 'Ni abaganga n’abayobozi gusa bemerewe.'
  },
  guidedFlowHeadline: {
    EN: 'Complete the case in small steps, not one long form.',
    FR: 'Complétez le dossier par petites étapes, pas un long formulaire.',
    SW: 'Kamilisha kesi kwa hatua ndogo, si fomu ndefu.',
    RW: 'Uzuza dosiye mu byiciro bito, si form ndende.'
  },
  guidedFlowBody: {
    EN: 'Move step by step through identity, clinical clues, tests, and DST before generating the report.',
    FR: "Avancez étape par étape : identité, indices cliniques, tests et DST avant le rapport.",
    SW: 'Nenda hatua kwa hatua: utambulisho, dalili, vipimo, na DST kabla ya ripoti.',
    RW: "Genda intambwe ku yindi: amakuru y’umurwayi, ibimenyetso, ibizamini, na DST mbere ya raporo."
  },
  flowEntryTitle: { EN: 'Entry', FR: 'Saisie', SW: 'Kuingiza', RW: 'Kwinjiza' },
  flowEntryBody: {
    EN: 'Use guided TB suggestions or type your own evidence.',
    FR: 'Utilisez les suggestions TB ou saisissez vos propres éléments.',
    SW: 'Tumia mapendekezo ya TB au andika ushahidi wako.',
    RW: 'Koresha ibitekerezo bya TB cyangwa wandike ibimenyetso byawe.'
  },
  flowOrderTitle: { EN: 'Order', FR: 'Ordre', SW: 'Mpangilio', RW: 'Uko bikurikirana' },
  flowOrderBody: {
    EN: 'Keep the same clinician workflow for new and existing patients.',
    FR: 'Gardez le même flux pour nouveaux et anciens patients.',
    SW: 'Tumia mtiririko ule ule kwa wagonjwa wapya na waliopo.',
    RW: 'Komeza uko abaganga bakora ku murwayi mushya cyangwa usanzwe.'
  },
  flowOutputTitle: { EN: 'Output', FR: 'Résultat', SW: 'Matokeo', RW: 'Ibisohoka' },
  flowOutputBody: {
    EN: 'Generate TB type, DST review, and treatment guidance at the end.',
    FR: 'Générez type TB, revue DST et recommandations de traitement à la fin.',
    SW: 'Toa aina ya TB, uchambuzi wa DST, na mwongozo wa matibabu mwishoni.',
    RW: 'Sohora ubwoko bwa TB, isesengura rya DST, n’inama z’ubuvuzi ku musozo.'
  },
  patientInfoTitle: { EN: 'Patient information', FR: 'Informations patient', SW: 'Taarifa za mgonjwa', RW: "Amakuru y'umurwayi" },
  patientInfoSubtitle: {
    EN: 'Structured evidence entry for TB screening, species estimation, DST review, and treatment planning.',
    FR: 'Saisie structurée pour dépistage TB, estimation espèce, DST et plan de traitement.',
    SW: 'Uingizaji wa ushahidi kwa uchunguzi wa TB, kukadiria aina, DST na kupanga matibabu.',
    RW: 'Kwinjiza ibimenyetso bifasha gusuzuma TB, kugereranya ubwoko, DST no gutegura ubuvuzi.'
  },
  suggestedItemsHint: {
    EN: 'Suggested items are TB-focused. Custom typing is always allowed.',
    FR: 'Les suggestions sont centrées TB. La saisie libre est toujours possible.',
    SW: 'Mapendekezo yamelenga TB. Unaweza kuandika mwenyewe muda wote.',
    RW: 'Ibitekerezo biba byibanda kuri TB. Ushobora no kwandika ibyawe igihe cyose.'
  },
  stepHint: {
    EN: 'You can move between steps without losing typed content.',
    FR: 'Vous pouvez changer d’étape sans perdre le contenu saisi.',
    SW: 'Unaweza kubadilisha hatua bila kupoteza ulichoandika.',
    RW: 'Ushobora guhindura ibyiciro utatakaje ibyo wanditse.'
  },
  previousStep: { EN: 'Previous step', FR: 'Étape précédente', SW: 'Hatua iliyopita', RW: 'Intambwe ibanza' },
  nextStep: { EN: 'Next step', FR: 'Étape suivante', SW: 'Hatua inayofuata', RW: 'Intambwe ikurikira' },
  analyzing: { EN: 'Analyzing...', FR: 'Analyse...', SW: 'Inachambua...', RW: 'Birimo gusesengura...' },
  analyzeDiagnose: { EN: 'Analyze & Diagnose', FR: 'Analyser & Diagnostiquer', SW: 'Chambua & Gundiua', RW: 'Sesengura & Sobanura' },
  diagnosticReport: { EN: 'Diagnostic report', FR: 'Rapport de diagnostic', SW: 'Ripoti ya uchunguzi', RW: 'Raporo y’isuzuma' },
  idLabel: { EN: 'ID', FR: 'ID', SW: 'ID', RW: 'ID' },
  symptomAnalysis: { EN: 'Symptom analysis', FR: 'Analyse des symptômes', SW: 'Uchambuzi wa dalili', RW: 'Isesengura ry’ibimenyetso' },
  testEvaluation: { EN: 'Test evaluation', FR: 'Évaluation des tests', SW: 'Tathmini ya vipimo', RW: 'Isuzuma ry’ibizamini' },
  scoreLabel: { EN: 'Score', FR: 'Score', SW: 'Alama', RW: 'Amanota' },
  showThisSection: { EN: 'Open section', FR: 'Ouvrir section', SW: 'Fungua sehemu', RW: 'Fungura igice' },
  filterTitle: { EN: 'Show by section', FR: 'Afficher par section', SW: 'Onyesha kwa sehemu', RW: 'Erekana ukoresheje ibice' },
  filterSubtitle: {
    EN: 'Choose “Show all” or a single section to focus on.',
    FR: 'Choisissez “Tout afficher” ou une seule section.',
    SW: 'Chagua “Onyesha zote” au sehemu moja.',
    RW: 'Hitamo “Erekana byose” cyangwa igice kimwe.'
  },
  showAllSections: { EN: 'Show all', FR: 'Tout afficher', SW: 'Onyesha zote', RW: 'Erekana byose' },
  indexKicker: {
    EN: 'TB Diagnostic System',
    FR: 'Système de diagnostic TB',
    SW: 'Mfumo wa uchunguzi wa TB',
    RW: 'Sisitemu yo gusuzuma igituntu'
  },
  indexHeadline: {
    EN: 'Home page: TB confirmation features explained',
    FR: "Page d'accueil : explication des éléments pour confirmer la TB",
    SW: 'Ukurasa wa mwanzo: maelezo ya vipengele vya kuthibitisha TB',
    RW: "Urupapuro rubanza: ibisobanuro by'ibifasha kwemeza igituntu"
  },
  indexSubhead: {
    EN: 'This home page explains every field you will see during diagnosis (identity, symptoms, exposure, tests, DST) in simple language (RW/SW/FR/EN).',
    FR: "Cette page d'accueil explique tous les champs utilisés pendant le diagnostic (identité, symptômes, exposition, tests, DST) en langage simple (RW/SW/FR/EN).",
    SW: 'Ukurasa huu wa mwanzo unaeleza kila sehemu utakayoona wakati wa uchunguzi (utambulisho, dalili, historia ya kuambukizwa, vipimo, DST) kwa maneno rahisi (RW/SW/FR/EN).',
    RW: "Uru rupapuro rubanza rusobanura buri gice uzabona mu isuzuma (amakuru y’umurwayi, ibimenyetso, aho ashobora kwandurira, ibizamini, DST) mu magambo yoroshye (RW/SW/FR/EN)."
  },
  goToLogin: { EN: 'Go to Login', FR: 'Aller à la connexion', SW: 'Nenda kwenye kuingia', RW: 'Jya ku kwinjira' },
  fieldGuideTitle: {
    EN: 'Here is what each field means in your TB Diagnostic System',
    FR: 'Voici ce que signifie chaque champ dans votre système de diagnostic de la TB',
    SW: 'Hivi ndivyo kila sehemu inamaanisha kwenye mfumo wako wa uchunguzi wa TB',
    RW: "Dore ibisobanuro bya buri gice muri sisitemu yawe yo gusuzuma igituntu"
  },
  fieldGuideSubtitle: {
    EN: 'Simple explanation (for clinicians and non-clinicians) + why the information matters for confirming TB and choosing treatment.',
    FR: "Explication simple (pour cliniciens et non-cliniciens) + pourquoi l'information est importante pour confirmer la TB et choisir le traitement.",
    SW: 'Maelezo rahisi (kwa wataalamu na wasio wataalamu) + kwa nini taarifa ni muhimu kuthibitisha TB na kuchagua matibabu.',
    RW: "Ibisobanuro byoroshye (abaforomo/abaganga n'abandi) + impamvu ibi bisabwa mu kwemeza igituntu no guhitamo imiti."
  },
  showDetails: { EN: 'Show details', FR: 'Voir détails', SW: 'Onyesha maelezo', RW: 'Erekana ibisobanuro' },
  hideDetails: { EN: 'Hide details', FR: 'Masquer', SW: 'Ficha', RW: 'Hisha' },
  aiUseTitle: {
    EN: 'How your AI model could use these fields',
    FR: "Comment le modèle IA peut utiliser ces champs",
    SW: 'Jinsi modeli ya AI inaweza kutumia hizi sehemu',
    RW: "Uko AI yakoresha ibi bice"
  },
  additionalDataTitle: {
    EN: 'Optional extra data (not all are in the form yet)',
    FR: "Données supplémentaires (pas toutes dans le formulaire pour l'instant)",
    SW: 'Taarifa za ziada (sio zote zipo kwenye fomu kwa sasa)',
    RW: "Amakuru y’inyongera (si yose ari kuri form ubu)"
  },
  additionalDataSubtitle: {
    EN: 'These can improve accuracy and clinical context, especially when lab results are missing or unclear.',
    FR: "Ces informations améliorent la précision et le contexte clinique, surtout quand les résultats de labo manquent ou sont peu clairs.",
    SW: 'Husaidia kuongeza usahihi na muktadha wa kitabibu, hasa vipimo vya maabara vinapokosekana au kuwa na mashaka.',
    RW: "Bifasha kongera ukuri n’isobanurampamvu, cyane iyo ibisubizo bya labo bibuze cyangwa bitumvikana."
  },
  additionalDataList: {
    EN: [
      'Age',
      'Sex',
      'Weight',
      'Persistent cough duration',
      'Fever',
      'Night sweats',
      'Weight loss',
      'Chest pain',
      'Shortness of breath',
      'Contact with TB patient',
      'Previous TB treatment',
      'Smoking history',
      'Alcohol use',
      'Oxygen saturation (SpO₂)'
    ],
    FR: [
      'Âge',
      'Sexe',
      'Poids',
      'Durée de la toux persistante',
      'Fièvre',
      'Sueurs nocturnes',
      'Perte de poids',
      'Douleur thoracique',
      'Essoufflement',
      'Contact avec un patient TB',
      'Traitement TB antérieur',
      'Tabagisme',
      "Consommation d'alcool",
      'Saturation en oxygène (SpO₂)'
    ],
    SW: [
      'Umri',
      'Jinsia',
      'Uzito',
      'Muda wa kikohozi kinachoendelea',
      'Homa',
      'Kutokwa jasho usiku',
      'Kupungua uzito',
      'Maumivu ya kifua',
      'Upungufu wa pumzi',
      'Kuwasiliana na mgonjwa wa TB',
      'Tiba ya TB hapo awali',
      'Historia ya uvutaji sigara',
      'Matumizi ya pombe',
      'Kiwango cha oksijeni (SpO₂)'
    ],
    RW: [
      'Imyaka',
      'Igitsina',
      'Ibiro',
      "Igihe inkorora imaze (nk'ibyumweru 2+)",
      'Umuriro',
      "Kubira icyuya nijoro",
      "Kugabanuka kw'ibiro",
      "Kubabara mu gatuza",
      "Kubura umwuka",
      "Kuba warahuye n'ufite igituntu",
      "Kuba warigeze kuvurwa igituntu",
      "Kunywa itabi (history)",
      "Kunywa inzoga (history)",
      'Oksijeni mu maraso (SpO₂)'
    ]
  }
}

const uiLanguage = ref('EN')
const languageMenuOpen = ref(false)
const fieldGuideOpen = ref(true)
const publicView = ref('index')
const indexSelectedSection = ref('all')

const selectedLanguageOption = computed(() => {
  return languageOptions.find(option => option.code === uiLanguage.value) || languageOptions[0]
})

function t(valueByLanguage) {
  if (Array.isArray(valueByLanguage)) return valueByLanguage
  if (!valueByLanguage || typeof valueByLanguage !== 'object') return String(valueByLanguage || '')
  return valueByLanguage[uiLanguage.value] ?? valueByLanguage.EN ?? ''
}

useHead(() => ({
  title: t(TEXT.indexKicker)
}))

function tf(valueByLanguage, vars = {}) {
  const template = t(valueByLanguage)
  return template.replace(/\{(\w+)\}/g, (_, key) => String(vars[key] ?? ''))
}

function setLanguage(code) {
  uiLanguage.value = code
  languageMenuOpen.value = false
}

const FIELD_LABELS = {
  bacteria_species: {
    EN: 'TB Bacteria Species',
    FR: 'Espèce de bactérie TB',
    SW: 'Aina ya bakteria wa TB',
    RW: "Ubwoko bw'udukoko dutera igituntu"
  },
  tb_culture: {
    EN: 'TB Culture',
    FR: 'Culture TB',
    SW: 'Utamaduni wa TB (Culture)',
    RW: 'Culture ya TB (gukura udukoko muri labo)'
  },
  sputum_smear_test: {
    EN: 'Sputum Smear',
    FR: "Frottis d'expectoration",
    SW: 'Sputum Smear',
    RW: "Sputum Smear (Isuzuma ry'igikororwa)"
  },
  genexpert_test: {
    EN: 'GeneXpert',
    FR: 'GeneXpert',
    SW: 'GeneXpert',
    RW: 'GeneXpert'
  },
  chest_xray: {
    EN: 'Chest X-ray',
    FR: 'Radiographie thoracique',
    SW: 'X-ray ya kifua',
    RW: "Ifoto ya X-ray y'igituza"
  },
  drug_resistance: {
    EN: 'Drug Resistance',
    FR: 'Résistance aux médicaments',
    SW: 'Ustahimilivu wa dawa',
    RW: "Kudakurikiza/kurwanya imiti (Resistance)"
  },
  tst: {
    EN: 'TST (Tuberculin Skin Test)',
    FR: 'TST (Test cutané à la tuberculine)',
    SW: 'TST (Kipimo cha ngozi)',
    RW: "TST (Ikizamini cyo ku ruhu)"
  },
  igra: {
    EN: 'IGRA (Blood test)',
    FR: 'IGRA (Test sanguin)',
    SW: 'IGRA (Kipimo cha damu)',
    RW: "IGRA (Ikizamini cy'amaraso)"
  },
  hiv: {
    EN: 'HIV Status',
    FR: 'Statut VIH',
    SW: 'Hali ya VVU (HIV)',
    RW: 'HIV Status (Uburwayi bwa SIDA/VIH)'
  },
  diabetes: {
    EN: 'Diabetes',
    FR: 'Diabète',
    SW: 'Kisukari (Diabetes)',
    RW: 'Diyabete (Indwara ya sukari)'
  }
}

const FIELD_HELP = {
  bacteria_species: {
    EN: 'The type of TB-causing bacteria. Choose Auto-detect to let the system estimate based on the full patient record.',
    FR: "Le type de bactérie responsable de la TB. Choisissez Auto-detect pour laisser le système estimer à partir du dossier du patient.",
    SW: 'Aina ya bakteria wanaosababisha TB. Chagua Auto-detect ili mfumo ukadirie kulingana na taarifa zote za mgonjwa.',
    RW: "Ubwoko bw'udukoko dutera igituntu. Hitamo Auto-detect kugirango sisitemu ibigereranye ikoresheje amakuru yose y'umurwayi."
  },
  tb_culture: {
    EN: 'A lab test where a sample is grown to detect TB bacteria. One of the most reliable confirmations.',
    FR: "Test de laboratoire où l'échantillon est cultivé pour détecter la bactérie. Très fiable pour confirmer la TB.",
    SW: 'Kipimo cha maabara ambacho sampuli hukuzwa ili kuonekana bakteria wa TB. Ni kipimo cha kuaminika sana kuthibitisha TB.',
    RW: "Ikizamini cya labo aho bafata sample bakayikuzamo udukoko (culture) kugira ngo barebe TB. Ni kimwe mu bipimo byizewe cyane mu kwemeza igituntu."
  },
  sputum_smear_test: {
    EN: 'Microscope check of coughed-up mucus (sputum) to see TB bacteria. Simple question: “TB bacteria found in coughed-up mucus?” Fast and cheap, but less sensitive than GeneXpert.',
    FR: "Examen au microscope des crachats (sputum) pour voir les bacilles TB. Question simple : « Bacilles TB trouvés dans les crachats ? » Rapide et peu coûteux, mais moins sensible que GeneXpert.",
    SW: 'Uchunguzi wa makohozi (sputum) kwa darubini kuona bakteria wa TB. Swali rahisi: “Je, bakteria wa TB wamepatikana kwenye makohozi?” Ni wa haraka na nafuu, lakini si nyeti kama GeneXpert.',
    RW: "Gusuzuma igikororwa (ibikororwa umuntu akorora bivuye mu bihaha) harebwa niba harimo udukoko dutera igituntu. Ikibazo cyoroshye: “Ese mu gikororwa habonetse udukoko dutera igituntu?” Birihuta kandi birahendutse, ariko ntibibona neza nka GeneXpert."
  },
  genexpert_test: {
    EN: 'A molecular test that detects TB DNA and some drug resistance. WHO-recommended rapid TB test.',
    FR: "Test moléculaire qui détecte l'ADN de la TB et certaines résistances. Test rapide recommandé par l’OMS.",
    SW: 'Kipimo cha kijenetiki (molecular) kinachotambua DNA ya TB na baadhi ya usugu wa dawa. Kinapendekezwa na WHO kwa uchunguzi wa haraka.',
    RW: "Ikizamini cya molecular gimenya DNA ya TB kandi kigatanga n'ibimenyetso bimwe by'ukudakurikiza imiti. WHO igisaba nk'ikizamini cyihuse."
  },
  chest_xray: {
    EN: 'Imaging to check lung changes that may suggest TB (infiltrates, cavities, nodules, pleural effusion).',
    FR: "Imagerie pour détecter des anomalies pulmonaires pouvant suggérer la TB (infiltrats, cavernes, nodules, épanchement pleural).",
    SW: 'Picha ya mapafu ku X-ray kuona mabadiliko yanayoweza kuashiria TB (infiltrates, mashimo/cavities, nodules, maji kwenye kifua).',
    RW: "Ifoto ya X-ray ireba impinduka mu bihaha zishobora kugaragaza TB (infiltrates, cavities, nodules, amazi mu gatuza)."
  },
  drug_resistance: {
    EN: 'Shows if TB may be resistant to standard medicines (e.g., MDR-TB, XDR-TB). This changes the treatment regimen.',
    FR: "Indique si la TB peut résister aux médicaments standards (ex. MDR-TB, XDR-TB). Cela change le schéma thérapeutique.",
    SW: 'Inaonyesha kama TB inaweza kuwa sugu kwa dawa za kawaida (mf. MDR-TB, XDR-TB). Hii hubadilisha mpango wa matibabu.',
    RW: "Kwerekana niba TB ishobora kurwanya imiti isanzwe (nka MDR-TB, XDR-TB). Ibi bihindura gahunda yo kuvura."
  },
  tst: {
    EN: 'Skin test to detect TB infection (exposure). It cannot separate active TB from latent TB.',
    FR: "Test cutané pour détecter l’infection TB (exposition). Ne distingue pas TB active et TB latente.",
    SW: 'Kipimo cha ngozi kuonyesha maambukizi/kuwahi kuathiriwa na TB. Hakitofautishi TB iliyo hai na TB iliyolala (latent).',
    RW: "Ikizamini cyo ku ruhu kigaragaza kuba umuntu yarahuye na TB. Ntigishobora gutandukanya TB ikora na TB yihishe (latent)."
  },
  igra: {
    EN: 'Blood test to detect TB infection (e.g., QuantiFERON-TB Gold, T‑SPOT.TB). Often more specific than TST.',
    FR: "Test sanguin pour détecter l’infection TB (ex. QuantiFERON-TB Gold, T‑SPOT.TB). Souvent plus spécifique que le TST.",
    SW: 'Kipimo cha damu kugundua maambukizi ya TB (mf. QuantiFERON-TB Gold, T‑SPOT.TB). Mara nyingi ni sahihi zaidi kuliko TST.',
    RW: "Ikizamini cy'amaraso gishaka infection ya TB (nka QuantiFERON-TB Gold, T‑SPOT.TB). Akenshi kiba gifite ukwizerwa kurusha TST."
  },
  hiv: {
    EN: 'HIV greatly increases the risk of developing active TB and can change urgency and treatment monitoring.',
    FR: "Le VIH augmente fortement le risque de TB active et peut changer l’urgence et la surveillance du traitement.",
    SW: 'VVU (HIV) huongeza sana hatari ya kupata TB iliyo hai na inaweza kubadilisha uharaka na ufuatiliaji wa matibabu.',
    RW: "HIV yongera cyane ibyago byo kugira TB ikora kandi ishobora guhindura uko kwihutira kuvura no gukurikirana umurwayi."
  },
  diabetes: {
    EN: 'Diabetes increases susceptibility to TB and can affect treatment outcomes.',
    FR: "Le diabète augmente la susceptibilité à la TB et peut affecter les résultats du traitement.",
    SW: 'Kisukari huongeza uwezekano wa kupata TB na kinaweza kuathiri matokeo ya matibabu.',
    RW: "Indwara ya sukari yongera ibyago byo kugira TB kandi ishobora kugira ingaruka ku musaruro w'ubuvuzi."
  }
}

const indexSectionCards = [
  {
    id: 'identity',
    kicker: { EN: 'Section 1', FR: 'Section 1', SW: 'Sehemu 1', RW: 'Igice 1' },
    title: { EN: 'Patient identity', FR: 'Identité du patient', SW: 'Utambulisho', RW: "Amakuru y'umurwayi" },
    body: {
      EN: 'Used to save/reopen records and avoid mixing patients.',
      FR: 'Sert à enregistrer/rouvrir le dossier et éviter les confusions.',
      SW: 'Hutumika kuhifadhi/kufungua rekodi na kuepuka kuchanganya wagonjwa.',
      RW: "Bifasha kubika no kongera gufungura dosiye y'umurwayi no kwirinda kuyivanga."
    }
  },
  {
    id: 'clues',
    kicker: { EN: 'Section 2', FR: 'Section 2', SW: 'Sehemu 2', RW: 'Igice 2' },
    title: { EN: 'Symptoms & exposure', FR: 'Symptômes & exposition', SW: 'Dalili & kuambukizwa', RW: 'Ibimenyetso & aho yandurira' },
    body: {
      EN: 'Shows risk and urgency even before lab tests.',
      FR: "Montre le risque et l'urgence même avant les tests.",
      SW: 'Huonyesha hatari na uharaka hata kabla ya vipimo.',
      RW: "Bigaragaza ibyago n'ukwihutira no mbere y'ibizamini."
    }
  },
  {
    id: 'tests',
    kicker: { EN: 'Section 3', FR: 'Section 3', SW: 'Sehemu 3', RW: 'Igice 3' },
    title: { EN: 'Tests & imaging', FR: 'Tests & imagerie', SW: 'Vipimo & picha', RW: 'Ibizamini & X-ray' },
    body: {
      EN: 'Culture, smear, GeneXpert, X‑ray help confirm TB.',
      FR: 'Culture, frottis, GeneXpert, radio aident à confirmer la TB.',
      SW: 'Culture, smear, GeneXpert, X‑ray husaidia kuthibitisha TB.',
      RW: "Culture, smear, GeneXpert, X‑ray bifasha kwemeza TB."
    }
  },
  {
    id: 'dst',
    kicker: { EN: 'Section 4', FR: 'Section 4', SW: 'Sehemu 4', RW: 'Igice 4' },
    title: { EN: 'DST & treatment support', FR: 'DST & traitement', SW: 'DST & matibabu', RW: 'DST & ubuvuzi' },
    body: {
      EN: 'Resistance and DST guide which medicines to use.',
      FR: 'La résistance et le DST guident le choix des médicaments.',
      SW: 'Usugu wa dawa na DST huongoza uchaguzi wa dawa.',
      RW: "Resistance na DST bifasha guhitamo imiti."
    }
  }
]

const baseIndexFieldGroups = [
  {
    id: 'identity',
    title: { EN: '1) Patient identity fields', FR: "1) Champs d'identité", SW: '1) Sehemu za utambulisho', RW: "1) Amakuru y'umurwayi" },
    description: {
      EN: 'These fields help uniquely identify the patient and manage follow-up.',
      FR: "Ces champs servent à identifier le patient et assurer le suivi.",
      SW: 'Sehemu hizi husaidia kumtambua mgonjwa na kufuatilia matokeo.',
      RW: "Ibi bifasha kumenya neza umurwayi no gukurikirana dosiye ye."
    },
    items: [
      {
        id: 'patient_id',
        title: { EN: 'Patient ID', FR: 'ID patient', SW: 'Namba ya mgonjwa', RW: "ID y'umurwayi" },
        lines: {
          EN: ['Unique number/code for the patient record.', 'Importance: helps reopen the correct record and avoid duplicates.'],
          FR: ['Numéro/code unique du dossier patient.', "Importance : permet de rouvrir le bon dossier et éviter les doublons."],
          SW: ['Namba/kanuni ya kipekee ya rekodi ya mgonjwa.', 'Umuhimu: husaidia kufungua rekodi sahihi na kuepuka kurudia.'],
          RW: ["Nimero/code yihariye ya dosiye y'umurwayi.", "Icy’ingenzi: bifasha gufungura dosiye nyayo no kwirinda kwandikisha kabiri."]
        }
      },
      {
        id: 'names',
        title: { EN: 'First name & Last name', FR: 'Prénom & Nom', SW: 'Jina la kwanza & la mwisho', RW: 'Izina & Irindi zina' },
        lines: {
          EN: ['The patient’s names used on the report and for searching.', 'Importance: reduces confusion between patients.'],
          FR: ["Noms du patient utilisés dans le rapport et la recherche.", 'Importance : réduit les confusions.'],
          SW: ['Majina ya mgonjwa hutumika kwenye ripoti na utafutaji.', 'Umuhimu: hupunguza kuchanganya wagonjwa.'],
          RW: ["Amazina y'umurwayi agaragara muri raporo no mu gushakisha.", "Icy’ingenzi: bifasha kwirinda kuyivanga n’abandi."]
        }
      },
      {
        id: 'age_gender',
        title: { EN: 'Age & Gender', FR: 'Âge & Sexe', SW: 'Umri & Jinsia', RW: 'Imyaka & Igitsina' },
        lines: {
          EN: ['Basic patient profile.', 'Importance: supports risk estimation and treatment considerations.'],
          FR: ['Profil de base du patient.', "Importance : aide à estimer le risque et orienter le traitement."],
          SW: ['Taarifa za msingi za mgonjwa.', 'Umuhimu: husaidia kukadiria hatari na kuchagua matibabu.'],
          RW: ["Amakuru y'ibanze y'umurwayi.", "Icy’ingenzi: bifasha kugereranya ibyago no guhitamo ubuvuzi."]
        }
      },
      {
        id: 'city',
        title: { EN: 'City', FR: 'Ville', SW: 'Mji', RW: 'Umujyi/Aho atuye' },
        lines: {
          EN: ['Where the patient lives or is seen.', 'Importance: helps follow-up and public health reporting.'],
          FR: ['Lieu de résidence ou de consultation.', "Importance : aide au suivi et au signalement de santé publique."],
          SW: ['Mahali mgonjwa anaishi au anapoonekana.', 'Umuhimu: husaidia ufuatiliaji na taarifa za afya ya umma.'],
          RW: ["Aho umurwayi atuye cyangwa aho yitabwaho.", "Icy’ingenzi: bifasha gukurikirana no gutanga amakuru ku rwego rw'ubuzima rusange."]
        }
      }
    ]
  },
  {
    id: 'clues',
    title: { EN: '2) Clinical clues (symptoms and exposure)', FR: "2) Indices cliniques (symptômes et exposition)", SW: '2) Dalili na kuambukizwa', RW: '2) Ibimenyetso n’aho yandurira' },
    description: {
      EN: 'These are often the first signs that raise TB suspicion, especially when tests are missing.',
      FR: "Souvent les premiers signes de suspicion de TB, surtout si les tests manquent.",
      SW: 'Mara nyingi ni ishara za mwanzo zinazozua shaka ya TB, hasa vipimo vikikosekana.',
      RW: "Akenshi ni byo bitangira gutera amakenga ya TB, cyane iyo ibizamini bibuze."
    },
    items: [
      {
        id: 'symptoms',
        title: { EN: 'Symptoms', FR: 'Symptômes', SW: 'Dalili', RW: 'Ibimenyetso' },
        lines: {
          EN: ['List symptoms (cough, fever, night sweats, weight loss, chest pain, etc.).', 'Importance: helps estimate TB risk and urgency.'],
          FR: ['Listez les symptômes (toux, fièvre, sueurs nocturnes, perte de poids, douleur thoracique, etc.).', "Importance : aide à estimer le risque et l'urgence."],
          SW: ['Orodhesha dalili (kikohozi, homa, jasho usiku, kupungua uzito, maumivu ya kifua, n.k.).', 'Umuhimu: husaidia kukadiria hatari na uharaka.'],
          RW: ["Andika ibimenyetso (inkorora, umuriro, kubira icyuya nijoro, kugabanuka ibiro, kubabara mu gatuza, n'ibindi).", "Icy’ingenzi: bifasha kugereranya ibyago n'ukwihutira kwitabwaho."]
        }
      },
      {
        id: 'exposure',
        title: { EN: 'Exposure history', FR: "Historique d'exposition", SW: 'Historia ya kuambukizwa', RW: "Amateka y'aho yandurira" },
        lines: {
          EN: ['Contact with a TB patient, crowded living, prison, healthcare work, animal/milk exposure, etc.', 'Importance: supports the suspicion and may hint at species source.'],
          FR: ["Contact TB, vie en promiscuité, prison, travail de santé, exposition animale/lait, etc.", "Importance : renforce la suspicion et peut orienter la source."],
          SW: ['Kuwasiliana na mgonjwa wa TB, makazi yenye msongamano, gereza, kazi ya afya, wanyama/maziwa, n.k.', 'Umuhimu: huongeza ushahidi wa shaka na inaweza kuonyesha chanzo.'],
          RW: ["Guhura n'ufite TB, kuba mu buzima bufite ubucucike, gereza, gukora mu buvuzi, amatungo/amata, n'ibindi.", "Icy’ingenzi: byongera ibimenyetso bya TB kandi bishobora no kwerekana aho byaturutse."]
        }
      }
    ]
  },
  {
    id: 'dst',
    title: { EN: '4) DST and resistance details', FR: '4) Détails DST et résistance', SW: '4) Maelezo ya DST na usugu', RW: '4) Ibisobanuro bya DST na resistance' },
    description: {
      EN: 'These fields help decide which drugs are likely to work.',
      FR: 'Ces champs aident à choisir les médicaments efficaces.',
      SW: 'Sehemu hizi husaidia kuchagua dawa zitakazofanya kazi.',
      RW: "Ibi bifasha guhitamo imiti ishobora gukora."
    },
    items: [
      {
        id: 'antibiogram',
        title: { EN: 'Antibiogram / DST summary', FR: 'Antibiogramme / Résumé DST', SW: 'Muhtasari wa DST', RW: 'Incamake ya DST' },
        lines: {
          EN: ['Write DST notes (lab summary) about resistance/susceptibility.', 'Importance: supports the treatment regimen decision.'],
          FR: ["Saisissez le résumé DST (labo) sur résistance/sensibilité.", "Importance : guide le schéma thérapeutique."],
          SW: ['Andika muhtasari wa DST (maabara) kuhusu usugu/ustahimilivu.', 'Umuhimu: husaidia kuchagua mpango wa matibabu.'],
          RW: ["Andika incamake ya DST (ibyo labo yavuze) ku kurwanya/kwumva imiti.", "Icy’ingenzi: bifasha guhitamo gahunda y'ubuvuzi."]
        }
      },
      {
        id: 'resistant_to',
        title: { EN: 'Resistant to', FR: 'Résistant à', SW: 'Inakataa dawa', RW: 'Irwanya iyi miti' },
        lines: {
          EN: ['List medicines that the TB bacteria resist.', 'Importance: avoid ineffective drugs.'],
          FR: ['Listez les médicaments auxquels la TB résiste.', "Importance : éviter les traitements inefficaces."],
          SW: ['Orodhesha dawa ambazo TB inazikataa (resistant).', 'Umuhimu: kuepuka dawa zisizofanya kazi.'],
          RW: ['Andika imiti TB irwanya (resistant).', "Icy’ingenzi: kwirinda imiti itazakora."]
        }
      },
      {
        id: 'susceptible_to',
        title: { EN: 'Susceptible to', FR: 'Sensible à', SW: 'Inakubali dawa', RW: 'Yumva iyi miti' },
        lines: {
          EN: ['List medicines that are likely effective against the TB bacteria.', 'Importance: helps select the safest effective regimen.'],
          FR: ["Listez les médicaments probablement efficaces.", "Importance : aide à choisir le traitement le plus sûr et efficace."],
          SW: ['Orodhesha dawa zinazoweza kufanya kazi dhidi ya TB.', 'Umuhimu: husaidia kuchagua mpango salama na wenye ufanisi.'],
          RW: ['Andika imiti ishobora gukora kuri TB (susceptible).', "Icy’ingenzi: bifasha guhitamo gahunda itekanye kandi ikora."]
        }
      }
    ]
  }
]

function fieldLabel(key) {
  return t(FIELD_LABELS[key] || { EN: key })
}

function fieldHelp(key) {
  return t(FIELD_HELP[key] || { EN: '' })
}

const fieldGuideItems = [
  {
    id: 'bacteria_species',
    title: FIELD_LABELS.bacteria_species,
    lines: {
      EN: [
        'The type of TB-causing bacteria identified in the patient.',
        'Auto-detect → System predicts the most likely species based on patient data.',
        'Mycobacterium tuberculosis → Most common cause of human TB.',
        'Mycobacterium bovis → Often from infected cattle or unpasteurized milk.',
        'Mycobacterium africanum → Common in some African regions.',
        'Mycobacterium canettii → Rare species found in limited areas.',
        'Mycobacterium microti → Rare, mainly infects animals but can infect humans.',
        'Importance: Helps interpret exposure sources and supports the overall diagnosis and treatment plan.'
      ],
      FR: [
        "Le type de bactérie responsable de la TB chez le patient.",
        "Auto-detect → Le système prédit l'espèce la plus probable selon les données.",
        'Mycobacterium tuberculosis → Cause la plus fréquente de TB humaine.',
        'Mycobacterium bovis → Souvent lié au bétail ou au lait non pasteurisé.',
        'Mycobacterium africanum → Fréquent dans certaines régions africaines.',
        'Mycobacterium canettii → Espèce rare dans des zones limitées.',
        "Mycobacterium microti → Rare, surtout chez l'animal mais possible chez l'humain.",
        "Importance : Aide à interpréter la source d'exposition et à soutenir le diagnostic et le plan thérapeutique."
      ],
      SW: [
        'Aina ya bakteria wanaosababisha TB iliyotambuliwa kwa mgonjwa.',
        'Auto-detect → Mfumo hukadiria aina inayowezekana zaidi kulingana na taarifa za mgonjwa.',
        'Mycobacterium tuberculosis → Sababu ya kawaida zaidi ya TB kwa binadamu.',
        'Mycobacterium bovis → Mara nyingi hutoka kwa ng’ombe walioambukizwa au maziwa yasiyochemshwa/pasteurized.',
        'Mycobacterium africanum → Huonekana zaidi katika baadhi ya maeneo ya Afrika.',
        'Mycobacterium canettii → Ni nadra na hupatikana maeneo machache.',
        'Mycobacterium microti → Ni nadra, huambukiza wanyama zaidi lakini inaweza kwa binadamu.',
        'Umuhimu: Husaidia kuelewa chanzo cha maambukizi na kuimarisha uamuzi wa uchunguzi na matibabu.'
      ],
      RW: [
        "Ubwoko bw'udukoko dutera igituntu bwagaragajwe ku murwayi.",
        'Auto-detect → Sisitemu igereranya ubwoko bushoboka kurusha ubundi ikoresheje amakuru y’umurwayi.',
        'Mycobacterium tuberculosis → Bikunze gutera igituntu ku bantu.',
        "Mycobacterium bovis → Ishobora kuzanwa n’amatungo (inka) cyangwa kunywa amata atapasteurizwemo.",
        'Mycobacterium africanum → Igaragara cyane mu bice bimwe by’Afurika.',
        'Mycobacterium canettii → Ni gake kandi iboneka ahantu hake.',
        'Mycobacterium microti → Ni gake, ikunze gufata inyamaswa ariko ishobora no gufata abantu.',
        "Icy’ingenzi: Bifasha gusobanukirwa aho kwandura bishobora kuba byaturutse, kandi bigafasha gufata umwanzuro w'isuzuma n'ubuvuzi."
      ]
    }
  },
  {
    id: 'tb_culture',
    title: FIELD_LABELS.tb_culture,
    lines: {
      EN: [
        'A laboratory test where a patient sample is grown to detect TB bacteria.',
        'Positive → TB bacteria grew in the laboratory.',
        'Negative → No TB bacteria detected.',
        'Unknown → Test not performed or result unavailable.',
        'Importance: Considered one of the most reliable methods for confirming TB.'
      ],
      FR: [
        "Test de laboratoire où l'échantillon du patient est cultivé pour détecter la TB.",
        'Positive → La bactérie TB a poussé au laboratoire.',
        'Negative → Aucune bactérie TB détectée.',
        'Unknown → Test non réalisé ou résultat indisponible.',
        'Importance : Une des méthodes les plus fiables pour confirmer la TB.'
      ],
      SW: [
        'Kipimo cha maabara ambacho sampuli ya mgonjwa hukuzwa ili kugundua bakteria wa TB.',
        'Positive → Bakteria wa TB wamekua maabarani.',
        'Negative → Hakuna bakteria wa TB waliogunduliwa.',
        'Unknown → Kipimo hakikufanyika au majibu hayapo.',
        'Umuhimu: Ni miongoni mwa vipimo vinavyoaminika zaidi kuthibitisha TB.'
      ],
      RW: [
        'Ikizamini cya labo aho sample y’umurwayi ikurizwa (culture) kugira ngo hamenyekane udukoko twa TB.',
        'Positive → Udukoko twa TB twakuze muri labo.',
        'Negative → Nta dukoko twa TB twabonetse.',
        'Unknown → Ikizamini nticyakozwe cyangwa ibisubizo ntibihari.',
        'Icy’ingenzi: Ni kimwe mu bizamini byizewe cyane mu kwemeza igituntu.'
      ]
    }
  },
  {
    id: 'sputum_smear_test',
    title: FIELD_LABELS.sputum_smear_test,
    lines: {
      EN: [
        'Microscopic examination of sputum (mucus coughed from the lungs).',
        'Simple wording: “TB bacteria found in coughed-up mucus?”',
        'Positive → TB bacteria seen under microscope.',
        'Negative → No bacteria seen.',
        'Unknown → No result available.',
        'Importance: Quick and inexpensive test but less sensitive than GeneXpert.'
      ],
      FR: [
        "Examen au microscope des crachats (mucus provenant des poumons).",
        'Formulation simple : « Bacilles TB trouvés dans les crachats ? »',
        'Positive → Bacilles TB visibles au microscope.',
        'Negative → Aucune bactérie vue.',
        'Unknown → Résultat non disponible.',
        'Importance : Rapide et peu coûteux, mais moins sensible que GeneXpert.'
      ],
      SW: [
        'Uchunguzi wa makohozi (kamasi kutoka mapafuni) kwa darubini.',
        'Maneno rahisi: “Je, bakteria wa TB wamepatikana kwenye makohozi?”',
        'Positive → Bakteria wa TB wanaonekana kwa darubini.',
        'Negative → Hakuna bakteria wanaoonekana.',
        'Unknown → Hakuna majibu.',
        'Umuhimu: Ni wa haraka na nafuu, lakini si nyeti kama GeneXpert.'
      ],
      RW: [
        "Gusuzuma igikororwa (ibikororwa umuntu akorora bivuye mu bihaha) harebwa uko biri ku mikorosikopi.",
        "Imvugo yoroshye: “Ese mu gikororwa habonetse udukoko dutera igituntu?”",
        "Positive → Mu gikororwa habonetse udukoko dutera igituntu.",
        "Negative → Nta dukoko twabonetse.",
        "Unknown → Nta gisubizo gihari.",
        "Icy’ingenzi: Birihuta kandi birahendutse, ariko ntibibona neza nka GeneXpert."
      ]
    }
  },
  {
    id: 'genexpert_test',
    title: FIELD_LABELS.genexpert_test,
    lines: {
      EN: [
        'A molecular test that detects TB DNA and some drug resistance.',
        'Positive → TB DNA detected.',
        'Negative → TB DNA not detected.',
        'Unknown → Test not done.',
        'Importance: Recommended by the World Health Organization as a rapid TB diagnostic test.'
      ],
      FR: [
        "Test moléculaire qui détecte l'ADN de la TB et certaines résistances.",
        'Positive → ADN TB détecté.',
        'Negative → ADN TB non détecté.',
        'Unknown → Test non réalisé.',
        "Importance : Recommandé par l'OMS comme test rapide de diagnostic de la TB."
      ],
      SW: [
        'Kipimo cha molecular kinachotambua DNA ya TB na baadhi ya usugu wa dawa.',
        'Positive → DNA ya TB imegunduliwa.',
        'Negative → DNA ya TB haijagunduliwa.',
        'Unknown → Kipimo hakikufanyika.',
        'Umuhimu: Kinapendekezwa na WHO kama kipimo cha haraka cha TB.'
      ],
      RW: [
        "Ikizamini cya molecular gimenya DNA ya TB kandi kigatanga n'ibimenyetso bimwe by'ukudakurikiza imiti.",
        'Positive → DNA ya TB yabonetse.',
        'Negative → DNA ya TB ntiyabonetse.',
        'Unknown → Ikizamini nticyakozwe.',
        "Icy’ingenzi: WHO igisaba nk'ikizamini cyihuse cyo gusuzuma TB."
      ]
    }
  },
  {
    id: 'chest_xray',
    title: FIELD_LABELS.chest_xray,
    lines: {
      EN: [
        'Imaging test used to identify lung abnormalities suggestive of TB.',
        'Normal → No signs of TB visible.',
        'Abnormal/Suggestive of TB → Findings may indicate TB.',
        'Unknown → No X-ray result available.',
        'Common TB X-ray findings: lung infiltrates, cavities, nodules, pleural effusion.'
      ],
      FR: [
        "Imagerie pour identifier des anomalies pulmonaires suggérant une TB.",
        'Normal → Aucun signe visible de TB.',
        'Abnormal/Suggestive of TB → Les images peuvent indiquer une TB.',
        'Unknown → Résultat non disponible.',
        'Trouvailles fréquentes : infiltrats, cavernes, nodules, épanchement pleural.'
      ],
      SW: [
        'Kipimo cha picha (X-ray) kuona mabadiliko ya mapafu yanayoweza kuashiria TB.',
        'Normal → Hakuna dalili ya TB inayoonekana.',
        'Abnormal/Suggestive of TB → Matokeo yanaweza kuonyesha TB.',
        'Unknown → Hakuna majibu ya X-ray.',
        'Mara nyingi huonekana: infiltrates, cavities, nodules, maji kwenye kifua (pleural effusion).'
      ],
      RW: [
        "Ifoto ya X-ray ikoreshwa kureba impinduka mu bihaha zishobora kugaragaza igituntu.",
        "Normal → Nta kimenyetso cya TB kigaragara.",
        "Abnormal/Suggestive of TB → Ibiboneka bishobora kugaragaza TB.",
        "Unknown → Nta gisubizo cya X-ray gihari.",
        "Ibisanzwe biboneka: infiltrates, cavities, nodules, amazi mu gatuza (pleural effusion)."
      ]
    }
  },
  {
    id: 'drug_resistance',
    title: FIELD_LABELS.drug_resistance,
    lines: {
      EN: [
        'Whether the TB bacteria are resistant to standard TB medications.',
        'No → Drug-sensitive TB.',
        'Yes → Drug-resistant TB.',
        'Examples: MDR-TB (Multidrug-Resistant TB), XDR-TB (Extensively Drug-Resistant TB).',
        'Importance: Determines which treatment regimen should be used.'
      ],
      FR: [
        "Indique si la bactérie TB est résistante aux médicaments standards.",
        'No → TB sensible aux médicaments.',
        'Yes → TB résistante.',
        'Exemples : MDR-TB, XDR-TB.',
        'Importance : Détermine le schéma thérapeutique à utiliser.'
      ],
      SW: [
        'Kama bakteria wa TB wana usugu kwa dawa za kawaida za TB.',
        'No → TB inayotibika kwa dawa za kawaida.',
        'Yes → TB sugu kwa dawa.',
        'Mifano: MDR-TB, XDR-TB.',
        'Umuhimu: Huamua mpango wa dawa utakao tumika.'
      ],
      RW: [
        "Kwerekana niba udukoko twa TB turwanya imiti isanzwe ya TB.",
        'No → TB yumva imiti (drug-sensitive).',
        'Yes → TB irwanya imiti (drug-resistant).',
        'Ingero: MDR-TB, XDR-TB.',
        "Icy’ingenzi: Bifasha guhitamo gahunda y'imiti ikoreshwa."
      ]
    }
  },
  {
    id: 'tst',
    title: FIELD_LABELS.tst,
    lines: {
      EN: [
        'Skin test used to detect TB infection (exposure).',
        'Positive → Exposure to TB bacteria likely.',
        'Negative → No evidence of infection.',
        'Unknown → Not tested.',
        'Note: Cannot distinguish active TB from latent TB.'
      ],
      FR: [
        "Test cutané pour détecter l'infection TB (exposition).",
        'Positive → Exposition probable.',
        "Negative → Pas d'argument d'infection.",
        'Unknown → Non testé.',
        'Note : Ne distingue pas TB active et TB latente.'
      ],
      SW: [
        'Kipimo cha ngozi kugundua maambukizi ya TB (kuwahi kuathiriwa).',
        'Positive → Inaonyesha huenda uliwahi kuathiriwa na TB.',
        'Negative → Hakuna ushahidi wa maambukizi.',
        'Unknown → Hakikufanyika.',
        'Kumbuka: Hakitofautishi TB iliyo hai na TB iliyolala (latent).'
      ],
      RW: [
        "Ikizamini cyo ku ruhu kigaragaza infection/ko wahuye na TB.",
        "Positive → Birashoboka ko wahuye n’udukoko twa TB.",
        "Negative → Nta kimenyetso cy'uko wanduye.",
        "Unknown → Nticyakozwe.",
        "Icyitonderwa: Ntigitandukanya TB ikora na TB yihishe (latent)."
      ]
    }
  },
  {
    id: 'igra',
    title: FIELD_LABELS.igra,
    lines: {
      EN: [
        'Blood test used to detect TB infection.',
        'Positive → Immune response suggests TB infection.',
        'Negative → No evidence of TB infection.',
        'Unknown → Test not performed.',
        'Examples: QuantiFERON‑TB Gold, T‑SPOT.TB. Advantage: More specific than TST.'
      ],
      FR: [
        "Test sanguin pour détecter l'infection TB.",
        'Positive → La réponse immunitaire suggère une infection TB.',
        "Negative → Pas d'argument d'infection TB.",
        'Unknown → Test non réalisé.',
        'Exemples : QuantiFERON‑TB Gold, T‑SPOT.TB. Avantage : plus spécifique que le TST.'
      ],
      SW: [
        'Kipimo cha damu kugundua maambukizi ya TB.',
        'Positive → Kinga ya mwili inaonyesha maambukizi ya TB.',
        'Negative → Hakuna ushahidi wa maambukizi ya TB.',
        'Unknown → Kipimo hakikufanyika.',
        'Mifano: QuantiFERON‑TB Gold, T‑SPOT.TB. Faida: Ni sahihi zaidi kuliko TST.'
      ],
      RW: [
        "Ikizamini cy'amaraso gishaka infection ya TB.",
        "Positive → Uko umubiri witwara bugaragaza infection ya TB.",
        "Negative → Nta kimenyetso cy'infection ya TB.",
        "Unknown → Ikizamini nticyakozwe.",
        "Ingero: QuantiFERON‑TB Gold, T‑SPOT.TB. Ibyiza: Akenshi kiba gifite ukwizerwa kurusha TST."
      ]
    }
  },
  {
    id: 'hiv',
    title: FIELD_LABELS.hiv,
    lines: {
      EN: [
        'Whether the patient is infected with HIV.',
        'Yes → HIV positive.',
        'No → HIV negative.',
        'Unknown → Status not known.',
        'Importance: HIV greatly increases the risk of developing active TB.'
      ],
      FR: [
        'Indique si le patient est infecté par le VIH.',
        'Yes → VIH positif.',
        'No → VIH négatif.',
        'Unknown → Statut inconnu.',
        'Importance : Le VIH augmente fortement le risque de TB active.'
      ],
      SW: [
        'Kama mgonjwa ana VVU (HIV) au la.',
        'Yes → VVU chanya.',
        'No → VVU hasi.',
        'Unknown → Haijulikani.',
        'Umuhimu: VVU huongeza sana hatari ya kupata TB iliyo hai.'
      ],
      RW: [
        'Kwerekana niba umurwayi afite HIV.',
        'Yes → HIV positive.',
        'No → HIV negative.',
        'Unknown → Ntibizwi.',
        "Icy’ingenzi: HIV yongera cyane ibyago byo kugira TB ikora."
      ]
    }
  },
  {
    id: 'diabetes',
    title: FIELD_LABELS.diabetes,
    lines: {
      EN: [
        'Whether the patient has diabetes.',
        'Yes → Patient has diabetes.',
        'No → Patient does not have diabetes.',
        'Unknown → Status not known.',
        'Importance: Diabetes increases susceptibility to TB and can affect treatment outcomes.'
      ],
      FR: [
        'Indique si le patient est diabétique.',
        'Yes → Diabète présent.',
        'No → Pas de diabète.',
        'Unknown → Statut inconnu.',
        'Importance : Le diabète augmente la susceptibilité à la TB et peut affecter le traitement.'
      ],
      SW: [
        'Kama mgonjwa ana kisukari (diabetes) au la.',
        'Yes → Ana kisukari.',
        'No → Hana kisukari.',
        'Unknown → Haijulikani.',
        'Umuhimu: Kisukari huongeza uwezekano wa TB na huathiri matokeo ya tiba.'
      ],
      RW: [
        "Kwerekana niba umurwayi afite indwara ya sukari (diabetes).",
        'Yes → Afite diabetes.',
        'No → Nta diabetes afite.',
        'Unknown → Ntibizwi.',
        "Icy’ingenzi: Diabetes yongera ibyago bya TB kandi ishobora kugira ingaruka ku musaruro w'ubuvuzi."
      ]
    }
  }
]

const indexFieldGroups = computed(() => {
  const identity = baseIndexFieldGroups.find(group => group.id === 'identity')
  const clues = baseIndexFieldGroups.find(group => group.id === 'clues')
  const dst = baseIndexFieldGroups.find(group => group.id === 'dst')

  const tests = {
    id: 'tests',
    title: {
      EN: '3) Tests, imaging, and risk conditions',
      FR: '3) Tests, imagerie et facteurs de risque',
      SW: '3) Vipimo, picha, na vihatarishi',
      RW: '3) Ibizamini, X-ray, n’ibindi byongera ibyago'
    },
    description: {
      EN: 'These results are commonly used to confirm TB and understand severity.',
      FR: 'Ces résultats servent souvent à confirmer la TB et évaluer la gravité.',
      SW: 'Majibu haya hutumika kuthibitisha TB na kupima ukali.',
      RW: 'Ibi bisubizo bikoreshwa kwemeza TB no gusobanukirwa ubukana.'
    },
    items: fieldGuideItems
  }

  return [identity, clues, tests, dst].filter(Boolean)
})

const visibleIndexFieldGroups = computed(() => {
  if (indexSelectedSection.value === 'all') return indexFieldGroups.value
  return indexFieldGroups.value.filter(group => group.id === indexSelectedSection.value)
})

function selectIndexSection(sectionId) {
  indexSelectedSection.value = sectionId === 'all' ? 'all' : String(sectionId || 'all')
  fieldGuideOpen.value = true
}

const aiUseRows = [
  {
    id: 'ai1',
    field: FIELD_LABELS.bacteria_species,
    purpose: {
      EN: 'Predict causative species',
      FR: "Prédire l'espèce causale",
      SW: 'Kutabiri aina ya bakteria',
      RW: "Gugerageza ubwoko bw'udukoko"
    }
  },
  {
    id: 'ai2',
    field: FIELD_LABELS.tb_culture,
    purpose: { EN: 'Confirm TB diagnosis', FR: 'Confirmer le diagnostic TB', SW: 'Kuthibitisha TB', RW: "Kwemeza igituntu" }
  },
  {
    id: 'ai3',
    field: FIELD_LABELS.sputum_smear_test,
    purpose: {
      EN: 'Detect infectious pulmonary TB',
      FR: 'Détecter la TB pulmonaire contagieuse',
      SW: 'Kugundua TB ya mapafu inayoambukiza',
      RW: 'Kumenya TB y’ibihaha ishobora kwanduza'
    }
  },
  {
    id: 'ai4',
    field: FIELD_LABELS.genexpert_test,
    purpose: { EN: 'Detect TB and resistance', FR: 'Détecter TB et résistance', SW: 'Kugundua TB na usugu wa dawa', RW: 'Kumenya TB n’uko irwanya imiti' }
  },
  {
    id: 'ai5',
    field: FIELD_LABELS.chest_xray,
    purpose: { EN: 'Identify lung damage/signs', FR: 'Identifier signes pulmonaires', SW: 'Kuona dalili/uharibifu wa mapafu', RW: 'Kureba ibimenyetso mu bihaha' }
  },
  {
    id: 'ai6',
    field: FIELD_LABELS.drug_resistance,
    purpose: { EN: 'Select appropriate drugs', FR: 'Choisir les médicaments adaptés', SW: 'Kuchagua dawa sahihi', RW: 'Guhitamo imiti iboneye' }
  },
  {
    id: 'ai7',
    field: FIELD_LABELS.tst,
    purpose: { EN: 'Detect TB infection', FR: "Détecter l'infection TB", SW: 'Kugundua maambukizi ya TB', RW: 'Kumenya infection ya TB' }
  },
  {
    id: 'ai8',
    field: FIELD_LABELS.igra,
    purpose: { EN: 'Detect TB infection', FR: "Détecter l'infection TB", SW: 'Kugundua maambukizi ya TB', RW: 'Kumenya infection ya TB' }
  },
  {
    id: 'ai9',
    field: FIELD_LABELS.hiv,
    purpose: { EN: 'Assess risk and severity', FR: 'Évaluer le risque et la gravité', SW: 'Kupima hatari na ukali', RW: 'Gupima ibyago n’ubukana' }
  },
  {
    id: 'ai10',
    field: FIELD_LABELS.diabetes,
    purpose: {
      EN: 'Assess risk and treatment outcomes',
      FR: 'Évaluer le risque et la réponse au traitement',
      SW: 'Kupima hatari na matokeo ya tiba',
      RW: "Gupima ibyago n'uko azitwara ku miti"
    }
  }
]

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
  if (!currentUser.value) return t(TEXT.authenticatedUser)
  return currentUser.value.username || currentUser.value.email || t(TEXT.authenticatedUser)
})
const userRoleLabel = computed(() => {
  if (!currentUser.value?.role) return t(TEXT.authorizedRole)
  return String(currentUser.value.role).replace(/_/g, ' ')
})

const tabs = computed(() => [
  { id: 'diagnose', label: t(TEXT.tabDiagnose), icon: '🏥' },
  { id: 'patients', label: t(TEXT.tabPatients), icon: '👥' },
  { id: 'alerts', label: t(TEXT.tabAlerts), icon: '🔔' }
])

const loginWorkflowSteps = [
  {
    id: 'collect',
    stepLabel: TEXT.workflowStep1,
    title: TEXT.workflowCollect,
    accent: 'border-emerald-200 dark:border-emerald-800/60',
    kickerClass: 'text-emerald-700 dark:text-emerald-300'
  },
  {
    id: 'analyze',
    stepLabel: TEXT.workflowStep2,
    title: TEXT.workflowAnalyze,
    accent: 'border-blue-200 dark:border-blue-800/60',
    kickerClass: 'text-blue-700 dark:text-blue-300'
  },
  {
    id: 'classify',
    stepLabel: TEXT.workflowStep3,
    title: TEXT.workflowClassify,
    accent: 'border-violet-200 dark:border-violet-800/60',
    kickerClass: 'text-violet-700 dark:text-violet-300'
  },
  {
    id: 'treat',
    stepLabel: TEXT.workflowStep4,
    title: TEXT.workflowTreat,
    accent: 'border-green-200 dark:border-green-800/60',
    kickerClass: 'text-green-700 dark:text-green-300'
  }
]

const loginWorkflowSummaryCards = [
  { id: 'patient', title: TEXT.workflowPatient, lines: [TEXT.workflowSymptoms, TEXT.workflowTests] },
  { id: 'tb', title: TEXT.workflowTbType, lines: [TEXT.workflowBacteria, TEXT.workflowResistance] },
  { id: 'report', title: TEXT.workflowReport, lines: [TEXT.workflowTreatment, TEXT.workflowGuidance] }
]

const diagnosisSteps = computed(() => [
  {
    id: 1,
    title: t({
      EN: 'Patient identity',
      FR: 'Identité du patient',
      SW: 'Utambulisho wa mgonjwa',
      RW: "Amakuru y'umurwayi"
    }),
    short: t({ EN: 'name and record', FR: 'nom et dossier', SW: 'majina na rekodi', RW: 'izina na dosiye' }),
    description: t({
      EN: 'Capture the identity used to save, reopen, and display the clinical record.',
      FR: "Saisir l'identité pour enregistrer, rouvrir et afficher le dossier clinique.",
      SW: 'Weka utambulisho ili kuhifadhi, kufungua tena, na kuonyesha rekodi ya mgonjwa.',
      RW: "Andika amakuru y'ibanze afasha kubika, kongera gufungura, no kwerekana dosiye."
    }),
    footer: t({
      EN: 'Confirm identity details before moving to symptoms.',
      FR: "Confirmez l'identité avant les symptômes.",
      SW: 'Thibitisha utambulisho kabla ya dalili.',
      RW: 'Emeza amakuru y’umurwayi mbere yo kujya ku bimenyetso.'
    })
  },
  {
    id: 2,
    title: t({ EN: 'Clinical clues', FR: 'Indices cliniques', SW: 'Dalili za kliniki', RW: 'Ibimenyetso bya kliniki' }),
    short: t({ EN: 'symptoms and exposure', FR: 'symptômes et exposition', SW: 'dalili na kuambukizwa', RW: "ibimenyetso n'aho yandurira" }),
    description: t({
      EN: 'Document symptoms and exposure history using suggestions or direct typing.',
      FR: "Notez les symptômes et l'exposition via les suggestions ou en saisie libre.",
      SW: 'Andika dalili na historia ya kuambukizwa kwa mapendekezo au kuandika mwenyewe.',
      RW: "Andika ibimenyetso n'amateka y'aho yandurira ukoresheje ibitekerezo cyangwa ukabyandika."
    }),
    footer: t({
      EN: 'Review symptoms/exposure, then continue to tests.',
      FR: 'Revoyez symptômes/exposition puis passez aux tests.',
      SW: 'Kagua dalili/kuambukizwa kisha endelea na vipimo.',
      RW: "Subiramo ibimenyetso/aho yandurira hanyuma ujye ku bizamini."
    })
  },
  {
    id: 3,
    title: t({ EN: 'Tests and results', FR: 'Tests et résultats', SW: 'Vipimo na majibu', RW: 'Ibizamini n’ibisubizo' }),
    short: t({ EN: 'results and evidence', FR: 'résultats et preuves', SW: 'majibu na ushahidi', RW: 'ibisubizo n’ibimenyetso' }),
    description: t({
      EN: 'Enter smear, culture, GeneXpert, X‑ray, TST, IGRA, and related evidence.',
      FR: 'Saisir frottis, culture, GeneXpert, radio, TST, IGRA et preuves associées.',
      SW: 'Weka smear, culture, GeneXpert, X‑ray, TST, IGRA na ushahidi unaohusiana.',
      RW: 'Andika smear, culture, GeneXpert, X‑ray, TST, IGRA n’ibindi bimenyetso.'
    }),
    footer: t({
      EN: 'Check test results before moving to DST and resistance.',
      FR: 'Vérifiez les tests avant le DST et la résistance.',
      SW: 'Kagua majibu kabla ya DST na usugu wa dawa.',
      RW: 'Reba ibisubizo by’ibizamini mbere yo kujya kuri DST na resistance.'
    })
  },
  {
    id: 4,
    title: t({ EN: 'DST and resistance', FR: 'DST et résistance', SW: 'DST na usugu', RW: 'DST na resistance' }),
    short: t({ EN: 'drug decision support', FR: 'aide médicaments', SW: 'msaada wa dawa', RW: "ubufasha ku miti" }),
    description: t({
      EN: 'Complete DST summary, resistance, and susceptibility details before generating the report.',
      FR: "Complétez le résumé DST, la résistance et la sensibilité avant le rapport.",
      SW: 'Kamilisha muhtasari wa DST, usugu na usikivu wa dawa kabla ya ripoti.',
      RW: "Uzuza incamake ya DST, resistance na susceptibility mbere yo gukora raporo."
    }),
    footer: t({
      EN: 'Finish the last step and run the analysis.',
      FR: "Terminez l'étape et lancez l'analyse.",
      SW: 'Maliza hatua ya mwisho kisha endesha uchambuzi.',
      RW: 'Soza igice cya nyuma hanyuma ukore isesengura.'
    })
  }
])

const symptomOptions = [
  { value: 'Persistent cough for 2+ weeks', label: { EN: 'Persistent cough for 2+ weeks', FR: 'Toux persistante 2+ semaines', SW: 'Kikohozi kinachoendelea wiki 2+', RW: 'Inkorora imaze ibyumweru 2+' } },
  { value: 'Hemoptysis', label: { EN: 'Hemoptysis', FR: 'Hémoptysie', SW: 'Kukohoa damu', RW: 'Gukorora amaraso' } },
  { value: 'Fever', label: { EN: 'Fever', FR: 'Fièvre', SW: 'Homa', RW: 'Umuriro' } },
  { value: 'Night sweats', label: { EN: 'Night sweats', FR: 'Sueurs nocturnes', SW: 'Kutokwa jasho usiku', RW: 'Kubira icyuya nijoro' } },
  { value: 'Weight loss', label: { EN: 'Weight loss', FR: 'Perte de poids', SW: 'Kupungua uzito', RW: "Kugabanuka kw'ibiro" } },
  { value: 'Chest pain', label: { EN: 'Chest pain', FR: 'Douleur thoracique', SW: 'Maumivu ya kifua', RW: 'Kubabara mu gatuza' } },
  { value: 'Fatigue', label: { EN: 'Fatigue', FR: 'Fatigue', SW: 'Uchovu', RW: 'Umunaniro' } },
  { value: 'Breathlessness', label: { EN: 'Breathlessness', FR: 'Essoufflement', SW: 'Upungufu wa pumzi', RW: 'Kubura umwuka' } },
  { value: 'Loss of appetite', label: { EN: 'Loss of appetite', FR: "Perte d'appétit", SW: 'Kupoteza hamu ya kula', RW: 'Kudashaka kurya' } },
  { value: 'Lymph node swelling', label: { EN: 'Lymph node swelling', FR: 'Adénopathie', SW: 'Kuvimba tezi', RW: 'Kubyimba imisate y’amaraso (lymph nodes)' } },
  { value: 'Back pain', label: { EN: 'Back pain', FR: 'Douleur du dos', SW: 'Maumivu ya mgongo', RW: "Kubabara mu mugongo" } },
  { value: 'Abdominal pain', label: { EN: 'Abdominal pain', FR: 'Douleur abdominale', SW: 'Maumivu ya tumbo', RW: "Kubabara mu nda" } },
  { value: 'Neck stiffness', label: { EN: 'Neck stiffness', FR: 'Raideur de la nuque', SW: 'Shingo kukakamaa', RW: 'Kubyimba/kukakamaa mu ijosi' } },
  { value: 'Pleural chest pain', label: { EN: 'Pleural chest pain', FR: 'Douleur pleurale', SW: 'Maumivu ya pleura', RW: 'Kubabara mu gatuza (pleura)' } }
]

const exposureOptions = [
  { value: 'Household TB contact', label: { EN: 'Household TB contact', FR: 'Contact TB à domicile', SW: 'Kukaa na mwenye TB', RW: "Guhura n’ufite TB mu rugo" } },
  { value: 'Close contact with MDR-TB patient', label: { EN: 'Close contact with MDR‑TB patient', FR: 'Contact proche MDR‑TB', SW: 'Kukaribiana na MDR‑TB', RW: 'Guhura n’ufite MDR‑TB' } },
  { value: 'Cattle exposure', label: { EN: 'Cattle exposure', FR: 'Contact avec bovins', SW: 'Kugusana na ng’ombe', RW: "Kwegera inka" } },
  { value: 'Goat or sheep exposure', label: { EN: 'Goat or sheep exposure', FR: 'Contact chèvre/mouton', SW: 'Kugusana na mbuzi/kondoo', RW: "Kwegera ihene/intonzi" } },
  { value: 'Unpasteurized milk intake', label: { EN: 'Unpasteurized milk intake', FR: 'Lait non pasteurisé', SW: 'Maziwa yasiyopasteurizwa', RW: 'Kunywa amata atapasteurizwemo' } },
  { value: 'Rodent exposure', label: { EN: 'Rodent exposure', FR: 'Exposition rongeurs', SW: 'Kukutana na panya', RW: 'Kwegera imbeba' } },
  { value: 'Marine mammal exposure', label: { EN: 'Marine mammal exposure', FR: 'Mammifères marins', SW: 'Wanyama wa baharini', RW: 'Inyamaswa zo mu nyanja' } },
  { value: 'South Asia travel history', label: { EN: 'South Asia travel history', FR: 'Voyage Asie du Sud', SW: 'Safari Asia Kusini', RW: 'Ingendo muri Asia y’Epfo' } },
  { value: 'West Africa residence history', label: { EN: 'West Africa residence history', FR: 'Séjour Afrique de l’Ouest', SW: 'Kuishi Afrika Magharibi', RW: 'Kuba warabaye muri Afurika y’Uburengerazuba' } },
  { value: 'Horn of Africa travel history', label: { EN: 'Horn of Africa travel history', FR: "Voyage Corne de l'Afrique", SW: 'Safari Pembe ya Afrika', RW: 'Ingendo mu ihembe rya Afurika' } },
  { value: 'Prison or crowded living conditions', label: { EN: 'Prison or crowded living', FR: 'Prison ou promiscuité', SW: 'Gereza/mazingira yenye msongamano', RW: 'Gereza/aho abantu bacucitse' } },
  { value: 'Healthcare worker exposure', label: { EN: 'Healthcare worker exposure', FR: 'Exposition travailleur santé', SW: 'Kazi ya afya (exposure)', RW: 'Gukora mu buvuzi (exposure)' } },
  { value: 'Previous untreated TB episode', label: { EN: 'Previous untreated TB episode', FR: 'TB passé non traité', SW: 'TB ya zamani bila matibabu', RW: 'Kuba warigeze kugira TB itavuwe' } },
  { value: 'Livestock herd exposure', label: { EN: 'Livestock herd exposure', FR: 'Troupeau (bétail)', SW: 'Mifugo (kundi)', RW: 'Kwegera umukumbi w’amatungo' } }
]

const antibiogramOptions = [
  { value: 'Fully susceptible first-line profile', label: { EN: 'Fully susceptible first‑line profile', FR: 'Sensibilité complète 1ère ligne', SW: 'Inakubali dawa za kwanza', RW: 'Yumva imiti y’ibanze (first‑line)' } },
  { value: 'Rifampicin resistance detected', label: { EN: 'Rifampicin resistance detected', FR: 'Résistance rifampicine', SW: 'Usugu wa rifampicin', RW: 'Resistance ya rifampicin' } },
  { value: 'Isoniazid resistance detected', label: { EN: 'Isoniazid resistance detected', FR: 'Résistance isoniazide', SW: 'Usugu wa isoniazid', RW: 'Resistance ya isoniazid' } },
  { value: 'Pyrazinamide resistance suspected', label: { EN: 'Pyrazinamide resistance suspected', FR: 'Résistance pyrazinamide suspectée', SW: 'Usugu wa pyrazinamide (shaka)', RW: 'Pyrazinamide resistance (gukeka)' } },
  { value: 'MDR profile confirmed by DST', label: { EN: 'MDR confirmed by DST', FR: 'MDR confirmé (DST)', SW: 'MDR imethibitishwa (DST)', RW: 'MDR yemejwe na DST' } },
  { value: 'XDR profile suspected', label: { EN: 'XDR profile suspected', FR: 'XDR suspecté', SW: 'XDR inashukiwa', RW: 'XDR ikekwa' } },
  { value: 'Fluoroquinolone susceptible', label: { EN: 'Fluoroquinolone susceptible', FR: 'Sensible fluoroquinolones', SW: 'Inakubali fluoroquinolone', RW: 'Yumva fluoroquinolone' } },
  { value: 'Linezolid active', label: { EN: 'Linezolid active', FR: 'Linezolid actif', SW: 'Linezolid inafanya kazi', RW: 'Linezolid ikora' } },
  { value: 'Clofazimine active', label: { EN: 'Clofazimine active', FR: 'Clofazimine actif', SW: 'Clofazimine inafanya kazi', RW: 'Clofazimine ikora' } },
  { value: 'Reference laboratory confirmation recommended', label: { EN: 'Reference lab confirmation recommended', FR: 'Confirmation labo de référence', SW: 'Thibitisha kwenye maabara ya rufaa', RW: 'Kwemeza kuri labo y’icyitegererezo' } }
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
const customCommaInputs = ref({
  symptoms: '',
  exposure_history: '',
  antibiogram_result: '',
  resistant_to: '',
  susceptible_to: ''
})
const openCustomCommaInputs = ref({
  symptoms: false,
  exposure_history: false,
  antibiogram_result: false,
  resistant_to: false,
  susceptible_to: false
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
const currentDiagnosisMeta = computed(() => diagnosisSteps.value.find(step => step.id === currentDiagnosisStep.value) || diagnosisSteps.value[0])

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
  if (nextStep < 1 || nextStep > diagnosisSteps.value.length) return
  currentDiagnosisStep.value = nextStep
}

function nextDiagnosisStep() {
  if (currentDiagnosisStep.value >= diagnosisSteps.value.length) return
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

function openCustomListInput(field) {
  if (!(field in openCustomCommaInputs.value)) return
  openCustomCommaInputs.value[field] = true
}

function closeCustomListInput(field) {
  if (!(field in openCustomCommaInputs.value)) return
  customCommaInputs.value[field] = ''
  openCustomCommaInputs.value[field] = false
}

function addCustomListValue(field) {
  const draftValue = String(customCommaInputs.value[field] || '').trim()
  if (!draftValue) return
  appendSuggestedValue(field, draftValue)
  closeCustomListInput(field)
}

function formatPercent(value) {
  const numeric = Number(value)
  if (!Number.isFinite(numeric)) return '-'
  return `${(numeric * 100).toFixed(1)}%`
}

function formatPredictionLabel(value, type = 'tb') {
  const normalized = String(value || '').trim().toLowerCase()
  if (!normalized) return t(TEXT.notAvailable)
  if (type === 'tb') {
    if (normalized === 'yes' || normalized === 'positive') return t(TEXT.tbLikely)
    if (normalized === 'no' || normalized === 'negative') return t(TEXT.tbNotLikely)
  }
  if (type === 'resistance') {
    if (normalized === 'yes' || normalized === 'positive') return t(TEXT.drugResistanceLikely)
    if (normalized === 'no' || normalized === 'negative') return t(TEXT.drugResistanceNotPredicted)
  }
  return translateBackendText(value)
}

function buildConfidenceSummary(predictionBlock, type = 'tb') {
  if (!predictionBlock) return t(TEXT.noModelConfidence)
  const predictionLabel = formatPredictionLabel(predictionBlock.prediction, type)
  return tf(TEXT.modelConfidenceSummary, { label: predictionLabel, confidence: formatPercent(predictionBlock.confidence) })
}

function formatProbabilityList(probabilities) {
  if (!probabilities || typeof probabilities !== 'object') return []
  return Object.entries(probabilities).map(([label, value]) => ({
    label: translateBackendText(label),
    value: formatPercent(value)
  }))
}

function translateBackendText(value) {
  const raw = String(value ?? '').trim()
  if (!raw) return raw

  const exact = {
    'Unknown': t(TEXT.statusUnknown),
    'Not provided': t(TEXT.notProvided),
    'No': t(TEXT.statusNo),
    'Yes': t(TEXT.statusYes),
    'default': t(TEXT.modeDefault),
    'first-line': t(TEXT.regimenFirstLine),
    'second-line': t(TEXT.regimenSecondLine),
    'modified first-line': t(TEXT.regimenModifiedFirstLine),
    'individualized second-line': t(TEXT.regimenIndividualizedSecondLine),
    'preventive therapy': t(TEXT.regimenPreventiveTherapy),
    'HIGH': t(TEXT.urgencyHigh),
    'URGENT': t(TEXT.urgencyUrgent),
    'CRITICAL - LIFE THREATENING': t(TEXT.urgencyCritical),
    'Pulmonary TB': t(TEXT.pulmonaryTb),
    'Lungs': t(TEXT.lungsLabel),
    'Lymph Node TB': t(TEXT.lymphNodeTb),
    'Lymph nodes': t(TEXT.lymphNodesLabel),
    'Bone and Joint TB': t(TEXT.boneJointTb),
    'Spine, bones, or joints': t(TEXT.bonesJointsSite),
    'TB Meningitis': t(TEXT.tbMeningitis),
    'Central nervous system': t(TEXT.centralNervousSystem),
    'Genitourinary TB': t(TEXT.genitourinaryTb),
    'Genitourinary tract': t(TEXT.genitourinaryTract),
    'Abdominal TB': t(TEXT.abdominalTb),
    'Abdomen/peritoneum': t(TEXT.abdomenPeritoneum),
    'Pleural TB': t(TEXT.pleuralTb),
    'Pleura': t(TEXT.pleuraLabel),
    'Miliary TB': t(TEXT.miliaryTb),
    'Disseminated / whole body spread': t(TEXT.disseminatedSite),
    'Latent TB Infection': t(TEXT.latentTbInfection),
    'No active organ disease': t(TEXT.noActiveOrganDisease),
    'TB/HIV Co-infection': t(TEXT.tbHivCoinfection),
    'Systemic comorbidity': t(TEXT.systemicComorbidity),
    'The most common cause of human tuberculosis worldwide.': t(TEXT.backendSpeciesDescMtuberculosis),
    'Defaulted to the most common human TB species because the patient record did not contain enough species-specific evidence.': t(TEXT.backendSpeciesReasonDefault),
    'Human-to-human airborne transmission.': t(TEXT.backendTypicalSourceHuman),
    'Routine TB molecular tests and culture commonly target this species within the MTBC.': t(TEXT.backendLabNoteRoutineMtbc),
    'WHO-aligned TB rule engine with species notes, infection-site classification, and DST-aware regimen escalation.': t(TEXT.backendGuidelineWhoEngine),
    'Chosen because rifampicin and isoniazid resistance is present or strongly suspected.': t(TEXT.backendChosenMdr),
    'TB not likely': t(TEXT.tbNotLikely),
    'Drug resistance not predicted': t(TEXT.drugResistanceNotPredicted),
    'TB likely': t(TEXT.tbLikely),
    'Drug resistance likely': t(TEXT.drugResistanceLikely),
    '18-24 months': t(TEXT.duration18to24Months),
    '18-24 months total': t(TEXT.duration18to24MonthsTotal),
    'WHO MDR-TB second-line regimen': t(TEXT.whoMdrRegimen),
    'CONFIRMED PULMONARY TB (PTB)': t(TEXT.confirmedPulmonaryTb),
    'CLINICALLY DIAGNOSED PULMONARY TB (PTB)': t(TEXT.clinicallyDiagnosedPulmonaryTb),
    'PRESUMPTIVE PULMONARY TB (PTB)': t(TEXT.presumptivePulmonaryTb),
    'No specific TB infection pattern confirmed': t(TEXT.noSpecificTbPattern),
    'Drug-sensitive TB (DS-TB)': t(TEXT.dsTbLabel),
    'Initiate treatment promptly according to national guidelines; ensure airborne precautions': t(TEXT.whoRecommendationStartTreatment),
    'OBSERVATION AND FURTHER TESTING': t(TEXT.observationFurtherTesting),
    'MODERATE': t(TEXT.moderateLabel),
    'NO EVIDENCE OF TB': t(TEXT.noEvidenceOfTb),
    'N/A': t(TEXT.durationNa),
    'No anti-TB treatment unless clinical suspicion remains high': t(TEXT.noAntiTbTreatmentHighSuspicion),
    'Intensive: N/A, Continuation: N/A': t(TEXT.dosageNa),
    'Intensive phase: N/A; continuation phase: N/A; daily DOTS/supervised dosing where feasible.': t(TEXT.administrationNa),
    'Monitor symptoms, consider other diagnoses': t(TEXT.monitorSymptomsAlternativeDx),
    'Monitor closely, repeat tests as indicated, evaluate for alternative diagnoses': t(TEXT.monitorCloselyRepeatTests),
    'Fully susceptible first-line profile': t(TEXT.dstFullySusceptible),
    'Rifampicin resistance detected': t(TEXT.dstRifampicinResistance),
    'Pyrazinamide resistance suspected': t(TEXT.dstPyrazinamideSuspected),
    'Isoniazid resistance detected': t(TEXT.dstIsoniazidResistance),
    'MDR profile confirmed by DST': t(TEXT.dstMdrConfirmed),
    'XDR profile suspected': t(TEXT.dstXdrSuspected)
  }
  if (exact[raw]) return exact[raw]

  if (raw.startsWith('Primary TB classification: ')) {
    return `${t(TEXT.primaryTbClassification)}: ${translateBackendText(raw.slice('Primary TB classification: '.length))}`
  }
  if (raw.startsWith('Bacteria estimate: ')) {
    return `${t(TEXT.bacteriaEstimate)}: ${translateBackendText(raw.slice('Bacteria estimate: '.length))}`
  }
  if (raw.startsWith('Resistance class: ')) {
    return `${t(TEXT.resistanceClassLabel)}: ${translateBackendText(raw.slice('Resistance class: '.length))}`
  }
  if (raw.startsWith('Antibiogram/DST summary: ')) {
    return `${t(TEXT.antibiogramDstSummary)}: ${translateBackendText(raw.slice('Antibiogram/DST summary: '.length))}`
  }
  if (raw.startsWith('TB culture: ')) {
    return `${t(TEXT.tbCultureLabel)}: ${translateBackendText(raw.slice('TB culture: '.length))}`
  }
  if (raw.startsWith('TST: ')) {
    return `${t(TEXT.tstShortLabel)}: ${translateBackendText(raw.slice('TST: '.length))}`
  }
  if (raw.startsWith('IGRA: ')) {
    return `${t(TEXT.igraShortLabel)}: ${translateBackendText(raw.slice('IGRA: '.length))}`
  }
  if (raw.startsWith('No specific TB infection pattern confirmed - ')) {
    return `${t(TEXT.noSpecificTbPattern)} - ${translateBackendText(raw.slice('No specific TB infection pattern confirmed - '.length))}`
  }
  if (raw.startsWith('ALERT: ')) {
    return `${t(TEXT.alertLabel)}: ${translateBackendText(raw.slice('ALERT: '.length))}`
  }

  const alertMatch = raw.match(/^Patient (.+) \(ID: (.+)\) classified as (.+) with estimated bacteria (.+)\. (.+)$/)
  if (alertMatch) {
    return tf(TEXT.backendAlertTemplate, {
      patientName: alertMatch[1],
      patientId: alertMatch[2],
      category: translateBackendText(alertMatch[3]),
      species: translateBackendText(alertMatch[4]),
      recommendation: translateBackendText(alertMatch[5])
    })
  }

  const inlineReplacements = [
    ['Initiate treatment promptly according to national guidelines; ensure airborne precautions', t(TEXT.whoRecommendationStartTreatment)],
    ['CONFIRMED PULMONARY TB (PTB)', t(TEXT.confirmedPulmonaryTb)],
    ['CLINICALLY DIAGNOSED PULMONARY TB (PTB)', t(TEXT.clinicallyDiagnosedPulmonaryTb)],
    ['PRESUMPTIVE PULMONARY TB (PTB)', t(TEXT.presumptivePulmonaryTb)],
    ['NO EVIDENCE OF TB', t(TEXT.noEvidenceOfTb)],
    ['Fully susceptible first-line profile', t(TEXT.dstFullySusceptible)],
    ['Rifampicin resistance detected', t(TEXT.dstRifampicinResistance)],
    ['Pyrazinamide resistance suspected', t(TEXT.dstPyrazinamideSuspected)],
    ['Isoniazid resistance detected', t(TEXT.dstIsoniazidResistance)],
    ['MDR profile confirmed by DST', t(TEXT.dstMdrConfirmed)],
    ['XDR profile suspected', t(TEXT.dstXdrSuspected)]
  ]

  let replaced = raw
  for (const [from, to] of inlineReplacements) {
    if (from && replaced.includes(from)) replaced = replaced.split(from).join(to)
  }

  return replaced
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
  headers['X-UI-Language'] = uiLanguage.value

  // #region debug-point A:api-fetch
  fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"A",location:"frontend/app.vue:615",msg:"[DEBUG] apiFetch request",data:{path,hasToken:!!token.value,authorizationHeader:!!headers.Authorization,currentView:currentView.value},ts:Date.now()})}).catch(()=>{})
  // #endregion
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  // #region debug-point B:api-response
  fetch("http://127.0.0.1:7777/event",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({sessionId:"patients-empty-api",runId:"pre-fix",hypothesisId:"B",location:"frontend/app.vue:621",msg:"[DEBUG] apiFetch response",data:{path,status:response.status,ok:response.ok},ts:Date.now()})}).catch(()=>{})
  // #endregion
  if (response.status === 401) {
    clearSession()
    loginError.value = t(TEXT.sessionExpired)
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
      headers: {
        'Content-Type': 'application/json',
        'X-UI-Language': uiLanguage.value
      },
      body: JSON.stringify({ email: loginEmail.value, password: loginPassword.value })
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      loginError.value = err.msg || t(TEXT.invalidEmailOrPassword)
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
    loginError.value = t(TEXT.loginFailed)
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
    loginError.value = error?.message === 'Unauthorized' ? t(TEXT.sessionExpired) : t(TEXT.diagnosisRequestFailed)
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
    loginError.value = error?.message === 'Unauthorized' ? t(TEXT.sessionExpired) : t(TEXT.patientsLoadFailed)
  }
}

async function loadAlerts() {
  try {
    if (!isLoggedIn.value) return
    const response = await apiFetch('/alerts')
    const data = await response.json()
    alerts.value = data.alerts || []
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? t(TEXT.sessionExpired) : t(TEXT.alertsLoadFailed)
  }
}

async function markAsRead(alert) {
  if (alert.is_read) return
  try {
    await apiFetch(`/alerts/${alert.id}/read`, { method: 'PUT' })
    alert.is_read = true
  } catch (error) {
    loginError.value = error?.message === 'Unauthorized' ? t(TEXT.sessionExpired) : t(TEXT.alertMarkReadFailed)
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
  uiLanguage.value = readStoredValue('tb_ui_language', 'EN')
  applyDarkMode(isDarkMode.value)

  if (token.value) {
    loadCurrentUser().catch(() => clearSession())
  }

  if (isLoggedIn.value) {
    loadPatients()
    loadAlerts()
  }
})

watch(uiLanguage, (value) => {
  writeStoredValue('tb_ui_language', String(value || 'EN'))
})
</script>
