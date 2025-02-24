<template>
  <h2 class="text-xl">Активные выборы</h2>
  <DataTable :value="activeElections" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
    <Column field="election_name" header="Название"></Column>
    <Column field="start_date" header="Начало"></Column>
    <Column field="end_date" header="Окончание"></Column>
    <Column header="">
      <template #body="slotProps">
        <Button v-if="authStore.tokenData?.role === 'voter'" @click="vote(slotProps.data)" label="Голосовать"
          :text="true"></Button>
      </template>
    </Column>
  </DataTable>

  <h2 class="text-xl pt-10">Прошедшие выборы</h2>
  <DataTable :value="passedElections" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
    <Column field="election_name" header="Название"></Column>
    <Column field="start_date" header="Начало"></Column>
    <Column field="end_date" header="Окончание"></Column>
    <!-- <Column header="">
      <template #body="slotProps">
        <Button @click="vote(slotProps.data)" label="Голосовать" :text="true"></Button>
      </template>
    </Column> -->
  </DataTable>
</template>

<script lang="ts" setup>
import type { Election } from '@/api/types';
import { useElectionStore } from '@/stores/election-store';
import { DataTable, Column, Button } from 'primevue';
import { computed } from 'vue';
import { useDialog } from 'primevue/usedialog';
import SelectCandidateModal from './SelectCandidateModal.vue';
import { useAuthStore } from '@/stores/auth-store';
import { useVoterStore } from '@/stores/voter-store';
import { useRouter } from 'vue-router';

const dialog = useDialog();
const electionStore = useElectionStore();
const authStore = useAuthStore();
const voterStore = useVoterStore();
const router = useRouter();


if (authStore.tokenData?.role === 'voter' && !voterStore.hasSavedVoter()) {
  router.push({
    'path': '/register/voter',
  })
}

electionStore.fetchElections();

const activeElections = computed(() => {
  const now = Date.now();
  return electionStore.elections.filter(elect => elect.end_date && Date.parse(elect.end_date) > now)
})

const passedElections = computed(() => {
  const active = activeElections.value;
  return electionStore.elections.filter(elect => !active.includes(elect));
})

const vote = (data: Election) => {
  dialog.open(SelectCandidateModal, {
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
