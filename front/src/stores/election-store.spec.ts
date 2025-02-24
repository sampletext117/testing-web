import { setActivePinia, createPinia } from 'pinia';
import { useElectionStore } from '@/stores/election-store';
import { vi, describe, it, beforeEach, expect, afterEach } from 'vitest';

describe('Election Store', () => {
    let electionStore: ReturnType<typeof useElectionStore>;
    const mockApi = vi.hoisted(() => ({
        GET: vi.fn(),
    }));

    beforeEach(() => {
        setActivePinia(createPinia());
        vi.mock('@/api/api', () => ({ useApi: () => ({ value: mockApi }) }));
        electionStore = useElectionStore();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('initializes with default values', () => {
        expect(electionStore.elections).toEqual([]);
        expect(electionStore.election).toBeUndefined();
    });

    it('fetches elections and updates state', async () => {
        const mockElectionList = [{ id: 1, name: 'Election 1' }, { id: 2, name: 'Election 2' }];
        mockApi.GET.mockResolvedValueOnce({ data: mockElectionList });

        await electionStore.fetchElections();
        expect(electionStore.elections).toEqual(mockElectionList);
    });

    it('fetches a specific election and updates state', async () => {
        const mockElection = { id: 1, name: 'Mock Election' };
        mockApi.GET.mockResolvedValueOnce({ data: mockElection });

        await electionStore.fetchElection(1);
        expect(electionStore.election).toEqual(mockElection);
    });

    it('handles fetchElection when API returns no data', async () => {
        mockApi.GET.mockResolvedValueOnce({ data: null });

        await electionStore.fetchElection(1);
        expect(electionStore.election).toBeNull();
    });
});
