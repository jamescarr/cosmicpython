from dataclasses import dataclass
from typing import List


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


def allocate(line: OrderLine, batches: list) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(line)


class OutOfStock(Exception):
    def __init__(self, line: OrderLine):
        super().__init__(f"Out of stock: {line.sku}")
        self.line = line


class NoBatchContainingOrderLine(Exception):
    def __init__(self, line: OrderLine):
        super().__init__(f"No batch containing order {line.orderid}")
        self.line = line


class Product:
    sku: str
    batches: List[Batch]

    def __init__(self, sku: str, batches: List[Batch]) -> None:
        self.sku = sku
        self.batches = batches

    def deallocate(self, line: OrderLine):
        for batch in self.batches:
            if batch.contains(line):
                batch.deallocate(line)
                return
        raise NoBatchContainingOrderLine(line)

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            return batch.reference
        except StopIteration:
            raise OutOfStock(line)
