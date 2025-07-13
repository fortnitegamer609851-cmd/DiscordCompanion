import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.welcome_channel_id = 1393737919121854584
        self.custom_wave_emoji = "<:parp_wave:1384992297879470123>"
        self.fallback_wave_emoji = "👋"

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when a new member joins"""
        try:
            # Get the welcome channel
            welcome_channel = self.bot.get_channel(self.welcome_channel_id)
            
            if not welcome_channel:
                logger.error(f'Welcome channel not found: {self.welcome_channel_id}')
                return
            
            # Try to use custom emoji, fallback to standard emoji
            try:
                # Test if custom emoji is available
                wave_emoji = self.custom_wave_emoji
                # If we can't use custom emoji, it will raise an error when sending
            except:
                wave_emoji = self.fallback_wave_emoji
            
            # Create welcome message
            welcome_message = f"{wave_emoji} Welcome to **Pennsylvania State Roleplay** {member.mention}, we hope you enjoy your stay here!"
            
            # Send welcome message
            await welcome_channel.send(welcome_message)
            logger.info(f'Welcome message sent for {member.name} ({member.id})')
            
        except discord.Forbidden:
            logger.error(f'No permission to send message in welcome channel')
        except discord.HTTPException as e:
            logger.error(f'HTTP error sending welcome message: {e}')
            # Try with fallback emoji
            try:
                fallback_message = f"{self.fallback_wave_emoji} Welcome to **Pennsylvania State Roleplay** {member.mention}, we hope you enjoy your stay here!"
                await welcome_channel.send(fallback_message)
            except Exception as fallback_error:
                logger.error(f'Failed to send fallback welcome message: {fallback_error}')
        except Exception as e:
            logger.error(f'Error sending welcome message: {e}')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Log when a member leaves"""
        logger.info(f'Member left: {member.name} ({member.id})')

async def setup(bot):
    await bot.add_cog(WelcomeCog(bot))
