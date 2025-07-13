
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import asyncio
import logging
from bot.utils.permissions import has_moderator_role

logger = logging.getLogger(__name__)

class SessionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_key = None  # You'll need to set this in your .env file
        
    async def get_server_data(self):
        """Fetch server data from ERLC API"""
        if not self.server_key:
            return None
            
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.policeroleplay.community/v1/server/{self.server_key}"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception as e:
            logger.error(f"Failed to fetch server data: {e}")
            return None

    @app_commands.command(name='sessions', description='View Pennsylvania State Roleplay session information')
    async def sessions(self, interaction: discord.Interaction):
        """Display session information for Pennsylvania State Roleplay"""
        # Check if user is authorized
        if interaction.user.id != 1121609529868681337:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Create the main embed with the PA Sessions header
        embed = discord.Embed(
            title="",
            color=0x1e40af,  # Blue color matching the PA theme
            timestamp=discord.utils.utcnow()
        )
        
        # Set the banner image - using the Pennsylvania Sessions banner
        embed.set_image(url="https://i.imgur.com/your-pa-sessions-banner.png")  # You'll need to upload the 2nd image and replace this URL
        
        # Add Pennsylvania State Roleplay Sessions description
        embed.add_field(
            name="🏛️ Pennsylvania State Roleplay Sessions",
            value="Pennsylvania State Roleplay offers the most immersive & realistic roleplay experience out there. From our professional moderation team to our advanced liveries and features we bring.\n\nReact the button below to be pinged for sessions.",
            inline=False
        )
        
        # Fetch server data
        server_data = await self.get_server_data()
        
        if server_data:
            # Server Status section
            player_count = server_data.get('CurrentPlayers', 0)
            max_players = server_data.get('MaxPlayers', 40)
            queue_count = server_data.get('JoinQueue', 0)
            moderating_count = len([staff for staff in server_data.get('Staff', []) if staff.get('Permission') in ['Owner', 'Admin', 'Moderator']])
            
            embed.add_field(
                name="📊 Server Status",
                value=f"**Playercount:** {player_count}/{max_players}\n**Queue Count:** {queue_count}\n**Currently Moderating:** {moderating_count}",
                inline=True
            )
            
            # Last Updated
            embed.add_field(
                name="🕒 Last Updated",
                value="Just now",
                inline=True
            )
        else:
            # Fallback if API is unavailable
            embed.add_field(
                name="📊 Server Status",
                value="**Playercount:** 0/40\n**Queue Count:** 0\n**Currently Moderating:** 0",
                inline=True
            )
            
            embed.add_field(
                name="🕒 Last Updated",
                value="12 seconds ago",
                inline=True
            )
        
        # Session Role section
        embed.add_field(
            name="🎭 Session Role",
            value="Click the button below to get notified when sessions start!",
            inline=False
        )
        
        # Set footer with Pennsylvania branding - using the 3rd image
        embed.set_footer(
            text="Pennsylvania State Roleplay",
            icon_url="https://i.imgur.com/your-pa-logo.png"  # You'll need to upload the 3rd image and replace this URL
        )
        
        # Create view with session ping button
        view = SessionView()
        
        await interaction.followup.send(embed=embed, view=view)
        
        # Fixed logging call
        try:
            from bot.utils.command_logger import log_command_usage
            await log_command_usage(interaction, 'sessions')
        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")

    @app_commands.command(name='announce_session', description='Announce a new session (Staff Only)')
    @app_commands.describe(message="Custom message for the session announcement")
    async def announce_session(self, interaction: discord.Interaction, message: str = None):
        """Announce a new session and ping session role"""
        
        # Check permissions
        if not has_moderator_role(interaction.user, interaction.guild):
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)
            return
        
        SESSION_ROLE_ID = 1234567890123456789  # Replace with actual role ID
        session_role = interaction.guild.get_role(SESSION_ROLE_ID)
        
        if not session_role:
            await interaction.response.send_message("❌ Session role not found.", ephemeral=True)
            return
        
        # Create announcement embed
        announce_embed = discord.Embed(
            title="🚨 Session Starting!",
            description=message or "A new Pennsylvania State Roleplay session is starting! Join now!",
            color=0x1e40af,
            timestamp=discord.utils.utcnow()
        )
        
        announce_embed.set_thumbnail(url="https://i.imgur.com/your-pa-logo.png")  # Replace with actual logo
        announce_embed.set_footer(text="Pennsylvania State Roleplay")
        
        await interaction.response.send_message(
            content=f"{session_role.mention}",
            embed=announce_embed
        )
        
        # Fixed logging call
        try:
            from bot.utils.command_logger import log_command_usage
            await log_command_usage(interaction, 'announce_session', f'Message: {message or "Default announcement"}')
        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")

class SessionView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='🔔 Get Session Notifications', style=discord.ButtonStyle.primary, custom_id='session_notifications')
    async def session_notifications(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle session notifications for the user"""
        
        # Define the session role ID (you'll need to create this role)
        SESSION_ROLE_ID = 1234567890123456789  # Replace with actual role ID
        
        session_role = interaction.guild.get_role(SESSION_ROLE_ID)
        
        if not session_role:
            await interaction.response.send_message("❌ Session role not found. Please contact an administrator.", ephemeral=True)
            return
        
        if session_role in interaction.user.roles:
            # Remove role
            await interaction.user.remove_roles(session_role)
            await interaction.response.send_message("🔕 You will no longer receive session notifications.", ephemeral=True)
        else:
            # Add role
            await interaction.user.add_roles(session_role)
            await interaction.response.send_message("🔔 You will now receive notifications when sessions start!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SessionsCog(bot))
