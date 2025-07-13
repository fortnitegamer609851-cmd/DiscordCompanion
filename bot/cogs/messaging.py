import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.permissions import has_moderator_role
from bot.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

class MessagingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='say', description='Send a message as the bot')
    @app_commands.describe(message='The message to send')
    async def say(self, interaction: discord.Interaction, message: str):
        """Send a message as the bot without replying"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Check if bot has permission to send messages
            if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message('I do not have permission to send messages in this channel.', ephemeral=True)
                return
            
            # Send the message
            await interaction.channel.send(message)
            
            # Confirm to the user
            await interaction.response.send_message(f'Message sent successfully!', ephemeral=True)
            logger.info(f'Say command used by {interaction.user.name} in {interaction.channel.name}: {message[:50]}...')
            await log_command_usage(self.bot, interaction, 'say', f'Message: {message[:50]}...')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to send messages in this channel.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error sending message: {e}')
            await interaction.response.send_message('An error occurred while sending the message.', ephemeral=True)

    @app_commands.command(name='dm', description='Send a direct message to a user')
    @app_commands.describe(user='The user to send a DM to', message='The message to send')
    async def dm(self, interaction: discord.Interaction, user: discord.Member, message: str):
        """Send a direct message to a user"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Send the DM as a plain message (looks like normal person typing)
            await user.send(message)
            
            # Confirm to the moderator
            confirm_embed = discord.Embed(
                title='✅ DM Sent Successfully',
                description=f'Your message has been sent to {user.mention}',
                color=discord.Color.green()
            )
            confirm_embed.add_field(name='Message', value=message, inline=False)
            confirm_embed.add_field(name='Recipient', value=f'{user.name}#{user.discriminator}', inline=False)
            
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            logger.info(f'DM sent by {interaction.user.name} to {user.name}: {message[:50]}...')
            await log_command_usage(self.bot, interaction, 'dm', f'To: {user.name} | Message: {message[:50]}...')
            
        except discord.Forbidden:
            # User has DMs disabled or blocked the bot
            error_embed = discord.Embed(
                title='❌ DM Failed',
                description=f'Could not send DM to {user.mention}',
                color=discord.Color.red()
            )
            error_embed.add_field(name='Possible Reasons', value='• User has DMs disabled\n• User has blocked the bot\n• User is not accepting DMs from server members', inline=False)
            error_embed.add_field(name='Attempted Message', value=message, inline=False)
            
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            logger.warning(f'Failed to send DM to {user.name}: DMs disabled or blocked')
            
        except discord.HTTPException as e:
            logger.error(f'HTTP error sending DM: {e}')
            await interaction.response.send_message('An HTTP error occurred while sending the DM. The message may be too long or contain invalid content.', ephemeral=True)
            
        except Exception as e:
            logger.error(f'Error sending DM: {e}')
            await interaction.response.send_message('An unexpected error occurred while sending the DM.', ephemeral=True)

    @app_commands.command(name='announce', description='Send an announcement with embed')
    @app_commands.describe(
        title='Title of the announcement',
        message='The announcement message',
        color='Color for the embed (red, green, blue, yellow, purple, orange)'
    )
    async def announce(self, interaction: discord.Interaction, title: str, message: str, color: str = 'blue'):
        """Send an announcement with embed formatting"""
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Color mapping
            color_map = {
                'red': discord.Color.red(),
                'green': discord.Color.green(),
                'blue': discord.Color.blue(),
                'yellow': discord.Color.yellow(),
                'purple': discord.Color.purple(),
                'orange': discord.Color.orange()
            }
            
            embed_color = color_map.get(color.lower(), discord.Color.blue())
            
            # Create announcement embed
            embed = discord.Embed(
                title=title,
                description=message,
                color=embed_color
            )
            embed.set_footer(text=f'Announced by {interaction.user.name}', icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
            
            # Send the announcement
            await interaction.channel.send(embed=embed)
            
            # Confirm to the user
            await interaction.response.send_message(f'Announcement sent successfully!', ephemeral=True)
            logger.info(f'Announcement sent by {interaction.user.name} in {interaction.channel.name}: {title}')
            await log_command_usage(self.bot, interaction, 'announce', f'Title: {title} | Color: {color}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to send messages in this channel.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error sending announcement: {e}')
            await interaction.response.send_message('An error occurred while sending the announcement.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(MessagingCog(bot))
