import abc
from cosmicpython.models import Batch

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError

    @abc.abstractmethod
    def list(self) -> list[Batch]:
        raise NotImplementedError

class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: Batch):
        self._session.add(batch)

    def get(self, reference) -> Batch:
        return self._session.query(Batch).filter_by(reference=reference).one()

    def list(self) -> list[Batch]:
        return self._session.query(Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list[Batch]:
        return list(self._batches)
