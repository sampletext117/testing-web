<template>
  <div class="flex flex-col gap-5 pb-10" v-if="dialogRef?.data.election">
    <div>
      {{ dialogRef?.data.election.description }}
    </div>
  </div>

  <div class="flex flex-col gap-5 pb-10">
    <h2 class="text-xl">Победитель</h2>

    <div v-if="electStore.results?.winner">
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
import { Column, DataTable } from 'primevue';
import { inject, watchEffect, type Ref } from 'vue';
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
