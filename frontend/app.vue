<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-emerald-600 rounded-lg flex items-center justify-center text-white text-xl font-bold">
              TB
            </div>
            <div>
              <h1 class="text-xl font-bold text-gray-900 dark:text-white">TB Diagnostic System</h1>
              <p class="text-sm text-gray-500 dark:text-gray-400">Comprehensive Patient Analysis & Treatment</p>
            </div>
          </div>
          <div class="flex items-center gap-4">
            <div v-if="isLoggedIn" class="hidden text-right md:block">
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ userDisplayName }}</p>
              <p class="text-xs uppercase tracking-wide text-emerald-600 dark:text-emerald-400">{{ userRoleLabel }}</p>
            </div>
            <button
              v-if="isLoggedIn"
              @click="logout"
              class="px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 text-sm"
            >
              Logout
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
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="!isLoggedIn" class="grid grid-cols-1 gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <section class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <p class="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-600 dark:text-emerald-400">Authenticated Clinical Workspace</p>
          <h2 class="mt-3 text-3xl font-bold text-gray-900 dark:text-white">TB diagnosis, patient review, treatment guidance, and alerts in one dashboard.</h2>
          <p class="mt-4 text-base leading-7 text-gray-600 dark:text-gray-300">
            Sign in to analyze symptoms, evaluate TB test results, review patient history from the database, and generate clinician-friendly treatment recommendations.
          </p>
          <div class="mt-6 grid gap-4 md:grid-cols-2">
            <div class="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-900/20">
              <h3 class="font-semibold text-emerald-800 dark:text-emerald-300">What the system does</h3>
              <ul class="mt-2 space-y-2 text-sm text-emerald-700 dark:text-emerald-400">
                <li>Analyzes TB symptoms and red flags</li>
                <li>Evaluates GeneXpert, smear, and X-ray results</li>
                <li>Uses patient records stored in the database</li>
                <li>Recommends treatment and follow-up monitoring</li>
              </ul>
            </div>
            <div class="rounded-xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
              <h3 class="font-semibold text-blue-800 dark:text-blue-300">Access control</h3>
              <ul class="mt-2 space-y-2 text-sm text-blue-700 dark:text-blue-400">
                <li>JWT authentication protects patient and alert data</li>
                <li>Role-based backend authorization is enforced on protected endpoints</li>
                <li>Only signed-in users can open clinical tabs</li>
                <li>Sessions restore safely on the client after page load</li>
              </ul>
            </div>
          </div>
        </section>

        <section class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
          <h2 class="text-xl font-semibold mb-2 text-gray-900 dark:text-white">Sign in</h2>
          <p class="mb-4 text-sm text-gray-500 dark:text-gray-400">Use a seeded clinician or administrator account to unlock the protected tools.</p>
          <form @submit.prevent="login" class="space-y-4">
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Email</label>
              <input
                v-model="loginEmail"
                type="email"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="you@example.com"
                required
              />
            </div>
            <div>
              <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Password</label>
              <input
                v-model="loginPassword"
                type="password"
                class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                placeholder="Password"
                required
              />
            </div>
            <p class="text-xs text-gray-500 dark:text-gray-400">
              Backend setup and seeded accounts are created with `python bootstrap.py --runserver`.
            </p>
            <p v-if="loginError" class="text-sm text-red-600 dark:text-red-400">{{ loginError }}</p>
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition"
            >
              {{ loading ? 'Signing in...' : 'Sign in' }}
            </button>
          </form>
        </section>
      </div>

      <!-- Diagnose View -->
      <div v-else-if="currentView === 'diagnose'">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Patient Form -->
          <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg">
            <h2 class="text-xl font-semibold mb-6 text-gray-900 dark:text-white">Patient Information</h2>
            <form @submit.prevent="diagnosePatient" class="space-y-4">
              <div class="grid grid-cols-2 gap-4">
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
              <div class="grid grid-cols-2 gap-4">
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
              <div class="grid grid-cols-2 gap-4">
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
              <div>
                <label class="block mb-1 text-sm font-medium text-gray-700 dark:text-gray-300">Symptoms</label>
                <textarea
                  v-model="patient.symptoms"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                  rows="3"
                  placeholder="Describe symptoms (e.g., Persistent cough, fever, night sweats, weight loss, chest pain, coughing blood)"
                ></textarea>
              </div>
              <div class="grid grid-cols-2 gap-4">
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
              <div class="grid grid-cols-2 gap-4">
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
              <div class="grid grid-cols-2 gap-4">
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
              <button
                type="submit"
                :disabled="loading"
                class="w-full bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold py-3 px-6 rounded-lg transition"
              >
                {{ loading ? 'Analyzing...' : 'Analyze & Diagnose' }}
              </button>
            </form>
          </div>

          <!-- Results -->
          <div v-if="diagnosisResult" class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg space-y-6">
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

            <!-- ML Prediction -->
            <div v-if="diagnosisResult.ml_prediction" class="space-y-3">
              <h3 class="font-semibold text-gray-800 dark:text-gray-200">ML Prediction</h3>
              <div class="p-4 bg-purple-50 dark:bg-purple-900/30 rounded-lg border border-purple-200 dark:border-purple-800">
                <p class="font-medium text-purple-800 dark:text-purple-300">
                  Drug Resistance Prediction: {{ diagnosisResult.ml_prediction.prediction }}
                </p>
                <div class="mt-2 text-sm space-y-1">
                  <p v-for="(prob, cls) in diagnosisResult.ml_prediction.probabilities" :key="cls" class="text-purple-700 dark:text-purple-400">
                    {{ cls }}: {{ prob }}%
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
                    {{ diagnosisResult.treatment_recommendation.type }}
                  </p>
                  <span class="text-xs px-2 py-1 bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300 rounded font-medium">
                    {{ diagnosisResult.treatment_recommendation.urgency }}
                  </span>
                </div>
                <p class="text-sm text-emerald-700 dark:text-emerald-400 mb-1">
                  <strong>Category:</strong> {{ diagnosisResult.treatment_recommendation.category }}
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
                <p class="text-xs text-emerald-600 dark:text-emerald-500 mt-2">
                  {{ diagnosisResult.treatment_recommendation.notes }}
                </p>
              </div>
            </div>

            <p class="text-xs text-gray-500 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              Disclaimer: This system is for educational purposes only. Always consult qualified medical professionals.
            </p>
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
const currentUser = ref(null)
const token = ref('')
const loginEmail = ref('')
const loginPassword = ref('')
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

const patient = ref({
  patient_id: '',
  first_name: '',
  last_name: '',
  age: 30,
  gender: 'Male',
  city: '',
  symptoms: '',
  sputum_smear_test: 'Unknown',
  genexpert_test: 'Unknown',
  chest_xray: 'Unknown',
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
