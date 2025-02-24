import { setActivePinia, createPinia } from 'pinia';
import { useVoterStore } from '@/stores/voter-store';
import { vi, describe, it, beforeEach, expect, afterEach } from 'vitest';

describe('Voter Store', () => {
    let voterStore: ReturnType<typeof useVoterStore>;
    const mockApi = vi.hoisted(() => ({
        GET: vi.fn(),
    }));

    beforeEach(() => {
        setActivePinia(createPinia());
        vi.mock('@/api/api', () => ({ useApi: () => ({ value: mockApi }) }));
        voterStore = useVoterStore();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('initializes with default values', () => {
        expect(voterStore.voters).toEqual([]);
        expect(voterStore.voter).toBeUndefined();
        expect(voterStore.self).toBeDefined();
    });

    it('fetches voters and updates state', async () => {
        const mockVoterList = [{ id: 1, name: 'Voter 1' }, { id: 2, name: 'Voter 2' }];
        mockApi.GET.mockResolvedValueOnce({ data: mockVoterList });

        await voterStore.fetchVoters();
        expect(voterStore.voters).toEqual(mockVoterList);
    });

    it('fetches a specific voter and updates state', async () => {
        const mockVoter = { id: 1, name: 'Mock Voter' };
        mockApi.GET.mockResolvedValueOnce({ data: mockVoter });

        await voterStore.fetchVoter(1);
        expect(voterStore.voter).toEqual(mockVoter);
    });

    it('handles fetchVoter when API returns no data', async () => {
        mockApi.GET.mockResolvedValueOnce({ data: null });

        await voterStore.fetchVoter(1);
        expect(voterStore.voter).toBeNull();
    });
});
