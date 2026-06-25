
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'doctor' | 'lab_tech' | 'pharmacist' | 'hospital_admin';
}

export const useAuth = () => {
  const authToken = useCookie('auth_token', { maxAge: 60 * 60 * 24 * 7 });
  const currentUser = useState<User | null>('auth_user', () => null);

  const isLoggedIn = computed(() => !!authToken.value && !!currentUser.value);

  const userRole = computed(() => currentUser.value?.role);

  const login = async (email: string, password: string) => {
    try {
      const data = await $fetch('http://127.0.0.1:5000/api/auth/login', {
        method: 'POST',
        body: { email, password },
      });

      authToken.value = (data as any).access_token;

      const userProfile = (data as any).user;

      currentUser.value = userProfile as User;
      return { success: true };
    } catch (e) {
      console.error(e);
      return { success: false, error: (e as any).data?.msg || 'Login failed' };
    }
  };

  const logout = () => {
    authToken.value = null;
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

