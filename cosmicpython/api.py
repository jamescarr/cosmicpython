from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from cosmicpython.models import OrderLine
from cosmicpython.repository import SQLAlchemyRepository
from cosmicpython import config, models

app = FastAPI()


get_session = config.init_db()

class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int

def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}

@app.post("/allocate")
def allocate(request: AllocationRequest, response: Response):
    session = get_session()
    batches = SQLAlchemyRepository(session).list()
    line = OrderLine(
        request.orderid, request.sku, request.qty
    )

    if not is_valid_sku(line.sku, batches):
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": f"Invalid sku {line.sku}"}

    try:
        batchref = models.allocate(line, batches)
    except models.OutOfStock as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}

    session.commit()

    response.status_code = status.HTTP_201_CREATED
    return {"batchref": batchref}

@app.get("/")
def read_root():
    return {"Hello": "World"}

