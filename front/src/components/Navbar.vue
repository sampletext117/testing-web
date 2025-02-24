<template>
  <nav class="nav">
    <span class="text-xl font-bold">EVoting</span>

    <div class="flex flex-row gap-4 items-center">
      <Chip v-if="authStore.tokenData?.role" :label="chipText">
      </Chip>
      <span v-if="ustore.email" class="text-zinc-500">
        {{ ustore.email }}
      </span>
      <Button v-if="authStore.isAuthorized" label="Выход" @click="authStore.logout" icon="pi pi-sign-out"></Button>
      <Button v-if="!authStore.isAuthorized" as="router-link" to="/login" label="Войти" icon="pi pi-sign-in"></Button>
    </div>
  </nav>
</template>

<script lang="ts" setup>
import { useAuthStore } from '@/stores/auth-store';
import { useUserStore } from '@/stores/user-store';
import { Button, Chip } from 'primevue';
import { computed } from 'vue';



const ustore = useUserStore();
const authStore = useAuthStore();

const chipText = computed(() => {
  if (authStore.tokenData?.role === 'admin') {
    return 'Администратор';
  } else if (authStore.tokenData?.role === 'candidate') {
    return 'Кандидат'
  }
  return 'Избиратель'
});


</script>

<style scoped>
.nav {
  max-width: 1200px;
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
}


</style>
