from typing import Optional
import logging
import pprint

logging.basicConfig(level=logging.INFO)

from cosmicpython.domain.models import OrderLine
from cosmicpython.domain import models
from cosmicpython.service_layer.unit_of_work import AbstractUnitOfWork, unit_of_work


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork
) -> Optional[str]:
    line = OrderLine(orderid=orderid, sku=sku, qty=qty)

    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            raise InvalidSku(sku)

        batchref = product.allocate(line)
        uow.commit()
        return batchref


def add_batch(
    reference: str, sku: str, qty: int, eta, uow: AbstractUnitOfWork
) -> Optional[models.Batch]:

    with uow:
        product = uow.products.get(sku=sku)
        logging.info("Add batch structure:\n%s", pprint.pformat(product))
        if product is None:
            product = models.Product(sku, batches=[])
            uow.products.add(product)
        batch = models.Batch(reference, sku, qty, eta)
        product.batches.append(batch)
        uow.commit()
        return batch


def deallocate(orderid: str, sku: str, qty: int, uow: AbstractUnitOfWork):
    line = OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        logging.info(
            "Deallocate structure:\n%s",
            pprint.pformat([b._allocations for b in product.batches]),
        )
        logging.info(f"Line profivided: {line.orderid}")
        try:
            product.deallocate(line)
            uow.commit()
        except models.NoBatchContainingOrderLine as e:
            uow.rollback()
            raise e


def reallocate(line: OrderLine, uow: AbstractUnitOfWork) -> Optional[str]:
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
