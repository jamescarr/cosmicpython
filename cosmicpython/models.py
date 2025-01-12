
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderLine:
    orderid: str
    sku: str
    qty: int

class Batch:
    def __init__(self, reference, sku, qty, eta) -> None:
        self.reference = reference
        self.sku = sku
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, orderline: OrderLine) -> None:
        self.available_quantity -= orderline.qty

    def can_allocate(self, line: OrderLine) -> bool:
        return line.sku == self.sku and self.available_quantity >= line.qty
