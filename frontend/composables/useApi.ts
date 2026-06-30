
import type { User } from './useAuth';

export interface Patient {
  id: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  age: number;
  gender: string;
  city: string;
  symptoms: string;
  tb_risk_score?: number;
  tb_risk_level?: string;
  tb_type?: string;
}

export interface DetailedLabResult {
  id: number;
  patient_id?: number;
  hospital?: string;
  test_name: string;
  test_value?: string;
  unit?: string;
  reference_range?: string;
  collection_date?: string;
  source_dataset?: string;
}

export interface AntibioticResistance {
  id: number;
  sample_id: string;
  patient_name?: string;
  patient_email?: string;
  bacterial_species?: string;
  diabetes?: string;
  hypertension?: string;
  amx_amp?: string;
  amc?: string;
  cz?: string;
  fox?: string;
  ctx_cro?: string;
  ipm?: string;
  gen?: string;
  an?: string;
  nalidixic_acid?: string;
  ofx?: string;
  cip?: string;
  chloramphenicol?: string;
  co_trimoxazole?: string;
  furanes?: string;
  colistine?: string;
  notes?: string;
}

export const useApi = () => {
  const { authToken } = useAuth();
  const config = useRuntimeConfig();
  const API_BASE = config.public.apiBase;

  const request = async (url: string, options: any = {}) => {
    return $fetch(`${API_BASE}${url}`, {
      ...options,
      headers: {
        Authorization: authToken.value ? `Bearer ${authToken.value}` : undefined,
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });
  };

  return {
    getPatients: (page = 1, perPage = 20, search = '') => {
      let url = `/patients?page=${page}&per_page=${perPage}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;
      return request(url);
    },
    getPatientById: (id: number) => request(`/patients/${id}`),
    createPatient: (data: Partial<Patient>) => request('/patients', { method: 'POST', body: data }),
    getDetailedLabResults: (page = 1, perPage = 20) => request(`/detailed-lab-results?page=${page}&per_page=${perPage}`),
    getAntibioticResistanceRecords: (page = 1, perPage = 20) => request(`/antibiotic-resistance?page=${page}&per_page=${perPage}`),
    getPrescriptions: () => request('/prescriptions'),
    getDashboardStats: () => request('/dashboard'),
    diagnose: (data: any) => request('/diagnose', { method: 'POST', body: data }),
    getDiagnoses: (page = 1, perPage = 20) => request(`/diagnoses?page=${page}&per_page=${perPage}`),
    getAtcDrugs: (page = 1, perPage = 20) => request(`/atc-drugs?page=${page}&per_page=${perPage}`),
    getAlerts: (page = 1, perPage = 20, unreadOnly = false) => {
      let url = `/alerts?page=${page}&per_page=${perPage}`;
      if (unreadOnly) url += `&unread_only=true`;
      return request(url);
    },
    markAlertRead: (id: number) => request(`/alerts/${id}/read`, { method: 'PUT' }),
    getDashboardCharts: () => request('/dashboard/charts'),
    // Pharmacy inventory methods
    getPharmacyInventory: () => request('/pharmacy-inventory'),
    createPharmacyInventory: (data: any) => request('/pharmacy-inventory', { method: 'POST', body: data }),
    updatePharmacyInventory: (id: number, data: any) => request(`/pharmacy-inventory/${id}`, { method: 'PUT', body: data }),
    checkPrescriptionStock: (id: number) => request(`/prescriptions/${id}/check-stock`),
    approvePrescription: (id: number, data: any) => request(`/prescriptions/${id}`, { method: 'PUT', body: data }),
    dispensePrescription: (id: number) => request(`/prescriptions/${id}/dispense`, { method: 'POST' }),
    getHospitals: () => request('/hospitals'),
    // Lab test methods
    getPendingLabTests: () => request('/lab-tests/pending'),
    getAllLabTests: () => request('/lab-tests'),
    updateLabTestStatus: (id: number, status: string) => request(`/lab-tests/${id}`, { method: 'PUT', body: { status } }),
    submitLabTestResult: (id: number, data: any) => request(`/lab-tests/${id}/submit-result`, { method: 'POST', body: data }),
  };
};

