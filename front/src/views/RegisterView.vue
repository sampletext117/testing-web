<template>
  <div class="login">
    <Card class="w-96 max-w-screen p-2">
      <template #title>Регистрация в EVoting</template>
      <template #content>
        <div class="flex flex-col gap-5">
          <div class="flex flex-col gap-2">
            <span>Почта</span>
            <InputText type="text" v-model="email" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Пароль</span>
            <Password :feedback="false" @keydown.enter="register" toggleMask v-model="password" />
          </div>
          <div>
            <Select v-model="selectedRole" :options="roles" optionLabel="name" optionValue="value" class="w-full">
            </Select>
          </div>
          <Button @click="register" label="Зарегистрироваться"></Button>
        </div>


        <div class="flex flex-row pt-4 items-center justify-center gap-1">
          <span class="pb-1">Уже зарегистрированы?</span>
          <Button to="/login" size="small" as="router-link" label="Войти" text></Button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { useApi } from '@/api/api';
import Select from 'primevue/select';
import Card from 'primevue/card';
import { Button, Password } from 'primevue';
import InputText from 'primevue/inputtext';
import { ref, watchEffect } from 'vue';
import { useAuthStore } from '@/stores/auth-store';
import { useRouter } from 'vue-router';
import { useCandidateStore } from '@/stores/candidate-store';
import { useVoterStore } from '@/stores/voter-store';

const authStore = useAuthStore();
const candStore = useCandidateStore();
const voterStore = useVoterStore();
const router = useRouter();

const email = ref('');
const password = ref('');

const roles: Array<{ value: 'candidate' | 'voter', name: string }> = [
  { value: 'candidate', name: 'Я Кандидат' },
  { value: 'voter', name: 'Я Избиратель' },
]

const selectedRole = ref(roles[0].value);

watchEffect(() => {
  if (authStore.isAuthorized) {
    if (selectedRole.value === 'candidate') {
      candStore.clearSelfCandidate();
    } else {
      voterStore.clearSelfVoter();
    }

    router.push({
      path: '/dashboard'
    });
  }
})

const register = async () => {
  await authStore.register({
    email: email.value,
    password: password.value,
    role: selectedRole.value,
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
