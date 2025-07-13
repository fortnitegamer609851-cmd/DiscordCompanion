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
        self.custom_person_emoji = "<:flst_person:1384991790838448209>"
        self.fallback_person_emoji = "👤"

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send welcome message when a new member joins"""
        try:
            # Get the welcome channel
            welcome_channel = self.bot.get_channel(self.welcome_channel_id)
            
            if not welcome_channel:
                logger.error(f'Welcome channel not found: {self.welcome_channel_id}')
                return
            
            # Try to use custom emojis, fallback to standard emojis
            try:
                wave_emoji = self.custom_wave_emoji
                person_emoji = self.custom_person_emoji
            except:
                wave_emoji = self.fallback_wave_emoji
                person_emoji = self.fallback_person_emoji
            
            # Get member count
            member_count = member.guild.member_count
            
            # Create welcome message with member count
            welcome_message = f"{wave_emoji} Welcome to **Pennsylvania State Roleplay** {member.mention}, we hope you enjoy your stay here! We now have {person_emoji} {member_count} members."
            
            # Send welcome message
            await welcome_channel.send(welcome_message)
            logger.info(f'Welcome message sent for {member.name} ({member.id})')
            
        except discord.Forbidden:
            logger.error(f'No permission to send message in welcome channel')
        except discord.HTTPException as e:
            logger.error(f'HTTP error sending welcome message: {e}')
            # Try with fallback emojis
            try:
                fallback_message = f"{self.fallback_wave_emoji} Welcome to **Pennsylvania State Roleplay** {member.mention}, we hope you enjoy your stay here! We now have {self.fallback_person_emoji} {member_count} members."
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
