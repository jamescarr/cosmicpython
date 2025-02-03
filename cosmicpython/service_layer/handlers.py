import logging
import pprint

from cosmicpython.domain import events, models
from cosmicpython.domain.models import OrderLine, InvalidSku
from cosmicpython.service_layer import unit_of_work



def add_batch(
    event: events.BatchCreated,
    uow: unit_of_work.AbstractUnitOfWork,
):

    print(f"Batch created with ref: {event.ref}, SKU: {event.sku}, Quantity: {event.qty}, ETA: {event.eta}")
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = models.Product(event.sku, batches=[])
            uow.products.add(product)
        logging.info("Add batch structure:\n%s", pprint.pformat(product))
        batch = models.Batch(event.ref,
                             event.sku,
                             event.qty,
                             event.eta)
        product.batches.append(batch)
        uow.commit()
        return batch


def allocate(
    event: events.AllocationRequired,
    uow: unit_of_work.AbstractUnitOfWork,
) -> str | None:
    line = OrderLine(event.orderid, event.sku, event.qty)

    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(line.sku)

        batchref = product.allocate(line)
        uow.commit()
        return batchref


def change_batch_quantity(
    event: events.BatchQuantityChanged,
    uow: unit_of_work.AbstractUnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(
    event: events.OutOfStock,
    uow: unit_of_work.AbstractUnitOfWork,
):
    print(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )
