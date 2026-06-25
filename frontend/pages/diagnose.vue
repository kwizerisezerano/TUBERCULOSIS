<template>
  <DashboardLayout page-title="Diagnose & Predict">
    <div class="space-y-6">
      <!-- Patient Selection -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Patient</h3>
          <div class="flex gap-2">
            <button 
              v-for="tab in ['Select Existing', 'New Patient']" 
              :key="tab"
              @click="patientMode = tab"
              :class="['px-4 py-2 rounded-lg text-sm font-medium transition', patientMode === tab ? 'bg-emerald-600 text-white' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600']"
            >
              {{ tab }}
            </button>
          </div>
        </div>

        <!-- Select Existing Patient -->
        <div v-if="patientMode === 'Select Existing'" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Search</label>
              <input 
                v-model="patientSearch"
                @input="debounceLoadPatients"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                placeholder="Search patients..."
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Page</label>
              <div class="flex gap-2">
                <button @click="patientPage = Math.max(1, patientPage - 1)" :disabled="patientPage <= 1" class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  ←
                </button>
                <span class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg text-gray-900 dark:text-white">
                  {{ patientPage }} / {{ patientTotalPages }}
                </span>
                <button @click="patientPage = Math.min(patientTotalPages, patientPage + 1)" :disabled="patientPage >= patientTotalPages" class="px-4 py-2 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed">
                  →
                </button>
              </div>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Select Patient</label>
            <select 
              v-model="selectedPatientId"
              @change="loadPatient"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select a patient...</option>
              <option v-for="patient in patientsList" :key="patient.id" :value="patient.id">
                {{ patient.patient_id }} - {{ patient.first_name }} {{ patient.last_name }} (Age: {{ patient.age }})
              </option>
            </select>
          </div>
        </div>

        <!-- New Patient Form -->
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Patient ID</label>
            <input 
              v-model="form.patient_id"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              placeholder="e.g., TB-001"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name</label>
            <input 
              v-model="form.first_name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name</label>
            <input 
              v-model="form.last_name"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Age</label>
            <input 
              v-model.number="form.age"
              type="number"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Gender</label>
            <select 
              v-model="form.gender"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Weight (kg)</label>
            <input 
              v-model.number="form.weight"
              type="number"
              step="0.1"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">City</label>
            <input 
              v-model="form.city"
              type="text"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Oxygen Saturation (SpO2 %)</label>
            <input 
              v-model.number="form.oxygen_saturation_spo2"
              type="number"
              step="0.1"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>
      </div>

      <!-- Clinical Data Form -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Symptoms & History -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Symptoms Checkboxes -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Symptoms</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              <div v-for="symptom in symptomsList" :key="symptom.key" class="flex items-center gap-2">
                <select v-model="form[symptom.key]" class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-sm text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
                <span class="text-gray-700 dark:text-gray-300 text-sm">{{ symptom.label }}</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Persistent Cough Duration (weeks)</label>
              <input 
                v-model.number="form.persistent_cough_duration_weeks"
                type="number"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          <!-- Risk Factors -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Risk Factors</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Contact with TB Patient</label>
                <select v-model="form.contact_with_tb_patient" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Previous TB Treatment</label>
                <select v-model="form.previous_tb_treatment" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">HIV Status</label>
                <select v-model="form.hiv" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Diabetes</label>
                <select v-model="form.diabetes" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Smoking Status</label>
                <select v-model="form.smoking_status" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Never">Never</option>
                  <option value="Former">Former</option>
                  <option value="Current">Current</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Alcohol Use</label>
                <select v-model="form.alcohol_use" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Never">Never</option>
                  <option value="Occasional">Occasional</option>
                  <option value="Regular">Regular</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Lab Tests -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Lab Results</h3>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sputum Smear</label>
                <select v-model="form.sputum_smear_test" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="Unknown">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">GeneXpert</label>
                <select v-model="form.genexpert_test" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="Unknown">Unknown</option>
                  <option value="Positive">Positive</option>
                  <option value="Negative">Negative</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Chest X-ray</label>
                <select v-model="form.chest_xray" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="Unknown">Unknown</option>
                  <option value="Normal">Normal</option>
                  <option value="Abnormal">Abnormal</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Drug Resistance</label>
                <select v-model="form.drug_resistance" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                  <option value="">Unknown</option>
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Actions & Quick Results -->
        <div class="space-y-6">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <button 
              @click="handleDiagnose"
              :disabled="isLoading"
              class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-semibold text-lg"
            >
              {{ isLoading ? 'Analyzing...' : 'Diagnose & Predict' }}
            </button>
            <p class="text-sm text-gray-500 dark:text-gray-400 mt-3 text-center">
              Uses machine learning and WHO guidelines
            </p>
          </div>

          <!-- Previous Diagnoses -->
          <div v-if="diagnoses.length" class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Previous Diagnoses</h3>
            <div class="space-y-3 max-h-64 overflow-y-auto">
              <div 
                v-for="d in diagnoses.slice(0, 5)" 
                :key="d.id"
                class="p-3 rounded-xl bg-gray-50 dark:bg-gray-700/50 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 transition"
              >
                <p class="font-medium text-gray-900 dark:text-white">{{ d.diagnosis_type }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ new Date(d.created_at).toLocaleDateString() }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Section -->
      <div v-if="diagnosisResult" class="space-y-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Diagnosis Results</h2>

        <!-- Key Metrics -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Risk Level</p>
            <p 
              :class="['text-2xl font-bold mt-1', 
                diagnosisResult.symptom_analysis?.risk_level === 'HIGH RISK' ? 'text-red-600' :
                diagnosisResult.symptom_analysis?.risk_level === 'MODERATE RISK' ? 'text-yellow-600' :
                diagnosisResult.symptom_analysis?.risk_level === 'LOW RISK' ? 'text-blue-600' : 'text-green-600']"
            >
              {{ diagnosisResult.symptom_analysis?.risk_level_display || 'Unknown' }}
            </p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Score: {{ diagnosisResult.symptom_analysis?.risk_score }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Primary Diagnosis</p>
            <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.who_standards?.primary_diagnosis || 'Pending' }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Bacteria Species</p>
            <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.bacteria_assessment?.species || 'Unknown' }}</p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <p class="text-gray-500 dark:text-gray-400 text-sm">Resistance Class</p>
            <p class="text-xl font-bold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.resistance_profile?.classification || 'Unknown' }}</p>
          </div>
        </div>

        <!-- Detailed Results -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Test Evaluation -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Test Evaluation</h3>
            <div class="space-y-3">
              <p class="text-gray-700 dark:text-gray-300"><span class="font-medium">Classification:</span> {{ diagnosisResult.test_evaluation?.classification }}</p>
              <p class="text-gray-700 dark:text-gray-300"><span class="font-medium">Confidence:</span> {{ diagnosisResult.test_evaluation?.confidence_percent }}%</p>
              <div v-if="diagnosisResult.test_evaluation?.findings?.length">
                <p class="font-medium text-gray-700 dark:text-gray-300 mb-2">Findings:</p>
                <div class="flex flex-wrap gap-2">
                  <span v-for="(f, i) in diagnosisResult.test_evaluation.findings" :key="i" class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-full text-xs">
                    {{ f }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Red Flags & Clinical Advice -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Clinical Guidance</h3>
            <div v-if="diagnosisResult.symptom_analysis?.red_flags?.length">
              <p class="font-medium text-red-600 mb-2">Red Flags:</p>
              <ul class="list-disc pl-5 mb-4 text-gray-700 dark:text-gray-300">
                <li v-for="(rf, i) in diagnosisResult.symptom_analysis.red_flags" :key="i">{{ rf }}</li>
              </ul>
            </div>
            <div class="p-4 bg-emerald-50 dark:bg-emerald-900/20 rounded-xl">
              <p class="font-medium text-emerald-800 dark:text-emerald-300 mb-1">Advice:</p>
              <p class="text-emerald-700 dark:text-emerald-400">{{ diagnosisResult.symptom_analysis?.clinical_advice }}</p>
            </div>
          </div>

          <!-- ML Predictions -->
          <div v-if="diagnosisResult.ml_prediction" class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">ML Predictions</h3>
            <div class="space-y-4">
              <div v-if="diagnosisResult.ml_prediction.tb_status">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">TB Status</span>
                  <span class="text-sm font-bold text-gray-900 dark:text-white">{{ diagnosisResult.ml_prediction.tb_status.prediction }}</span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    class="bg-emerald-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${diagnosisResult.ml_prediction.tb_status.confidence * 100}%` }"
                  ></div>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">Confidence: {{ Math.round(diagnosisResult.ml_prediction.tb_status.confidence * 100) }}%</p>
              </div>
              <div v-if="diagnosisResult.ml_prediction.drug_resistance">
                <div class="flex justify-between items-center mb-1">
                  <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Drug Resistance</span>
                  <span class="text-sm font-bold text-gray-900 dark:text-white">{{ diagnosisResult.ml_prediction.drug_resistance.prediction }}</span>
                </div>
                <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div 
                    class="bg-red-600 h-2 rounded-full transition-all duration-300"
                    :style="{ width: `${diagnosisResult.ml_prediction.drug_resistance.confidence * 100}%` }"
                  ></div>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">Confidence: {{ Math.round(diagnosisResult.ml_prediction.drug_resistance.confidence * 100) }}%</p>
              </div>
            </div>
          </div>

          <!-- Infection Assessment -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Infection Assessment</h3>
            <div class="space-y-2 text-gray-700 dark:text-gray-300">
              <p v-if="diagnosisResult.infection_assessment?.primary_infection">
                <span class="font-medium">Primary:</span> {{ diagnosisResult.infection_assessment.primary_infection }}
              </p>
              <p v-if="diagnosisResult.infection_assessment?.site">
                <span class="font-medium">Site:</span> {{ diagnosisResult.infection_assessment.site }}
              </p>
            </div>
          </div>
        </div>

        <!-- Treatment Plan -->
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-6">
            Treatment Recommendation
          </h3>
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-xl">
              <p class="text-sm text-gray-500 dark:text-gray-400">Regimen</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.regimen_name }}</p>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-xl">
              <p class="text-sm text-gray-500 dark:text-gray-400">Duration</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.duration }}</p>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-xl">
              <p class="text-sm text-gray-500 dark:text-gray-400">Urgency</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.urgency }}</p>
            </div>
            <div class="p-4 border border-gray-200 dark:border-gray-700 rounded-xl">
              <p class="text-sm text-gray-500 dark:text-gray-400">Guideline</p>
              <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">{{ diagnosisResult.treatment_recommendation?.guideline_source }}</p>
            </div>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Drugs</h4>
              <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                <p class="text-gray-700 dark:text-gray-300">{{ diagnosisResult.treatment_recommendation?.drugs }}</p>
              </div>
            </div>
            <div>
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Dosage</h4>
              <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl">
                <p class="text-gray-700 dark:text-gray-300">{{ diagnosisResult.treatment_recommendation?.dosage }}</p>
              </div>
            </div>
            <div>
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">How to Take</h4>
              <div class="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
                <p class="text-blue-800 dark:text-blue-300">{{ diagnosisResult.treatment_recommendation?.administration || 'Follow clinician instructions' }}</p>
              </div>
            </div>
            <div>
              <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Monitoring</h4>
              <div class="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-200 dark:border-purple-800">
                <p class="text-purple-800 dark:text-purple-300">{{ diagnosisResult.treatment_recommendation?.monitoring || 'Regular check-ups required' }}</p>
              </div>
            </div>
          </div>

          <div class="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-xl border border-amber-200 dark:border-amber-800">
            <h4 class="text-md font-semibold text-amber-800 dark:text-amber-300 mb-2">Notes</h4>
            <p class="text-amber-700 dark:text-amber-400">{{ diagnosisResult.treatment_recommendation?.notes }}</p>
          </div>
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
  { key: 'has_shortness_of_breath', label: 'Shortness of Breath' },
];

