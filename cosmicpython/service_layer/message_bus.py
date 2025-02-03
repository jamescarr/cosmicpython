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
            queue.extend(uow.collect_new_events())
    return results

class MessageBus(AbstractMessageBus):
  HANDLERS = {
      events.OutOfStock: [handlers.send_out_of_stock_notification],
      events.BatchCreated: [handlers.add_batch],
      events.AllocationRequired: [handlers.allocate],
      events.BatchQuantityChanged: [handlers.change_batch_quantity],
  }


def handle(event: events.Event, uow: AbstractUnitOfWork):
  MessageBus().handle(event, uow)
