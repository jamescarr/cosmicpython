from cosmicpython.models import OrderLine, OutOfStock

def allocate(line: OrderLine, batches: list) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(line)

