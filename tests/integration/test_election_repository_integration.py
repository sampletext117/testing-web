import pytest
import pytest_asyncio
from datetime import date

from election_app.data_access.election_repository import PostgresElectionRepository
from election_app.domain.entities.election import Election

@pytest_asyncio.fixture
async def election_repo() -> PostgresElectionRepository:
    repo = PostgresElectionRepository()
    yield repo
    # Опционально: можно добавить очистку таблицы после тестов

@pytest.mark.asyncio
class TestElectionRepositoryIntegration:
    async def test_create_and_find_election(self, election_repo: PostgresElectionRepository):
        election_name = "Test Election"
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 10)
        description = "Integration test election"
        eid = await election_repo.create_election(election_name, start_date, end_date, description)
        assert eid > 0, "Созданный election_id должен быть > 0"

        election = await election_repo.find_election_by_id(eid)
        assert election is not None, "Выборы должны быть найдены"
        assert election.election_id == eid
        assert election.election_name == election_name
        assert election.start_date == start_date
        assert election.end_date == end_date
        assert election.description == description

    async def test_list_all_elections(self, election_repo: PostgresElectionRepository):
        # Создаем две выборы
        eid1 = await election_repo.create_election("Election 1", date(2025, 2, 1), date(2025, 2, 5), "Desc 1")
        eid2 = await election_repo.create_election("Election 2", date(2025, 3, 1), date(2025, 3, 5), "Desc 2")
        elections = await election_repo.list_all_elections()
        election_ids = [e.election_id for e in elections]
        assert eid1 in election_ids, "Election 1 должен присутствовать в списке"
        assert eid2 in election_ids, "Election 2 должен присутствовать в списке"

    async def test_patch_election(self, election_repo: PostgresElectionRepository):
        # Создаем выборы
        eid = await election_repo.create_election("Old Election", date(2025, 4, 1), date(2025, 4, 10), "Old Desc")
        # Патчим данные
        new_name = "New Election"
        new_start = date(2025, 4, 2)
        new_end = date(2025, 4, 12)
        new_desc = "New Desc"
        ok = await election_repo.patch_election(eid, new_name, new_start, new_end, new_desc)
        assert ok is True, "Патч должен вернуть True"
        election = await election_repo.find_election_by_id(eid)
        assert election is not None, "Выборы должны быть найдены после патча"
        assert election.election_name == new_name
        assert election.start_date == new_start
        assert election.end_date == new_end
        assert election.description == new_desc

    async def test_delete_election(self, election_repo: PostgresElectionRepository):
        eid = await election_repo.create_election("Delete Election", date(2025, 5, 1), date(2025, 5, 10), "To be deleted")
        election = await election_repo.find_election_by_id(eid)
        assert election is not None, "Выборы должны существовать до удаления"
        success = await election_repo.delete_election(eid)
        assert success is True, "Удаление должно вернуть True"
        deleted = await election_repo.find_election_by_id(eid)
        assert deleted is None, "Выборы не должны быть найдены после удаления"
