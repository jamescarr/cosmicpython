import abc
from typing import Optional, Set

from cosmicpython.adapters import orm
from cosmicpython.domain.models import Batch, OrderLine, Product


class AbstractProductRepository(abc.ABC):
    def __init__(self):
        self.seen = set()  # type: Set[Product]  #(1)

    def add(self, product: Product):  # (2)
        self._add(product)
        self.seen.add(product)

    def get(self, sku) -> Product:  # (3)
        product = self._get(sku)
        if product:
            self.seen.add(product)
        return product

    def get_by_batchref(self, batchref) -> Product:
        product = self._get_by_batchref(batchref)
        if product:
            self.seen.add(product)
        return product

    @abc.abstractmethod
    def _get_by_batchref(self, batchref) -> Product:
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, product): ...

    @abc.abstractmethod
    def _get(self, sku) -> Product: ...


class SqlAlchemyProductRepository(AbstractProductRepository):
    def __init__(self, session) -> None:
        super().__init__()
        self._session = session

    def _add(self, product):
        self._session.add(product)

    def _get(self, sku) -> Product:
        return self._session.query(Product).filter_by(sku=sku).first()

    def _get_by_batchref(self, batchref):
        return (
            self._session.query(Product)
            .join(Batch)
            .filter(orm.batches.c.reference == batchref)
            .first()
        )


class FakeProductRepository(AbstractProductRepository):
    _products: set

    def __init__(self, products) -> None:
        self._products = set(products)
        super().__init__()

        for product in products:
            self.add(product)

    def _add(self, product):
        self._products.add(product)

    def _get(self, sku) -> Product:
        return next((p for p in self._products if p.sku == sku), None)

    def _get_by_batchref(self, batchref):
        return next(
            (p for p in self._products for b in p.batches if b.reference == batchref),
            None,
        )


class ProductNotFoundForSku(Exception):
    def __init__(self, sku) -> None:
        super().__init__(f"No product found for sku {sku}")


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference=None, sku=None) -> Batch:
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

    def get(self, reference=None, sku=None) -> Batch:
        query = self._session.query(Batch)
        if reference:
            query = query.filter_by(reference=reference)
        elif sku:
            query = query.filter_by(sku=sku)

        return query.first()

    def list(self) -> list[Batch]:
        return self._session.query(Batch).all()

    def find_containing_line(self, line: OrderLine) -> Batch:
        batch = (
            self._session.query(Batch)
            .join(Batch._allocations)
            .filter(
                OrderLine.orderid == line.orderid,
            )
            .first()
        )
        if batch:
            return batch
        raise NoBatchContainingOrderLine(line)


class NoBatchContainingOrderLine(Exception):
    def __init__(self, line: OrderLine):
        super().__init__(f"No batch containing order {line.orderid}")
        self.line = line


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
