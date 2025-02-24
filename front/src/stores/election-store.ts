import { useApi } from '@/api/api';
import type { Election, ElectionCreateRequest } from '@/api/types';
import { mockElections } from '@/mocks';
import { defineStore } from 'pinia';
import { computed, ref, watchEffect } from 'vue';
import { useRouter } from 'vue-router';


export const useElectionStore = defineStore('election', () => {
  const api = useApi();
  const router = useRouter();

  const elections = ref<Election[]>([]);
  const election = ref<Election>();

  const fetchElections = async () => {
    const { data } = await api.value.GET("/v1/elections");
    elections.value = data ?? [];
    // elections.value = mockElections;
  }

  const fetchElection = async (id: number) => {
    const { data } = await api.value.GET("/v1/elections/{election_id}", {
      params: {
        path: {
          election_id: id,
        }
      }
    });
    election.value = data;
  }

  const createElection = async (values: ElectionCreateRequest) => {
    const { data, error } = await api.value.POST("/v1/elections", {
      body: {
        ...values
      }
    });

    if (data) {
      fetchElections();
    }
  }

  return {
    elections,
    election,

    fetchElections,
    fetchElection,
    createElection,

  };
});
