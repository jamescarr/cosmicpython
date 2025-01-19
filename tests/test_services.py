import pytest
from cosmicpython.domain import models
from cosmicpython.service_layer import services
from cosmicpython.adapters.repository import FakeRepository
from cosmicpython.service_layer.unit_of_work import FakeUnitOfWork


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "CRUNCHY-ARMCHAIR", 100, None, uow)  # (3)
    assert uow.batches.get("b1") is not None
    assert uow.committed


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "COMPLICATED-LAMP", 100, None, uow)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)  # (2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "AREALSKU", 100, None, uow)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "OMINOUS-MIRROR", 100, None, uow)

    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True


def test_deallocate_decrements_available_quantity():
    uow = FakeUnitOfWork()
    services.add_batch("b1", "BLUE-PLINTH", 100, None, uow)

    services.allocate("o1", "BLUE-PLINTH", 10, uow)
    with uow:
        batch = uow.batches.get(reference="b1")
        assert batch.available_quantity == 90

    services.deallocate("o1", "BLUE-PLINTH", 10, uow)

    assert batch.available_quantity == 100


def test_deallocate_decrements_correct_quantity(): ...  #  TODO - check that we decrement the right sku


def test_trying_to_deallocate_unallocated_batch(): ...  #  TODO: should this error or pass silently? up to you.
