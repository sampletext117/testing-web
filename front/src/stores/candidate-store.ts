import { useApi } from '@/api/api';
import type { Candidate, CandidateCreateRequest, CandidatePatchRequest } from '@/api/types';
import { mockCandidates } from '@/mocks';
import { defineStore } from 'pinia';
import { computed, ref, watchEffect } from 'vue';
import { useRouter } from 'vue-router';

const CANDIDATE_KEY = 'selfCandidate';

type CandidateAdditionalData = Pick<CandidateCreateRequest, 'program_description'>;

export const useCandidateStore = defineStore('candidate', () => {
  const api = useApi();
  const router = useRouter();

  const candidates = ref<Candidate[]>([]);
  const candidate = ref<Candidate>();
  const self = ref<Candidate & CandidateAdditionalData>();

  const savedSelf = localStorage.getItem(CANDIDATE_KEY);
  if (savedSelf) {
    self.value = JSON.parse(savedSelf);
  }

  const fetchCandidates = async () => {
    const { data } = await api.value.GET("/v1/candidates");
    candidates.value = data ?? [];
    // candidates.value = mockCandidates;
  }

  const fetchCandidate = async (id: number) => {
    const { data } = await api.value.GET("/v1/candidates/{candidate_id}", {
      params: {
        path: {
          candidate_id: id,
        }
      }
    });
    candidate.value = data;
  }

  const patchSelf = async (value: CandidatePatchRequest) => {
    if (!self.value) {
      console.log('Error self not presented');
      return;
    }
    const id = self.value.candidate_id ?? 0;
    const { data, error } = await api.value.PATCH("/v1/candidates/{candidate_id}", {
      params: {
        path: {
          candidate_id: id,
        }
      },
      body: {
        ...value
      }
    });

    if (data && !error) {
      const cand: Candidate & CandidateAdditionalData = {
        ...data,
        program_description: value.program_description,
      }
      self.value = cand;
      localStorage.setItem(CANDIDATE_KEY, JSON.stringify(cand));
    }
  }

  const createCandidate = async (values: CandidateCreateRequest) => {
    const { data, error } = await api.value.POST("/v1/candidates", {
      body: {
        ...values
      }
    });
    if (data && !error) {
      const cand: Candidate & CandidateAdditionalData = {
        ...data,
        program_description: values.program_description,
      }
      self.value = cand;
      localStorage.setItem(CANDIDATE_KEY, JSON.stringify(cand));
    }
  }

  const hasSavedCandidate = () => {
    return !!localStorage.getItem(CANDIDATE_KEY);
  }

  return {
    candidates,
    candidate,
    self,

    fetchCandidates,
    fetchCandidate,
    patchSelf,
    hasSavedCandidate,
    createCandidate,
  };
});
