import pytest
from sqlalchemy import text
from cosmicpython.domain import models as model
from cosmicpython.service_layer import unit_of_work


def get_allocated_batch_ref(session, orderid, sku):
    [[orderlineid]] = session.execute(  # (1)
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku),
    )
    [[batchref]] = session.execute(  # (1)
        text(
            "SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id"
            " WHERE orderline_id=:orderlineid"
        ),
        dict(orderlineid=orderlineid),
    )
    return batchref


def insert_batch(session, ref, sku, qty, eta):
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta)"
        ),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def insert_product_with_batch(sku, batch, session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        uow.products.add(model.Product(sku=sku, batches=[batch]))
        uow.commit()


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    sku = "HIPSTER-WORKBENCH"
    insert_batch(session, "batch1", sku, 100, None)
    insert_product_with_batch(
        sku, model.Batch("batch1", sku, 100, None), session_factory
    )
    session.commit()

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)  # (1)
    with uow:
        product = uow.products.get(sku=sku)  # (2)
        line = model.OrderLine("o1", sku, 10)
        product.allocate(line)
        uow.commit()  # (3)

    batchref = get_allocated_batch_ref(session, "o1", sku)
    assert batchref == "batch1"


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with uow:
        insert_batch(uow.session, "batch1", "MEDIUM-PLINTH", 100, None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)
    with pytest.raises(MyException):
        with uow:
            insert_batch(uow.session, "batch1", "LARGE-FORK", 100, None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
