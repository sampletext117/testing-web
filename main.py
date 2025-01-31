import argparse
from datetime import datetime, date

from election_app.usecases.register_voter import RegisterVoterUseCase
from election_app.usecases.register_candidate import RegisterCandidateUseCase
from election_app.usecases.vote import VoteUseCase
from election_app.usecases.finalize_election import FinalizeElectionUseCase

from election_app.usecases.register_election import RegisterElectionUseCase

from election_app.data_access.passport_repository import PostgresPassportRepository
from election_app.data_access.voter_repository import PostgresVoterRepository
from election_app.data_access.candidate_repository import PostgresCandidateRepository
from election_app.data_access.campaign_program_repository import PostgresCampaignProgramRepository
from election_app.data_access.candidate_account_repository import PostgresCandidateAccountRepository
from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.data_access.vote_repository import PostgresVoteRepository


def str_to_date(date_str: str) -> date:
    """Утилита для преобразования строки вида 'YYYY-MM-DD' в date."""
    return datetime.strptime(date_str, "%Y-%m-%d").date()


def cmd_register_voter(args):
    """
    Обработка команды "register-voter" (регистрация избирателя).
    Пример использования:
    python main.py register-voter --name "Иванов Иван" --birth-date 1990-05-20 \
        --passport-number "1234 567890" --issued-by "ОВД г.Москвы" \
        --issue-date 2010-02-15 --country Россия
    """
    # Создаём объекты репозиториев
    voter_repo = PostgresVoterRepository()
    passport_repo = PostgresPassportRepository()

    # Создаём use case
    use_case = RegisterVoterUseCase(voter_repo, passport_repo)

    # Вызываем
    voter_id = use_case.execute(
        full_name=args.name,
        birth_date=str_to_date(args.birth_date),
        passport_number=args.passport_number,
        issued_by=args.issued_by,
        issue_date=str_to_date(args.issue_date) if args.issue_date else None,
        country=args.country
    )
    print(f"Избиратель зарегистрирован, voter_id={voter_id}")


def cmd_register_candidate(args):
    """
    Обработка команды "register-candidate".
    Пример:
    python main.py register-candidate --name "Петров Петр" --birth-date 1980-01-10 \
        --passport-number "1234 555000" --country Россия \
        --program "Моя замечательная программа" --issued-by "УФМС" --issue-date 2000-10-10
    """
    # Репозитории
    candidate_repo = PostgresCandidateRepository()
    passport_repo = PostgresPassportRepository()
    program_repo = PostgresCampaignProgramRepository()
    account_repo = PostgresCandidateAccountRepository()

    use_case = RegisterCandidateUseCase(
        candidate_repo,
        passport_repo,
        program_repo,
        account_repo
    )

    candidate_id = use_case.execute(
        full_name=args.name,
        birth_date=str_to_date(args.birth_date),
        passport_number=args.passport_number,
        issued_by=args.issued_by,
        issue_date=str_to_date(args.issue_date) if args.issue_date else None,
        country=args.country,
        program_description=args.program,
        initial_balance=args.balance
    )
    print(f"Кандидат зарегистрирован, candidate_id={candidate_id}")


def cmd_create_election(args):
    """
    Пример команды "create-election".
    python main.py create-election --name "Выборы 2025" --start 2025-03-01 --end 2025-03-10 --desc "Описание выборов"
    """
    election_repo = PostgresElectionRepository()
    # Допустим, у нас есть use case, который мы не расписывали ранее, но покажем пример:
    # register_election_usecase = RegisterElectionUseCase(election_repo)

    # Для упрощения сделаем напрямую:
    start_d = str_to_date(args.start_date)
    end_d = str_to_date(args.end_date)

    new_id = election_repo.create_election(
        election_name=args.name,
        start_date=start_d,
        end_date=end_d,
        description=args.desc
    )
    print(f"Выборы созданы, election_id={new_id}")


def cmd_vote(args):
    """
    Обработка команды "vote": избиратель голосует за кандидата на конкретных выборах.
    Пример:
    python main.py vote --voter 10 --candidate 2 --election 1
    """
    voter_repo = PostgresVoterRepository()
    candidate_repo = PostgresCandidateRepository()
    election_repo = PostgresElectionRepository()
    vote_repo = PostgresVoteRepository()

    use_case = VoteUseCase(voter_repo, candidate_repo, election_repo, vote_repo)

    vote_id = use_case.execute(
        voter_id=args.voter,
        candidate_id=args.candidate,
        election_id=args.election
    )
    print(f"Голос зарегистрирован, vote_id={vote_id}")


