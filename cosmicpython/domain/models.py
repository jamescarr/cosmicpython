from dataclasses import dataclass
from typing import List

from cosmicpython.domain import events
from cosmicpython.domain.events import Event


class InvalidSku(Exception):
    def __init__(self, sku: str) -> None:
        super().__init__(f"Invalid sku {sku}")


@dataclass(unsafe_hash=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int


class Batch:
    def __init__(self, reference, sku, qty, eta) -> None:
        self.reference = reference
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocations = set()

    def allocate(self, orderline: OrderLine) -> None:
        if self.can_allocate(orderline):
            self._allocations.add(orderline)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def deallocate(self, line: OrderLine) -> None:
        if self.contains(line):
            self._allocations.remove(line)

    def contains(self, line: OrderLine) -> bool:
        return line in self._allocations

    def can_allocate(self, line: OrderLine) -> bool:
        return line.sku == self.sku and self.available_quantity >= line.qty

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def deallocate_one(self) -> OrderLine:
        return self._allocations.pop()


class NoBatchContainingOrderLine(Exception):
    def __init__(self, line: OrderLine):
        super().__init__(f"No batch containing order {line.orderid}")
        self.line = line


class Product:
    sku: str
    batches: List[Batch]
    events: List[Event]

    def __init__(self, sku: str, batches: List[Batch], version=0) -> None:
        self.sku = sku
        self.batches = batches
        self.version = version
        self.events = []

    def deallocate(self, line: OrderLine):
        for batch in self.batches:
            if batch.contains(line):
                batch.deallocate(line)
                return
        raise NoBatchContainingOrderLine(line)

    def allocate(self, line: OrderLine) -> str | None:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            self.version += 1
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            self.events.append(events.OutOfStock(line.sku))
            return None

    def change_batch_quantity(self, ref: str, qty: int):
        batch = next(b for b in self.batches if b.reference == ref)
        batch._purchased_quantity = qty
        while batch.available_quantity < 0:
            line = batch.deallocate_one()
            self.events.append(
                events.AllocationRequired(line.orderid, line.sku, line.qty)
            )
