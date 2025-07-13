import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.permissions import has_moderator_role
from bot.utils.case_tracker import CaseTracker
from bot.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.case_tracker = CaseTracker()
        self.checkmark_emoji = "<:checkmark:1384993844671545506>"
        self.fallback_checkmark = "✅"

    def get_checkmark_emoji(self):
        """Get checkmark emoji with fallback"""
        try:
            return self.checkmark_emoji
        except:
            return self.fallback_checkmark

    @app_commands.command(name='kick', description='Kick a member from the server')
    @app_commands.describe(member='The member to kick', reason='Reason for the kick')
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided'):
        """Kick a member with case tracking"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Check if bot has permission
            if not interaction.guild.me.guild_permissions.kick_members:
                await interaction.response.send_message('I do not have permission to kick members.', ephemeral=True)
                return
            
            # Check if target is kickable
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message('I cannot kick this member due to role hierarchy.', ephemeral=True)
                return
            
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title='You have been kicked',
                    description=f'You have been kicked from **{interaction.guild.name}**',
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name='Reason', value=reason, inline=False)
                dm_embed.add_field(name='Case Number', value=f'#{case_number}', inline=False)
                dm_embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
                
                await member.send(embed=dm_embed)
                dm_sent = True
            except discord.Forbidden:
                dm_sent = False
            
            # Kick the member
            await member.kick(reason=f'Case #{case_number}: {reason}')
            
            # Save case
            self.case_tracker.save_case(case_number, 'kick', member.id, interaction.user.id, reason)
            
            # Create response embed
            embed = discord.Embed(
                title=f'{self.get_checkmark_emoji()} Member Kicked',
                description=f'**{member.name}** has been kicked from the server.',
                color=discord.Color.orange()
            )
            embed.add_field(name='Case Number', value=f'#{case_number}', inline=True)
            embed.add_field(name='Reason', value=reason, inline=True)
            embed.add_field(name='Moderator', value=interaction.user.mention, inline=True)
            embed.add_field(name='DM Sent', value='Yes' if dm_sent else 'No (DMs disabled)', inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'Member kicked: {member.name} ({member.id}) by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'kick', f'Target: {member.name} | Reason: {reason} | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to kick this member.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error kicking member: {e}')
            await interaction.response.send_message('An error occurred while kicking the member.', ephemeral=True)

    @app_commands.command(name='ban', description='Ban a member from the server')
    @app_commands.describe(member='The member to ban', reason='Reason for the ban', delete_days='Days of messages to delete (0-7)')
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided', delete_days: int = 0):
        """Ban a member with case tracking"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Validate delete_days
            if delete_days < 0 or delete_days > 7:
                await interaction.response.send_message('Delete days must be between 0 and 7.', ephemeral=True)
                return
            
            # Check if bot has permission
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.response.send_message('I do not have permission to ban members.', ephemeral=True)
                return
            
            # Check if target is bannable
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message('I cannot ban this member due to role hierarchy.', ephemeral=True)
                return
            
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title='You have been banned',
                    description=f'You have been banned from **{interaction.guild.name}**',
                    color=discord.Color.red()
                )
                dm_embed.add_field(name='Reason', value=reason, inline=False)
                dm_embed.add_field(name='Case Number', value=f'#{case_number}', inline=False)
                dm_embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
                
                await member.send(embed=dm_embed)
                dm_sent = True
            except discord.Forbidden:
                dm_sent = False
            
            # Ban the member
            await member.ban(reason=f'Case #{case_number}: {reason}', delete_message_days=delete_days)
            
            # Save case
            self.case_tracker.save_case(case_number, 'ban', member.id, interaction.user.id, reason)
            
            # Create response embed
            embed = discord.Embed(
                title=f'{self.get_checkmark_emoji()} Member Banned',
                description=f'**{member.name}** has been banned from the server.',
                color=discord.Color.red()
            )
            embed.add_field(name='Case Number', value=f'#{case_number}', inline=True)
            embed.add_field(name='Reason', value=reason, inline=True)
            embed.add_field(name='Moderator', value=interaction.user.mention, inline=True)
            embed.add_field(name='Messages Deleted', value=f'{delete_days} days', inline=True)
            embed.add_field(name='DM Sent', value='Yes' if dm_sent else 'No (DMs disabled)', inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'Member banned: {member.name} ({member.id}) by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'ban', f'Target: {member.name} | Reason: {reason} | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to ban this member.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error banning member: {e}')
            await interaction.response.send_message('An error occurred while banning the member.', ephemeral=True)

    @app_commands.command(name='softban', description='Softban a member (ban then immediately unban)')
    @app_commands.describe(member='The member to softban', reason='Reason for the softban', delete_days='Days of messages to delete (0-7)')
    async def softban(self, interaction: discord.Interaction, member: discord.Member, reason: str = 'No reason provided', delete_days: int = 1):
        """Softban a member with case tracking"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Validate delete_days
            if delete_days < 0 or delete_days > 7:
                await interaction.response.send_message('Delete days must be between 0 and 7.', ephemeral=True)
                return
            
            # Check if bot has permission
            if not interaction.guild.me.guild_permissions.ban_members:
                await interaction.response.send_message('I do not have permission to ban members.', ephemeral=True)
                return
            
            # Check if target is bannable
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message('I cannot softban this member due to role hierarchy.', ephemeral=True)
                return
            
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title='You have been softbanned',
                    description=f'You have been softbanned from **{interaction.guild.name}**\n(Your messages were deleted but you can rejoin)',
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name='Reason', value=reason, inline=False)
                dm_embed.add_field(name='Case Number', value=f'#{case_number}', inline=False)
                dm_embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
                
                await member.send(embed=dm_embed)
                dm_sent = True
            except discord.Forbidden:
                dm_sent = False
            
            # Softban the member (ban then unban)
            await member.ban(reason=f'Case #{case_number}: {reason}', delete_message_days=delete_days)
            await interaction.guild.unban(member, reason=f'Softban - Case #{case_number}')
            
            # Save case
            self.case_tracker.save_case(case_number, 'softban', member.id, interaction.user.id, reason)
            
            # Create response embed
            embed = discord.Embed(
                title=f'{self.get_checkmark_emoji()} Member Softbanned',
                description=f'**{member.name}** has been softbanned from the server.',
                color=discord.Color.orange()
            )
            embed.add_field(name='Case Number', value=f'#{case_number}', inline=True)
            embed.add_field(name='Reason', value=reason, inline=True)
            embed.add_field(name='Moderator', value=interaction.user.mention, inline=True)
            embed.add_field(name='Messages Deleted', value=f'{delete_days} days', inline=True)
            embed.add_field(name='DM Sent', value='Yes' if dm_sent else 'No (DMs disabled)', inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'Member softbanned: {member.name} ({member.id}) by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'softban', f'Target: {member.name} | Reason: {reason} | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to softban this member.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error softbanning member: {e}')
            await interaction.response.send_message('An error occurred while softbanning the member.', ephemeral=True)

    @app_commands.command(name='mute', description='Mute a member (timeout)')
    @app_commands.describe(member='The member to mute', duration='Duration in minutes', reason='Reason for the mute')
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str = 'No reason provided'):
        """Mute a member with case tracking"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Validate duration
            if duration < 1 or duration > 40320:  # Max 28 days
                await interaction.response.send_message('Duration must be between 1 and 40320 minutes (28 days).', ephemeral=True)
                return
            
            # Check if bot has permission
            if not interaction.guild.me.guild_permissions.moderate_members:
                await interaction.response.send_message('I do not have permission to timeout members.', ephemeral=True)
                return
            
            # Check if target is muteable
            if member.top_role >= interaction.guild.me.top_role:
                await interaction.response.send_message('I cannot mute this member due to role hierarchy.', ephemeral=True)
                return
            
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Try to DM the user first
            try:
                dm_embed = discord.Embed(
                    title='You have been muted',
                    description=f'You have been muted in **{interaction.guild.name}**',
                    color=discord.Color.orange()
                )
                dm_embed.add_field(name='Duration', value=f'{duration} minutes', inline=False)
                dm_embed.add_field(name='Reason', value=reason, inline=False)
                dm_embed.add_field(name='Case Number', value=f'#{case_number}', inline=False)
                dm_embed.add_field(name='Moderator', value=interaction.user.mention, inline=False)
                
                await member.send(embed=dm_embed)
                dm_sent = True
            except discord.Forbidden:
                dm_sent = False
            
            # Mute the member
            import datetime
            until = discord.utils.utcnow() + datetime.timedelta(minutes=duration)
            await member.timeout(until, reason=f'Case #{case_number}: {reason}')
            
            # Save case
            self.case_tracker.save_case(case_number, 'mute', member.id, interaction.user.id, f'{reason} (Duration: {duration} minutes)')
            
            # Create response embed
            embed = discord.Embed(
                title=f'{self.get_checkmark_emoji()} Member Muted',
                description=f'**{member.name}** has been muted.',
                color=discord.Color.orange()
            )
            embed.add_field(name='Case Number', value=f'#{case_number}', inline=True)
            embed.add_field(name='Duration', value=f'{duration} minutes', inline=True)
            embed.add_field(name='Reason', value=reason, inline=True)
            embed.add_field(name='Moderator', value=interaction.user.mention, inline=True)
            embed.add_field(name='DM Sent', value='Yes' if dm_sent else 'No (DMs disabled)', inline=True)
            
            await interaction.response.send_message(embed=embed)
            logger.info(f'Member muted: {member.name} ({member.id}) by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'mute', f'Target: {member.name} | Duration: {duration}min | Reason: {reason} | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to mute this member.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error muting member: {e}')
            await interaction.response.send_message('An error occurred while muting the member.', ephemeral=True)

    @app_commands.command(name='purge', description='Delete multiple messages')
    @app_commands.describe(amount='Number of messages to delete (1-100)')
    async def purge(self, interaction: discord.Interaction, amount: int):
        """Purge messages with case tracking"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Validate amount
            if amount < 1 or amount > 100:
                await interaction.response.send_message('Amount must be between 1 and 100.', ephemeral=True)
                return
            
            # Check if bot has permission
            if not interaction.guild.me.guild_permissions.manage_messages:
                await interaction.response.send_message('I do not have permission to manage messages.', ephemeral=True)
                return
            
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Defer response since this might take a while
            await interaction.response.defer()
            
            # Purge messages
            deleted = await interaction.channel.purge(limit=amount)
            deleted_count = len(deleted)
            
            # Save case
            self.case_tracker.save_case(case_number, 'purge', interaction.channel.id, interaction.user.id, f'Deleted {deleted_count} messages')
            
            # Create response embed
            embed = discord.Embed(
                title=f'{self.get_checkmark_emoji()} Messages Purged',
                description=f'Successfully deleted **{deleted_count}** messages.',
                color=discord.Color.green()
            )
            embed.add_field(name='Case Number', value=f'#{case_number}', inline=True)
            embed.add_field(name='Channel', value=interaction.channel.mention, inline=True)
            embed.add_field(name='Moderator', value=interaction.user.mention, inline=True)
            
            await interaction.followup.send(embed=embed)
            logger.info(f'Messages purged: {deleted_count} in {interaction.channel.name} by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'purge', f'Deleted: {deleted_count} messages | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.followup.send('I do not have permission to delete messages in this channel.')
        except Exception as e:
            logger.error(f'Error purging messages: {e}')
            await interaction.followup.send('An error occurred while purging messages.')

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