def cmd_finalize_election(args):
    """
    Обработка команды "finalize-election": администратор подводит итоги.
    Пример:
    python main.py finalize-election --election 1
    """
    election_repo = PostgresElectionRepository()
    vote_repo = PostgresVoteRepository()
    candidate_repo = PostgresCandidateRepository()

    use_case = FinalizeElectionUseCase(election_repo, vote_repo, candidate_repo)

    results = use_case.execute(args.election)
    print("\n== ИТОГИ ВЫБОРОВ ==")
    print(f"Идентификатор: {results['election_id']}")
    print(f"Название: {results['election_name']}")
    print(f"Период: {results['start_date']} -- {results['end_date']}")
    print("Результаты (кандидат -> голоса):")
    for item in results["results"]:
        print(f"  - {item['candidate_name']} (ID={item['candidate_id']}) : {item['vote_count']}")
    winner = results["winner"]
    print(f"\nПОБЕДИТЕЛЬ: {winner['candidate_name']} (голоса: {winner['vote_count']})")


def main():
    parser = argparse.ArgumentParser(description="Система электронного голосования (CLI)")
    subparsers = parser.add_subparsers(help="Команды")

    # --- register-voter ---
    parser_voter = subparsers.add_parser("register-voter", help="Зарегистрировать избирателя")
    parser_voter.add_argument("--name", required=True, help="Полное имя")
    parser_voter.add_argument("--birth-date", required=True, help="Дата рождения (YYYY-MM-DD)")
    parser_voter.add_argument("--passport-number", required=True, help="Номер паспорта")
    parser_voter.add_argument("--issued-by", required=False, help="Кем выдан (опционально)")
    parser_voter.add_argument("--issue-date", required=False, help="Дата выдачи (YYYY-MM-DD, опционально)")
    parser_voter.add_argument("--country", required=True, help="Страна (например, Россия)")
    parser_voter.set_defaults(func=cmd_register_voter)

    # --- register-candidate ---
    parser_candidate = subparsers.add_parser("register-candidate", help="Зарегистрировать кандидата")
    parser_candidate.add_argument("--name", required=True, help="Полное имя")
    parser_candidate.add_argument("--birth-date", required=True, help="Дата рождения (YYYY-MM-DD)")
    parser_candidate.add_argument("--passport-number", required=True, help="Номер паспорта")
    parser_candidate.add_argument("--issued-by", required=False, help="Кем выдан (опционально)")
    parser_candidate.add_argument("--issue-date", required=False, help="Дата выдачи (YYYY-MM-DD, опционально)")
    parser_candidate.add_argument("--country", required=True, help="Страна (например, Россия)")
    parser_candidate.add_argument("--program", required=True, help="Текст предвыборной программы")
    parser_candidate.add_argument("--balance", type=float, default=0.0, help="Начальный баланс счёта")
    parser_candidate.set_defaults(func=cmd_register_candidate)

    # --- create-election ---
    parser_election = subparsers.add_parser("create-election", help="Создать новые выборы")
    parser_election.add_argument("--name", required=True, help="Название выборов")
    parser_election.add_argument("--start-date", required=True, help="Дата начала (YYYY-MM-DD)")
    parser_election.add_argument("--end-date", required=True, help="Дата окончания (YYYY-MM-DD)")
    parser_election.add_argument("--desc", required=False, default="", help="Описание")
    parser_election.set_defaults(func=cmd_create_election)

    # --- vote ---
    parser_vote = subparsers.add_parser("vote", help="Голосовать")
    parser_vote.add_argument("--voter", type=int, required=True, help="ID избирателя")
    parser_vote.add_argument("--candidate", type=int, required=True, help="ID кандидата")
    parser_vote.add_argument("--election", type=int, required=True, help="ID выборов")
    parser_vote.set_defaults(func=cmd_vote)

    # --- finalize-election ---
    parser_finalize = subparsers.add_parser("finalize-election", help="Подвести итоги выборов")
    parser_finalize.add_argument("--election", type=int, required=True, help="ID выборов")
    parser_finalize.set_defaults(func=cmd_finalize_election)

    args = parser.parse_args()

    if hasattr(args, "func"):
        # Вызываем соответствующую функцию для подкоманды
        try:
            args.func(args)
        except Exception as e:
            print(f"Ошибка: {e}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
