from sqlalchemy import text
import pytest

from cosmicpython import service_layer
from cosmicpython.domain import models
from cosmicpython.adapters import repository


def test_repository_can_save_a_batch(session):
    batch = models.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(batch)  # (1)
    session.commit()

    rows = session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session):
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty)"
            ' VALUES ("order1", "GENERIC-SOFA", 12)'
        )
    )
    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid="order1", sku="GENERIC-SOFA"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            ' VALUES (:batch_id, "GENERIC-SOFA", 100, null)'
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text(
            'SELECT id FROM batches WHERE reference=:batch_id AND sku="GENERIC-SOFA"'
        ),
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id)"
            " VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_product_loads_saved_products_by_sku(session):
    products = repository.SqlAlchemyProductRepository(session)
    p1 = models.Product(
        sku="NOW-LISTEN",
        batches=[models.Batch(reference="FOO", sku="BAR-BAZ", qty=10, eta=None)],
    )

    products.add(p1)

    p2 = products.get(p1.sku)
    assert p2.sku == p1.sku
    assert p1.batches == p2.batches


def test_fetch_batch_by_order_line(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SQLAlchemyRepository(session)
    line = models.OrderLine("order1", "GENERIC-SOFA", 100)

    batch = repo.find_containing_line(line)

    assert batch.reference == "batch1"


def test_behavior_when_batch_not_found(session):
    repo = repository.SQLAlchemyRepository(session)
    line = models.OrderLine("order256", "GENERIC-SOFA", 100)

    with pytest.raises(repository.NoBatchContainingOrderLine):
        repo.find_containing_line(line)
