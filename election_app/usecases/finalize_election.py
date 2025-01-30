from datetime import datetime


class FinalizeElectionUseCase:
    def __init__(
        self,
        election_repository,   # IElectionRepository
        vote_repository,       # IVoteRepository
        candidate_repository   # ICandidateRepository
    ):
        """
        :param election_repository: Интерфейс репозитория для чтения/обновления выборов
        :param vote_repository: Интерфейс репозитория для подсчёта голосов
        :param candidate_repository: Интерфейс репозитория для получения сведений о кандидатах
        """
        self.election_repo = election_repository
        self.vote_repo = vote_repository
        self.candidate_repo = candidate_repository

    def execute(self, election_id: int) -> dict:
        """
        Подводит итоги выборов, возвращает структуру вида:
        {
          "election_id": <int>,
          "election_name": <str>,
          "start_date": <date>,
          "end_date": <date>,
          "results": [
             {
               "candidate_id": int,
               "candidate_name": str,
               "vote_count": int
             },
             ...
          ],
          "winner": {
             "candidate_id": int,
             "candidate_name": str,
             "vote_count": int
          }
        }

        По желанию можно сохранить результаты в БД и/или установить статус выборов "FINISHED".
        """

        # 1. Проверяем, что выборы существуют
        election = self.election_repo.find_election_by_id(election_id)
        if not election:
            raise ValueError(f"Выборы с id={election_id} не найдены.")

        # 2. Проверяем, что выборы закончились (считаем, что дата окончания <= сейчас)
        now = datetime.now().date()
        if election.end_date is None:
            raise ValueError("У данных выборов не указана дата окончания.")
        if now <= election.end_date:
            raise ValueError(
                "Невозможно подвести итоги: выборы ещё не завершены (end_date > сегодня)."
            )

        # 3. Запрашиваем из репозитория голосов сводку:
        # Предположим, метод count_votes_by_election возвращает
        # dict {candidate_id: vote_count} или список кортежей [(candidate_id, count), ...]
        vote_counts = self.vote_repo.count_votes_by_election(election_id)
        # Например, vote_counts = {1: 120, 2: 95, 5: 300}  # candidate_id -> голоса

        results_list = []
        for cand_id, count in vote_counts.items():
            candidate = self.candidate_repo.find_candidate_by_id(cand_id)
            candidate_name = candidate.full_name if candidate else f"Unknown ID={cand_id}"
            results_list.append({
                "candidate_id": cand_id,
                "candidate_name": candidate_name,
                "vote_count": count
            })

        # 4. Определяем победителя (кандидата с максимальным числом голосов)
        # Если голосов нет, нужно решить, что делать (возможно, передавать None или "No votes").
        if results_list:
            winner_entry = max(results_list, key=lambda item: item["vote_count"])
        else:
            winner_entry = {
                "candidate_id": None,
                "candidate_name": "No votes",
                "vote_count": 0
            }

        # 5. (Опционально) Обновляем статус выборов в БД:
        #    например, election_repo.update_election_status(election_id, "FINISHED")
        #    или сохраняем результаты в отдельной таблице.

        # 6. Готовим структуру ответа
        result_data = {
            "election_id": election.election_id,
            "election_name": election.election_name,
            "start_date": election.start_date,
            "end_date": election.end_date,
            "results": results_list,
            "winner": winner_entry
        }

        return result_data
