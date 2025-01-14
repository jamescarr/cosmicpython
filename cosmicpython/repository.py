import abc
from typing import Optional
from cosmicpython.models import Batch, OrderLine

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

    @abc.abstractmethod
    def find_containing_line(self, line: OrderLine) -> Optional[Batch]:
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

    def find_containing_line(self, line: OrderLine) -> Batch:
        batch = (
            self._session.query(Batch)
            .join(Batch._allocations)
            .filter(
                OrderLine.orderid == line.orderid,
            )
            .one_or_none()
        )
        if batch:
            return batch
        raise Exception("No batch found")

class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)


    def list(self) -> list[Batch]:
        return list(self._batches)


    def find_containing_line(self, line: OrderLine) -> Optional[Batch]:
        for batch in self._batches:
            if batch.contains(line):
                return batch
        return None
