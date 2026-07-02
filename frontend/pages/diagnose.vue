<template>
  <DashboardLayout>
    <NotificationModal
      :is-open="notification.isOpen"
      :title="notification.title"
      :message="notification.message"
      :type="notification.type"
      @close="closeNotification"
    />
    <div class="space-y-6">
      <!-- Progress Steps -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6">
        <div class="flex items-center justify-between mb-4">
          <h2 class="text-xl font-bold text-gray-900 dark:text-white">Diagnosis Workflow</h2>
          <span class="text-sm text-gray-500 dark:text-gray-400">Step {{ currentStep }} of {{ totalSteps }}</span>
        </div>
        <div class="flex items-center gap-2 sm:gap-4 overflow-x-auto pb-2">
          <div v-for="(step, index) in steps" :key="step.id" class="flex items-center">
            <button @click="goToStep(index + 1)" :disabled="isStepAccessible(index + 1)" :class="[
              'flex items-center justify-center w-10 h-10 rounded-full font-semibold text-sm transition-all shrink-0',
              currentStep === index + 1
                ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-500/30'
                : index + 1 < currentStep
                ? 'bg-primary-900/50 text-primary-400 border border-primary-700'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
            ]">
              <svg v-if="index + 1 < currentStep" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </button>
            <div class="ml-2 sm:ml-3 text-left min-w-[80px] sm:min-w-[100px]">
              <p :class="['text-xs sm:text-sm font-medium', currentStep >= index + 1 ? 'text-white' : 'text-gray-500']">
                {{ step.title }}
              </p>
            </div>
            <div v-if="index < steps.length - 1" class="w-4 sm:w-8 h-0.5 mx-1 sm:mx-2 bg-gray-700"></div>
          </div>
        </div>
      </div>

      <!-- Step Content -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl border border-gray-200 dark:border-gray-700 p-6 sm:p-8">
        <!-- Step 1: Patient Selection -->
        <div v-if="currentStep === 1" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Select Patient</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Choose an existing patient or create a new one</p>
            </div>
          </div>

          <!-- Mode Toggle -->
          <div class="flex gap-3 p-1 bg-gray-100 dark:bg-gray-700/50 rounded-xl">
            <button @click="patientMode = 'existing'" :class="[
              'flex-1 py-3 rounded-lg text-sm font-semibold transition-all',
              patientMode === 'existing'
                ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-500/30'
                : 'text-gray-400 hover:text-white'
            ]">
              Select Existing Patient
            </button>
            <button @click="patientMode = 'new'" :class="[
              'flex-1 py-3 rounded-lg text-sm font-semibold transition-all',
              patientMode === 'new'
                ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg shadow-primary-500/30'
                : 'text-gray-400 hover:text-white'
            ]">
              Create New Patient
            </button>
          </div>

          <!-- Existing Patient -->
          <div v-if="patientMode === 'existing'" class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Search Patients</label>
                <div class="relative">
                  <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0118 0z"></path>
                  </svg>
                  <input
                    v-model="patientSearch"
                    @input="debounceLoadPatients"
                    @keyup.enter="handleSearchEnter"
                    type="text"
                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                    placeholder="Search by name or patient ID... (Press Enter to auto-select)"
                  />
                </div>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Or Enter Patient ID Manually</label>
                <div class="flex gap-2">
                  <input
                    v-model="manualPatientId"
                    type="text"
                    class="flex-1 px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                    placeholder="e.g., PAT-1000"
                  />
                  <button
                    @click="loadPatientByManualId"
                    :disabled="!manualPatientId || loadingManualPatient"
                    class="px-4 py-3 rounded-xl bg-primary-600 hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    {{ loadingManualPatient ? 'Loading...' : 'Find' }}
                  </button>
                  <button
                    @click="requestOtp"
                    :disabled="isOtpLoading || !manualPatientId"
                    class="px-4 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    {{ isOtpLoading ? 'Sending...' : 'Request OTP' }}
                  </button>
                </div>
                <!-- OTP Input -->
                <div v-if="otpSent" class="flex gap-2 mt-2">
                  <input
                    v-model="otpCode"
                    type="text"
                    placeholder="Enter OTP"
                    maxlength="6"
                    class="flex-1 px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                  />
                  <button
                    @click="verifyOtp"
                    :disabled="isOtpLoading || !otpCode"
                    class="px-4 py-3 rounded-xl bg-green-600 hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition"
                  >
                    {{ isOtpLoading ? 'Verifying...' : 'Verify OTP' }}
                  </button>
                </div>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Patient</label>
              <select
                v-model="selectedPatientId"
                @change="loadPatient"
                class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none"
              >
                <option value="" disabled>Select a patient from the list...</option>
                <option v-for="patient in patientsList" :key="patient.id" :value="patient.id">
                  {{ patient.patient_id }} - {{ patient.first_name }} {{ patient.last_name }} (Age: {{ patient.age }}, {{ patient.gender }}){{ patient.hospital?.name ? ' — ' + patient.hospital.name : '' }}
                </option>
              </select>
            </div>
            <div v-if="selectedPatient" class="p-4 rounded-xl bg-primary-900/30 border border-primary-700/50">
              <p class="text-primary-600 dark:text-primary-400 text-sm font-medium">
                ✓ Patient selected: {{ selectedPatient.first_name }} {{ selectedPatient.last_name }}
              </p>
              <p v-if="selectedPatient.hospital?.name" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                🏥 Hospital: {{ selectedPatient.hospital.name }}{{ selectedPatient.hospital.hospital_id ? ' (ID: ' + selectedPatient.hospital.hospital_id + ')' : '' }}
              </p>
            </div>
          </div>

          <!-- New Patient Form -->
          <div v-else class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">First Name</label>
                <input
                  v-model="form.first_name"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Last Name</label>
                <input
                  v-model="form.last_name"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Age</label>
                <input
                  v-model.number="form.age"
                  type="number"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Gender</label>
                <select
                  v-model="form.gender"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none"
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Weight (kg)</label>
                <input
                  v-model.number="form.weight"
                  type="number"
                  step="0.1"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">City</label>
                <input
                  v-model="form.city"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Oxygen Saturation (SpO2 %)</label>
                <input
                  v-model.number="form.oxygen_saturation_spo2"
                  type="number"
                  step="0.1"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Symptoms & History -->
        <div v-if="currentStep === 2" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-blue-600 to-blue-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Symptoms & Clinical History</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Record patient symptoms and risk factors</p>
            </div>
          </div>
          <div class="space-y-4">
            <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Symptoms</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div v-for="symptom in symptomsList" :key="symptom.key" class="flex items-center gap-2">
                <select v-model="form[symptom.key]" class="flex-1 px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-sm text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
                <span class="text-sm text-gray-700 dark:text-gray-300 text-left min-w-[140px]">{{ symptom.label }}</span>
              </div>
            </div>
          </div>
          <div class="space-y-2">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">Persistent Cough Duration (weeks)</label>
            <input
              v-model.number="form.persistent_cough_duration_weeks"
              type="number"
              class="w-full px-4 py-3 rounded-xl border border-gray-600 bg-gray-700/60 text-white placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
            />
          </div>
          <div class="space-y-4">
            <h4 class="text-sm font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wide">Risk Factors</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Contact with TB Patient</label>
                <select v-model="form.contact_with_tb_patient" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Previous TB Treatment</label>
                <select v-model="form.previous_tb_treatment" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">HIV Status</label>
                <select v-model="form.hiv" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Diabetes</label>
                <select v-model="form.diabetes" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Smoking Status</label>
                <select v-model="form.smoking_status" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Never">Never</option>
                  <option value="Former">Former</option>
                  <option value="Current">Current</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Alcohol Use</label>
                <select v-model="form.alcohol_use" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Never">Never</option>
                  <option value="Occasional">Occasional</option>
                  <option value="Regular">Regular</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 3: Antibiotic Assessment -->
        <div v-if="currentStep === 3" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-600 to-amber-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Antibiotic Usage Assessment</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Assess antibiotic history to detect misuse and resistance risks</p>
            </div>
          </div>

          <div class="space-y-4">
            <div class="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700">
              <p class="text-sm text-amber-700 dark:text-amber-400">
                This assessment helps identify antibiotic misuse, overuse, and resistance risks before diagnosis.
              </p>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  <input type="checkbox" v-model="antibioticAssessment.used_antibiotics_before" class="rounded text-amber-600">
                  <span class="text-sm text-gray-900 dark:text-white">Has used antibiotics before?</span>
                </label>
              </div>
              <div>
                <label class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  <input type="checkbox" v-model="antibioticAssessment.self_medicated" class="rounded text-amber-600">
                  <span class="text-sm text-gray-900 dark:text-white">Self-medicated antibiotics?</span>
                </label>
              </div>
              <div>
                <label class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  <input type="checkbox" v-model="antibioticAssessment.stopped_early" class="rounded text-amber-600">
                  <span class="text-sm text-gray-900 dark:text-white">Stopped treatment early?</span>
                </label>
              </div>
              <div>
                <label class="flex items-center gap-2 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700">
                  <input type="checkbox" v-model="antibioticAssessment.completed_treatment" class="rounded text-amber-600">
                  <span class="text-sm text-gray-900 dark:text-white">Completed full treatment?</span>
                </label>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Which antibiotics were taken?</label>
              <div class="relative">
                <input
                  v-model="antibioticSearch"
                  @input="debounceLoadAntibiotics"
                  @focus="loadAntibioticsList"
                  type="text"
                  placeholder="Click to see antibiotics or search (e.g., Amoxicillin)..."
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-amber-500 outline-none"
                />
                <div v-if="antibioticsList.length > 0" class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                  <div
                    v-for="antibiotic in antibioticsList"
                    :key="antibiotic.id"
                    @click="selectAntibiotic(antibiotic)"
                    class="px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-sm text-gray-900 dark:text-white border-b border-gray-100 dark:border-gray-700 last:border-0"
                  >
                    <div class="font-medium">{{ antibiotic.drug_name }}</div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">{{ antibiotic.atc_code }}</div>
                  </div>
                </div>
                <div v-if="antibioticsList.length === 0 && antibioticSearch" class="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-xl shadow-lg p-3 text-sm text-gray-500 dark:text-gray-400">
                  No antibiotics found matching "{{ antibioticSearch }}"
                </div>
              </div>
              <div v-if="selectedAntibiotics.length > 0" class="mt-2 flex flex-wrap gap-2">
                <span
                  v-for="(antibiotic, index) in selectedAntibiotics"
                  :key="index"
                  class="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-300 rounded-full text-sm"
                >
                  {{ antibiotic.drug_name }}
                  <button @click="removeAntibiotic(index)" class="hover:text-amber-600 dark:hover:text-amber-400">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                    </svg>
                  </button>
                </span>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Duration of antibiotic use (days)</label>
              <input
                v-model.number="antibioticAssessment.duration_days"
                type="number"
                placeholder="Number of days"
                class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-amber-500 outline-none"
              />
            </div>

            <button
              @click="runAntibioticAssessment"
              :disabled="!selectedPatientId"
              class="w-full py-3 px-4 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-700 hover:to-amber-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-all shadow-lg shadow-amber-500/30"
            >
              Run Antibiotic Assessment
            </button>

            <!-- Assessment Results -->
            <div v-if="antibioticAssessmentResult" class="space-y-4">
              <div class="p-4 rounded-xl" :class="antibioticAssessmentResult.risk_factors.resistance_risk === 'high' ? 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700' : antibioticAssessmentResult.risk_factors.resistance_risk === 'medium' ? 'bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700' : 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-700'">
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-sm font-bold" :class="antibioticAssessmentResult.risk_factors.resistance_risk === 'high' ? 'text-red-800 dark:text-red-300' : antibioticAssessmentResult.risk_factors.resistance_risk === 'medium' ? 'text-amber-800 dark:text-amber-300' : 'text-green-800 dark:text-green-300'">
                    Resistance Risk: {{ antibioticAssessmentResult.risk_factors.resistance_risk.toUpperCase() }}
                  </h4>
                  <span class="text-2xl font-bold" :class="antibioticAssessmentResult.risk_factors.resistance_risk === 'high' ? 'text-red-600 dark:text-red-400' : antibioticAssessmentResult.risk_factors.resistance_risk === 'medium' ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'">
                    {{ antibioticAssessmentResult.risk_factors.risk_score }}%
                  </span>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div v-if="antibioticAssessmentResult.risk_factors.self_medication" class="flex items-center gap-1 text-red-600 dark:text-red-400">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>
                    Self-medication detected
                  </div>
                  <div v-if="antibioticAssessmentResult.risk_factors.incomplete_treatment" class="flex items-center gap-1 text-red-600 dark:text-red-400">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>
                    Incomplete treatment
                  </div>
                  <div v-if="antibioticAssessmentResult.risk_factors.overuse" class="flex items-center gap-1 text-amber-600 dark:text-amber-400">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>
                    Potential overuse
                  </div>
                </div>
              </div>

              <div v-if="antibioticAssessmentResult.recommendations.length > 0" class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700">
                <h4 class="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-3">Recommendations</h4>
                <div class="space-y-2">
                  <div v-for="(rec, index) in antibioticAssessmentResult.recommendations" :key="index" class="flex items-start gap-2">
                    <span class="text-blue-600 dark:text-blue-400 mt-0.5">•</span>
                    <div>
                      <p class="text-sm font-medium text-gray-900 dark:text-white">{{ rec.action }}</p>
                      <p class="text-xs text-gray-600 dark:text-gray-400">{{ rec.reason }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Lab Results -->
        <div v-if="currentStep === 4" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Lab Test Results</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">View lab results submitted by technicians</p>
            </div>
          </div>

          <!-- Patient's Lab Results from Database -->
          <div v-if="patientLabTests.length > 0" class="space-y-4">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Patient's Lab Results</h4>
            <div v-for="test in patientLabTests" :key="test.id" class="p-4 rounded-xl border relative z-10 transition-all" :class="selectedLabTests.some(t => t.id === test.id) ? 'bg-indigo-100 dark:bg-indigo-900/30 border-indigo-500 dark:border-indigo-400 ring-2 ring-indigo-300 dark:ring-indigo-600' : 'bg-gray-50 dark:bg-gray-700/30 border-gray-200 dark:border-gray-600'">
              <div class="flex justify-between items-start mb-2">
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white">{{ test.test_type }}</h4>
                <span class="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                  Completed
                </span>
              </div>
              <div class="space-y-2 text-sm">
                <p class="text-gray-500 dark:text-gray-400">Result: <span :class="['font-medium', getResultColor(test.results)]">{{ test.results || 'Pending' }}</span></p>
                <p v-if="test.notes" class="text-gray-500 dark:text-gray-400">Notes: <span class="text-gray-900 dark:text-white">{{ test.notes }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Completed by: <span class="text-gray-900 dark:text-white">Tech #{{ test.completed_by }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Completed at: <span class="text-gray-900 dark:text-white">{{ formatDate(test.completed_at) }}</span></p>
              </div>
              <button
                @click.stop="useLabResult(test)"
                class="mt-3 px-3 py-1 text-xs font-medium rounded-lg cursor-pointer pointer-events-auto"
                :class="selectedLabTests.some(t => t.id === test.id) ? 'bg-indigo-700 hover:bg-indigo-800 text-white' : 'bg-indigo-600 hover:bg-indigo-700 text-white'"
                type="button"
              >
                {{ selectedLabTests.some(t => t.id === test.id) ? 'Selected' : 'Use This Result' }}
              </button>
            </div>
          </div>

          <div v-else class="p-6 text-center text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-xl">
            <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p>No lab results found for this patient</p>
            <p class="text-xs mt-1">Request a new lab test below</p>
          </div>

          <!-- Drug Resistance Info (if available) -->
          <div v-if="form.drug_resistance" class="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700">
            <div class="flex items-center gap-2 mb-2">
              <svg class="w-5 h-5 text-amber-600 dark:text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
              <h4 class="text-sm font-semibold text-amber-800 dark:text-amber-300">Drug Resistance Information</h4>
            </div>
            <p class="text-sm text-amber-700 dark:text-amber-400">{{ form.drug_resistance }}</p>
            <p class="text-xs text-amber-600 dark:text-amber-500 mt-1">This information will be used to adjust the treatment regimen.</p>
          </div>

          <!-- Request New Lab Test -->
          <div class="mt-6 p-4 bg-indigo-50 dark:bg-indigo-900/20 rounded-xl border border-indigo-200 dark:border-indigo-700">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Request Lab Tests (Select Multiple)</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="Sputum Smear" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">Sputum Smear</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="GeneXpert" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">GeneXpert MTB/RIF</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="Chest X-ray" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">Chest X-ray</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="TB Culture" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">TB Culture</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="TST" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">Tuberculin Skin Test (TST)</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="IGRA" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">IGRA</span>
              </label>
              <label class="flex items-center gap-2 p-2 rounded-lg bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-600">
                <input type="checkbox" v-model="labTestRequest.test_types" value="Drug Susceptibility" class="rounded text-indigo-600">
                <span class="text-sm text-gray-900 dark:text-white">Drug Susceptibility Test</span>
              </label>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-3">
              <div>
                <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Priority</label>
                <select v-model="labTestRequest.priority" class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm">
                  <option value="routine">Routine</option>
                  <option value="urgent">Urgent</option>
                  <option value="emergency">Emergency</option>
                </select>
              </div>
            </div>
            <div class="mb-3">
              <label class="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">Notes (optional)</label>
              <textarea v-model="labTestRequest.notes" rows="2" placeholder="Additional instructions or clinical context..." class="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"></textarea>
            </div>
            <button
              @click="requestLabTest"
              :disabled="labTestRequest.test_types.length === 0 || !selectedPatientId"
              class="w-full py-2 px-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
            >
              Request {{ labTestRequest.test_types.length }} Lab Test{{ labTestRequest.test_types.length !== 1 ? 's' : '' }}
            </button>
            <p v-if="labTestRequestMessage" class="mt-2 text-xs" :class="labTestRequestSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'">
              {{ labTestRequestMessage }}
            </p>
          </div>

          <!-- Selected Lab Tests Display -->
          <div v-if="selectedLabTests.length > 0" class="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 border-2 border-indigo-300 dark:border-indigo-700 mb-4">
            <div class="flex items-center gap-2 mb-3">
              <div class="w-6 h-6 rounded-full bg-indigo-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <h4 class="text-sm font-bold text-indigo-800 dark:text-indigo-300">Using {{ selectedLabTests.length }} Lab Result{{ selectedLabTests.length !== 1 ? 's' : '' }}</h4>
            </div>
            <div class="space-y-2">
              <div v-for="test in selectedLabTests" :key="test.id" class="text-sm p-2 rounded bg-white dark:bg-gray-800/50">
                <p class="font-semibold text-gray-900 dark:text-white">{{ test.test_type }}</p>
                <p class="text-gray-600 dark:text-gray-400">Result: <span :class="['font-medium', getResultColor(test.results)]">{{ test.results }}</span></p>
                <p class="text-xs text-gray-500 dark:text-gray-500">Completed: {{ formatDate(test.completed_at) }}</p>
              </div>
            </div>
          </div>

          <!-- Manual Entry Fallback -->
          <div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Or manually enter lab findings:</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sputum Smear</label>
                <select v-model="form.sputum_smear_test" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="Unknown">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">GeneXpert</label>
                <select v-model="form.genexpert_test" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="Unknown">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Chest X-ray</label>
                <select v-model="form.chest_xray" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="Unknown">Unknown</option>
                  <option value="Normal">Normal</option>
                  <option value="Abnormal">Abnormal</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">TB Culture</label>
                <select v-model="form.tb_culture" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                  <option value="Inconclusive">Inconclusive</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">TST (Tuberculin Skin Test)</label>
                <select v-model="form.tst" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">IGRA</label>
                <select v-model="form.igra" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Drug Resistance</label>
                <select v-model="form.drug_resistance" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 5: Review & Diagnose -->
        <div v-if="currentStep === 5" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-amber-600 to-amber-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Review & Diagnose</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Review patient data and run diagnosis</p>
            </div>
          </div>
          
          <!-- Error Message -->
          <div v-if="diagnosisError" class="p-4 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800">
            <p class="text-sm text-red-600 dark:text-red-400">{{ diagnosisError }}</p>
          </div>
          
          <div class="space-y-4">
            <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                Patient Summary
              </h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                <p class="text-gray-500 dark:text-gray-400">Name: <span class="text-gray-900 dark:text-white font-medium">{{ form.first_name }} {{ form.last_name }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Age: <span class="text-gray-900 dark:text-white font-medium">{{ form.age }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Gender: <span class="text-gray-900 dark:text-white font-medium">{{ form.gender }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Patient ID: <span class="text-gray-900 dark:text-white font-medium">{{ form.patient_id }}</span></p>
              </div>
            </div>
            <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Key Symptoms & Factors
              </h4>
              <div class="space-y-2 text-sm">
                <div class="flex flex-wrap gap-2">
                  <span v-for="symptom in symptomsList.filter(s => form[s.key] === 'Yes')" :key="symptom.key" class="px-3 py-1 rounded-full text-xs font-medium bg-green-600 text-white border border-green-500">
                    {{ symptom.label }}
                  </span>
                  <span v-if="symptomsList.filter(s => form[s.key] === 'Yes').length === 0" class="text-gray-400 dark:text-gray-500 text-sm">No symptoms selected</span>
                </div>
                <div v-if="form.symptoms" class="mt-2">
                  <p class="text-gray-500 dark:text-gray-400">Additional symptoms: <span class="text-gray-900 dark:text-white font-medium">{{ form.symptoms }}</span></p>
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-2">
                  <p v-if="form.hiv" class="text-gray-500 dark:text-gray-400">HIV: <span :class="['font-medium', form.hiv === 'Yes' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.hiv }}</span></p>
                  <p v-if="form.diabetes" class="text-gray-500 dark:text-gray-400">Diabetes: <span :class="['font-medium', form.diabetes === 'Yes' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.diabetes }}</span></p>
                  <p v-if="form.contact_with_tb_patient" class="text-gray-500 dark:text-gray-400">TB Contact: <span :class="['font-medium', form.contact_with_tb_patient === 'Yes' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.contact_with_tb_patient }}</span></p>
                  <p v-if="form.previous_tb_treatment" class="text-gray-500 dark:text-gray-400">Previous TB Treatment: <span class="text-gray-900 dark:text-white font-medium">{{ form.previous_tb_treatment }}</span></p>
                  <p v-if="form.smoking_status" class="text-gray-500 dark:text-gray-400">Smoking: <span class="text-gray-900 dark:text-white font-medium">{{ form.smoking_status }}</span></p>
                  <p v-if="form.alcohol_use" class="text-gray-500 dark:text-gray-400">Alcohol Use: <span class="text-gray-900 dark:text-white font-medium">{{ form.alcohol_use }}</span></p>
                </div>
              </div>
            </div>
            <div class="p-4 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Lab Results
              </h4>
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
                <p v-if="form.sputum_smear_test && form.sputum_smear_test !== 'Unknown'" class="text-gray-500 dark:text-gray-400">Sputum Smear: <span :class="['font-medium', form.sputum_smear_test === 'Positive' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.sputum_smear_test }}</span></p>
                <p v-if="form.genexpert_test && form.genexpert_test !== 'Unknown'" class="text-gray-500 dark:text-gray-400">GeneXpert: <span :class="['font-medium', form.genexpert_test === 'Positive' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.genexpert_test }}</span></p>
                <p v-if="form.chest_xray && form.chest_xray !== 'Unknown'" class="text-gray-500 dark:text-gray-400">Chest X-ray: <span :class="['font-medium', form.chest_xray === 'Abnormal' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.chest_xray }}</span></p>
                <p v-if="form.tb_culture && form.tb_culture !== '' && form.tb_culture !== 'Unknown'" class="text-gray-500 dark:text-gray-400">TB Culture: <span :class="['font-medium', form.tb_culture === 'Positive' ? 'text-red-600 dark:text-red-400' : form.tb_culture === 'Negative' ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-300']">{{ form.tb_culture }}</span></p>
                <p v-if="form.tst && form.tst !== '' && form.tst !== 'Unknown'" class="text-gray-500 dark:text-gray-400">TST: <span :class="['font-medium', form.tst === 'Positive' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.tst }}</span></p>
                <p v-if="form.igra && form.igra !== '' && form.igra !== 'Unknown'" class="text-gray-500 dark:text-gray-400">IGRA: <span :class="['font-medium', form.igra === 'Positive' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.igra }}</span></p>
                <p v-if="form.drug_resistance && form.drug_resistance !== ''" class="text-gray-500 dark:text-gray-400">Drug Resistance: <span :class="['font-medium', form.drug_resistance === 'Yes' ? 'text-red-600 dark:text-red-400' : 'text-green-600 dark:text-green-400']">{{ form.drug_resistance }}</span></p>
                <p v-if="!form.sputum_smear_test || form.sputum_smear_test === 'Unknown'" class="text-gray-400 dark:text-gray-500 text-sm col-span-2">No lab results entered</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 6: Results -->
        <div v-if="currentStep === 6 && diagnosisResult" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Diagnosis Results</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Complete analysis and treatment recommendations</p>
            </div>
          </div>

          <!-- Risk Assessment Banner -->
          <div :class="[
            'p-4 rounded-xl border-l-4',
            diagnosisResult.symptom_analysis?.risk_level === 'HIGH RISK' 
              ? 'bg-red-50 dark:bg-red-900/20 border-red-500' 
              : diagnosisResult.symptom_analysis?.risk_level === 'MODERATE RISK' 
              ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' 
              : 'bg-green-50 dark:bg-green-900/20 border-green-500'
          ]">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-xs font-semibold uppercase tracking-wide mb-1" :class="[
                  diagnosisResult.symptom_analysis?.risk_level === 'HIGH RISK' ? 'text-red-600 dark:text-red-400' 
                    : diagnosisResult.symptom_analysis?.risk_level === 'MODERATE RISK' 
                    ? 'text-yellow-600 dark:text-yellow-400' 
                    : 'text-green-600 dark:text-green-400'
                ]">Risk Assessment</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ diagnosisResult.symptom_analysis?.risk_level_display || 'Unknown' }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">Risk Score: {{ diagnosisResult.symptom_analysis?.risk_score }}/100</p>
              </div>
              <div class="text-right">
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ diagnosisResult.who_standards?.primary_diagnosis || 'Pending' }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">Primary Diagnosis</p>
              </div>
            </div>
          </div>

          <!-- Resistance Warning for Returning Patients (HIGH PRIORITY) -->
          <div v-if="diagnosisResult.resistance_warning && diagnosisResult.resistance_warning.has_previous_treatment" class="p-5 rounded-xl bg-gradient-to-br from-red-50 to-rose-50 dark:from-red-900/20 dark:to-rose-900/20 border-2 border-red-300 dark:border-red-700">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-lg font-bold text-red-800 dark:text-red-300">Resistance Pattern Alert</h4>
                <p class="text-xs text-red-600 dark:text-red-400">Previous treatment history detected</p>
              </div>
            </div>
            <div class="space-y-3">
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-red-200 dark:border-red-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">Previous Medications</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(med, i) in diagnosisResult.resistance_warning.previous_medications" :key="i" class="px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                    {{ med }}
                  </span>
                </div>
              </div>
              <div v-if="diagnosisResult.resistance_warning.resistance_detected" class="p-3 rounded-lg bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-600">
                <p class="text-sm font-semibold text-red-800 dark:text-red-300 mb-2">⚠️ Resistance Detected</p>
                <p class="text-xs text-red-700 dark:text-red-400 mb-2">The following drugs show resistance patterns:</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(drug, i) in diagnosisResult.resistance_warning.resistant_drugs" :key="i" class="px-3 py-1 rounded-full text-xs font-bold bg-red-200 text-red-900 dark:bg-red-800 dark:text-red-200 border border-red-400">
                    {{ drug }}
                  </span>
                </div>
                <p class="text-xs text-red-700 dark:text-red-400 mt-2">Regimen has been adjusted to avoid resistant medications.</p>
              </div>
              <div v-else class="p-3 rounded-lg bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-600">
                <p class="text-sm font-semibold text-green-800 dark:text-green-300">✓ No Resistance Detected</p>
                <p class="text-xs text-green-700 dark:text-green-400">Standard regimen can be used based on previous treatment history.</p>
              </div>
            </div>
          </div>

          <!-- Treatment Regimen Card -->
          <div class="p-6 rounded-xl bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-900/20 dark:to-blue-900/20 border border-indigo-200 dark:border-indigo-700">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-lg font-bold text-gray-900 dark:text-white">Treatment Regimen</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">WHO-aligned TB treatment protocol</p>
              </div>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Regimen</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.treatment_recommendation?.regimen_name }}</p>
              </div>
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Duration</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.treatment_recommendation?.duration }}</p>
              </div>
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Urgency</p>
                <p :class="[
                  'text-base font-bold',
                  diagnosisResult.treatment_recommendation?.urgency === 'HIGH' ? 'text-red-600 dark:text-red-400'
                    : diagnosisResult.treatment_recommendation?.urgency === 'MODERATE' ? 'text-yellow-600 dark:text-yellow-400'
                    : 'text-green-600 dark:text-green-400'
                ]">{{ diagnosisResult.treatment_recommendation?.urgency }}</p>
              </div>
            </div>

            <!-- Medications List -->
            <div class="p-4 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 mb-4">
              <p class="text-sm font-semibold text-gray-900 dark:text-white mb-3">Prescribed Medications</p>
              <div class="space-y-3">
                <div v-if="diagnosisResult.treatment_recommendation?.drugs" class="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
                  <div class="w-8 h-8 rounded-full bg-indigo-100 dark:bg-indigo-900/30 flex items-center justify-center shrink-0">
                    <svg class="w-4 h-4 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path>
                    </svg>
                  </div>
                  <div class="flex-1">
                    <p class="font-semibold text-gray-900 dark:text-white">{{ diagnosisResult.treatment_recommendation.drugs }}</p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">{{ diagnosisResult.treatment_recommendation?.dosage }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Antibiotic Recommendations (if drug resistance detected) -->
            <div v-if="diagnosisResult.drug_resistance === 'Yes' || antibioticAssessmentResult?.risk_factors?.resistance_risk === 'high'" class="p-4 rounded-lg bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border-2 border-amber-300 dark:border-amber-700 mb-4">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-8 h-8 rounded-lg bg-amber-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                  </svg>
                </div>
                <p class="text-base font-bold text-amber-800 dark:text-amber-300">Alternative Antibiotic Recommendations</p>
              </div>
              <p class="text-sm text-amber-700 dark:text-amber-400 mb-3">
                Based on hospital antibiogram and patient resistance patterns, consider these alternatives:
              </p>
              <button
                @click="getAntibioticRecommendations"
                :disabled="!selectedPatientId || loadingRecommendations"
                class="w-full py-2 px-4 bg-amber-600 hover:bg-amber-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors"
              >
                {{ loadingRecommendations ? 'Loading...' : 'Get Antibiotic Recommendations' }}
              </button>
              <div v-if="antibioticRecommendations.length > 0" class="mt-4 space-y-2">
                <div v-for="(rec, index) in antibioticRecommendations" :key="index" class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-amber-200 dark:border-amber-700">
                  <div class="flex justify-between items-start mb-2">
                    <p class="font-semibold text-gray-900 dark:text-white">{{ rec.antibiotic }}</p>
                    <span class="px-2 py-1 text-xs font-medium rounded-full" :class="rec.recommendation_strength === 'high' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'">
                      {{ rec.recommendation_strength }} confidence
                    </span>
                  </div>
                  <div class="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Susceptibility</p>
                      <p class="font-medium text-green-600 dark:text-green-400">{{ rec.susceptibility_rate }}%</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Resistance</p>
                      <p class="font-medium text-red-600 dark:text-red-400">{{ rec.resistance_rate }}%</p>
                    </div>
                  </div>
                  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    Based on {{ rec.total_samples }} samples
                  </div>
                </div>
              </div>
            </div>

            <!-- Detailed Dosage Breakdown - Per Drug (Only show if TB detected) -->
            <div v-if="diagnosisResult.treatment_recommendation?.medicines && diagnosisResult.treatment_recommendation.medicines.length > 0 && diagnosisResult.treatment_recommendation?.recommendation !== 'No medication needed'" class="p-4 rounded-lg bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 border-2 border-green-300 dark:border-green-700 mb-4">
              <div class="flex items-center gap-2 mb-4">
                <div class="w-8 h-8 rounded-lg bg-green-600 flex items-center justify-center">
                  <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <p class="text-base font-bold text-green-800 dark:text-green-300">Dosage Breakdown by Drug</p>
              </div>
              
              <!-- Display individual drugs if available -->
              <div v-if="diagnosisResult.treatment_recommendation?.medicines && diagnosisResult.treatment_recommendation.medicines.length > 0" class="space-y-3">
                <div v-for="(med, index) in diagnosisResult.treatment_recommendation.medicines" :key="index" class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700">
                  <div class="flex justify-between items-start mb-2">
                    <p class="font-semibold text-gray-900 dark:text-white">{{ med.name }}</p>
                    <span class="px-2 py-1 text-xs font-medium rounded-full" :class="med.phase === 'intensive' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300' : med.phase === 'continuation' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300' : 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'">
                      {{ med.phase === 'intensive' ? 'Intensive' : med.phase === 'continuation' ? 'Continuation' : 'Continuous' }}
                    </span>
                  </div>
                  <div class="grid grid-cols-2 sm:grid-cols-4 gap-2 text-sm">
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Dosage</p>
                      <p class="font-medium text-gray-900 dark:text-white">{{ med.dosage_mg }} mg</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Frequency</p>
                      <p class="font-medium text-gray-900 dark:text-white">{{ med.frequency }}</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Duration</p>
                      <p class="font-medium text-gray-900 dark:text-white">{{ med.duration_days }} days</p>
                    </div>
                    <div>
                      <p class="text-xs text-gray-500 dark:text-gray-400">Total Tablets</p>
                      <p class="font-medium text-green-600 dark:text-green-400">{{ med.total_tablets }}</p>
                    </div>
                  </div>
                  <div class="mt-2 text-xs text-gray-500 dark:text-gray-400">
                    {{ med.tablets_per_dose }} tablet(s) per dose
                  </div>
                </div>
              </div>
              
              <!-- Fallback to single calculation if no detailed medicines -->
              <div v-else>
                <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Dosage</p>
                    <p class="text-lg font-bold text-gray-900 dark:text-white">{{ calculatedDosage.dosageMg }} <span class="text-sm font-normal">mg</span></p>
                  </div>
                  <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Frequency</p>
                    <p class="text-lg font-bold text-gray-900 dark:text-white">{{ calculatedDosage.timesPerDay }} <span class="text-sm font-normal">times/day</span></p>
                  </div>
                  <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Duration</p>
                    <p class="text-lg font-bold text-gray-900 dark:text-white">{{ calculatedDosage.durationDays }} <span class="text-sm font-normal">days</span></p>
                  </div>
                  <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-green-200 dark:border-green-700">
                    <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Total Tablets</p>
                    <p class="text-lg font-bold text-green-600 dark:text-green-400">{{ calculatedDosage.totalTablets }}</p>
                  </div>
                </div>
                <div class="mt-3 p-3 rounded-lg bg-green-100 dark:bg-green-900/30 border border-green-300 dark:border-green-600">
                  <p class="text-sm font-semibold text-green-800 dark:text-green-300">Tablets per Dose: {{ calculatedDosage.tabletsPerDose }}</p>
                  <p class="text-xs text-green-700 dark:text-green-400 mt-1">Based on {{ calculatedDosage.tabletStrength }}mg tablet strength</p>
                </div>
              </div>
            </div>

            <!-- Dosage Instructions -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="p-4 rounded-lg bg-blue-100 dark:bg-blue-900/20 border border-blue-300 dark:border-blue-700">
                <div class="flex items-center gap-2 mb-2">
                  <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  <p class="text-sm font-semibold text-blue-800 dark:text-blue-300">Administration</p>
                </div>
                <p class="text-sm text-blue-700 dark:text-blue-400">{{ diagnosisResult.treatment_recommendation?.administration || 'Daily oral therapy under supervision' }}</p>
              </div>
              <div class="p-4 rounded-lg bg-purple-100 dark:bg-purple-900/20 border border-purple-300 dark:border-purple-700">
                <div class="flex items-center gap-2 mb-2">
                  <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  <p class="text-sm font-semibold text-purple-800 dark:text-purple-300">Monitoring</p>
                </div>
                <p class="text-sm text-purple-700 dark:text-purple-400">{{ diagnosisResult.treatment_recommendation?.monitoring || 'Regular clinical and lab monitoring required' }}</p>
              </div>
            </div>
          </div>

          <!-- TB Infection Assessment -->
          <div class="p-5 rounded-xl bg-gradient-to-br from-orange-50 to-amber-50 dark:from-orange-900/20 dark:to-amber-900/20 border border-orange-200 dark:border-orange-700">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl bg-orange-600 flex items-center justify-center">
                <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path>
                </svg>
              </div>
              <div>
                <h4 class="text-lg font-bold text-gray-900 dark:text-white">TB Infection Assessment</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">Detailed infection classification</p>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Primary Infection</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.infection_assessment?.primary_infection || 'Not specified' }}</p>
              </div>
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Infection Site</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.infection_assessment?.site || 'Not specified' }}</p>
              </div>
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Bacteria Species</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.bacteria_assessment?.species || 'Not identified' }}</p>
              </div>
              <div class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Resistance Pattern</p>
                <p class="text-base font-bold text-gray-900 dark:text-white">{{ diagnosisResult.resistance_profile?.classification || 'Not specified' }}</p>
              </div>
            </div>
          </div>

          <!-- Key Findings Grid (MEDIUM PRIORITY) -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div class="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center">
                  <svg class="w-4 h-4 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path>
                  </svg>
                </div>
                <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Bacteria Species</p>
              </div>
              <p class="text-lg font-bold text-gray-900 dark:text-white">{{ diagnosisResult.bacteria_assessment?.species || 'Unknown' }}</p>
            </div>
            <div class="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-red-100 dark:bg-red-900/30 flex items-center justify-center">
                  <svg class="w-4 h-4 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                  </svg>
                </div>
                <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Resistance</p>
              </div>
              <p class="text-lg font-bold text-gray-900 dark:text-white">{{ diagnosisResult.resistance_profile?.classification || 'Unknown' }}</p>
            </div>
            <div class="p-4 rounded-xl bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 shadow-sm">
              <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center">
                  <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <p class="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase">Confidence</p>
              </div>
              <p class="text-lg font-bold text-gray-900 dark:text-white">{{ diagnosisResult.test_evaluation?.confidence_percent || 0 }}%</p>
            </div>
          </div>

          <!-- ML Predictions (LOW PRIORITY) -->
          <div v-if="diagnosisResult.ml_prediction" class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
            <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              ML Model Predictions
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div v-if="diagnosisResult.ml_prediction.tb_status" class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm text-gray-600 dark:text-gray-400">TB Status</span>
                  <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="diagnosisResult.ml_prediction.tb_status.prediction === 'Yes' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'">
                    {{ diagnosisResult.ml_prediction.tb_status.prediction }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div class="bg-primary-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${diagnosisResult.ml_prediction.tb_status.confidence * 100}%` }"></div>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Confidence: {{ Math.round(diagnosisResult.ml_prediction.tb_status.confidence * 100) }}%</p>
              </div>
              <div v-if="diagnosisResult.ml_prediction.drug_resistance" class="p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
                <div class="flex justify-between items-center mb-2">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Drug Resistance</span>
                  <span class="px-2 py-1 rounded-full text-xs font-semibold" :class="diagnosisResult.ml_prediction.drug_resistance.prediction === 'Yes' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'">
                    {{ diagnosisResult.ml_prediction.drug_resistance.prediction }}
                  </span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                  <div class="bg-red-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${diagnosisResult.ml_prediction.drug_resistance.confidence * 100}%` }"></div>
                </div>
                <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Confidence: {{ Math.round(diagnosisResult.ml_prediction.drug_resistance.confidence * 100) }}%</p>
              </div>
            </div>
          </div>

          <!-- Clinical Notes -->
          <div v-if="diagnosisResult.treatment_recommendation?.notes" class="p-4 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-700">
            <div class="flex items-start gap-3">
              <svg class="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div>
                <p class="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">Clinical Notes</p>
                <p class="text-sm text-amber-700 dark:text-amber-400">{{ diagnosisResult.treatment_recommendation.notes }}</p>
              </div>
            </div>
          </div>

          <!-- Prescription Status -->
          <div v-if="prescriptionCreated" class="p-4 rounded-xl bg-green-50 dark:bg-green-900/20 border border-green-300 dark:border-green-700">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-green-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </div>
              <div>
                <p class="text-sm font-semibold text-green-800 dark:text-green-300">Prescription Created Automatically</p>
                <p class="text-xs text-green-700 dark:text-green-400">The pharmacist can now review and dispense the medication.</p>
              </div>
            </div>
          </div>

          <!-- No Prescription - No TB Detected -->
          <div v-if="!prescriptionCreated && diagnosisResult" class="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-300 dark:border-blue-700">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center">
                <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div>
                <p class="text-sm font-semibold text-blue-800 dark:text-blue-300">No Prescription Created</p>
                <p class="text-xs text-blue-700 dark:text-blue-400">No TB detected. Antibiotics not prescribed per antimicrobial stewardship guidelines.</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3">
            <button @click="printReport" class="flex-1 py-3 px-6 rounded-xl bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 font-semibold text-sm transition flex items-center justify-center gap-2 hover:bg-gray-50 dark:hover:bg-gray-700">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
              </svg>
              Print Report
            </button>
          </div>
        </div>

        <!-- Navigation Buttons -->
        <div class="flex flex-col sm:flex-row gap-3 pt-4 border-t border-gray-700 mt-6">
          <button v-if="currentStep > 1" @click="prevStep" class="flex-1 py-3 px-6 rounded-xl bg-gray-700 hover:bg-gray-600 text-white font-semibold text-sm transition flex items-center justify-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            Previous
          </button>
          <div class="flex-1"></div>
          <button v-if="currentStep < 4" @click="nextStep" :disabled="!canProceed" class="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-primary-500/30">
            Next
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
          <button v-if="currentStep === 4" @click="handleDiagnose" :disabled="isLoading" class="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-primary-500/30">
            <svg v-if="isLoading" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
            </svg>
            {{ isLoading ? 'Analyzing...' : 'Run Diagnosis & Predict' }}
          </button>
          <button v-if="currentStep === 5 && diagnosisResult" @click="nextStep" class="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-500 hover:to-primary-600 text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-primary-500/30">
            View Results & Treatment
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
          <button v-if="currentStep === 6" @click="resetDiagnosis" class="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-green-500/30">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.575-7.027M17 17v5h-5m10-3a7.004.004 0 00-7.027-4.576"></path>
            </svg>
            <span>Start New Diagnosis</span>
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
import NotificationModal from '~/components/NotificationModal.vue';
import { useAuth } from '~/composables/useAuth';
const { getPatients, diagnose, getDiagnoses, getPatientById } = useApi();
const { authToken } = useAuth();

const symptomsList = [
  { key: 'has_fever', label: 'Fever' },
  { key: 'has_cough', label: 'Cough' },
  { key: 'has_weight_loss', label: 'Weight Loss' },
  { key: 'has_night_sweats', label: 'Night Sweats' },
  { key: 'has_chest_pain', label: 'Chest Pain' },
  { key: 'has_blood', label: 'Hemoptysis' },
  { key: 'has_fatigue', label: 'Fatigue' },
  { key: 'has_shortness_of_breath', label: 'Shortness of Breath' }
];

const steps = [
  { id: 1, title: 'Patient' },
  { id: 2, title: 'Symptoms' },
  { id: 3, title: 'Antibiotic Assessment' },
  { id: 4, title: 'Lab Results' },
  { id: 5, title: 'Review' },
  { id: 6, title: 'Results' }
];

const currentStep = ref(1);
const totalSteps = computed(() => steps.length);
const patientMode = ref('new');
const patientsList = ref<any[]>([]);
const patientSearch = ref('');
const selectedPatientId = ref<string | number | null>(null);
const selectedPatient = ref<any>(null);
const manualPatientId = ref('');
const loadingManualPatient = ref(false);
const diagnoses = ref<any[]>([]);
const isLoading = ref(false);
const diagnosisResult = ref<any>(null);
const prescriptionCreated = ref(false);
const config = useRuntimeConfig()
const API_BASE = config.public.apiBase;

// OTP related
const findPatientId = ref('');
const otpCode = ref('');
const otpSent = ref(false);
const isOtpLoading = ref(false);

// Notification modal
const notification = ref({
  isOpen: false,
  title: '',
  message: '',
  type: 'info' as 'success' | 'error' | 'warning' | 'info'
});

const showNotification = (title: string, message: string, type: 'success' | 'error' | 'warning' | 'info' = 'info') => {
  notification.value = {
    isOpen: true,
    title,
    message,
    type
  };
};

const closeNotification = () => {
  notification.value.isOpen = false;
};

const requestOtp = async () => {
  findPatientId.value = manualPatientId.value;
  isOtpLoading.value = true;
  try {
    const res = await $fetch(`${config.public.apiBase}/patients/request-otp`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken.value}`
      },
      body: {
        patient_id: findPatientId.value
      }
    });
    if ((res as any).already_associated) {
      showNotification('Already Associated', 'Patient is already associated with your hospital! Click "Find" to load the patient.', 'info');
      // Refresh patients list to ensure the patient appears in search
      await loadPatientsList();
    } else {
      otpSent.value = true;
      showNotification('OTP Sent', 'OTP sent to patient\'s phone!', 'success');
    }
  } catch (e: any) {
    console.error('Request OTP failed:', e);
    showNotification('Error', e.data?.msg || 'Failed to send OTP', 'error');
  } finally {
    isOtpLoading.value = false;
  }
};

const verifyOtp = async () => {
  findPatientId.value = manualPatientId.value;
  isOtpLoading.value = true;
  try {
    const res = await $fetch(`${config.public.apiBase}/patients/verify-otp`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${authToken.value}`,
        'Content-Type': 'application/json'
      },
      body: {
        patient_id: findPatientId.value,
        otp_code: otpCode.value
      }
    });
    showNotification('OTP Verified', 'Patient is now associated with your hospital!', 'success');
    // Reset OTP state
    otpSent.value = false;
    otpCode.value = '';
    // Refresh patients list to include newly associated patient
    await loadPatientsList();
    // Load the patient
    await loadPatientByManualId();
  } catch (e: any) {
    console.error('Verify OTP failed:', e);
    showNotification('Verification Failed', e.data?.msg || 'Invalid or expired OTP', 'error');
  } finally {
    isOtpLoading.value = false;
  }
};

