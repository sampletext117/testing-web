import { useApi } from '@/api/api';
import type { Voter, VoterCreateRequest } from '@/api/types';
import { mockVotes } from '@/mocks';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const VOTER_KEY = "selfVoter";

export const useVoterStore = defineStore('voter', () => {
  const api = useApi();
  const router = useRouter();

  const voters = ref<Voter[]>([]);
  const voter = ref<Voter>();
  const self = ref<Voter>();

  const savedSelf = localStorage.getItem(VOTER_KEY);
  if (savedSelf) {
    self.value = JSON.parse(savedSelf);
  }


  const fetchVoters = async () => {
    const { data } = await api.value.GET("/v1/voters");
    voters.value = data ?? [];
    // voters.value = mockVoters;
  }

  const fetchVoter = async (id: number) => {
    const { data } = await api.value.GET("/v1/voters/{voter_id}", {
      params: {
        path: {
          voter_id: id,
        }
      }
    });
    voter.value = data;
  }


  const createVoter = async (values: VoterCreateRequest) => {
    const { data, error } = await api.value.POST("/v1/voters", {
      body: {
        ...values
      }
    });
    if (data && !error) {
      const voter: Voter = {
        ...data,
      }
      self.value = voter;
      localStorage.setItem(VOTER_KEY, JSON.stringify(voter));
    }
  }

  const hasSavedVoter = () => {
    return !!localStorage.getItem(VOTER_KEY);
  }

  const clearSelfVoter = () => {
    localStorage.removeItem(VOTER_KEY);
    self.value = undefined;
  }


  return {
    voters,
    voter,
    self,

    fetchVoters,
    fetchVoter,
    hasSavedVoter,
    createVoter,
    clearSelfVoter,
  };
});
