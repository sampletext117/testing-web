<template>
  <div class="flex flex-col gap-5 pb-10" v-if="dialogRef?.data.election">
    <!-- <h2 class="text-xl">{{dialogRef?.data.election.election_name}}</h2> -->
    <div>
      {{ dialogRef?.data.election.description }}
    </div>
  </div>

  <h2 class="text-xl pb-5">Список кандидатов</h2>

  <DataTable :value="candStore.candidates" tableStyle="min-width: 50rem" class="overflow-x-auto max-w-screen">
    <Column field="full_name" header="ФИО"></Column>
    <Column field="birth_date" header="Дата рождения"></Column>
    <Column header="">
      <template #body="slotProps">
        <Button v-if="!alreadyVoted" @click="vote(slotProps.data)" label="Голосовать" :text="true"></Button>
        <template v-if="alreadyVoted">
          <span v-if="isVoted(slotProps.data)" class="text-green-500">Вы проголосовали</span>
          <span v-else>Нельзя проголосовать</span>
        </template>
      </template>
    </Column>
  </DataTable>
</template>

<script lang="ts" setup>
import { useCandidateStore } from '@/stores/candidate-store';
import { Button, Column, DataTable } from 'primevue';
import type { Candidate } from '@/api/types';
import { useVoteStore } from '@/stores/vote-store';
import { useVoterStore } from '@/stores/voter-store';
import { computed, inject, type Ref } from 'vue';
import type { DynamicDialogInstance } from 'primevue/dynamicdialogoptions';

const candStore = useCandidateStore();
const voteStore = useVoteStore();
const voterStore = useVoterStore();

const dialogRef = inject<Ref<DynamicDialogInstance>>('dialogRef');

candStore.fetchCandidates();
voteStore.fetchVotes();
voterStore.fetchVoters();

const alreadyVoted = computed(() => {
  const votes = voteStore.votes;
  const election_id = dialogRef?.value.data.election.election_id;
  const self = voterStore.self;
  console.log(votes, election_id, self)

  return Boolean(votes.find(vote => vote.election_id == election_id && vote.voter_id == self?.voter_id));
});

const isVoted = (cand: Candidate) => {
  const votes = voteStore.votes;
  const election_id = dialogRef?.value.data.election.election_id;
  const self = voterStore.self;

  return Boolean(votes.find(vote =>
    vote.election_id == election_id
    && vote.voter_id == self?.voter_id
    && vote.candidate_id == cand.candidate_id));
}

const vote = async (data: Candidate) => {
  const election_id = dialogRef?.value.data.election.election_id;
  const self = voterStore.self;
  await voteStore.vote({
    candidate_id: data.candidate_id ?? 0,
    election_id: election_id,
    voter_id: self?.voter_id ?? 0,
  })

  await voteStore.fetchVotes();
}

</script>

<style scoped></style>