// Antibiotic assessment
const antibioticAssessment = ref({
  used_antibiotics_before: false,
  self_medicated: false,
  stopped_early: false,
  completed_treatment: false,
  which_antibiotics_text: '',
  duration_days: null
});
const antibioticAssessmentResult = ref<any>(null);

// Antibiotic autocomplete
const antibioticSearch = ref('');
const antibioticsList = ref<any[]>([]);
const showAntibioticDropdown = ref(false);
const selectedAntibiotics = ref<any[]>([]);

// Antibiotic recommendations
const antibioticRecommendations = ref<any[]>([]);
const loadingRecommendations = ref(false);

const { antibioticAssessment: apiAntibioticAssessment, recommendAntibiotics, getAntibiotics } = useApi();

const runAntibioticAssessment = async () => {
  if (!selectedPatientId.value) return;

  // Update which_antibiotics_text from selected antibiotics
  antibioticAssessment.value.which_antibiotics_text = selectedAntibiotics.value.map(a => a.drug_name).join(', ');

  try {
    const data = {
      used_antibiotics_before: antibioticAssessment.value.used_antibiotics_before,
      self_medicated: antibioticAssessment.value.self_medicated,
      stopped_early: antibioticAssessment.value.stopped_early,
      completed_treatment: antibioticAssessment.value.completed_treatment,
      which_antibiotics: selectedAntibiotics.value.map(a => a.drug_name),
      duration_days: antibioticAssessment.value.duration_days
    };

    const result = await apiAntibioticAssessment(Number(selectedPatientId.value), data);
    antibioticAssessmentResult.value = result;
  } catch (error) {
    console.error('Antibiotic assessment failed:', error);
  }
};

