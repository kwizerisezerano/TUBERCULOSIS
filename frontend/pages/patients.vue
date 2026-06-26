<template>
  <DashboardLayout page-title="Patients">
    <div class="space-y-6">
      <div class="flex flex-col sm:flex-row items-center justify-between gap-4">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">Patient Records</h2>
        <div class="flex flex-col sm:flex-row items-center gap-3">
          <div class="relative">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            <input
              v-model="searchQuery"
              @input="debounceLoadResults"
              type="text"
              placeholder="Search patients..."
              class="pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-emerald-500 outline-none"
            />
          </div>
          <button @click="router.push('/diagnose')" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 shadow-sm">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            New Patient
          </button>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <p class="text-sm text-gray-500 dark:text-gray-400">Total Patients</p>
          <p class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ totalPatients }}</p>
        </div>
        <div class="bg-red-50 dark:bg-red-900/20 p-4 rounded-xl border border-red-200 dark:border-red-800 shadow-sm">
          <p class="text-sm text-red-700 dark:text-red-400">High Risk</p>
          <p class="text-2xl font-bold text-red-700 dark:text-red-400 mt-1">{{ highRiskPatients }}</p>
        </div>
        <div class="bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-xl border border-yellow-200 dark:border-yellow-800 shadow-sm">
          <p class="text-sm text-yellow-700 dark:text-yellow-400">Medium Risk</p>
          <p class="text-2xl font-bold text-yellow-700 dark:text-yellow-400 mt-1">{{ mediumRiskPatients }}</p>
        </div>
        <div class="bg-green-50 dark:bg-green-900/20 p-4 rounded-xl border border-green-200 dark:border-green-800 shadow-sm">
          <p class="text-sm text-green-700 dark:text-green-400">Low Risk</p>
          <p class="text-2xl font-bold text-green-700 dark:text-green-400 mt-1">{{ lowRiskPatients }}</p>
        </div>
      </div>

      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">ID</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Name</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Age / Gender</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">City</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Symptoms</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Risk Level</th>
                <th class="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider text-gray-700 dark:text-gray-300">Actions</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="patient in patients"
                :key="patient.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition"
              >
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300 font-mono">{{ patient.patient_id }}</td>
                <td class="px-6 py-4">
                  <p class="font-medium text-gray-900 dark:text-white">{{ patient.first_name }} {{ patient.last_name }}</p>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ patient.age }} / {{ patient.gender }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300">{{ patient.city }}</td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-300 truncate max-w-xs">{{ patient.symptoms || 'No symptoms' }}</td>
                <td class="px-6 py-4">
                  <span :class="['px-3 py-1 rounded-full text-xs font-semibold', getRiskInfo(patient).class]">
                    {{ getRiskInfo(patient).text }}
                  </span>
                </td>
                <td class="px-6 py-4">
                  <button
                    @click="openPatientDetails(patient.id)"
                    class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition"
                    title="View Patient Details"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                    </svg>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="bg-gray-50 dark:bg-gray-700/30 px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p class="text-sm text-gray-600 dark:text-gray-300">
            Showing <span class="font-semibold">{{ (currentPage - 1) * perPage + 1 }}</span> to <span class="font-semibold">{{ Math.min(currentPage * perPage, totalPatients) }}</span> of <span class="font-semibold">{{ totalPatients }}</span> patients
          </p>
          <div class="flex items-center gap-2">
            <button
              @click="currentPage = Math.max(1, currentPage - 1)"
              :disabled="currentPage === 1"
              class="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Previous
            </button>
            <div class="flex gap-1">
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="currentPage = page"
                :class="['px-3 py-1 rounded text-sm font-medium transition',
                  page === currentPage
                    ? 'bg-emerald-600 text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                ]"
              >
                {{ page }}
              </button>
            </div>
            <button
              @click="currentPage = Math.min(totalPages, currentPage + 1)"
              :disabled="currentPage === totalPages"
              class="px-3 py-1 rounded border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100 dark:hover:bg-gray-700"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Patient Details Modal -->
    <div v-if="showPatientModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4" @click.self="closePatientModal">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl border border-gray-200 dark:border-gray-700 w-full max-w-5xl max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white dark:bg-gray-800 px-6 py-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">Patient Details</h3>
          <button @click="closePatientModal" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-6">
          <!-- Basic Info -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Basic Information</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Patient ID</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.patient_id || 'N/A' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Full Name</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.first_name }} {{ selectedPatient?.last_name }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Age / Gender</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.age }} / {{ selectedPatient?.gender }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">City</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.city }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Weight (kg)</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.weight }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Oxygen Saturation (%)</p>
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedPatient?.oxygen_saturation_spo2 }}</p>
              </div>
            </div>
          </div>

          <!-- Symptoms & History -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Symptoms & Risk Factors</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Fever</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_fever === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_fever || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Cough</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_cough === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_cough || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Weight Loss</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_weight_loss === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_weight_loss || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Night Sweats</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_night_sweats === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_night_sweats || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Chest Pain</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_chest_pain === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_chest_pain || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Hemoptysis</p>
                <p :class="['text-sm font-medium', selectedPatient?.has_blood === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-green-700 dark:text-green-400']">{{ selectedPatient?.has_blood || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Contact with TB Patient</p>
                <p :class="['text-sm font-medium', selectedPatient?.contact_with_tb_patient === 'Yes' ? 'text-yellow-700 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.contact_with_tb_patient || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Previous TB Treatment</p>
                <p :class="['text-sm font-medium', selectedPatient?.previous_tb_treatment === 'Yes' ? 'text-yellow-700 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.previous_tb_treatment || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">HIV Status</p>
                <p :class="['text-sm font-medium', selectedPatient?.hiv === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.hiv || 'Unknown' }}</p>
              </div>
            </div>
          </div>

          <!-- Lab Results -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Lab Test Results</h4>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Sputum Smear</p>
                <p :class="['text-sm font-medium', selectedPatient?.sputum_smear_test === 'Positive' ? 'text-red-700 dark:text-red-400' : selectedPatient?.sputum_smear_test === 'Negative' ? 'text-green-700 dark:text-green-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.sputum_smear_test || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">GeneXpert</p>
                <p :class="['text-sm font-medium', selectedPatient?.genexpert_test === 'Positive' ? 'text-red-700 dark:text-red-400' : selectedPatient?.genexpert_test === 'Negative' ? 'text-green-700 dark:text-green-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.genexpert_test || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Chest X-ray</p>
                <p :class="['text-sm font-medium', selectedPatient?.chest_xray === 'Abnormal' ? 'text-red-700 dark:text-red-400' : selectedPatient?.chest_xray === 'Normal' ? 'text-green-700 dark:text-green-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.chest_xray || 'Unknown' }}</p>
              </div>
              <div>
                <p class="text-xs text-gray-500 dark:text-gray-400 uppercase">Drug Resistance</p>
                <p :class="['text-sm font-medium', selectedPatient?.drug_resistance === 'Yes' ? 'text-red-700 dark:text-red-400' : 'text-gray-600 dark:text-gray-300']">{{ selectedPatient?.drug_resistance || 'Unknown' }}</p>
              </div>
            </div>
          </div>

          <!-- Detailed Lab Results -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Detailed Lab Results</h4>
            <div v-if="patientDetails?.detailed_lab_results?.length" class="space-y-3">
              <div v-for="lab in patientDetails.detailed_lab_results" :key="lab.id" class="bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ lab.test_name }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300">{{ lab.test_value }} {{ lab.unit }} · Reference: {{ lab.reference_range }} · {{ lab.hospital }} · {{ lab.collection_date ? new Date(lab.collection_date).toLocaleDateString() : 'N/A' }}</p>
              </div>
            </div>
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No detailed lab results</div>
          </div>

          <!-- Antibiotic Resistance -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Antimicrobial Resistance Records</h4>
            <div v-if="patientDetails?.antibiotic_resistance_records?.length" class="space-y-3">
              <div v-for="record in patientDetails.antibiotic_resistance_records" :key="record.id" class="bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3">
                <div class="flex items-center justify-between mb-2">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">{{ record.sample_id }} · {{ record.bacterial_species }}</p>
                  <p class="text-xs text-gray-500 dark:text-gray-400">{{ record.collection_date ? new Date(record.collection_date).toLocaleDateString() : 'N/A' }}</p>
                </div>
                <div class="flex flex-wrap gap-2">
                  <span v-if="record.amx_amp === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">AMX/AMP R</span>
                  <span v-if="record.cip === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">CIP R</span>
                  <span v-if="record.gen === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">GEN R</span>
                  <span v-if="record.amc === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">AMC R</span>
                  <span v-if="record.cz === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">CZ R</span>
                  <span v-if="record.fox === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">FOX R</span>
                  <span v-if="record.ctx_cro === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">CTX/CRO R</span>
                  <span v-if="record.ipm === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">IPM R</span>
                  <span v-if="record.an === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">AN R</span>
                  <span v-if="record.nalidixic_acid === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">Nalidixic Acid R</span>
                  <span v-if="record.ofx === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">OFX R</span>
                  <span v-if="record.chloramphenicol === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">Chloramphenicol R</span>
                  <span v-if="record.co_trimoxazole === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">Co-Trimoxazole R</span>
                  <span v-if="record.furanes === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">Furanes R</span>
                  <span v-if="record.colistine === 'R'" class="px-2 py-0.5 text-xs rounded-full bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400">Colistine R</span>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Diabetes: {{ record.diabetes }} · Hypertension: {{ record.hypertension }} · Notes: {{ record.notes }}</p>
              </div>
            </div>
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No antimicrobial resistance records yet</div>
          </div>

          <!-- Diagnoses -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Diagnoses</h4>
            <div v-if="patientDetails?.diagnoses?.length" class="space-y-3">
              <div v-for="diagnosis in patientDetails.diagnoses" :key="diagnosis.id" class="bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">{{ diagnosis.diagnosis_type }}</p>
                  <span :class="['px-2 py-0.5 rounded-full text-xs font-semibold', getRiskInfoFromLevel(diagnosis.risk_level).class]">
                    {{ diagnosis.risk_level || 'Unknown' }}
                  </span>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">Created: {{ diagnosis.created_at ? new Date(diagnosis.created_at).toLocaleDateString() : 'N/A' }} · Confidence: {{ diagnosis.confidence_percent ? `${diagnosis.confidence_percent}%` : 'N/A' }}</p>
              </div>
            </div>
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No diagnoses yet</div>
          </div>

          <!-- Prescriptions -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Prescriptions</h4>
            <div v-if="patientDetails?.prescriptions?.length" class="space-y-3">
              <div v-for="presc in patientDetails.prescriptions" :key="presc.id" class="bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3">
                <div class="flex items-center justify-between">
                  <p class="text-sm font-medium text-gray-900 dark:text-white">{{ presc.medication }}</p>
                  <span :class="['px-2 py-0.5 rounded-full text-xs font-semibold',
                    presc.status === 'approved' ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' :
                    presc.status === 'rejected' ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' :
                    'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                  ]">
                    {{ presc.status?.charAt(0).toUpperCase() + presc.status?.slice(1) || 'Pending' }}
                  </span>
                </div>
                <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">Dosage: {{ presc.dosage }} · Duration: {{ presc.duration }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">Created: {{ presc.created_at ? new Date(presc.created_at).toLocaleDateString() : 'N/A' }}</p>
              </div>
            </div>
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No prescriptions yet</div>
          </div>

          <!-- Treatments -->
          <div class="bg-gray-50 dark:bg-gray-700/30 rounded-xl p-4">
            <h4 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Treatments</h4>
            <div v-if="patientDetails?.treatments?.length" class="space-y-3">
              <div v-for="treatment in patientDetails.treatments" :key="treatment.id" class="bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ treatment.treatment_type }}</p>
                <p class="text-xs text-gray-600 dark:text-gray-300 mt-1">Drugs: {{ treatment.drugs }} · Dosage: {{ treatment.dosage }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">Duration: {{ treatment.duration }} · Notes: {{ treatment.administration_notes }}</p>
              </div>
            </div>
            <div v-else class="text-center py-4 text-gray-500 dark:text-gray-400">No treatments yet</div>
          </div>
        </div>
      </div>
    </div>
  </DashboardLayout>
</template>

<script setup lang="ts">
import DashboardLayout from '~/components/DashboardLayout.vue';
const { getPatients, getPatientById } = useApi();
const router = useRouter();

const patients = ref<any[]>([]);
const searchQuery = ref('');
const currentPage = ref(1);
const perPage = 20;
const totalPatients = ref(0);
const totalPages = ref(1);
const highRiskPatients = ref(0);
const mediumRiskPatients = ref(0);
const lowRiskPatients = ref(0);
const showPatientModal = ref(false);
const selectedPatientId = ref<number | null>(null);
const selectedPatient = ref<any>(null);
const patientDetails = ref<any>(null);

function getRiskInfo(patient: any): { class: string; text: string } {
  let score = 0;
  if (patient.tb_status_label === 'Yes') score += 10;
  if (patient.genexpert_test === 'Positive') score += 8;
  if (patient.sputum_smear_test === 'Positive') score += 6;
  if (patient.chest_xray === 'Abnormal') score += 4;
  if (patient.has_fever === 'Yes') score += 1;
  if (patient.has_cough === 'Yes') score += 1;
  if (patient.has_weight_loss === 'Yes') score += 1;
  if (patient.has_night_sweats === 'Yes') score += 1;
  if (patient.has_chest_pain === 'Yes') score += 1;
  if (patient.has_blood === 'Yes') score += 2;

  if (score >= 8) {
    return { class: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400', text: 'High Risk' };
  } else if (score >= 4) {
    return { class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400', text: 'Medium Risk' };
  } else {
    return { class: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400', text: 'Low Risk' };
  }
}

function getRiskInfoFromLevel(level: string | null): { class: string } {
  if (!level) return { class: 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300' };
  const levelLower = level.toLowerCase();
  if (levelLower.includes('high')) return { class: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' };
  if (levelLower.includes('medium') || levelLower.includes('moderate')) return { class: 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400' };
  return { class: 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400' };
}

const visiblePages = computed(() => {
  const pages = [];
  const startPage = Math.max(1, currentPage.value - 2);
  const endPage = Math.min(totalPages.value, startPage + 4);
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  return pages;
});

let debounceTimer: number;
const debounceLoadResults = () => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    currentPage.value = 1;
    loadPatients();
  }, 300) as unknown as number;
};

const loadPatients = async () => {
  const res = await getPatients(currentPage.value, perPage, searchQuery.value);
  patients.value = (res as any).patients || [];
  totalPatients.value = (res as any).total || patients.value.length;
  totalPages.value = (res as any).pages || Math.ceil(totalPatients.value / perPage);
  
  // Use risk counts from API if available
  if ((res as any).risk_counts) {
    highRiskPatients.value = (res as any).risk_counts.high || 0;
    mediumRiskPatients.value = (res as any).risk_counts.medium || 0;
    lowRiskPatients.value = (res as any).risk_counts.low || 0;
  }
};

const openPatientDetails = async (patientId: number) => {
  selectedPatientId.value = patientId;
  selectedPatient.value = patients.value.find(p => p.id === patientId) || null;
  try {
    const detailsRes = await getPatientById(patientId);
    patientDetails.value = detailsRes;
  } catch (e) {
    console.error('Failed to load patient details', e);
  }
  showPatientModal.value = true;
};

const closePatientModal = () => {
  showPatientModal.value = false;
  selectedPatientId.value = null;
  selectedPatient.value = null;
  patientDetails.value = null;
};

watch(currentPage, () => loadPatients());

onMounted(async () => {
  await loadPatients();
});
</script>
