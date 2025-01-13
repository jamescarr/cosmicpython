import pytest
from cosmicpython import models, services
from cosmicpython.repository import FakeRepository

class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = models.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = models.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeRepository([batch])  #(1)

    result = services.allocate(line, repo, FakeSession())  #(2) (3)
    assert result == "b1"


def test_error_for_invalid_sku():
    line = models.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = models.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeRepository([batch])  #(1)

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())  #(2) (3)

