<template>

  <h2 class="text-xl pb-5">Профиль администратора</h2>
  <div class="flex flex-row justify-center w-full pb-10">
    <SelectButton v-model="selectedTab" :options="options" :allow-empty="false" />
  </div>

  <div v-if="selectedTab === 'Новые выборы'" style="width: 50rem;" class="max-w-screen">
    <h3 class="text-xl pb-4">Создать выборы</h3>
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <span>Название</span>
        <InputText type="text" v-model="election_name" />
      </div>
      <div class="flex flex-col gap-2">
        <span>Дата начала</span>
        <DatePicker v-model="start_date" />
      </div>
      <div class="flex flex-col gap-2">
        <span>Дата окончания</span>
        <DatePicker v-model="end_date" />
      </div>
      <div class="flex flex-col gap-2">
        <span>Описание</span>
        <Textarea v-model="description" rows="5" cols="30" ></Textarea>
      </div>
      <div class="pt-4">
        <Button class="w-full" @click="createElection" label="Создать"></Button>
      </div>
    </div>
  </div>

  <div v-if="selectedTab === 'Выборы'">
    <DataTable :value="electStore.elections" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
      <Column field="election_name" header="Название"></Column>
      <Column field="start_date" header="Начало"></Column>
      <Column field="end_date" header="Окончание"></Column>
      <Column header="">
        <template #body="slotProps">
          <Button v-if="!isActive(slotProps.data)" @click="showResults(slotProps.data)" label="Результаты" :text="true"></Button>
          <div v-if="isActive(slotProps.data)" class="h-10"></div>
        </template>
      </Column>
    </DataTable>
  </div>

  <div v-if="selectedTab === 'Кандидаты'">
    <DataTable :value="candStore.candidates" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
      <Column field="full_name" header="ФИО"></Column>
      <Column field="birth_date" header="Дата рождения"></Column>
    </DataTable>
  </div>

  <div v-if="selectedTab === 'Избиратели'">
    <DataTable :value="voterStore.voters" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
      <Column field="full_name" header="ФИО"></Column>
      <Column field="birth_date" header="Дата рождения"></Column>
      <Column field="passport_id" header="Номер паспорта"></Column>
    </DataTable>
  </div>


</template>

<script lang="ts" setup>
import { useCandidateStore } from '@/stores/candidate-store';
import { useElectionStore } from '@/stores/election-store';
import { useVoterStore } from '@/stores/voter-store';
import { Button, Column, DataTable, DatePicker, InputText, useDialog } from 'primevue';
import SelectButton from 'primevue/selectbutton';
import { ref, watchEffect } from 'vue';
import type { Election } from '@/api/types';
import Textarea from 'primevue/textarea';
import { DateTime } from 'luxon';
import ElectionResults from './ElectionResults.vue';


const dialog = useDialog();
const electStore = useElectionStore();
const candStore = useCandidateStore();
const voterStore = useVoterStore();

const options = ['Выборы', 'Новые выборы', 'Кандидаты', 'Избиратели'];
const selectedTab = ref(options[0]);

watchEffect(() => {
  switch (selectedTab.value) {
    case 'Выборы':
      electStore.fetchElections();
      break;
    case 'Кандидаты':
      candStore.fetchCandidates();
      break;
    case 'Избиратели':
      voterStore.fetchVoters();
      break;
  }
})

const election_name = ref('');
const start_date = ref(new Date());
const end_date = ref(new Date());
const description = ref('');

const createElection = async () => {
  await electStore.createElection({
    election_name: election_name.value,
    start_date: DateTime.fromJSDate(start_date.value).toISODate() ?? '',
    end_date: DateTime.fromJSDate(end_date.value).toISODate() ?? '',
    description: description.value,
  })
}

const isActive = (elect: Election) => {
  return elect.end_date && Date.parse(elect.end_date) > Date.now();
}


const showResults = (data: Election) => {
  dialog.open(ElectionResults, {
    props: {
      header: data.election_name,
      style: {
        width: '50vw',
        // height: '40vh',
      },
      breakpoints: {
        '960px': '75vw',
        '640px': '90vw'
      },
      modal: true,
      dismissableMask: true,
    },
    data: {
      election: data,
    }
  });
}


</script>

<style scoped></style>
