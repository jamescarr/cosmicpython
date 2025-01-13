from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from cosmicpython.repository import SQLAlchemyRepository
from cosmicpython import config, models, services

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


get_session = config.init_db()

class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int

@app.post("/allocate")
def allocate(request: AllocationRequest, response: Response):
    line = models.OrderLine(
        request.orderid, request.sku, request.qty
    )
    session = get_session()
    batches = SQLAlchemyRepository(session)
    try:
        batchref = services.allocate(line, batches, session)
        response.status_code = status.HTTP_201_CREATED
        return {"batchref": batchref}
    except (models.OutOfStock, services.InvalidSku) as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}

## /deallocate

@app.get("/")
def read_root():
    return {"Hello": "World"}