let antibioticDebounceTimer: number;
const debounceLoadAntibiotics = () => {
  clearTimeout(antibioticDebounceTimer);
  antibioticDebounceTimer = setTimeout(loadAntibioticsList, 300) as unknown as number;
};

const loadAntibioticsList = async () => {
  try {
    const res = await getAntibiotics(antibioticSearch.value, 50);
    antibioticsList.value = (res as any).antibiotics || [];
  } catch (e) {
    console.error('Failed to load antibiotics', e);
  }
};

const selectAntibiotic = (antibiotic: any) => {
  if (!selectedAntibiotics.value.find(a => a.id === antibiotic.id)) {
    selectedAntibiotics.value.push(antibiotic);
  }
  antibioticSearch.value = '';
  antibioticsList.value = [];
  showAntibioticDropdown.value = false;
};

const removeAntibiotic = (index: number) => {
  selectedAntibiotics.value.splice(index, 1);
};

const getAntibioticRecommendations = async () => {
  if (!selectedPatientId.value) return;
  
  loadingRecommendations.value = true;
  try {
    const data = {
      patient_id: Number(selectedPatientId.value),
      bacterial_species: form.value.bacteria_species || 'Mycobacterium tuberculosis'
    };
    
    const result = await recommendAntibiotics(data);
    antibioticRecommendations.value = result.recommendations || [];
  } catch (error) {
    console.error('Failed to get antibiotic recommendations:', error);
  } finally {
    loadingRecommendations.value = false;
  }
};

