const unreadAlertCount = ref(0);

export const useAlertCount = () => {
  const { authToken, userRole } = useAuth();
  const config = useRuntimeConfig();

  const refresh = async () => {
    if (!authToken.value || userRole.value === 'patient') return;
    try {
      const res = await fetch(`${config.public.apiBase}/alerts/unread-count`, {
        headers: { 'Authorization': `Bearer ${authToken.value}` }
      });
      const data = await res.json();
      unreadAlertCount.value = data.unread_count || 0;
    } catch {}
  };

  return { unreadAlertCount, refresh };
};