const patientMode = ref('New Patient');
const patientsList = ref<any[]>([]);
const patientSearch = ref('');
const patientPage = ref(1);
const patientTotalPages = ref(1);
const diagnoses = ref<any[]>([]);
const selectedPatientId = ref<number | null>(null);
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
  has_shortness_of_breath: '',
});

let debounceTimer: number;
const debounceLoadPatients = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(loadPatientsList, 300) as unknown as number;
};

const loadPatientsList = async () => {
  try {
    const res = await getPatients(patientPage.value, 20, patientSearch.value);
    patientsList.value = (res as any).patients || [];
    patientTotalPages.value = (res as any).pages || 1;
  } catch (e) {
    console.error('Failed to load patients', e);
  }
};

const loadPatient = async () => {
  if (!selectedPatientId.value) return;
  const patient = patientsList.value.find(p => p.id === selectedPatientId.value);
  if (!patient) return;

  // Load all patient fields
  Object.keys(form.value).forEach((key) => {
    if (patient.hasOwnProperty(key)) {
      form.value[key as keyof typeof form.value] = patient[key];
    }
  });
};

const handleDiagnose = async () => {
  try {
    isLoading.value = true;
    diagnosisResult.value = null;
    const res = await diagnose({ patient: form.value });
    diagnosisResult.value = res;
    await loadDiagnoses();
  } catch (e) {
    console.error('Diagnosis failed:', e);
    alert('Failed to get diagnosis. Please try again.');
  } finally {
    isLoading.value = false;
  }
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