// Computed dosage breakdown
const calculatedDosage = computed(() => {
  if (!diagnosisResult.value) {
    return { dosageMg: 0, timesPerDay: 0, durationDays: 0, totalTablets: 0, tabletsPerDose: 0, tabletStrength: 0 };
  }
  
  const treatment = diagnosisResult.value.treatment_recommendation;
  const dosageText = treatment?.dosage || '300mg daily';
  
  // Parse dosage mg
  let dosageMg = 300;
  const mgMatch = dosageText.match(/(\d+)mg/);
  if (mgMatch) {
    dosageMg = parseInt(mgMatch[1]);
  }
  
  // Parse frequency
  let timesPerDay = 1;
  if (dosageText.toLowerCase().includes('twice') || dosageText.toLowerCase().includes('2 times')) {
    timesPerDay = 2;
  } else if (dosageText.toLowerCase().includes('3 times')) {
    timesPerDay = 3;
  }
  
  // Parse duration
  let durationDays = 180; // Default 6 months
  const durationText = treatment?.duration || '6 months';
  const monthMatch = durationText.match(/(\d+)\s*month/i);
  if (monthMatch) {
    durationDays = parseInt(monthMatch[1]) * 30;
  }
  
  // Tablet strength (default 300mg for TB drugs)
  const tabletStrength = 300;
  
  // Calculate tablets per dose
  const tabletsPerDose = Math.ceil(dosageMg / tabletStrength);
  
  // Calculate total tablets
  const totalTablets = tabletsPerDose * timesPerDay * durationDays;
  
  return {
    dosageMg,
    timesPerDay,
    durationDays,
    totalTablets,
    tabletsPerDose,
    tabletStrength
  };
});

