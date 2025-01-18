import abc
from typing import AbstractSet

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cosmicpython import config
from cosmicpython.adapters import repository


class AbstractUnitOfWork(abc.ABC):
    batches: repository.AbstractRepository  # (1)

    def __exit__(self, *args):  # (2)
        self.rollback()  # (4)

    @abc.abstractmethod
    def commit(self):  # (3)
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):  # (4)
        raise NotImplementedError

    def __enter__(self):
        return self


DEFAULT_SESSION_FACTORY = sessionmaker(  # (1)
    bind=create_engine(
        config.get_postgres_uri(),
    )
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        super().__init__()
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.batches = repository.SQLAlchemyRepository(self.session)
        return super().__enter__()


    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        return self.session.rollback()


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self) -> None:
        self.batches = repository.FakeRepository([])

    def commit(self):
        self.committed = True

    def rollback(self):
        pass
