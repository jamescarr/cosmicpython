
class OrderLine:
    def __init__(self, reference: str, item: str, qty: int) -> None:
        self.reference = reference
        self.item = item
        self.qty = qty

class Batch:
    def __init__(self, number, item, qty, eta) -> None:
        self.number = number
        self.item = item
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, orderline: OrderLine) -> None:
        self.available_quantity -= orderline.qty