const patientLabTests = ref<any[]>([]);

const labTestRequest = ref({
  test_types: [],
  priority: 'routine',
  notes: ''
});
const labTestRequestMessage = ref('');
const labTestRequestSuccess = ref(false);
const selectedLabTests = ref<any[]>([]);

const form = ref({
  patient_id: '',
  first_name: '',
  last_name: '',
  age: null,
  gender: '',
  weight: null,
  city: '',
  oxygen_saturation_spo2: null,
  symptoms: '',
  persistent_cough_duration_weeks: null,
  contact_with_tb_patient: '',
  previous_tb_treatment: '',
  hiv: '',
  diabetes: '',
  smoking_status: '',
  alcohol_use: '',
  sputum_smear_test: 'Unknown',
  genexpert_test: 'Unknown',
  chest_xray: 'Unknown',
  drug_resistance: '',
  antibiotic_usage_history: '',
  exposure_history: '',
  tb_culture: '',
  tst: '',
  igra: '',
  bacteria_species: '',
  tb_status_label: '',
  treatment_type: '',
  duration_of_treatment: null,
  treatment_outcome: '',
  relapse: '',
  mortality: '',
  complications: '',
  malnutrition: '',
  region: '',
  occupation: '',
  date_of_diagnosis: null,
  source_dataset: '',
  source_row_id: '',
  has_fever: '',
  has_cough: '',
  has_weight_loss: '',
  has_night_sweats: '',
  has_chest_pain: '',
  has_blood: '',
  has_fatigue: '',
  has_shortness_of_breath: ''
});

