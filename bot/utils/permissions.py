import discord
import logging

logger = logging.getLogger(__name__)

MODERATOR_ROLE_ID = 1393754910088101958

def has_moderator_role(user: discord.Member) -> bool:
    """Check if a user has the moderator role"""
    try:
        # Check if user has the specific moderator role
        for role in user.roles:
            if role.id == MODERATOR_ROLE_ID:
                return True
        
        # Also check if user is guild owner
        if user.guild.owner_id == user.id:
            return True
        
        # Check if user has administrator permission
        if user.guild_permissions.administrator:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f'Error checking moderator role: {e}')
        return False

def has_permission(user: discord.Member, permission: str) -> bool:
    """Check if a user has a specific permission"""
    try:
        # First check if they have moderator role
        if has_moderator_role(user):
            return True
        
        # Check specific permission
        permissions = user.guild_permissions
        return getattr(permissions, permission, False)
        
    except Exception as e:
        logger.error(f'Error checking permission {permission}: {e}')
        return False

def is_moderator_or_higher(user: discord.Member) -> bool:
    """Check if user is moderator or has higher permissions"""
    return has_moderator_role(user)

def can_moderate_member(moderator: discord.Member, target: discord.Member) -> bool:
    """Check if moderator can moderate the target member"""
    try:
        # Check if moderator has permission
        if not has_moderator_role(moderator):
            return False
        
        # Check role hierarchy
        if target.top_role >= moderator.top_role and moderator.guild.owner_id != moderator.id:
            return False
        
        # Check if target is guild owner
        if target.guild.owner_id == target.id:
            return False
        
        return True
        
    except Exception as e:
        logger.error(f'Error checking moderation permissions: {e}')
        return False
