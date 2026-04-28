import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Order, OrderCreate, OrderPublic, OrdersPublic, OrderUpdate, Message


router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("/", response_model=OrdersPublic)
def read_orders(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve orders.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Order)
        count = session.exec(count_statement).one()
        statement = (
            select(Order).order_by(col(Order.created_at).desc()).offset(skip).limit(limit)
        )
        orders = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Order)
            .where(Order.user_id == current_user.id)
            .where(Order.status.in_(['DELIVERED']))  # 后端默认只过滤 DELIVERED
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Order)
            .where(Order.user_id == current_user.id)
            .where(Order.status.in_(['DELIVERED']))  # 这里也只筛选了 DELIVERED
            .order_by(col(Order.created_at).desc())
            .offset(skip)
            .limit(limit)
        )
        orders = session.exec(statement).all()

    orders_public = [OrderPublic.model_validate(order) for order in orders]
    return OrdersPublic(data=orders_public, count=count)


@router.get("/{id}", response_model=OrderPublic)
def read_order(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get order by ID.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_superuser and (order.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order


@router.post("/", response_model=OrderPublic)
def create_order(
    *, session: SessionDep, current_user: CurrentUser, order_in: OrderCreate
) -> Any:
    """
    Create new order.
    """
    order = Order.model_validate(order_in, update={"user_id": current_user.id})
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.put("/{id}", response_model=OrderPublic)
def update_order(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    order_in: OrderUpdate,
) -> Any:
    """
    Update an order.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_superuser and (order.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    update_dict = order_in.model_dump(exclude_unset=True)
    order.sqlmodel_update(update_dict)
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@router.delete("/{id}")
def delete_order(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete an order.
    """
    order = session.get(Order, id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if not current_user.is_superuser and (order.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(order)
    session.commit()
    return Message(message="Order deleted successfully")

