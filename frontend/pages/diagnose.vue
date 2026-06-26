<template>
  <DashboardLayout>

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
                    type="text"
                    class="w-full pl-10 pr-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                    placeholder="Search by name or patient ID..."
                  />
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
                  {{ patient.patient_id }} - {{ patient.first_name }} {{ patient.last_name }} (Age: {{ patient.age }}, {{ patient.gender }})
                </option>
              </select>
            </div>
            <div v-if="selectedPatient" class="p-4 rounded-xl bg-primary-900/30 border border-primary-700/50">
              <p class="text-primary-600 dark:text-primary-400 text-sm font-medium">
                ✓ Patient selected: {{ selectedPatient.first_name }} {{ selectedPatient.last_name }}
              </p>
            </div>
          </div>

          <!-- New Patient Form -->
          <div v-else class="space-y-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Patient ID</label>
                <input
                  v-model="form.patient_id"
                  type="text"
                  class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-primary-500 outline-none"
                  placeholder="e.g., TB-001"
                />
              </div>
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

        <!-- Step 3: Lab Results -->
        <div v-if="currentStep === 3" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-purple-600 to-purple-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Lab Test Results</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Enter available lab test findings</p>
            </div>
          </div>
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
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Drug Resistance</label>
              <select v-model="form.drug_resistance" class="w-full px-4 py-3 rounded-xl border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-700/60 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 outline-none">
                <option value="">Unknown</option>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Step 4: Review & Diagnose -->
        <div v-if="currentStep === 4" class="space-y-6">
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
              <div class="flex flex-wrap gap-2">
                <span v-for="symptom in symptomsList.filter(s => form[s.key] === 'Yes')" :key="symptom.key" class="px-3 py-1 rounded-full text-xs font-medium bg-green-600 text-white border border-green-500">
                  {{ symptom.label }}
                </span>
                <span v-if="symptomsList.filter(s => form[s.key] === 'Yes').length === 0" class="text-gray-400 dark:text-gray-500 text-sm">No symptoms selected</span>
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
                <p class="text-gray-500 dark:text-gray-400">Sputum Smear: <span :class="['font-medium', form.sputum_smear_test === 'Positive' ? 'text-red-600 dark:text-red-400' : form.sputum_smear_test === 'Negative' ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-300']">{{ form.sputum_smear_test }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">GeneXpert: <span :class="['font-medium', form.genexpert_test === 'Positive' ? 'text-red-600 dark:text-red-400' : form.genexpert_test === 'Negative' ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-300']">{{ form.genexpert_test }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Chest X-ray: <span :class="['font-medium', form.chest_xray === 'Abnormal' ? 'text-red-600 dark:text-red-400' : form.chest_xray === 'Normal' ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-300']">{{ form.chest_xray }}</span></p>
                <p class="text-gray-500 dark:text-gray-400">Drug Resistance: <span :class="['font-medium', form.drug_resistance === 'Yes' ? 'text-red-600 dark:text-red-400' : form.drug_resistance === 'No' ? 'text-green-600 dark:text-green-400' : 'text-gray-900 dark:text-gray-300']">{{ form.drug_resistance }}</span></p>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 5: Results -->
        <div v-if="currentStep === 5 && diagnosisResult" class="space-y-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-primary-600 to-primary-700 flex items-center justify-center shrink-0">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900 dark:text-white">Diagnosis Results</h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">Complete analysis and recommendations</p>
            </div>
          </div>

          <!-- Key Metrics -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Risk Level</p>
              <p :class="[
                'text-2xl font-bold mt-2',
                diagnosisResult.symptom_analysis?.risk_level === 'HIGH RISK' ? 'text-red-600 dark:text-red-400'
                  : diagnosisResult.symptom_analysis?.risk_level === 'MODERATE RISK' ? 'text-yellow-600 dark:text-yellow-400'
                  : 'text-green-600 dark:text-green-400'
              ]">
                {{ diagnosisResult.symptom_analysis?.risk_level_display || 'Unknown' }}
              </p>
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Score: {{ diagnosisResult.symptom_analysis?.risk_score }}</p>
            </div>
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Primary Diagnosis</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">{{ diagnosisResult.who_standards?.primary_diagnosis || 'Pending' }}</p>
            </div>
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Bacteria Species</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">{{ diagnosisResult.bacteria_assessment?.species || 'Unknown' }}</p>
            </div>
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Resistance Class</p>
              <p class="text-2xl font-bold text-gray-900 dark:text-white mt-2">{{ diagnosisResult.resistance_profile?.classification || 'Unknown' }}</p>
            </div>
          </div>

          <!-- Detailed Sections -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                Test Evaluation
              </h4>
              <div class="space-y-2 text-sm">
                <p class="text-gray-700 dark:text-gray-300"><span class="font-medium text-gray-900 dark:text-white">Classification:</span> {{ diagnosisResult.test_evaluation?.classification }}</p>
                <p class="text-gray-700 dark:text-gray-300"><span class="font-medium text-gray-900 dark:text-white">Confidence:</span> {{ diagnosisResult.test_evaluation?.confidence_percent }}%</p>
                <div v-if="diagnosisResult.test_evaluation?.findings?.length">
                  <p class="font-medium text-gray-900 dark:text-white mb-1">Findings:</p>
                  <div class="flex flex-wrap gap-2">
                    <span v-for="(f, i) in diagnosisResult.test_evaluation.findings" :key="i" class="px-3 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 dark:border-blue-700 border border-blue-300">
                      {{ f }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Clinical Guidance
              </h4>
              <div v-if="diagnosisResult.symptom_analysis?.red_flags?.length" class="mb-3">
                <p class="font-medium text-red-600 dark:text-red-400 mb-1">Red Flags:</p>
                <ul class="list-disc pl-5 text-gray-700 dark:text-gray-300 text-sm">
                  <li v-for="(rf, i) in diagnosisResult.symptom_analysis.red_flags" :key="i">{{ rf }}</li>
                </ul>
              </div>
              <div class="p-3 rounded-xl bg-primary-100 dark:bg-primary-900/20 border border-primary-300 dark:border-primary-800/50">
                <p class="font-medium text-primary-800 dark:text-primary-300 text-sm">Advice:</p>
                <p class="text-primary-700 dark:text-primary-400 text-sm mt-1">{{ diagnosisResult.symptom_analysis?.clinical_advice }}</p>
              </div>
            </div>
            <div v-if="diagnosisResult.ml_prediction" class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                ML Predictions
              </h4>
              <div class="space-y-3">
                <div v-if="diagnosisResult.ml_prediction.tb_status">
                  <div class="flex justify-between items-center mb-1 text-sm">
                    <span class="text-gray-700 dark:text-gray-300">TB Status</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ diagnosisResult.ml_prediction.tb_status.prediction }}</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div class="bg-primary-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${diagnosisResult.ml_prediction.tb_status.confidence * 100}%` }"></div>
                  </div>
                  <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 text-right">Confidence: {{ Math.round(diagnosisResult.ml_prediction.tb_status.confidence * 100) }}%</p>
                </div>
                <div v-if="diagnosisResult.ml_prediction.drug_resistance">
                  <div class="flex justify-between items-center mb-1 text-sm">
                    <span class="text-gray-700 dark:text-gray-300">Drug Resistance</span>
                    <span class="font-semibold text-gray-900 dark:text-white">{{ diagnosisResult.ml_prediction.drug_resistance.prediction }}</span>
                  </div>
                  <div class="w-full bg-gray-200 dark:bg-gray-600 rounded-full h-2">
                    <div class="bg-red-600 h-2 rounded-full transition-all duration-300" :style="{ width: `${diagnosisResult.ml_prediction.drug_resistance.confidence * 100}%` }"></div>
                  </div>
                  <p class="text-xs text-gray-400 dark:text-gray-500 mt-1 text-right">Confidence: {{ Math.round(diagnosisResult.ml_prediction.drug_resistance.confidence * 100) }}%</p>
                </div>
              </div>
            </div>
            <div class="p-5 rounded-xl bg-gray-50 dark:bg-gray-700/30 border border-gray-200 dark:border-gray-600">
              <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
                <svg class="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-2.322l-.896-.298a2 2 0 01-1.333-2.322L18 7.5V6a2 2 0 00-2-2H8a2 2 0 00-2 2v1.5l.825 4.982a2 2 0 01-1.333 2.322l-.896.298a2 2 0 00-1.022 2.322V21h18v-4.572z"></path><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Infection Assessment
              </h4>
              <div class="space-y-2 text-sm text-gray-700 dark:text-gray-300">
                <p v-if="diagnosisResult.infection_assessment?.primary_infection"><span class="font-medium text-gray-900 dark:text-white">Primary:</span> {{ diagnosisResult.infection_assessment.primary_infection }}</p>
                <p v-if="diagnosisResult.infection_assessment?.site"><span class="font-medium text-gray-900 dark:text-white">Site:</span> {{ diagnosisResult.infection_assessment.site }}</p>
              </div>
            </div>
          </div>

          <!-- Treatment Plan -->
          <div class="p-5 rounded-xl bg-gray-100 dark:bg-gray-700/30 border border-gray-300 dark:border-gray-600">
            <h4 class="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 018.382 3.984M5 12H9a3 3 0 013 3V12a3 3 0 01-3 3H5z"></path>
              </svg>
              Treatment Recommendation
            </h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Regimen</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.regimen_name }}</p>
              </div>
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Duration</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.duration }}</p>
              </div>
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Urgency</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.urgency }}</p>
              </div>
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wide">Guideline</p>
                <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.guideline_source }}</p>
              </div>
            </div>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Drugs</p>
                <p class="text-gray-700 dark:text-gray-300 text-sm">{{ diagnosisResult.treatment_recommendation?.drugs }}</p>
              </div>
              <div class="p-3 rounded-xl bg-white dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700">
                <p class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Dosage</p>
                <p class="text-gray-700 dark:text-gray-300 text-sm">{{ diagnosisResult.treatment_recommendation?.dosage }}</p>
              </div>
              <div class="p-3 rounded-xl bg-blue-100 dark:bg-blue-900/20 border border-blue-300 dark:border-blue-700">
                <p class="text-sm font-semibold text-blue-800 dark:text-blue-300 mb-2">How to Take</p>
                <p class="text-blue-700 dark:text-blue-400 text-sm">{{ diagnosisResult.treatment_recommendation?.administration || 'Follow clinician instructions' }}</p>
              </div>
              <div class="p-3 rounded-xl bg-purple-100 dark:bg-purple-900/20 border border-purple-300 dark:border-purple-700">
                <p class="text-sm font-semibold text-purple-800 dark:text-purple-300 mb-2">Monitoring</p>
                <p class="text-purple-700 dark:text-purple-400 text-sm">{{ diagnosisResult.treatment_recommendation?.monitoring || 'Regular check-ups required' }}</p>
              </div>
            </div>
            <div class="mt-4 p-3 rounded-xl bg-amber-100 dark:bg-amber-900/20 border border-amber-300 dark:border-amber-700">
              <p class="text-sm font-semibold text-amber-800 dark:text-amber-300 mb-1">Notes</p>
              <p class="text-amber-700 dark:text-amber-400 text-sm">{{ diagnosisResult.treatment_recommendation?.notes }}</p>
            </div>
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
          <button v-if="currentStep === 5" @click="resetDiagnosis" class="flex-1 py-3 px-6 rounded-xl bg-gradient-to-r from-green-600 to-green-700 hover:from-green-500 hover:to-green-600 text-white font-semibold text-sm transition flex items-center justify-center gap-2 shadow-lg shadow-green-500/30">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.575-7.027M17 17v5h-5m10-3a7.004.004 0 00-7.027-4.576"></path>
            </svg>
            Start New Diagnosis
          </button>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
