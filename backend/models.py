from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Numeric, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password = Column(String)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    activation_token = Column(String, nullable=True)
    reset_token = Column(String, nullable=True)

class Contractor(Base):
    __tablename__ = "contractors"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    orders = relationship("Order", back_populates="contractor")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, server_default=func.now())
    delivery_date = Column(Date)
    is_delivered = Column(Boolean, default=False)
    contractor_id = Column(Integer, ForeignKey("contractors.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    contractor = relationship("Contractor", back_populates="orders")
    user = relationship("User")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Numeric(10, 2))
    total = Column(Numeric(10, 2))
    
    order = relationship("Order", back_populates="items") 