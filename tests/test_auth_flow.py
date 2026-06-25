import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.database import get_db
from app.main import app
from app.modules.auth.dependency import require_workspace_role
from app.modules.users.model import User
from app.modules.workspace.model import WorkspaceMembership, WorkspaceRole


@pytest.fixture
def db_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> TestClient:
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def register_user(client: TestClient, email: str = "student@example.com") -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "strongpassword",
            "full_name": "Student Worker",
            "workspace_name": "Student Workspace",
        },
    )
    assert response.status_code == 201
    return response.json()


def test_register_creates_user_workspace_and_owner_membership(
    client: TestClient,
    db_session: Session,
) -> None:
    data = register_user(client)

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "student@example.com"

    user = db_session.scalar(select(User).where(User.email == "student@example.com"))
    assert user is not None

    membership = db_session.scalar(
        select(WorkspaceMembership).where(WorkspaceMembership.user_id == user.id)
    )
    assert membership is not None
    assert membership.role == WorkspaceRole.owner
    assert membership.workspace.name == "Student Workspace"


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "student@example.com",
            "password": "anotherpassword",
            "full_name": "Duplicate",
        },
    )

    assert response.status_code == 409


def test_login_accepts_correct_password(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "strongpassword"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "student@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401


def test_current_user_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_current_user_accepts_valid_bearer_token(client: TestClient) -> None:
    data = register_user(client)

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "student@example.com"
    assert response.json()["memberships"][0]["role"] == "owner"


def test_workspace_list_returns_current_user_workspaces(client: TestClient) -> None:
    data = register_user(client)

    response = client.get(
        "/api/v1/workspaces/me",
        headers={"Authorization": f"Bearer {data['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()[0]["name"] == "Student Workspace"
    assert response.json()[0]["role"] == "owner"


def test_rbac_dependency_allows_owner_and_rejects_lower_roles(
    client: TestClient,
    db_session: Session,
) -> None:
    register_user(client)
    membership = db_session.scalar(select(WorkspaceMembership))
    assert membership is not None

    owner_guard = require_workspace_role(WorkspaceRole.owner)
    assert owner_guard(membership.workspace_id, membership.user, db_session) is None

    membership.role = WorkspaceRole.member
    db_session.commit()

    with pytest.raises(Exception) as exc_info:
        owner_guard(membership.workspace_id, membership.user, db_session)

    assert getattr(exc_info.value, "status_code", None) == 403
