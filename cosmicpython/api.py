from fastapi import FastAPI, status
from pydantic import BaseModel

app = FastAPI()

class AllocationRequest(BaseModel):
    orderid: str
    sku: str
    qty: int

@app.post("/allocate", status_code=status.HTTP_201_CREATED)
def allocate(request: AllocationRequest):
    # In reality you'd do domain logic here, e.g.:
    # batchref = my_service.allocate(request.orderid, request.sku, request.qty)
    # But let's just return a dummy "batchref" for now:
    return {"batchref": "SOME_BATCH_REF"}  # placeholder

@app.get("/")
def read_root():
    return {"Hello": "World"}

