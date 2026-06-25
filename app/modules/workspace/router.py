from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.modules.auth.dependency import get_current_user
from app.modules.users.model import User
from app.modules.workspace.repository import list_user_workspaces
from app.modules.workspace.schema import WorkspaceWithRole
from app.modules.workspace.service import serialize_workspace_memberships

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("/me", response_model=list[WorkspaceWithRole])
def read_current_user_workspaces(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[WorkspaceWithRole]:
    memberships = list_user_workspaces(db, user_id=current_user.id)
    return serialize_workspace_memberships(memberships)
