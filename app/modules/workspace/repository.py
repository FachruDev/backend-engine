import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.workspace.model import (
    Workspace,
    WorkspaceMembership,
    WorkspaceRole,
    slugify_workspace_name,
)


def get_workspace_by_slug(db: Session, slug: str) -> Workspace | None:
    statement = select(Workspace).where(Workspace.slug == slug)
    return db.scalar(statement)


def make_unique_workspace_slug(db: Session, name: str) -> str:
    base_slug = slugify_workspace_name(name)
    slug = base_slug
    suffix = 2

    while get_workspace_by_slug(db, slug) is not None:
        slug = f"{base_slug}-{suffix}"
        suffix += 1

    return slug


def create_workspace(db: Session, *, name: str, owner_id: uuid.UUID) -> Workspace:
    workspace = Workspace(
        name=name.strip(),
        slug=make_unique_workspace_slug(db, name),
        owner_id=owner_id,
    )
    db.add(workspace)
    return workspace


def create_membership(
    db: Session,
    *,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
    role: WorkspaceRole,
) -> WorkspaceMembership:
    membership = WorkspaceMembership(
        user_id=user_id,
        workspace_id=workspace_id,
        role=role,
    )
    db.add(membership)
    return membership


def list_user_workspaces(db: Session, *, user_id: uuid.UUID) -> list[WorkspaceMembership]:
    statement = (
        select(WorkspaceMembership)
        .where(WorkspaceMembership.user_id == user_id)
        .options(selectinload(WorkspaceMembership.workspace))
        .order_by(WorkspaceMembership.created_at)
    )
    return list(db.scalars(statement).all())


def get_membership(
    db: Session,
    *,
    user_id: uuid.UUID,
    workspace_id: uuid.UUID,
) -> WorkspaceMembership | None:
    statement = select(WorkspaceMembership).where(
        WorkspaceMembership.user_id == user_id,
        WorkspaceMembership.workspace_id == workspace_id,
    )
    return db.scalar(statement)