const canProceed = computed(() => {
  if (currentStep.value === 1) {
    if (patientMode.value === 'existing') {
      const isValid = selectedPatientId.value !== null && selectedPatientId.value !== '';
      return isValid;
    } else {
      return !!(form.value.first_name && form.value.last_name && form.value.age && form.value.gender);
    }
  }
  if (currentStep.value === 2) {
    return true;
  }
  if (currentStep.value === 3) {
    return true; // Antibiotic assessment is optional
  }
  if (currentStep.value === 4) {
    return true;
  }
  if (currentStep.value === 5) {
    return true;
  }
  return true;
});

const isStepAccessible = (step: number) => {
  return step > currentStep.value + 1 || (diagnosisResult.value && step > totalSteps.value);
};

const goToStep = (step: number) => {
  if (step <= currentStep.value || (diagnosisResult.value && step === totalSteps.value)) {
    currentStep.value = step;
  }
};

const nextStep = () => {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++;
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
};

let debounceTimer: number;
const debounceLoadPatients = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadPatientsList, 300) as unknown as number;
};

const loadPatientsList = async (searchTerm?: string) => {
  try {
    const searchToUse = searchTerm || patientSearch.value;
    const res = await getPatients(1, 50, searchToUse);
    patientsList.value = (res as any).patients || [];
    console.log('Loaded patients:', patientsList.value.length, 'search:', searchToUse);
    if (patientsList.value.length === 0 && searchToUse) {
      console.log('No patients found for search:', searchToUse);
    }
    console.log('Patient IDs in list:', patientsList.value.map(p => p.patient_id));
  } catch (e) {
    console.error('Failed to load patients', e);
    showNotification('Error', 'Failed to load patients list', 'error');
  }
};

const handleSearchEnter = async () => {
  if (!patientSearch.value) return;
  // Treat search input like manual patient ID - load and auto-select
  manualPatientId.value = patientSearch.value;
  await loadPatientByManualId();
};

const loadPatient = async () => {
  if (!selectedPatientId.value) return;
  const patient = patientsList.value.find(p => p.id === Number(selectedPatientId.value));
  if (!patient) return;
  selectedPatient.value = patient;
  Object.keys(form.value).forEach((key) => {
    if (patient.hasOwnProperty(key)) {
      form.value[key as keyof typeof form.value] = patient[key];
    }
  });
  
  // Auto-populate drug resistance from previous records
  await fetchPatientDrugResistance();
  
  // Load lab tests for this patient
  await fetchPatientLabTests();
};

const loadPatientByManualId = async () => {
  if (!manualPatientId.value) return;
  loadingManualPatient.value = true;
  try {
    // Load patients list with the manual patient ID as search term
    // This will trigger the exact patient_id match bypass in the backend
    await loadPatientsList(manualPatientId.value);
    
    console.log('Patients list after refresh:', patientsList.value.length);
    console.log('Searching for patient ID:', manualPatientId.value);
    
    // Search patients list by patient_id (case-insensitive)
    let patient = patientsList.value.find(p => {
      const match = p.patient_id && p.patient_id.toLowerCase() === manualPatientId.value.toLowerCase();
      if (match) console.log('Found patient:', p.patient_id);
      return match;
    });
    
    if (patient) {
      selectedPatientId.value = patient.id;
      selectedPatient.value = patient;
      Object.keys(form.value).forEach((key) => {
        if (patient.hasOwnProperty(key)) {
          form.value[key as keyof typeof form.value] = patient[key];
        }
      });
      // Auto-populate drug resistance and lab tests
      await fetchPatientDrugResistance();
      await fetchPatientLabTests();
    } else {
      console.log('Patient not found in list. List contents:', patientsList.value.map(p => p.patient_id));
      showNotification('Patient Not Found', 'Patient not found or not associated with your hospital. Use OTP verification to access cross-hospital patients.', 'error');
    }
  } catch (e) {
    console.error('Failed to load patient by ID', e);
    showNotification('Error', 'Failed to find patient. Please check your network connection or contact support.', 'error');
  } finally {
    loadingManualPatient.value = false;
  }
};

