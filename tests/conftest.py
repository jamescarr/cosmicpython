import subprocess
import time

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from cosmicpython import config
from cosmicpython.adapters.orm import (
    clear_mappers,
    mapper_registry,
    metadata,
    sessionmaker,
)
from cosmicpython.adapters.repository import AbstractRepository, SQLAlchemyRepository

ENTRYPOINT = "cosmicpython.endpoints.api:app"


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    config.start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture(scope="session")
def postgres_db():
    engine = create_engine(config.get_postgres_uri())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db):
    config.start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture(scope="session")
def restart_api():
    """
    Example fixture that starts the FastAPI app in a subprocess (using uvicorn),
    then tears it down after tests complete.
    """
    server_details = config.get_api_url()

    # Start the FastAPI server on some port, e.g. 8001
    with open("api.log", "a") as log_file:
        proc = subprocess.Popen(
            ["uvicorn", ENTRYPOINT, "--port", server_details.port],
            stdout=log_file,
            stderr=log_file,
        )

    # Optionally give it a moment to spin up
    time.sleep(1)

    # The test(s) now run
    yield

    # Teardown: kill the server
    proc.terminate()
    proc.wait(timeout=5)


@pytest.fixture
def repository(postgres_session) -> AbstractRepository:
    return SQLAlchemyRepository(postgres_session)


@pytest.fixture
def add_stock(postgres_session):
    batches_added = set()
    skus_added = set()

    def _add_stock(lines):
        for ref, sku, qty, eta in lines:
            postgres_session.execute(
                text(
                    "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
                    " VALUES (:ref, :sku, :qty, :eta)"
                ),
                dict(ref=ref, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = postgres_session.execute(
                text("SELECT id FROM batches WHERE reference=:ref AND sku=:sku"),
                dict(ref=ref, sku=sku),
            )
            batches_added.add(batch_id)
            skus_added.add(sku)
        postgres_session.commit()
        return SQLAlchemyRepository(postgres_session)

    yield _add_stock

    for batch_id in batches_added:
        postgres_session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        postgres_session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"),
            dict(batch_id=batch_id),
        )
    for sku in skus_added:
        postgres_session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"),
            dict(sku=sku),
        )
        postgres_session.commit()


def wait_for_postgres_to_come_up(engine):
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    pytest.fail("Postgres never came up")
