import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.modules.workspace.model import WorkspaceRole


class WorkspaceMembershipRead(BaseModel):
    workspace_id: uuid.UUID
    workspace_name: str
    workspace_slug: str
    role: WorkspaceRole


class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserWithMemberships(UserRead):
    memberships: list[WorkspaceMembershipRead]
