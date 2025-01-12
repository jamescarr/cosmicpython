from fastapi import FastAPI, status
from pydantic import BaseModel
from cosmicpython.models import Batch, OrderLine
from cosmicpython.repository import SQLAlchemyRepository
from cosmicpython.orm import sessionmaker
from cosmicpython import config, models

app = FastAPI()


get_session = config.init_db()

class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int

@app.post("/allocate", status_code=status.HTTP_201_CREATED)
def allocate(request: AllocationRequest):
    session = get_session()
    batches = SQLAlchemyRepository(session).list()
    line = OrderLine(
        request.orderid, request.sku, request.qty
    )
    batchref = models.allocate(line, batches)

    return {"batchref": batchref}

@app.get("/")
def read_root():
    return {"Hello": "World"}

