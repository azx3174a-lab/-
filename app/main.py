from fastapi import FastAPI
from app.database import engine, Base
# استيراد الموديلات (الجداول) لتنبيه SQLAlchemy بوجودها
from app.models import user, product, order 

# أمر سحري: يمر على كل الموديلات وينشئ الجداول في قاعدة البيانات إذا لم تكن موجودة
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Eyin Store API",
    description="الخلفية البرمجية لمتجر إلكتروني محترف ومستقر",
    version="1.0.0"
)

# رابط ترحيبي للتأكد من تشغيل السيرفر
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "مرحباً بك في متجر Eyin الإلكتروني! قاعدة البيانات والجداول جاهزة للعمل."
    }