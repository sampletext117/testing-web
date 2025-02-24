import { useApi } from '@/api/api';
import type { Candidate, Vote, VoteCreateRequest } from '@/api/types';
import { mockVoters, mockVotes } from '@/mocks';
import { defineStore } from 'pinia';
import { computed, ref, watchEffect } from 'vue';
import { useRouter } from 'vue-router';

export const useVoteStore = defineStore('vote', () => {
  const api = useApi();
  const router = useRouter();

  const votes = ref<Vote[]>([]);

  const fetchVotes = async () => {
    const { data } = await api.value.GET("/v1/votes");
    votes.value = data ?? [];

    // votes.value = mockVotes;
  }

  const vote = async (vote: VoteCreateRequest) => {
    const { data } = await api.value.POST("/v1/votes", {
      body: {
        ...vote,
      }
    });
    fetchVotes();
  }

  return {
    votes,

    fetchVotes,
    vote,
  };
});
