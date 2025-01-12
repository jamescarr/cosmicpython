import pytest
import uuid
import requests
from cosmicpython import config


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_api_returns_allocation(add_stock):
    sku, othersku = random_sku(), random_sku("other")  #(1)
    earlybatch = random_batchref("1")
    laterbatch = random_batchref("2")
    otherbatch = random_batchref("3")
    add_stock(  #(2)
        [
            (laterbatch, sku, 100, "2011-01-02"),
            (earlybatch, sku, 100, "2011-01-01"),
            (otherbatch, othersku, 100, None),
        ]
    )
    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url().url

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    print(r.content)

    assert r.json()["batchref"] == earlybatch
