from fastapi import APIRouter, Depends

from app.modules.auth.dependency import get_current_user
from app.modules.users.model import User
from app.modules.users.schema import UserWithMemberships
from app.modules.users.service import serialize_user_with_memberships

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserWithMemberships)
def read_current_user(current_user: User = Depends(get_current_user)) -> UserWithMemberships:
    return serialize_user_with_memberships(current_user)
