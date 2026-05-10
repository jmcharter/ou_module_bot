from pathlib import Path
from datetime import datetime, timezone

import pytest

from ou_bot.common.config import DatabaseConfig
from ou_bot.common.database import ModuleRepository
from ou_bot.common.ou_module import OUModule


@pytest.fixture
def repo(tmp_path: Path) -> ModuleRepository:
    return ModuleRepository(DatabaseConfig(database_path=tmp_path / "test.db"))


def make_module(code: str = "M269") -> OUModule:
    return OUModule(
        module_code=code,
        module_title="Algorithms and Data Structures",
        url="https://www.open.ac.uk/courses/modules/m269",
        credits=30,
        ou_study_level="2",
        next_start=datetime(2025, 10, 4, tzinfo=timezone.utc),
    )


class TestUpsertFind:
    def test_upsert_and_find(self, repo: ModuleRepository):
        repo.upsert(make_module("M269"))
        found = repo.find_by_codes(["M269"])
        assert len(found) == 1
        assert found[0].module_code == "M269"

    def test_find_nonexistent(self, repo: ModuleRepository):
        assert repo.find_by_codes(["ZZ99"]) == []

    def test_find_empty_list(self, repo: ModuleRepository):
        assert repo.find_by_codes([]) == []

    def test_upsert_replaces_existing(self, repo: ModuleRepository):
        repo.upsert(make_module("M269"))
        updated = OUModule(
            module_code="M269",
            module_title="Updated Title",
            url="https://example.com",
            credits=60,
            ou_study_level="3",
        )
        repo.upsert(updated)
        found = repo.find_by_codes(["M269"])
        assert len(found) == 1
        assert found[0].module_title == "Updated Title"
        assert found[0].credits == 60

    def test_get_all_codes(self, repo: ModuleRepository):
        repo.upsert(make_module("M269"))
        repo.upsert(make_module("TM112"))
        codes = repo.get_all_codes()
        assert sorted(codes) == ["M269", "TM112"]


class TestUpsertMany:
    def test_batch_upsert(self, repo: ModuleRepository):
        modules = [
            make_module("M269"),
            make_module("TM112"),
            make_module("M250"),
        ]
        repo.upsert_many(modules)
        assert len(repo.get_all_codes()) == 3
        found = repo.find_by_codes(["M269", "TM112"])
        assert {m.module_code for m in found} == {"M269", "TM112"}

    def test_upsert_many_empty_list(self, repo: ModuleRepository):
        repo.upsert_many([])
        assert repo.get_all_codes() == []
