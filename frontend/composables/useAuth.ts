
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'doctor' | 'lab_technician' | 'pharmacist' | 'hospital_admin' | 'patient';
}

export interface Patient {
  id: number;
  patient_id: string;
  first_name: string;
  last_name: string;
  role: 'patient';
}

export const useAuth = () => {
  const authToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 });
  const currentUser = useState<User | Patient | null>('auth_user', () => null);

  const isLoggedIn = computed(() => !!authToken.value && !!currentUser.value);

  const userRole = computed(() => currentUser.value?.role);

  const login = async (identifier: string, password: string, type: string = 'clinician') => {
  try {
    const body: any = { password, type };
    if (type === 'patient') {
      body.patient_id = identifier;
    } else {
      body.email = identifier;
    }

    const data = await $fetch('http://127.0.0.1:5000/api/auth/login', {
      method: 'POST',
      body,
    });

    authToken.value = (data as any).access_token;
    localStorage.setItem('auth_token', (data as any).access_token);

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
  };
};

