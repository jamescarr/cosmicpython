from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from cosmicpython.models import OrderLine, OutOfStock
from cosmicpython.repository import SQLAlchemyRepository
from cosmicpython import config, models, services

app = FastAPI()


get_session = config.init_db()

class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int

@app.post("/allocate")
def allocate(request: AllocationRequest, response: Response):
    line = OrderLine(
        request.orderid, request.sku, request.qty
    )
    session = get_session()
    batches = SQLAlchemyRepository(session)
    try:
        batchref = services.allocate(line, batches, session)
        response.status_code = status.HTTP_201_CREATED
        return {"batchref": batchref}
    except OutOfStock as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}
    except services.InvalidSku as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}



@app.get("/")
def read_root():
    return {"Hello": "World"}

