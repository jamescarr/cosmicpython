import pytest

from cosmicpython.domain import events
from cosmicpython.service_layer import message_bus, services
from cosmicpython.service_layer.unit_of_work import FakeUnitOfWork


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow)
    assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
    assert uow.committed


def test_returns_allocation():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "COMPLICATED-LAMP", 100, None), uow)

    result = services.allocate("o1", "COMPLICATED-LAMP", 10, uow)
    assert result == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "AREALSKU", 100, None), uow)
    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_commits():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "OMINOUS-MIRROR", 100, None), uow)

    services.allocate("o1", "OMINOUS-MIRROR", 10, uow)
    assert uow.committed is True
