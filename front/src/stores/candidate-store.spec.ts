import { setActivePinia, createPinia } from 'pinia';
import { useCandidateStore } from '@/stores/candidate-store';
import { vi, describe, it, beforeEach, expect, afterEach } from 'vitest';

describe('Candidate Store', () => {
    let candidateStore: ReturnType<typeof useCandidateStore>;
    const mockApi = vi.hoisted(() => ({
        GET: vi.fn(),
        PATCH: vi.fn(),
    }));

    beforeEach(() => {
        setActivePinia(createPinia());
        vi.mock('@/api/api', () => ({ useApi: () => ({ value: mockApi }) }));
        candidateStore = useCandidateStore();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('initializes with default values', () => {
        expect(candidateStore.candidates).toEqual([]);
        expect(candidateStore.candidate).toBeUndefined();
        expect(candidateStore.self).toBeUndefined();
    });

    it('fetches candidates and updates state', async () => {
        const mockCandidateList = [{ id: 1, name: 'Candidate 1' }, { id: 2, name: 'Candidate 2' }];
        mockApi.GET.mockResolvedValueOnce({ data: mockCandidateList });

        await candidateStore.fetchCandidates();
        expect(candidateStore.candidates).toEqual(mockCandidateList);
    });

    it('fetches a specific candidate and updates state', async () => {
        const mockCandidate = { id: 1, name: 'Mock Candidate' };
        mockApi.GET.mockResolvedValueOnce({ data: mockCandidate });

        await candidateStore.fetchCandidate(1);
        expect(candidateStore.candidate).toEqual(mockCandidate);
    });

    it('handles fetchCandidate when API returns no data', async () => {
        mockApi.GET.mockResolvedValueOnce({ data: null });

        await candidateStore.fetchCandidate(1);
        expect(candidateStore.candidate).toBeNull();
    });

    it('updates self candidate details', async () => {
        const updatedData = {
          program_description: 'program description',
        };
        mockApi.PATCH.mockResolvedValueOnce({ data: updatedData });
        candidateStore.self = {
          candidate_id: 123
        }

        await candidateStore.patchSelf(updatedData);
        expect(candidateStore.self).toEqual(updatedData);
    });
});