const fetchPatientDrugResistance = async () => {
  if (!selectedPatientId.value) return;
  try {
    const response = await fetch(`${API_BASE}/patients/${selectedPatientId.value}/drug-resistance`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (response.ok) {
      const data = await response.json();
      if (data.drug_resistance) {
        form.value.drug_resistance = data.drug_resistance;
        console.log('Auto-populated drug resistance:', data.drug_resistance);
      }
    }
  } catch (error) {
    console.error('Error fetching drug resistance:', error);
  }
};

const fetchPatientLabTests = async () => {
  if (!selectedPatientId.value) return;
  try {
    // Fetch lab tests across ALL hospitals the patient has visited
    const response = await fetch(`${API_BASE}/lab-tests?patient_id=${selectedPatientId.value}`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    const data = await response.json();
    patientLabTests.value = (data.lab_tests || []).filter(t => t.status === 'completed');

    // Also fetch previous diagnoses to pre-fill fields from most recent diagnosis
    await fetchAndPopulatePreviousDiagnosis();

    // Auto-populate form with most recent completed lab results
    autoPopulateLabResults();
  } catch (error) {
    console.error('Error fetching lab tests:', error);
  }
};

const fetchAndPopulatePreviousDiagnosis = async () => {
  if (!selectedPatientId.value) return;
  try {
    const response = await fetch(`${API_BASE}/diagnoses?patient_id=${selectedPatientId.value}&per_page=1`, {
      headers: { 'Authorization': `Bearer ${authToken.value}` }
    });
    if (!response.ok) return;
    const data = await response.json();
    const latest = (data.diagnoses || [])[0];
    if (!latest) return;

    // Pre-fill patient fields from most recent diagnosis details if not already set
    let details: any = {};
    try { details = JSON.parse(latest.details || '{}'); } catch { details = {}; }

    // Only fill fields the clinician hasn't already changed
    const fillIfEmpty = (key: string, value: any) => {
      if (value && (!form.value[key as keyof typeof form.value] || form.value[key as keyof typeof form.value] === 'Unknown' || form.value[key as keyof typeof form.value] === '')) {
        (form.value as any)[key] = value;
      }
    };

    // Fill from resistance profile
    const resistance = details.resistance_profile;
    if (resistance?.classification_code && resistance.classification_code !== 'DS') {
      fillIfEmpty('drug_resistance', 'Yes');
    }

    // Fill from bacteria assessment
    const bacteria = details.bacteria_assessment;
    if (bacteria?.species) fillIfEmpty('bacteria_species', bacteria.species);

    console.log('Pre-filled from previous diagnosis at hospital', latest.hospital_id);
  } catch (error) {
    console.error('Error fetching previous diagnosis:', error);
  }
};

const autoPopulateLabResults = () => {
  if (!patientLabTests.value || patientLabTests.value.length === 0) return;
  
  // Group tests by type and get the most recent completed one for each type
  const latestTests = {};
  patientLabTests.value.forEach(test => {
    const testType = test.test_type.toLowerCase();
    if (!latestTests[testType] || new Date(test.completed_at) > new Date(latestTests[testType].completed_at)) {
      latestTests[testType] = test;
    }
  });
  
  // Auto-populate form fields with latest results
  Object.values(latestTests).forEach(test => {
    const result = test.results?.toString().toLowerCase().trim();
    const testType = test.test_type.toLowerCase();
    
    if (testType.includes('sputum')) {
      if (result?.includes('positive')) form.value.sputum_smear_test = 'Positive';
      else if (result?.includes('negative')) form.value.sputum_smear_test = 'Negative';
    }
    if (testType.includes('genexpert')) {
      if (result?.includes('positive')) form.value.genexpert_test = 'Positive';
      else if (result?.includes('negative')) form.value.genexpert_test = 'Negative';
    }
    if (testType.includes('xray') || testType.includes('chest')) {
      if (result?.includes('normal') || result?.includes('negative')) form.value.chest_xray = 'Normal';
      else if (result?.includes('abnormal') || result?.includes('positive')) form.value.chest_xray = 'Abnormal';
    }
    if (testType.includes('culture')) {
      if (result?.includes('positive')) form.value.tb_culture = 'Positive';
      else if (result?.includes('negative')) form.value.tb_culture = 'Negative';
      else if (result?.includes('inconclusive')) form.value.tb_culture = 'Inconclusive';
    }
    if (testType.includes('tst')) {
      if (result?.includes('positive')) form.value.tst = 'Positive';
      else if (result?.includes('negative')) form.value.tst = 'Negative';
    }
    if (testType.includes('igra')) {
      if (result?.includes('positive')) form.value.igra = 'Positive';
      else if (result?.includes('negative')) form.value.igra = 'Negative';
    }
  });
  
  console.log('Auto-populated lab results from', Object.keys(latestTests).length, 'test types');
};

const requestLabTest = async () => {
  if (!selectedPatientId.value || labTestRequest.value.test_types.length === 0) {
    labTestRequestMessage.value = 'Please select a patient and at least one test type';
    labTestRequestSuccess.value = false;
    return;
  }

  const patientIdNum = parseInt(selectedPatientId.value);
  if (isNaN(patientIdNum)) {
    labTestRequestMessage.value = 'Invalid patient ID';
    labTestRequestSuccess.value = false;
    return;
  }

  try {
    console.log('Requesting lab tests for patient:', patientIdNum, 'tests:', labTestRequest.value.test_types);
    console.log('Auth token:', authToken.value);
    
    const requests = labTestRequest.value.test_types.map(testType => 
      fetch(`${API_BASE}/lab-tests`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${authToken.value}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          patient_id: patientIdNum,
          test_type: testType,
          notes: labTestRequest.value.notes
        })
      }).then(async response => {
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          console.error('Lab test request failed:', response.status, errorData);
          return { ok: false, error: errorData, testType };
        }
        return { ok: true, testType };
      })
    );

    const results = await Promise.all(requests);
    const allSuccessful = results.every(r => r.ok);
    const failedTests = results.filter(r => !r.ok);

    if (allSuccessful) {
      labTestRequestMessage.value = `${labTestRequest.value.test_types.length} lab test(s) requested successfully`;
      labTestRequestSuccess.value = true;
      labTestRequest.value = {
        test_types: [],
        priority: 'routine',
        notes: ''
      };
      setTimeout(() => {
        labTestRequestMessage.value = '';
      }, 3000);
    } else {
      const errorDetails = failedTests.map(f => `${f.testType}: ${f.error.msg || f.error.message || 'Unknown error'}`).join(', ');
      labTestRequestMessage.value = `Failed: ${errorDetails}`;
      labTestRequestSuccess.value = false;
    }
  } catch (error) {
    console.error('Error requesting lab tests:', error);
    labTestRequestMessage.value = `Network error: ${error.message}`;
    labTestRequestSuccess.value = false;
  }
};

const formatDate = (dateStr: string) => {
  if (!dateStr) return 'N/A';
  return new Date(dateStr).toLocaleDateString();
};

const getResultColor = (result: string) => {
  if (!result) return 'text-gray-500';
  const colors: Record<string, string> = {
    'Positive': 'text-red-600 font-bold',
    'Negative': 'text-green-600',
    'Abnormal': 'text-yellow-600',
    'Normal': 'text-blue-600',
    'Inconclusive': 'text-gray-600'
  };
  return colors[result] || 'text-gray-600';
};

const useLabResult = (test: any) => {
  console.log('Using lab result:', test);
  console.log('Test type:', test.test_type);
  console.log('Test results:', test.results);
  
  // Toggle selection (allow multiple)
  const index = selectedLabTests.value.findIndex(t => t.id === test.id);
  if (index >= 0) {
    // Deselect if already selected
    selectedLabTests.value.splice(index, 1);
  } else {
    // Add to selection
    selectedLabTests.value.push(test);
  }
  
  if (!test || !test.results) {
    console.log('Invalid test data or no results');
    return;
  }
  
  const result = test.results.toString().toLowerCase().trim();
  const testType = test.test_type.toLowerCase();
  
  console.log('Processed result:', result);
  console.log('Processed test type:', testType);
  
  // Map lab test results to form fields
  if (testType.includes('sputum')) {
    console.log('Processing sputum test');
    if (result.includes('positive')) {
      form.value.sputum_smear_test = 'Positive';
    } else if (result.includes('negative')) {
      form.value.sputum_smear_test = 'Negative';
    } else {
      form.value.sputum_smear_test = 'Unknown';
    }
    console.log('Updated sputum_smear_test:', form.value.sputum_smear_test);
  }
  if (testType.includes('genexpert')) {
    console.log('Processing genexpert test');
    if (result.includes('positive')) {
      form.value.genexpert_test = 'Positive';
    } else if (result.includes('negative')) {
      form.value.genexpert_test = 'Negative';
    } else {
      form.value.genexpert_test = 'Unknown';
    }
    console.log('Updated genexpert_test:', form.value.genexpert_test);
  }
  if (testType.includes('xray') || testType.includes('chest')) {
    console.log('Processing xray test');
    if (result.includes('normal') || result.includes('negative')) {
      form.value.chest_xray = 'Normal';
    } else if (result.includes('abnormal') || result.includes('positive')) {
      form.value.chest_xray = 'Abnormal';
    } else {
      form.value.chest_xray = 'Unknown';
    }
    console.log('Updated chest_xray:', form.value.chest_xray);
  }
  if (testType.includes('culture')) {
    console.log('Processing culture test');
    if (result.includes('positive')) {
      form.value.tb_culture = 'Positive';
    } else if (result.includes('negative')) {
      form.value.tb_culture = 'Negative';
    } else {
      form.value.tb_culture = 'Inconclusive';
    }
    console.log('Updated tb_culture:', form.value.tb_culture);
  }
  if (testType.includes('tst')) {
    console.log('Processing TST test');
    if (result.includes('positive')) {
      form.value.tst = 'Positive';
    } else if (result.includes('negative')) {
      form.value.tst = 'Negative';
    } else {
      form.value.tst = 'Unknown';
    }
    console.log('Updated tst:', form.value.tst);
  }
  if (testType.includes('igra')) {
    console.log('Processing IGRA test');
    if (result.includes('positive')) {
      form.value.igra = 'Positive';
    } else if (result.includes('negative')) {
      form.value.igra = 'Negative';
    } else {
      form.value.igra = 'Unknown';
    }
    console.log('Updated igra:', form.value.igra);
  }
  console.log('Form after using lab result:', form.value);
};

const diagnosisError = ref('');

