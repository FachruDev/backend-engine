import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.users.model import User


def get_user_by_email(db: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email.lower())
    return db.scalar(statement)


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    statement = select(User).where(User.id == user_id).options(selectinload(User.memberships))
    return db.scalar(statement)


def create_user(db: Session, *, email: str, full_name: str, hashed_password: str) -> User:
    user = User(
        email=email.lower(),
        full_name=full_name.strip(),
        hashed_password=hashed_password,
    )
    db.add(user)
    return user
