from abc import abstractmethod
from collections.abc import Callable
from typing import Dict, List, Type

from cosmicpython.domain import events
from cosmicpython.service_layer import handlers, services
from cosmicpython.service_layer.unit_of_work import AbstractUnitOfWork


class AbstractMessageBus:
    HANDLERS: Dict[Type[events.Event], List[Callable]]

    def handle(self, event: events.Event, uow: AbstractUnitOfWork):
        results = []
        queue = [event]
        while queue:
            event = queue.pop(0)
            for handler in self.HANDLERS[type(event)]:
                results.append(handler(event, uow=uow))
                self._handle_new_events(queue, uow.collect_new_events())
        return results

    @abstractmethod
    def _handle_new_events(self, queue, events): ...


class MessageBus(AbstractMessageBus):
    HANDLERS = {
        events.OutOfStock: [handlers.send_out_of_stock_notification],
        events.BatchCreated: [handlers.add_batch],
        events.AllocationRequired: [handlers.allocate],
        events.BatchQuantityChanged: [handlers.change_batch_quantity],
    }

    def _handle_new_events(self, queue, events):
        queue.extend(events)
