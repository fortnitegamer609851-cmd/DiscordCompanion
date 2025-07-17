import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.permissions import has_moderator_role
from bot.utils.case_tracker import CaseTracker
from bot.utils.command_logger import log_command_usage
import datetime

logger = logging.getLogger(__name__)

LIMITED_ROLE_ID = 1393737607653097614
LOCK_ROLE_ID = 1393754910088101958  # Role allowed to use /lock command
COMMUNITY_MEMBER_ROLE_ID = 1393737552502194238  # Community member role to lock/unlock

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.case_tracker = CaseTracker()
        self.checkmark_emoji = "<:checkmark:1384993844671545506>"
        self.fallback_checkmark = "✅"
        self.user_points = {}
        self.warn_points = 2
        self.ban_threshold = 12

    def get_checkmark_emoji(self):
        try:
            return self.checkmark_emoji
        except:
            return self.fallback_checkmark

    def add_points(self, user_id: int, points: int) -> int:
        current = self.user_points.get(user_id, 0)
        new_total = current + points
        self.user_points[user_id] = new_total
        return new_total

    def remove_points(self, user_id: int, points: int) -> int:
        current = self.user_points.get(user_id, 0)
        new_total = max(current - points, 0)
        self.user_points[user_id] = new_total
        return new_total

    async def send_dm(self, member: discord.Member, action: str, reason: str):
        try:
            await member.send(f"You have been **{action}** for: {reason}")
        except discord.Forbidden:
            pass

    def is_limited_moderator(self, member: discord.Member) -> bool:
        return any(role.id == LIMITED_ROLE_ID for role in member.roles)

    def can_execute(self, interaction: discord.Interaction, limited_only: bool = False) -> bool:
        if self.is_limited_moderator(interaction.user):
            return limited_only
        return has_moderator_role(interaction.user)

    def can_lock(self, member: discord.Member) -> bool:
        return any(role.id == LOCK_ROLE_ID for role in member.roles)

    @app_commands.command(name='warn', description='Warn a member (adds 2 points)')
    @app_commands.describe(member='Member to warn', reason='Reason for the warning')
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not self.can_execute(interaction, limited_only=True):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message('I do not have permission to ban members.', ephemeral=True)
            return

        total_points = self.add_points(member.id, self.warn_points)
        await self.send_dm(member, "warned", reason)
        emoji = self.get_checkmark_emoji()
        msg = f"{emoji} {member.mention} has been warned for {reason}. They now have {total_points}/12 points."

        if total_points >= self.ban_threshold and not self.is_limited_moderator(interaction.user):
            try:
                await member.ban(reason=f"Reached {total_points} points (auto-ban)")
                msg += f"\n🚨 {member.mention} has reached {total_points} points and has been permanently banned."
            except discord.Forbidden:
                msg += f"\n⚠️ I do not have permission to ban {member.mention}."
            except Exception as e:
                msg += f"\n⚠️ Failed to ban {member.mention}: {e}"

        await interaction.response.send_message(msg)

    @app_commands.command(name='kick', description='Kick a member')
    @app_commands.describe(member='Member to kick', reason='Reason for the kick')
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        if not self.can_execute(interaction, limited_only=True):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.kick_members:
            await interaction.response.send_message('I do not have permission to kick members.', ephemeral=True)
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message('I cannot kick this member due to role hierarchy.', ephemeral=True)
            return

        try:
            await self.send_dm(member, "kicked", reason)
            await member.kick(reason=reason)
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} {member.mention} has been kicked for: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message('Failed to kick member: insufficient permissions.', ephemeral=True)

    @app_commands.command(name='removepoints', description='Remove infraction points from a member')
    @app_commands.describe(member='Member to remove points from', amount='Amount of points to remove')
    async def removepoints(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if amount < 1:
            await interaction.response.send_message('Amount must be at least 1.', ephemeral=True)
            return

        new_total = self.remove_points(member.id, amount)
        emoji = self.get_checkmark_emoji()
        await interaction.response.send_message(f"{emoji} Removed {amount} points from {member.mention}. They now have {new_total}/12 points.", ephemeral=True)

    @app_commands.command(name='points', description='Check the points of a member')
    @app_commands.describe(member='The member to check points for')
    async def points(self, interaction: discord.Interaction, member: discord.Member):
        points = self.user_points.get(member.id, 0)
        emoji = self.get_checkmark_emoji()
        await interaction.response.send_message(f"{emoji} {member.mention} has {points}/12 points.", ephemeral=True)

    @app_commands.command(name='ban', description='Ban a member')
    @app_commands.describe(member='Member to ban', reason='Reason for the ban', delete_days='Days of messages to delete (0-7)')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str, delete_days: int = 0):
        if not self.can_execute(interaction):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if delete_days < 0 or delete_days > 7:
            await interaction.response.send_message('Delete days must be between 0 and 7.', ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.ban_members:
            await interaction.response.send_message('I do not have permission to ban members.', ephemeral=True)
            return

        if member.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message('I cannot ban this member due to role hierarchy.', ephemeral=True)
            return

        try:
            await self.send_dm(member, "banned", reason)
            await member.ban(reason=reason, delete_message_days=delete_days)
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} {member.mention} has been banned for: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message('Failed to ban member: insufficient permissions.', ephemeral=True)

    @app_commands.command(name='softban', description='Softban a member')
    @app_commands.describe(member='Member to softban', reason='Reason for the softban', delete_days='Days of messages to delete (0-7)')
    async def softban(self, interaction: discord.Interaction, member: discord.Member, reason: str, delete_days: int = 1):
        if not self.can_execute(interaction):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if delete_days < 0 or delete_days > 7:
            await interaction.response.send_message('Delete days must be between 0 and 7.', ephemeral=True)
            return

        try:
            await self.send_dm(member, "softbanned", reason)
            await member.ban(reason=reason, delete_message_days=delete_days)
            await interaction.guild.unban(discord.Object(id=member.id))
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} {member.mention} has been softbanned for: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message('Failed to softban member: insufficient permissions.', ephemeral=True)

    @app_commands.command(name='mute', description='Mute (timeout) a member')
    @app_commands.describe(member='Member to mute', duration='Duration in minutes', reason='Reason for the mute')
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str):
        if not self.can_execute(interaction):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        if duration < 1 or duration > 40320:
            await interaction.response.send_message('Duration must be between 1 and 40320 minutes.', ephemeral=True)
            return

        if not interaction.guild.me.guild_permissions.moderate_members:
            await interaction.response.send_message('I do not have permission to mute members.', ephemeral=True)
            return

        until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)

        try:
            await self.send_dm(member, f"muted for {duration} minutes", reason)
            await member.timeout(until, reason=reason)
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} {member.mention} has been muted for {duration} minutes. Reason: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message('Failed to mute member: insufficient permissions.', ephemeral=True)

    @app_commands.command(name="lock", description="Lock the current channel")
    async def lock(self, interaction: discord.Interaction):
        if not self.can_lock(interaction.user):
            await interaction.response.send_message("You do not have permission to lock channels.", ephemeral=True)
            return

        role = interaction.guild.get_role(COMMUNITY_MEMBER_ROLE_ID)
        if role is None:
            await interaction.response.send_message("Community member role not found.", ephemeral=True)
            return

        channel = interaction.channel
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = False

        try:
            await channel.set_permissions(role, overwrite=overwrite)
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} This channel has been locked for {role.name}.")
        except Exception as e:
            logger.error(f"Failed to lock channel: {e}")
            await interaction.response.send_message("Failed to lock the channel.", ephemeral=True)

    @app_commands.command(name="unlock", description="Unlock the current channel")
    async def unlock(self, interaction: discord.Interaction):
        if not self.can_lock(interaction.user):
            await interaction.response.send_message("You do not have permission to unlock channels.", ephemeral=True)
            return

        role = interaction.guild.get_role(COMMUNITY_MEMBER_ROLE_ID)
        if role is None:
            await interaction.response.send_message("Community member role not found.", ephemeral=True)
            return

        channel = interaction.channel
        overwrite = channel.overwrites_for(role)
        overwrite.send_messages = None  # Remove overwrite so permissions revert to default

        try:
            await channel.set_permissions(role, overwrite=overwrite)
            await interaction.response.send_message(f"{self.get_checkmark_emoji()} This channel has been unlocked for {role.name}.")
        except Exception as e:
            logger.error(f"Failed to unlock channel: {e}")
            await interaction.response.send_message("Failed to unlock the channel.", ephemeral=True)

    @app_commands.command(name="purge", description="Purge a number of messages from the current channel")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    async def purge(self, interaction: discord.Interaction, amount: int):
        if not any(role.id == LIMITED_ROLE_ID for role in interaction.user.roles):
            await interaction.response.send_message(
                "<:Denied:1370806202094583918> The command has failed", ephemeral=True
            )
            return

        if amount < 1 or amount > 100:
            await interaction.response.send_message(
                "<:Denied:1370806202094583918> The command has failed", ephemeral=True
            )
            return

        try:
            deleted = await interaction.channel.purge(limit=amount)
            await interaction.response.send_message(
                f"<:checkmark:1384993844671545506> Successfully purged {len(deleted)} messages.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Failed to purge messages: {e}")
            await interaction.response.send_message(
                "<:Denied:1370806202094583918> The command has failed", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerationCog(bot))
