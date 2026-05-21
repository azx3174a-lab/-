from fastapi import FastAPI
from app.database import engine, Base
from app.models import user, product, order 
# استيراد موديل المنتجات الجديد
from app.routers import products

# أمر إنشاء الجداول تلقائياً في قاعدة البيانات عند تشغيل السيرفر
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Eyin Store API",
    description="الخلفية البرمجية لمتجر إلكتروني محترف ومستقر",
    version="1.0.0"
)

# ربط روابط المنتجات بالسيرفر الرئيسي
app.include_router(products.router)

# الرابط الرئيسي والترحيبي للمتجر
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "مرحباً بك في متجر Eyin الإلكتروني! قاعدة البيانات والروابط جاهزة للعمل بنجاح."
    }