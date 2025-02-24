<template>
  <div class="login">
    <Card class="w-96 max-w-screen p-2">
      <template #title>Вход в EVoting</template>
      <template #content>
        <div class="flex flex-col gap-5">
          <div class="flex flex-col gap-2">
            <span>Почта</span>
            <InputText type="text" v-model="email" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Пароль</span>
            <Password :feedback="false" @keydown.enter="login" toggleMask  v-model="password" />
          </div>
          <Button @click="login"  label="Войти"></Button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { useApi } from '@/api/api';
import Card from 'primevue/card';
import { Button, Password } from 'primevue';
import InputText from 'primevue/inputtext';
import { ref, watchEffect } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

const email = ref('');
const password = ref('');

watchEffect(() => {
    if (authStore.isAuthorized) {
        router.push({
            path: '/dashboard'
        });
    }
})

const login = () => {
  authStore.login({
    email: email.value,
    password: password.value,
  })
}

</script>

<style>

.login {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
