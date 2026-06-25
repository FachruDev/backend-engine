from app.modules.users.model import User
from app.modules.users.schema import UserWithMemberships, WorkspaceMembershipRead


def serialize_user_with_memberships(user: User) -> UserWithMemberships:
    return UserWithMemberships(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        created_at=user.created_at,
        memberships=[
            WorkspaceMembershipRead(
                workspace_id=membership.workspace.id,
                workspace_name=membership.workspace.name,
                workspace_slug=membership.workspace.slug,
                role=membership.role,
            )
            for membership in user.memberships
        ],
    )
