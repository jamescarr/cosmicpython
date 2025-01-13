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

class InvalidSku(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Invalid sku {sku}")

