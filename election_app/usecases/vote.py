from typing import Optional
from datetime import datetime


class VoteUseCase:
    def __init__(
        self,
        voter_repository,      # IVoterRepository
        candidate_repository,  # ICandidateRepository
        election_repository,   # IElectionRepository
        vote_repository        # IVoteRepository
    ):
        """
        :param voter_repository: Интерфейс репозитория для работы с избирателями
        :param candidate_repository: Интерфейс репозитория для работы с кандидатами
        :param election_repository: Интерфейс репозитория для информации о выборах
        :param vote_repository: Интерфейс репозитория для учёта голосов
        """
        self.voter_repo = voter_repository
        self.candidate_repo = candidate_repository
        self.election_repo = election_repository
        self.vote_repo = vote_repository

    def execute(
        self,
        voter_id: int,
        candidate_id: int,
        election_id: int
    ) -> int:
        """
        Фиксирует голос избирателя за выбранного кандидата в рамках конкретных выборов.
        Возвращает идентификатор (vote_id) созданной записи.
        """

        voter = self.voter_repo.find_voter_by_id(voter_id)
        if not voter:
            raise ValueError(f"Избиратель с id={voter_id} не найден.")

        candidate = self.candidate_repo.find_candidate_by_id(candidate_id)
        if not candidate:
            raise ValueError(f"Кандидат с id={candidate_id} не найден.")

        election = self.election_repo.find_election_by_id(election_id)
        if not election:
            raise ValueError(f"Выборы с id={election_id} не найдены.")

        now = datetime.now().date()
        if election.start_date is None or election.end_date is None:
            raise ValueError("В данных о выборах не указаны start_date или end_date.")
        if not (election.start_date <= now <= election.end_date):
            raise ValueError("Выборы закрыты или ещё не начались.")

        if self.vote_repo.has_already_voted(voter_id, election_id):
            raise ValueError("Избиратель уже голосовал на этих выборах.")

        # 5. Записать голос
        vote_id = self.vote_repo.record_vote(
            voter_id=voter_id,
            candidate_id=candidate_id,
            election_id=election_id
        )

        return vote_id
