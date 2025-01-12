import abc
from cosmicpython.models import Batch

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> Batch:
        raise NotImplementedError

class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session) -> None:
        super().__init__()
        self._session = session

    def add(self, batch: Batch):
        self._session.add(batch)

    def get(self, reference) -> Batch:
        return self._session.query(Batch).filter_by(reference=reference).one()
