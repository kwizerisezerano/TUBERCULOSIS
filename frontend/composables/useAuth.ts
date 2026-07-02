
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'doctor' | 'lab_technician' | 'pharmacist' | 'hospital_admin' | 'patient';
  hospital_id: number;
  hospital?: any;
}

export interface Patient {
  id: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  role: 'patient';
}

export const useAuth = () => {
  const authToken = useCookie<string | null>('auth_token', { maxAge: 60 * 60 * 24 * 7, sameSite: 'lax' });
  const currentUser = useState<User | Patient | null>('auth_user', () => null);

  const isLoggedIn = computed(() => !!authToken.value);

  const restoreSession = async () => {
    const token = authToken.value || (process.client ? localStorage.getItem('auth_token') : null);
    if (!token || currentUser.value) {
      if (token) {
        authToken.value = token;
      }
      return;
    }

    authToken.value = token;

    try {
      const config = useRuntimeConfig();
      const data = await $fetch(`${config.public.apiBase}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      currentUser.value = ((data as any).user || (data as any).patient) as User | Patient;
      if (process.client) {
        localStorage.setItem('auth_token', token);
      }
    } catch (error: any) {
      const status = error?.response?.status;
      if (status === 401 || status === 403) {
        authToken.value = null;
        currentUser.value = null;
        if (process.client) {
          localStorage.removeItem('auth_token');
        }
      }
    }
  };

  const userRole = computed(() => currentUser.value?.role);

  const login = async (identifier: string, password: string, type: string = 'clinician') => {
  try {
    const body: any = { password, type };
    if (type === 'patient') {
      body.patient_id = identifier;
    } else {
      body.email = identifier;
    }

    const config = useRuntimeConfig()
    const data = await $fetch(`${config.public.apiBase}/auth/login`, {
      method: 'POST',
      body,
    });

    const token = (data as any).access_token;
    authToken.value = token;
    localStorage.setItem('auth_token', token);

    if (type === 'patient') {
      currentUser.value = (data as any).patient as Patient;
    } else {
      currentUser.value = (data as any).user as User;
    }

    return { success: true };
  } catch (e) {
    console.error(e);
    return { success: false, error: (e as any).data?.msg || 'Login failed' };
  }
};

const logout = () => {
  authToken.value = null;
  localStorage.removeItem('auth_token');
  currentUser.value = null;
  navigateTo('/');
};

  return {
    authToken,
    currentUser,
    isLoggedIn,
    userRole,
    login,
    logout,
    restoreSession,
  };
};

