from typing import Optional
from datetime import datetime
import psycopg2

from election_app.domain.repositories.icandidate_account_repository import ICandidateAccountRepository
from election_app.domain.entities.candidate_account import CandidateAccount
from election_app.data_access.database import get_connection


class PostgresCandidateAccountRepository(ICandidateAccountRepository):
    def create_account(self, candidate_id: int, balance: float) -> int:
        """
        Создаёт запись о счёте, возвращает account_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO elections.candidate_account (candidate_id, balance, last_transaction_date)
                        VALUES (%s, %s, %s)
                        RETURNING account_id
                        """,
                        (candidate_id, balance, datetime.now())
                    )
                    new_id = cur.fetchone()[0]
            return new_id
        finally:
            conn.close()

    def find_by_candidate_id(self, candidate_id: int) -> Optional[CandidateAccount]:
        """
        Ищет счёт по candidate_id.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT account_id, candidate_id, balance, last_transaction_date
                        FROM elections.candidate_account
                        WHERE candidate_id = %s
                        """,
                        (candidate_id,)
                    )
                    row = cur.fetchone()
                    if row:
                        return CandidateAccount(
                            account_id=row[0],
                            candidate_id=row[1],
                            balance=float(row[2]),
                            last_transaction_date=row[3]
                        )
                    return None
        finally:
            conn.close()

    def update_balance(self, account_id: int, new_balance: float) -> None:
        """
        Обновляет баланс счёта.
        """
        conn = get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        UPDATE elections.candidate_account
                        SET balance = %s,
                            last_transaction_date = %s
                        WHERE account_id = %s
                        """,
                        (new_balance, datetime.now(), account_id)
                    )
        finally:
            conn.close()
