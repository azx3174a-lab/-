from app.database import Base
from sqlalchemy import Column, Integer, Float, String, ForeignKey

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    status = Column(String, default="pending")  # pending, completed, cancelled