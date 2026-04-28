import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import Item, ItemCreate, Order, OrderCreate, OrderStatus, OrderUpdate, User, UserCreate, UserUpdate


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_order(*, session: Session, order_in: OrderCreate, user_id: uuid.UUID) -> Order:
    db_order = Order.model_validate(order_in, update={"user_id": user_id})
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


def update_order(*, session: Session, db_order: Order, order_in: OrderUpdate) -> Any:
    order_data = order_in.model_dump(exclude_unset=True)
    db_order.sqlmodel_update(order_data)
    session.add(db_order)
    session.commit()
    session.refresh(db_order)
    return db_order


def get_order_by_id(*, session: Session, order_id: uuid.UUID) -> Order | None:
    statement = select(Order).where(Order.id == order_id)
    session_order = session.exec(statement).first()
    return session_order


def get_orders_by_user(
    *,
    session: Session,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Order], int]:
    # 默认只过滤 status IN ('DELIVERED') - 这是我们要种下的第一个bug
    statement = select(Order).where(
        Order.user_id == user_id,
        Order.status.in_([OrderStatus.DELIVERED])  # 这里只筛选了DELIVERED
    ).offset(skip).limit(limit)
    results = session.exec(statement).all()
    count_statement = select(Order).where(
        Order.user_id == user_id,
        Order.status.in_([OrderStatus.DELIVERED])  # 这里也只筛选了DELIVERED
    )
    count_results = session.exec(count_statement)
    count = len(list(count_results))
    return results, count
