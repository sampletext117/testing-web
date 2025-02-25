<template>
  <h2 class="text-xl pb-5">Профиль кандидата</h2>
  <div class="flex">
    <Card class="w-2xl max-w-screen p-2">
      <template #title>Данные</template>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <span>ФИО</span>
            <InputText disabled type="text" v-model="full_name" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Дата рождения</span>
            <DatePicker disabled v-model="birth_date" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Номер паспорта</span>
            <InputNumber disabled v-model="passport_number" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Описание программы</span>
            <Textarea v-model="description" rows="5" cols="30"></Textarea>
          </div>
          <div class="pt-4">
            <Button class="w-full" @click="save" label="Сохранить"></Button>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { useCandidateStore } from '@/stores/candidate-store';
import type { Candidate } from '@/api/types';
import { Button, Card, InputNumber, InputText, Textarea } from 'primevue';
import { reactive, ref } from 'vue';
import DatePicker from 'primevue/datepicker';
import { useRouter } from 'vue-router';

const candStore = useCandidateStore();
const router = useRouter();

if (!candStore.hasSavedCandidate()) {
  router.push({
    path: '/register/candidate'
  })
}

const full_name = ref(candStore.self?.full_name ?? '');
const birth_date = ref(new Date(candStore.self?.birth_date ?? ''));
const passport_number = ref(candStore.self?.passport_id ?? 0);
const description = ref(candStore.self?.program_description ?? '');


const save = async () => {
  await candStore.patchSelf({
   program_description: description.value,
  })
}

</script>

<style scoped>

</style>
