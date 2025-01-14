from cosmicpython.models import OrderLine, OutOfStock
from cosmicpython import models
from cosmicpython.repository import AbstractRepository


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(line.sku)

    batchref = models.allocate(line, batches)
    session.commit()
    return batchref

def add_batch(reference: str, sku: str, qty: int, eta, repo: AbstractRepository, session) -> models.Batch:
    batch = models.Batch(reference, sku, qty, eta)
    repo.add(batch)
    session.commit()
    return batch

def deallocate(line: models.OrderLine, repo: AbstractRepository, session):
    batch = repo.find_containing_line(line)
    if batch != None:
        batch.deallocate(line)
        session.commit()

class InvalidSku(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Invalid sku {sku}")

