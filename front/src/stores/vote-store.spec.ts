import { setActivePinia, createPinia } from 'pinia';
import { useVoteStore } from '@/stores/vote-store';
import { vi, describe, it, beforeEach, expect, afterEach } from 'vitest';

describe('Vote Store', () => {
    let voteStore: ReturnType<typeof useVoteStore>;
    const mockApi = vi.hoisted(() => ({
        GET: vi.fn(),
        POST: vi.fn(),
    }));

    beforeEach(() => {
        setActivePinia(createPinia());
        vi.mock('@/api/api', () => ({ useApi: () => ({ value: mockApi }) }));
        voteStore = useVoteStore();
    });

    afterEach(() => {
        vi.restoreAllMocks();
    });

    it('initializes with default values', () => {
        expect(voteStore.votes).toEqual([]);
    });

    it('fetches votes and updates state', async () => {
        const mockVoteList = [{ id: 1, voter: 'User 1', candidate: 'Candidate 1' }, { id: 2, voter: 'User 2', candidate: 'Candidate 2' }];
        mockApi.GET.mockResolvedValueOnce({ data: mockVoteList });

        await voteStore.fetchVotes();
        expect(voteStore.votes).toEqual(mockVoteList);
    });

    it('submits a vote and refreshes vote list', async () => {
        const newVote = { voter_id: 1, candidate_id: 2, election_id: 1 };
        mockApi.POST.mockResolvedValueOnce({ data: { success: true } });
        const mockVoteList = [{ id: 1, voter: 'User 1', candidate: 'Candidate 1' }, { id: 2, voter: 'User 2', candidate: 'Candidate 2' }];
        mockApi.GET.mockResolvedValueOnce({ data: mockVoteList });

        await voteStore.vote(newVote);
        expect(mockApi.POST).toHaveBeenCalledWith("/v1/votes", { body: newVote });
    });
});
