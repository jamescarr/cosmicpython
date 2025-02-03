from datetime import date
from typing import Optional

from fastapi import FastAPI, Response, status
from pydantic import BaseModel
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from cosmicpython import config
from cosmicpython.domain import events, models
from cosmicpython.service_layer import handlers, services
from cosmicpython.service_layer.message_bus import MessageBus
from cosmicpython.service_layer.unit_of_work import SqlAlchemyUnitOfWork

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})
message_bus = MessageBus()

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
    uow = SqlAlchemyUnitOfWork()
    try:
        message_bus.handle(
            events.BatchCreated(
                ref=request.ref, sku=request.sku, qty=request.qty, eta=request.eta
            ),
            uow=uow,
        )
        return {"message": f"Batch added."}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"message": str(e)}


@app.post("/allocations")
def allocate(request: AllocationRequest, response: Response):
    uow = SqlAlchemyUnitOfWork()
    try:
        result = message_bus.handle(
            events.AllocationRequired(request.orderid, request.sku, request.qty), uow
        )
        batchref = result.pop()
        if not batchref:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {"message": f"Out of stock: {request.sku}"}
    except handlers.InvalidSku as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"message": str(e)}

    response.status_code = status.HTTP_201_CREATED
    return {"batchref": batchref}


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