const { getPatients, diagnose, getDiagnoses } = useApi();

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
  { id: 3, title: 'Lab Results' },
  { id: 4, title: 'Review' },
  { id: 5, title: 'Results' }
];

const currentStep = ref(1);
const totalSteps = computed(() => steps.length);
const patientMode = ref('new');
const patientsList = ref<any[]>([]);
const patientSearch = ref('');
const selectedPatientId = ref<string | number | null>(null);
const selectedPatient = ref<any>(null);
const diagnoses = ref<any[]>([]);
const isLoading = ref(false);
const diagnosisResult = ref<any>(null);

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
      return !!(form.value.patient_id && form.value.first_name && form.value.last_name && form.value.age && form.value.gender);
    }
  }
  if (currentStep.value === 2) {
    return true;
  }
  if (currentStep.value === 3) {
    return true;
  }
  if (currentStep.value === 4) {
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

const loadPatientsList = async () => {
  try {
    const res = await getPatients(1, 1000, patientSearch.value);
    patientsList.value = (res as any).patients || [];
  } catch (e) {
    console.error('Failed to load patients', e);
  }
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
};

const handleDiagnose = async () => {
  try {
    isLoading.value = true;
    const res = await diagnose({ patient: form.value });
    diagnosisResult.value = res;
    currentStep.value = 5;
    await loadDiagnoses();
  } catch (e) {
    console.error('Diagnosis failed:', e);
    alert('Failed to get diagnosis. Please try again.');
  } finally {
    isLoading.value = false;
  }
};

const resetDiagnosis = () => {
  diagnosisResult.value = null;
  currentStep.value = 1;
  patientMode.value = 'new';
  selectedPatientId.value = null;
  selectedPatient.value = null;
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
