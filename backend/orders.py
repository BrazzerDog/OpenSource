from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Order, OrderItem
import schemas
from weasyprint import HTML
from fastapi.responses import FileResponse
import tempfile
from sqlalchemy.exc import IntegrityError
import os
from datetime import date
from auth import get_current_user

orders_router = APIRouter(prefix="/orders")

@orders_router.get("/", response_model=List[schemas.Order])
def get_orders(
    skip: int = 0,
    limit: int = 10,
    date_from: date = Query(None),
    date_to: date = Query(None),
    is_delivered: bool = Query(None),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Order)
    
    if not current_user.is_admin:
        query = query.filter(Order.user_id == current_user.id)
    
    if date_from:
        query = query.filter(Order.date >= date_from)
    if date_to:
        query = query.filter(Order.date <= date_to)
    if is_delivered is not None:
        query = query.filter(Order.is_delivered == is_delivered)
        
    return query.offset(skip).limit(limit).all()

@orders_router.post("/", response_model=schemas.Order)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        db_order = Order(
            delivery_date=order.delivery_date,
            contractor_id=order.contractor_id,
            user_id=current_user.id
        )
        db.add(db_order)
        db.flush()  # Получаем id без коммита
        
        for item in order.items:
            db_item = OrderItem(**item.dict(), order_id=db_order.id)
            db.add(db_item)
        
        db.commit()
        db.refresh(db_order)
        return db_order
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Invalid data")
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

@orders_router.put("/{order_id}", response_model=schemas.Order)
def update_order(
    order_id: int,
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Обновляем основные поля заказа
    db_order.delivery_date = order.delivery_date
    db_order.contractor_id = order.contractor_id
    
    # Удаляем старые items
    db.query(OrderItem).filter(OrderItem.order_id == order_id).delete()
    
    # Добавляем новые items
    for item in order.items:
        db_item = OrderItem(**item.dict(), order_id=order_id)
        db.add(db_item)
    
    db.commit()
    db.refresh(db_order)
    return db_order

@orders_router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if not current_user.is_admin and db_order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_order)
    db.commit()
    return {"message": "Order deleted"}

@orders_router.get("/{order_id}/pdf")
def generate_order_pdf(order_id: int, db: Session = Depends(get_db)):
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        # Добавляем красивые стили для PDF
        html = f"""
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
            }}
            h1 {{
                color: #1890ff;
                border-bottom: 2px solid #1890ff;
                padding-bottom: 10px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 12px;
                border: 1px solid #ddd;
            }}
            th {{
                background: #f7f7f7;
                font-weight: bold;
            }}
            .total {{
                margin-top: 20px;
                text-align: right;
                font-size: 18px;
                font-weight: bold;
            }}
        </style>
        <h1>Заказ №{order.id}</h1>
        <p>Дата: {order.date}</p>
        <p>Контрагент: {order.contractor.name}</p>
        <table>
            <tr>
                <th>Наименование</th>
                <th>Количество</th>
                <th>Цена</th>
                <th>Сумма</th>
            </tr>
            {''.join(f"<tr><td>{item.name}</td><td>{item.quantity}</td><td>{item.price}</td><td>{item.total}</td></tr>" for item in order.items)}
        </table>
        """

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            HTML(string=html).write_pdf(tmp.name)
            return FileResponse(
                tmp.name,
                filename=f"order_{order_id}.pdf",
                media_type="application/pdf"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail="PDF generation failed")
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name) 