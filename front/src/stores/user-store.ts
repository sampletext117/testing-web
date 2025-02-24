import { useApi } from '@/api/api';
import { defineStore } from 'pinia';
import { useAuthStore } from './auth-store';
import { ref, watch, watchEffect } from 'vue';

export const useUserStore = defineStore('user', () => {
  const api = useApi();
  const authStore = useAuthStore();

  const email = ref('');

  watchEffect(() => {
    const token = authStore.tokenData;
    console.log('authStore.tokenData changed')
    if (!token) {
      return
    }
    email.value = token.sub;
  });

  return {
    email,

  };
});