const handleDiagnose = async () => {
  try {
    isLoading.value = true;
    diagnosisError.value = '';
    const res = await diagnose({ patient: form.value });
    diagnosisResult.value = res;
    currentStep.value = 5;
    await loadDiagnoses();
    
    // Only create prescription if TB is detected
    // Good practice: Don't prescribe antibiotics for non-TB cases
    const tbDetected = shouldCreatePrescription(res);
    if (tbDetected && res && selectedPatientId.value) {
      await autoCreatePrescription(res);
    } else if (!tbDetected) {
      console.log('No TB detected - prescription not created');
      prescriptionCreated.value = false;
    }
  } catch (e) {
    console.error('Diagnosis failed:', e);
    diagnosisError.value = 'Failed to get diagnosis. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const shouldCreatePrescription = (diagnosisData: any) => {
  // Check if TB is detected based on multiple indicators
  // Priority: ML prediction > Risk Level > Lab results > Treatment drugs
  
  // 1. ML prediction is the primary indicator - if it says No, don't prescribe
  const mlPrediction = diagnosisData.ml_prediction?.tb_status?.prediction;
  const mlConfidence = diagnosisData.ml_prediction?.tb_status?.confidence || 0;
  
  if (mlPrediction === 'No') {
    // If ML confidently says No (confidence > 50%), don't create prescription
    if (mlConfidence > 0.5) {
      console.log('ML predicts no TB with high confidence - no prescription');
      return false;
    }
  }
  
  // 2. Risk level - MINIMAL risk with no evidence of TB
  const riskLevel = diagnosisData.symptom_analysis?.risk_level;
  const riskScore = diagnosisData.symptom_analysis?.risk_score || 0;
  const primaryDiagnosis = diagnosisResult.value?.who_standards?.primary_diagnosis || '';
  
  if (riskLevel === 'MINIMAL RISK' && riskScore < 20) {
    // Check if primary diagnosis explicitly says no TB
    if (primaryDiagnosis.toLowerCase().includes('no evidence') || 
        primaryDiagnosis.toLowerCase().includes('not tb') ||
        primaryDiagnosis.toLowerCase().includes('unlikely')) {
      console.log('Minimal risk with no TB evidence - no prescription');
      return false;
    }
  }
  
  // 3. High or moderate risk level - create prescription
  if (riskLevel === 'HIGH RISK' || riskLevel === 'MODERATE RISK') {
    return true;
  }
  
  // 4. ML prediction indicates TB
  if (mlPrediction === 'Yes') {
    return true;
  }
  
  // 5. Treatment recommendation has actual drugs (but only if ML or risk supports it)
  const drugs = diagnosisData.treatment_recommendation?.drugs;
  if (drugs && drugs !== 'No medication needed' && drugs !== 'None') {
    // Only create if there's some supporting evidence
    const hasSupportingEvidence = 
      (mlPrediction === 'Yes') ||
      (riskLevel === 'HIGH RISK' || riskLevel === 'MODERATE RISK') ||
      (diagnosisData.who_standards?.primary_diagnosis?.toLowerCase().includes('tb'));
    
    if (hasSupportingEvidence) {
      return true;
    }
  }
  
  // 6. Positive lab results (but only if ML or risk supports it)
  const labPositive = 
    diagnosisData.who_standards?.primary_diagnosis?.toLowerCase().includes('tb') ||
    diagnosisData.bacteria_assessment?.species?.toLowerCase().includes('mycobacterium');
  
  if (labPositive) {
    // Only create if ML or risk supports it
    const hasSupportingEvidence = 
      (mlPrediction === 'Yes') ||
      (riskLevel === 'HIGH RISK' || riskLevel === 'MODERATE RISK');
    
    if (hasSupportingEvidence) {
      return true;
    }
  }
  
  // No TB detected - don't create prescription
  console.log('No TB detected based on combined indicators - no prescription');
  return false;
};

const autoCreatePrescription = async (diagnosisData: any) => {
  try {
    const token = authToken.value;
    const treatment = diagnosisData.treatment_recommendation;
    
    // Check if we have detailed medicines with dosages
    const medicines = treatment?.medicines;
    
    if (medicines && medicines.length > 0) {
      // Create individual prescriptions for each drug sequentially to avoid database deadlock
      let successCount = 0;
      for (const med of medicines) {
        const prescriptionData = {
          patient_id: selectedPatientId.value,
          diagnosis_id: null,
          medication: med.name,
          dosage: `${med.dosage_mg}mg ${med.frequency}`,
          dosage_mg: med.dosage_mg,
          frequency: med.frequency,
          duration_days: med.duration_days,
          duration: `${med.phase_duration_months} months (${med.phase})`,
          risk_level: diagnosisData.symptom_analysis?.risk_level,
          tablets_per_dose: med.tablets_per_dose,
          total_tablets: med.total_tablets
        };

        try {
          const response = await fetch(`${API_BASE}/prescriptions`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(prescriptionData)
          });

          if (response.ok) {
            successCount++;
          } else {
            console.error(`Failed to create prescription for ${med.name}`);
          }
        } catch (error) {
          console.error(`Error creating prescription for ${med.name}:`, error);
        }
      }
      
      if (successCount > 0) {
        prescriptionCreated.value = true;
        console.log(`Created ${successCount}/${medicines.length} prescriptions successfully`);
      }
    } else {
      // Fallback to single prescription with calculated dosage
      const dosage = calculatedDosage.value;
      const prescriptionData = {
        patient_id: selectedPatientId.value,
        diagnosis_id: null,
        medication: treatment?.drugs || 'TB Treatment',
        dosage: treatment?.dosage || '300mg daily',
        dosage_mg: dosage.dosageMg,
        frequency: dosage.timesPerDay === 1 ? '1 time daily' : dosage.timesPerDay === 2 ? '2 times daily' : `${dosage.timesPerDay} times daily`,
        duration_days: dosage.durationDays,
        duration: treatment?.duration || '6 months',
        risk_level: diagnosisData.symptom_analysis?.risk_level
      };

      const response = await fetch(`${API_BASE}/prescriptions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(prescriptionData)
      });

      if (response.ok) {
        prescriptionCreated.value = true;
        console.log('Prescription created automatically');
      } else {
        console.error('Failed to auto-create prescription');
      }
    }
  } catch (error) {
    console.error('Error auto-creating prescription:', error);
  }
};

const resetDiagnosis = () => {
  currentStep.value = 1;
  diagnosisResult.value = null;
  prescriptionCreated.value = false;
  form.value = {
    patient_id: '',
    first_name: '',
    last_name: '',
    age: null,
    gender: '',
    weight: null,
    city: '',
    oxygen_saturation_spo2: null,
    symptoms: '',
    persistent_cough_duration_weeks: null,
    contact_with_tb_patient: '',
    previous_tb_treatment: '',
    hiv: '',
    diabetes: '',
    smoking_status: '',
    alcohol_use: '',
    sputum_smear_test: 'Unknown',
    genexpert_test: 'Unknown',
    chest_xray: 'Unknown',
    drug_resistance: '',
    antibiotic_usage_history: '',
    exposure_history: '',
    tb_culture: '',
    tst: '',
    igra: '',
    bacteria_species: '',
    tb_status_label: '',
    treatment_type: '',
    duration_of_treatment: null,
    treatment_outcome: '',
    relapse: '',
    mortality: '',
    complications: '',
    malnutrition: '',
    region: '',
    occupation: '',
    date_of_diagnosis: null,
    source_dataset: '',
    source_row_id: '',
    has_fever: '',
    has_cough: '',
    has_weight_loss: '',
    has_night_sweats: '',
    has_chest_pain: '',
    has_blood: '',
    has_fatigue: '',
    has_shortness_of_breath: ''
  };
  selectedPatientId.value = null;
  selectedPatient.value = null;
  patientMode.value = 'new';
};

const createPrescription = async () => {
  if (!diagnosisResult.value || !selectedPatientId.value) {
    showNotification('Incomplete Diagnosis', 'Please complete diagnosis first', 'warning');
    return;
  }

  try {
    const token = authToken.value;
    const treatment = diagnosisResult.value.treatment_recommendation;
    
    // Parse dosage from treatment recommendation
    const dosageText = treatment?.dosage || 'Unknown';
    let dosageMg = 300; // default
    let frequency = '1 time daily';
    
    // Extract dosage mg if available
    const mgMatch = dosageText.match(/(\d+)mg/);
    if (mgMatch) {
      dosageMg = parseInt(mgMatch[1]);
    }
    
    // Extract frequency
    if (dosageText.toLowerCase().includes('twice') || dosageText.toLowerCase().includes('2 times')) {
      frequency = '2 times daily';
    } else if (dosageText.toLowerCase().includes('3 times')) {
      frequency = '3 times daily';
    }

    const prescriptionData = {
      patient_id: selectedPatientId.value,
      diagnosis_id: null, // Will be set after diagnosis creation
      medication: treatment?.drugs || 'TB Treatment',
      dosage: dosageText,
      dosage_mg: dosageMg,
      frequency: frequency,
      duration_days: 180, // Default 6 months
      duration: treatment?.duration || '6 months',
      risk_level: diagnosisResult.value.symptom_analysis?.risk_level
    };

    const response = await fetch(`${API_BASE}/prescriptions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(prescriptionData)
    });

    if (response.ok) {
      showNotification('Success', 'Prescription created successfully! The pharmacist will review and dispense the medication.', 'success');
      // Navigate to prescriptions page
      window.location.href = '/prescriptions';
    } else {
      const errorData = await response.json();
      showNotification('Error', `Failed to create prescription: ${errorData.msg || 'Unknown error'}`, 'error');
    }
  } catch (error) {
    console.error('Error creating prescription:', error);
    showNotification('Network Error', `Network error: ${error.message}`, 'error');
  }
};

const printReport = () => {
  if (!diagnosisResult.value) return;
  
  const reportContent = `
TB DIAGNOSIS REPORT
===================

Patient: ${form.value.first_name} ${form.value.last_name}
Patient ID: ${form.value.patient_id}
Age: ${form.value.age} | Gender: ${form.value.gender}
Weight: ${form.value.weight}kg

RISK ASSESSMENT
---------------
Risk Level: ${diagnosisResult.value.symptom_analysis?.risk_level_display}
Risk Score: ${diagnosisResult.value.symptom_analysis?.risk_score}/100
Primary Diagnosis: ${diagnosisResult.value.who_standards?.primary_diagnosis}

LABORATORY FINDINGS
-------------------
Bacteria Species: ${diagnosisResult.value.bacteria_assessment?.species}
Resistance Class: ${diagnosisResult.value.resistance_profile?.classification}
Confidence: ${diagnosisResult.value.test_evaluation?.confidence_percent}%

TREATMENT REGIMEN
-----------------
Regimen: ${diagnosisResult.value.treatment_recommendation?.regimen_name}
Duration: ${diagnosisResult.value.treatment_recommendation?.duration}
Urgency: ${diagnosisResult.value.treatment_recommendation?.urgency}

Medications: ${diagnosisResult.value.treatment_recommendation?.drugs}
Dosage: ${diagnosisResult.value.treatment_recommendation?.dosage}

Administration: ${diagnosisResult.value.treatment_recommendation?.administration}
Monitoring: ${diagnosisResult.value.treatment_recommendation?.monitoring}

ML PREDICTIONS
--------------
TB Status: ${diagnosisResult.value.ml_prediction?.tb_status?.prediction} (${Math.round(diagnosisResult.value.ml_prediction?.tb_status?.confidence * 100)}% confidence)
Drug Resistance: ${diagnosisResult.value.ml_prediction?.drug_resistance?.prediction} (${Math.round(diagnosisResult.value.ml_prediction?.drug_resistance?.confidence * 100)}% confidence)

CLINICAL NOTES
--------------
${diagnosisResult.value.treatment_recommendation?.notes}

Generated by TB Predictive EHR Analytics Dashboard
Date: ${new Date().toLocaleDateString()}
  `;
  
  const printWindow = window.open('', '_blank');
  printWindow.document.write(`<pre style="font-family: monospace; white-space: pre-wrap;">${reportContent}</pre>`);
  printWindow.document.close();
  printWindow.print();
};

const loadDiagnoses = async () => {
  try {
    const res = await getDiagnoses();
    diagnoses.value = (res as any).diagnoses || [];
  } catch (e) {
    console.error('Failed to load diagnoses', e);
  }
};

onMounted(async () => {
  await loadPatientsList();
  await loadDiagnoses();
});
</script>
