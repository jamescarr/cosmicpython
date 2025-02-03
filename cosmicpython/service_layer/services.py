import logging
import pprint
from typing import Optional

logging.basicConfig(level=logging.INFO)

from cosmicpython.domain import events, models
from cosmicpython.domain.models import OrderLine
from cosmicpython.service_layer.unit_of_work import AbstractUnitOfWork, unit_of_work


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
