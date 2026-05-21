from fastapi import FastAPI
from .database import engine, Base
from .models import user, product, order 
from .routers import products

# إنشاء الجداول تلقائياً
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Eyin Store API",
    description="الخلفية البرمجية لمتجر إلكتروني محترف ومستقر",
    version="1.0.0"
)

app.include_router(products.router)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "مرحباً بك في متجر Eyin الإلكتروني! قاعدة البيانات والروابط جاهزة للعمل بنجاح."
    }