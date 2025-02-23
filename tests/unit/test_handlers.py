from collections import defaultdict
from datetime import date
from typing import List

from cosmicpython.domain import events
from cosmicpython.service_layer.message_bus import AbstractMessageBus, MessageBus
from cosmicpython.service_layer.unit_of_work import FakeUnitOfWork

message_bus = MessageBus()


class TestAddBatch:
    def test_for_new_product(self):
        uow = FakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("b1", "CRUNCHY-ARMCHAIR", 100, None), uow
        )
        assert uow.products.get("CRUNCHY-ARMCHAIR") is not None
        assert uow.committed


class TestAllocate:
    def test_returns_allocation(self):
        uow = FakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("batch1", "COMPLICATED-LAMP", 100, None), uow
        )
        result = message_bus.handle(
            events.AllocationRequired("o1", "COMPLICATED-LAMP", 10), uow
        ).pop(0)
        assert result == "batch1"


class TestChangeBatchQuantity:
    def test_changes_available_quantity(self):
        uow = FakeUnitOfWork()
        message_bus.handle(
            events.BatchCreated("batch1", "ADORABLE-SETTEE", 100, None), uow
        )
        [batch] = uow.products.get(sku="ADORABLE-SETTEE").batches
        assert batch.available_quantity == 100  # (1)

        message_bus.handle(events.BatchQuantityChanged("batch1", 50), uow)

        assert batch.available_quantity == 50  # (1)

    def test_reallocates_if_necessary(self):
        uow = FakeUnitOfWork()
        event_history = [
            events.BatchCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            message_bus.handle(e, uow)
        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        message_bus.handle(events.BatchQuantityChanged("batch1", 25), uow)

        # order1 or order2 will be deallocated, so we'll have 25 - 20
        assert batch1.available_quantity == 5  # (2)
        # and 20 will be reallocated to the next batch
        assert batch2.available_quantity == 30  # (2)

    def test_reallocates_if_necessary_isolated(self):
        uow = FakeUnitOfWork()
        messagebus = FakeMessageBus()

        # test setup as before
        event_history = [
            events.BatchCreated("batch1", "INDIFFERENT-TABLE", 50, None),
            events.BatchCreated("batch2", "INDIFFERENT-TABLE", 50, date.today()),
            events.AllocationRequired("order1", "INDIFFERENT-TABLE", 20),
            events.AllocationRequired("order2", "INDIFFERENT-TABLE", 20),
        ]
        for e in event_history:
            messagebus.handle(e, uow)

        [batch1, batch2] = uow.products.get(sku="INDIFFERENT-TABLE").batches
        assert batch1.available_quantity == 10
        assert batch2.available_quantity == 50

        messagebus.handle(events.BatchQuantityChanged("batch1", 25), uow)

        # assert on new events emitted rather than downstream side-effects
        [reallocation_event] = messagebus.events_published
        assert isinstance(reallocation_event, events.AllocationRequired)
        assert reallocation_event.orderid in {"order1", "order2"}
        assert reallocation_event.sku == "INDIFFERENT-TABLE"


class FakeMessageBus(MessageBus):
    def __init__(self):
        super().__init__()
        self.events_published = []  # type: List[events.Event]

    def _handle_new_events(self, queue, events):
        self.events_published.extend(events)
