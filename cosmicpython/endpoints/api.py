from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from cosmicpython.adapters.repository import (
    NoBatchContainingOrderLine,
    SQLAlchemyRepository,
)
from cosmicpython import config
from cosmicpython.domain import models
from cosmicpython.service_layer import services

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


get_session = config.init_db()


class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int


def order_line_from_request(req: AllocationRequest):
    return models.OrderLine(req.orderid, req.sku, req.qty)


@app.post("/allocations")
def allocate(request: AllocationRequest, response: Response):
    session = get_session()
    batches = SQLAlchemyRepository(session)
    try:
        batchref = services.allocate(request.orderid,
                                     request.sku,
                                     request.qty, batches, session)
        response.status_code = status.HTTP_201_CREATED
        return {"batchref": batchref}
    except (models.OutOfStock, services.InvalidSku) as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}


@app.delete("/allocations")
def deallocate(request: AllocationRequest, response: Response):
    session = get_session()
    batches = SQLAlchemyRepository(session)

    try:
        services.deallocate(request.orderid, request.sku, request.qty, batches, session)
        response.status_code = HTTP_204_NO_CONTENT
        return {"message": "deleted"}
    except NoBatchContainingOrderLine as e:
        response.status_code = HTTP_404_NOT_FOUND
        return {"message": str(e)}


@app.get("/")
def read_root():
    return {"Hello": "World"}
