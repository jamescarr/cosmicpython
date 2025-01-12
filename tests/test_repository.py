from sqlalchemy import text

from cosmicpython import models, repository


def test_repository_can_save_a_batch(session):
    batch = models.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(batch)  #(1)
    session.commit()

    rows = session.execute(
        text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')
    )
    assert list(rows) == [("batch1", "RUSTY-SOAPDISH", 100, None)]
