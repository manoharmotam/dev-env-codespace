import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="TiffinStore Shipping Service")
Instrumentator().instrument(app).expose(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["tiffinstore_shipping"]
shipments_col = db["shipments"]

class DispatchReq(BaseModel):
    order_id: str
    user_id: str
    address: str

class StatusUpdateReq(BaseModel):
    status: str  # e.g., "Packed in Hot Tiffin", "Out for Delivery", "Delivered"

@app.get("/health")
def health():
    return {"status": "healthy", "service": "shipping-service", "db": "MongoDB"}

# 1. Called automatically by Payment Service when payment succeeds
@app.post("/api/shipping/dispatch")
def dispatch_order(req: DispatchReq):
    shipment_doc = {
        "order_id": req.order_id,
        "user_id": req.user_id,
        "address": req.address,
        "current_status": "Kitchen Preparing Tiffin",
        "history": [
            {
                "status": "Order Received from Payment Service",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        ]
    }
    shipments_col.insert_one(shipment_doc)
    return {"message": "Shipment created", "order_id": req.order_id, "status": "Kitchen Preparing Tiffin"}

# 2. Called by Frontend so users can track their breakfast delivery
@app.get("/api/shipping/{order_id}")
def track_order(order_id: str):
    shipment = shipments_col.find_one({"order_id": order_id}, {"_id": 0})
    if not shipment:
        raise HTTPException(status_code=404, detail="Order not found")
    return shipment

# 3. Update delivery status (great for testing API calls in DevOps)
@app.put("/api/shipping/{order_id}/status")
def update_status(order_id: str, req: StatusUpdateReq):
    result = shipments_col.update_one(
        {"order_id": order_id},
        {
            "$set": {"current_status": req.status},
            "$push": {
                "history": {
                    "status": req.status,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        }
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"order_id": order_id, "new_status": req.status}