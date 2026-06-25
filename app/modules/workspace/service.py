from app.modules.workspace.model import WorkspaceMembership
from app.modules.workspace.schema import WorkspaceWithRole


def serialize_workspace_memberships(memberships: list[WorkspaceMembership]) -> list[WorkspaceWithRole]:
    return [
        WorkspaceWithRole(
            id=membership.workspace.id,
            name=membership.workspace.name,
            slug=membership.workspace.slug,
            owner_id=membership.workspace.owner_id,
            created_at=membership.workspace.created_at,
            role=membership.role,
        )
        for membership in memberships
    ]
