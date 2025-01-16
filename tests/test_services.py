import pytest
from cosmicpython.domain import models
from cosmicpython.service_layer import services
from cosmicpython.adapters.repository import FakeRepository


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, repo, session)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10,
                               repo, FakeSession())  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "AREALSKU", 100, None, repo, session)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())  # (2) (3)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, repo, session)

    services.allocate("o1", "OMINOUS-MIRROR", 10, repo, session)
    assert session.committed is True


def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)

    services.allocate("o1", "BLUE-PLINTH", 10, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90

    services.deallocate("o1", "BLUE-PLINTH", 10, repo, session)

    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(): ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch(): ...  #  TODO: should this error or pass silently? up to you.
