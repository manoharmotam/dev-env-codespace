import os
from fastapi import FastAPI
from pymongo import MongoClient
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="TiffinStore Product Service")
Instrumentator().instrument(app).expose(app)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["tiffinstore_catalog"]
products_col = db["products"]

# Seed initial breakfast items if empty
@app.on_event("startup")
def seed_data():
    if products_col.count_documents({}) == 0:
        products_col.insert_many([
            {"item_id": "tiffin-1", "name": "Ghee Roast Masala Dosa", "price": 80, "category": "South Indian", "accompaniments": ["Coconut Chutney", "Sambar"]},
            {"item_id": "tiffin-2", "name": "Steamed Idli (4 pcs) & Vada", "price": 60, "category": "Steamed", "accompaniments": ["Groundnut Chutney", "Sambar"]},
            {"item_id": "tiffin-3", "name": "Ven Pongal", "price": 70, "category": "Comfort", "accompaniments": ["Gotsu", "Coconut Chutney"]},
            {"item_id": "tiffin-4", "name": "Pesarattu Upma", "price": 85, "category": "Telangana Special", "accompaniments": ["Ginger Chutney"]},
            {"item_id": "tiffin-5", "name": "Madras Filter Coffee", "price": 30, "category": "Beverage", "accompaniments": []}
        ])

@app.get("/health")
def health():
    return {"status": "healthy", "service": "product-service", "db": "MongoDB"}

@app.get("/api/products")
def get_products():
    items = list(products_col.find({}, {"_id": 0}))
    return {"products": items}