from sqlalchemy import Column, Integer, ForeignKey, Float, DateTime, String

app = FastAPI(
    title="Eyin Store API",
    description="الخلفية البرمجية لمتجر إلكتروني محترف",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "مرحباً بك في متجر Eyin الإلكتروني!"}