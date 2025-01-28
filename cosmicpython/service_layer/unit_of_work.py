import abc
from contextlib import contextmanager
from typing import AbstractSet

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from cosmicpython import config
from cosmicpython.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractProductRepository

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

    def __enter__(self):
        return self


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


@contextmanager
def unit_of_work(session_factory=DEFAULT_SESSION_FACTORY):
    """
    Function based contextmanager that does the exact same behavior as the
    below object version. This one has an implicit rather than explicit commit,
    however.

    Args:
        session_factory (sessionmaker): factory for creating sessions
    """
    session = session_factory()
    batches = repository.SQLAlchemyRepository(session)
    try:
        yield batches
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        super().__init__()
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.products = repository.SqlAlchemyProductRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        return self.session.rollback()


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self, batches=[]) -> None:
        self.products = repository.FakeProductRepository(batches)

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
