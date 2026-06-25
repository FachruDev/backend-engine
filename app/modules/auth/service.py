from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.modules.auth.jwt import create_access_token
from app.modules.auth.schema import LoginRequest, RegisterRequest, TokenResponse
from app.modules.users import repository as user_repository
from app.modules.workspace import repository as workspace_repository
from app.modules.workspace.model import WorkspaceRole

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def register_user(db: Session, payload: RegisterRequest) -> TokenResponse:
    existing_user = user_repository.get_user_by_email(db, payload.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = user_repository.create_user(
        db,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
    )
    db.flush()

    workspace_name = payload.workspace_name or f"{payload.full_name.strip()}'s Workspace"
    workspace = workspace_repository.create_workspace(db, name=workspace_name, owner_id=user.id)
    db.flush()

    workspace_repository.create_membership(
        db,
        user_id=user.id,
        workspace_id=workspace.id,
        role=WorkspaceRole.owner,
    )
    db.commit()
    db.refresh(user)

    return TokenResponse(access_token=create_access_token(user.id), user=user)


def authenticate_user(db: Session, payload: LoginRequest) -> TokenResponse:
    user = user_repository.get_user_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return TokenResponse(access_token=create_access_token(user.id), user=user)
