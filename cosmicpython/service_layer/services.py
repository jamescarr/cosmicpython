from cosmicpython.domain.models import OrderLine, OutOfStock
from cosmicpython.domain import models
from cosmicpython.adapters.repository import AbstractRepository
from cosmicpython.service_layer.unit_of_work import AbstractUnitOfWork, unit_of_work


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork) -> str:
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku, batches):  # we should push this into the repo
            raise InvalidSku(sku)

        batchref = models.allocate(OrderLine(orderid, sku, qty), batches)
        uow.commit()
        return batchref


def add_batch(
    reference: str, sku: str, qty: int, eta, uow: AbstractUnitOfWork
) -> models.Batch:
    with uow:
        batch = models.Batch(reference, sku, qty, eta)
        uow.batches.add(batch)
        uow.commit()
        return batch


def deallocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    line = OrderLine(orderid, sku, qty)
    with uow:
        batch = uow.batches.find_containing_line(line)
        if batch != None:
            batch.deallocate(line)
            uow.commit()


def reallocate(line: OrderLine, uow: AbstractUnitOfWork) -> str:
    with unit_of_work() as batches:
        batch = batches.get(sku=line.sku)
        if batch is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batch.deallocate(line)
        result = allocate(line.orderid, line.sku, line.qty, uow)
        return result


class InvalidSku(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Invalid sku {sku}")
