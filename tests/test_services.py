import pytest

from cosmicpython.domain import events, models
from cosmicpython.service_layer.message_bus import MessageBus
from cosmicpython.service_layer.unit_of_work import FakeUnitOfWork

message_bus = MessageBus()


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
    SKU = "COMPLICATED-LAMP"
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", SKU, 100, None), uow)

    result = message_bus.handle(events.AllocationRequired("o1", SKU, 10), uow)
    assert result.pop() == "b1"


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "AREALSKU", 100, None), uow)
    with pytest.raises(models.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        message_bus.handle(events.AllocationRequired("o1", "NONEXISTENTSKU", 10), uow)


def test_commits():
    uow = FakeUnitOfWork()
    message_bus.handle(events.BatchCreated("b1", "OMINOUS-MIRROR", 100, None), uow)

    message_bus.handle(events.AllocationRequired("o1", "OMINOUS-MIRROR", 10), uow)
    assert uow.committed is True
