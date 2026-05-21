from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from pydantic import BaseModel
from typing import Optional

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

class ProductCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    stock: int = 0
    image_url: Optional[str] = None

@router.post("/")
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = Product(
        title=product.title,
        description=product.description,
        price=product.price,
        stock=product.stock,
        image_url=product.image_url
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"message": "تم إضافة المنتج بنجاح!", "product": db_product}

@router.get("/")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products