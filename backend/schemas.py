from pydantic import BaseModel, EmailStr, constr, validator
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_admin: bool
    is_active: bool
    
    class Config:
        from_attributes = True

class OrderItemBase(BaseModel):
    name: str
    quantity: int
    price: Decimal
    total: Decimal

class OrderBase(BaseModel):
    delivery_date: date
    contractor_id: int
    items: List[OrderItemBase]

    @validator('delivery_date')
    def validate_delivery_date(cls, v):
        if v < date.today():
            raise ValueError('Delivery date cannot be in the past')
        return v

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    date: datetime
    is_delivered: bool
    user_id: int
    
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    name: str
    quantity: int
    price: Decimal
    total: Decimal

    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @validator('total')
    def validate_total(cls, v, values):
        if 'quantity' in values and 'price' in values:
            expected = values['quantity'] * values['price']
            if abs(v - expected) > Decimal('0.01'):
                raise ValueError('Total does not match quantity * price')
        return v 