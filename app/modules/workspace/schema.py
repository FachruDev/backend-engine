import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.workspace.model import WorkspaceRole


class WorkspaceRead(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    owner_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceWithRole(WorkspaceRead):
    role: WorkspaceRole
