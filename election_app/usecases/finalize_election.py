from datetime import datetime

class FinalizeElectionUseCase:
    def __init__(self, election_repository, vote_repository, candidate_repository):
        self.election_repo = election_repository
        self.vote_repo = vote_repository
        self.candidate_repo = candidate_repository

    async def execute(self, election_id: int) -> dict:
        election = await self.election_repo.find_election_by_id(election_id)
        if not election:
            raise ValueError(f"Выборы с id={election_id} не найдены.")

        now = datetime.now().date()
        if election.end_date is None:
            raise ValueError("У данных выборов не указана дата окончания.")
        if now <= election.end_date:
            raise ValueError("Невозможно подвести итоги: выборы ещё не завершены.")

        # Здесь тоже await:
        vote_counts = await self.vote_repo.count_votes_by_election(election_id)

        results_list = []
        for cand_id, count in vote_counts.items():
            candidate = await self.candidate_repo.find_candidate_by_id(cand_id)
            candidate_name = candidate.full_name if candidate else f"Unknown ID={cand_id}"
            results_list.append({
                "candidate_id": cand_id,
                "candidate_name": candidate_name,
                "vote_count": count
            })

        if results_list:
            winner_entry = max(results_list, key=lambda item: item["vote_count"])
        else:
            winner_entry = {
                "candidate_id": None,
                "candidate_name": "No votes",
                "vote_count": 0
            }

        await self.election_repo.update_election_status(election_id, "FINISHED")

        result_data = {
            "election_id": election.election_id,
            "election_name": election.election_name,
            "start_date": election.start_date,
            "end_date": election.end_date,
            "results": results_list,
            "winner": winner_entry
        }
        return result_data
