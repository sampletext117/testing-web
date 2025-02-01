from typing import Optional, List
from datetime import date, datetime
import asyncpg

from election_app.domain.repositories.icandidate_repository import ICandidateRepository
from election_app.domain.entities.candidate import Candidate
from election_app.data_access.database import get_connection

class PostgresCandidateRepository(ICandidateRepository):
    async def create_candidate(
        self,
        full_name: str,
        birth_date: date,
        passport_id: int
    ) -> int:
        """
        Создаёт запись о кандидате, возвращает candidate_id.
        (используется, например, когда мы уже создали passport_id).
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                INSERT INTO elections.candidate (full_name, birth_date, passport_id)
                VALUES ($1, $2, $3)
                RETURNING candidate_id
                """,
                full_name, birth_date, passport_id
            )
            return row["candidate_id"] if row else 0
        finally:
            await conn.close()

    async def update_candidate_program_and_account(
        self,
        candidate_id: int,
        campaign_program_id: int,
        account_id: int
    ) -> None:
        """
        Обновляет поля campaign_program_id и account_id у кандидата.
        Использовалось раньше, если мы после создания
        candidate_program / candidate_account хотели связать их с candidate.
        """
        conn = await get_connection()
        try:
            await conn.execute(
                """
                UPDATE elections.candidate
                SET campaign_program_id = $1,
                    account_id = $2
                WHERE candidate_id = $3
                """,
                campaign_program_id, account_id, candidate_id
            )
        finally:
            await conn.close()

    async def find_candidate_by_id(self, candidate_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по ID, или None, если не найден.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT candidate_id, full_name, birth_date, passport_id,
                       campaign_program_id, account_id, created_at
                FROM elections.candidate
                WHERE candidate_id = $1
                """,
                candidate_id
            )
            if row:
                return Candidate(
                    candidate_id=row["candidate_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    campaign_program_id=row["campaign_program_id"],
                    account_id=row["account_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

    async def find_by_passport_id(self, passport_id: int) -> Optional[Candidate]:
        """
        Находит кандидата по passport_id, или None.
        """
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """
                SELECT candidate_id, full_name, birth_date, passport_id,
                       campaign_program_id, account_id, created_at
                FROM elections.candidate
                WHERE passport_id = $1
                """,
                passport_id
            )
            if row:
                return Candidate(
                    candidate_id=row["candidate_id"],
                    full_name=row["full_name"],
                    birth_date=row["birth_date"],
                    passport_id=row["passport_id"],
                    campaign_program_id=row["campaign_program_id"],
                    account_id=row["account_id"],
                    created_at=row["created_at"]
                )
            return None
        finally:
            await conn.close()

    async def delete_candidate(self, candidate_id: int) -> bool:
        """
        Удаляет кандидата по ID, возвращает True/False (успешно/нет).
        """
        conn = await get_connection()
        try:
            result = await conn.execute(
                """
                DELETE FROM elections.candidate
                WHERE candidate_id = $1
                """,
                candidate_id
            )
            # result может быть, например, 'DELETE 1', если 1 строка удалена
            # Проверим, была ли удалена хоть одна строка
            row_count = int(result.split(" ")[1]) if result else 0
            return (row_count > 0)
        finally:
            await conn.close()

    async def list_candidates(self) -> List[Candidate]:
        """
        Возвращает список всех кандидатов (Candidate).
        """
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                """
                SELECT candidate_id, full_name, birth_date, passport_id,
                       campaign_program_id, account_id, created_at
                FROM elections.candidate
                ORDER BY candidate_id
                """
            )
            result = []
            for r in rows:
                result.append(
                    Candidate(
                        candidate_id=r["candidate_id"],
                        full_name=r["full_name"],
                        birth_date=r["birth_date"],
                        passport_id=r["passport_id"],
                        campaign_program_id=r["campaign_program_id"],
                        account_id=r["account_id"],
                        created_at=r["created_at"]
                    )
                )
            return result
        finally:
            await conn.close()

    async def patch_candidate(self, candidate_id: int, program: Optional[str], balance: Optional[float]) -> bool:
        """
        Частичное обновление.
        - Если program != None, обновляем description в campaign_program
        - Если balance != None, обновляем balance в candidate_account
        Возвращаем True, если обновление прошло успешно, False иначе.
        """
        conn = await get_connection()
        try:
            # Начинаем транзакцию (чтобы изменения были атомарными):
            async with conn.transaction():
                # Сначала узнаём, campaign_program_id и account_id у кандидата
                row = await conn.fetchrow(
                    """
                    SELECT campaign_program_id, account_id
                    FROM elections.candidate
                    WHERE candidate_id = $1
                    """,
                    candidate_id
                )
                if not row:
                    return False  # Кандидат не найден

                prog_id = row["campaign_program_id"]
                acct_id = row["account_id"]

                # Обновляем программу, если нужно
                if program is not None:
                    if prog_id is not None:
                        # Предположим, что запись в campaign_program уже есть
                        await conn.execute(
                            """
                            UPDATE elections.campaign_program
                            SET description = $2
                            WHERE campaign_program_id = $1
                            """,
                            prog_id,
                            program
                        )
                    else:
                        # Если нет program_id, можно создать новую запись.
                        # Или бросить ошибку. Решение зависит от вашей логики.
                        # Для примера сделаем "создаём новую запись".
                        new_prog_row = await conn.fetchrow(
                            """
                            INSERT INTO elections.campaign_program (candidate_id, description)
                            VALUES ($1, $2)
                            RETURNING campaign_program_id
                            """,
                            candidate_id, program
                        )
                        new_prog_id = new_prog_row["campaign_program_id"]
                        # и обновим candidate
                        await conn.execute(
                            """
                            UPDATE elections.candidate
                            SET campaign_program_id = $1
                            WHERE candidate_id = $2
                            """,
                            new_prog_id, candidate_id
                        )

                # Обновляем счёт, если нужно
                if balance is not None:
                    if acct_id is not None:
                        # Предположим, запись уже есть
                        await conn.execute(
                            """
                            UPDATE elections.candidate_account
                            SET balance = $2,
                                last_transaction_date = now()
                            WHERE account_id = $1
                            """,
                            acct_id, balance
                        )
                    else:
                        # Если нет account_id, создадим новую запись
                        new_acc_row = await conn.fetchrow(
                            """
                            INSERT INTO elections.candidate_account (candidate_id, balance, last_transaction_date)
                            VALUES ($1, $2, now())
                            RETURNING account_id
                            """,
                            candidate_id, balance
                        )
                        new_acc_id = new_acc_row["account_id"]
                        # Привяжем к candidate
                        await conn.execute(
                            """
                            UPDATE elections.candidate
                            SET account_id = $1
                            WHERE candidate_id = $2
                            """,
                            new_acc_id, candidate_id
                        )

            return True
        finally:
            await conn.close()
