<template>
  <h2 class="text-xl pb-5">Регистрация кандидата</h2>
  <div class="flex">
    <Card style="width: 50rem;" class=" max-w-screen p-2">
      <template #title>Данные</template>
      <template #content>
        <div class="flex flex-col gap-4">
          <div class="flex flex-col gap-2">
            <span>ФИО</span>
            <InputText type="text" v-model="full_name" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Дата рождения</span>
            <DatePicker v-model="birth_date" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Номер паспорта</span>
            <InputNumber v-model="passport_number" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Участок</span>
            <InputText type="text" v-model="issued_by" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Дата регистрации</span>
            <DatePicker v-model="issue_date" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Страна</span>
            <InputText type="text" v-model="country" placeholder="Россия" />
          </div>
          <div class="flex flex-col gap-2">
            <span>Описание программы</span>
            <Textarea v-model="description" rows="5" cols="30"></Textarea>
          </div>
          <div class="flex flex-col gap-2">
            <span>Начальный баланс</span>
            <InputNumber type="text" v-model="balance" placeholder="0" />
          </div>
          <div class="pt-4">
            <Button class="w-full" @click="createCandidate" label="Регистрация"></Button>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts" setup>
import { useCandidateStore } from '@/stores/candidate-store';
import type { Candidate } from '@/api/types';
import { Button, Card, InputText, Textarea } from 'primevue';
import { reactive, ref } from 'vue';
import InputNumber from 'primevue/inputnumber';
import { DateTime } from 'luxon';

// {
//   "full_name": "string",
//   "birth_date": "2025-02-23",
//   "passport_number": "string",
//   "issued_by": "string",
//   "issue_date": "2025-02-23",
//   "country": "string",
//   "program_description": "string",
//   "initial_balance": 0
// }

import DatePicker from 'primevue/datepicker';
import { useVoterStore } from '@/stores/voter-store';
import { useRouter } from 'vue-router';

const candStore = useCandidateStore();
const router = useRouter()

const full_name = ref('');
const birth_date = ref(new Date());
const passport_number = ref<number>();
const issued_by = ref('');
const issue_date = ref(new Date());
const country = ref('Россия');
const description = ref('');
const balance = ref(0);

const createCandidate = async () => {
  await candStore.createCandidate({
    full_name: full_name.value,
    birth_date: DateTime.fromJSDate(birth_date.value).toISODate() ?? '',
    passport_number: String(passport_number.value),
    issued_by: issued_by.value,
    issue_date: DateTime.fromJSDate(issue_date.value).toISODate(),
    country: country.value,
    initial_balance: balance.value,
    program_description: description.value
  })

  if (candStore.self) {
    router.push({
      path: '/candidate',
    })
  }
}

</script>

<style scoped></style>
