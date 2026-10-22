import os, uuid, requests
import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="TiffinStore Payment Service")
Instrumentator().instrument(app).expose(app)

DB_URI = os.getenv("POSTGRES_URI", "postgresql://postgres:postgres@localhost:5432/tiffinstore")
SHIPPING_URL = os.getenv("SHIPPING_SERVICE_URL", "http://localhost:5005")

def get_conn():
    return psycopg2.connect(DB_URI)

@app.on_event("startup")
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            tx_id VARCHAR(50) PRIMARY KEY,
            user_id VARCHAR(50),
            amount INT,
            status VARCHAR(20)
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

class PaymentReq(BaseModel):
    user_id: str
    amount: int
    address: str

@app.get("/health")
def health():
    return {"status": "healthy", "service": "payment-service", "db": "PostgreSQL"}

@app.post("/api/payments")
def process_payment(req: PaymentReq):
    tx_id = str(uuid.uuid4())[:8]
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO payments (tx_id, user_id, amount, status) VALUES (%s, %s, %s, %s)",
                (tx_id, req.user_id, req.amount, "SUCCESS"))
    conn.commit()
    cur.close()
    conn.close()

    # Trigger Shipping Service
    try:
        requests.post(f"{SHIPPING_URL}/api/shipping/dispatch", json={"order_id": tx_id, "user_id": req.user_id, "address": req.address}, timeout=3)
    except Exception as e:
        print(f"Shipping trigger warning: {e}")

    return {"tx_id": tx_id, "status": "SUCCESS", "message": "Payment processed & Tiffin dispatched!"}