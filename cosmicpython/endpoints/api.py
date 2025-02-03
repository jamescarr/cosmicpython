from datetime import date
from typing import Optional

from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from cosmicpython import config
from cosmicpython.domain import models, events
from cosmicpython.service_layer import services
from cosmicpython.service_layer.unit_of_work import SqlAlchemyUnitOfWork
from cosmicpython.service_layer import message_bus

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


get_session = config.init_db()


class OrderRequest(BaseModel):
    ref: str
    sku: str
    qty: int
    eta: Optional[date]


class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int


def order_line_from_request(req: AllocationRequest):
    return models.OrderLine(req.orderid, req.sku, req.qty)


@app.post("/add_batch", status_code=status.HTTP_201_CREATED)
def add_batch(request: OrderRequest, response: Response):
    uow = SqlAlchemyUnitOfWork(session_factory=get_session)
    try:
        message_bus.handle(events.BatchCreated(
                       ref=request.ref,
                       sku=request.sku,
                       qty=request.qty,
                       eta=request.eta),
                       uow=uow)
        return {"message": f"Batch added."}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}


@app.post("/allocations")
def allocate(request: AllocationRequest, response: Response):
    uow = SqlAlchemyUnitOfWork()
    try:
        batchref = services.allocate(request.orderid, request.sku, request.qty, uow)
        if batchref:
            response.status_code = status.HTTP_201_CREATED
            return {"batchref": batchref}
        else:  # this is a bad hack... we should be able to respond based on event.
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Out of stock: {request.sku}"}

    except services.InvalidSku as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}


@app.delete("/allocations")
def deallocate(request: AllocationRequest, response: Response):
    uow = SqlAlchemyUnitOfWork()
    try:
        services.deallocate(request.orderid, request.sku, request.qty, uow)
        response.status_code = HTTP_204_NO_CONTENT
        return {"message": "deleted"}
    except models.NoBatchContainingOrderLine as e:
        response.status_code = HTTP_404_NOT_FOUND
        return {"message": str(e)}


@app.get("/")
def read_root():
    return {"Hello": "World"}
