<template>
  <div class="flex flex-col gap-5 pb-10" v-if="dialogRef?.data.election">
    <!-- <h2 class="text-xl">{{dialogRef?.data.election.election_name}}</h2> -->
    <div>
      {{ dialogRef?.data.election.description }}
    </div>
  </div>


  <div v-if="electStore.results?.winner" class="flex flex-col gap-5 pb-10">
    <h2 class="text-xl">Победитель</h2>

    <div>
      <span class="font-bold">
        {{ electStore.results?.winner?.candidate_name }} ({{ electStore.results?.winner?.vote_count }} голосов)
      </span>
    </div>
  </div>

  <div class="flex flex-col gap-5">
    <h2 class="text-xl pb-5">Кандидаты</h2>

    <DataTable :value="electStore.results?.results" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
      <Column field="candidate_name" header="ФИО"></Column>
      <Column field="vote_count" header="Количество голосов"></Column>
    </DataTable>
  </div>
</template>

<script lang="ts" setup>
import { useCandidateStore } from '@/stores/candidate-store';
import { Button, Column, DataTable } from 'primevue';
import type { Candidate } from '@/api/types';
import { useVoteStore } from '@/stores/vote-store';
import { useVoterStore } from '@/stores/voter-store';
import { computed, inject, watchEffect, type Ref } from 'vue';
import type { DynamicDialogInstance } from 'primevue/dynamicdialogoptions';
import { useElectionStore } from '@/stores/election-store';

const dialogRef = inject<Ref<DynamicDialogInstance>>('dialogRef');
const electStore = useElectionStore();

watchEffect(() => {
  const election_id = dialogRef?.value.data.election.election_id;

  if (election_id) {
    electStore.fetchResults(election_id);
  }
});

</script>

<style scoped></style>
