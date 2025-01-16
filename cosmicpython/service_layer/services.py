from cosmicpython.domain.models import OrderLine, OutOfStock
from cosmicpython.domain import models
from cosmicpython.adapters.repository import AbstractRepository


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int,
             repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(sku, batches):
        raise InvalidSku(sku)

    batchref = models.allocate(OrderLine(orderid, sku, qty), batches)
    session.commit()
    return batchref


def add_batch(
    reference: str, sku: str, qty: int, eta, repo: AbstractRepository, session
) -> models.Batch:
    batch = models.Batch(reference, sku, qty, eta)
    repo.add(batch)
    session.commit()
    return batch


def deallocate(
        orderid: str, sku: str, qty: int
        , repo: AbstractRepository, session):
    line = OrderLine(orderid, sku, qty)
    batch = repo.find_containing_line(line)
    if batch != None:
        batch.deallocate(line)
        session.commit()


class InvalidSku(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Invalid sku {sku}")
