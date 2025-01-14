import pytest
from cosmicpython import models, services
from cosmicpython.repository import FakeRepository

class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = models.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = models.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])  #(1)

    result = services.allocate(line, repo, FakeSession())  #(2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    line = models.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = models.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])  #(1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())  #(2) (3)


def test_commits():
    line = models.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = models.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line, repo, session)
    assert session.committed is True

def test_deallocate_decrements_available_quantity():
    repo, session = FakeRepository([]), FakeSession()
    # TODO: you'll need to implement the services.add_batch method
    services.add_batch("b1", "BLUE-PLINTH", 100, None, repo, session)
    line = models.OrderLine("o1", "BLUE-PLINTH", 10)
    services.allocate(line, repo, session)
    batch = repo.get(reference="b1")
    assert batch.available_quantity == 90

    services.deallocate(line, repo, session)

    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity():
    ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch():
    ...  #  TODO: should this error or pass silently? up to you.
