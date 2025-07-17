import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.permissions import has_moderator_role
from bot.utils.command_logger import log_command_usage
import re

logger = logging.getLogger(__name__)

class MessagingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def contains_ping(self, message: str):
        # Check if the message contains @everyone or @here
        return re.search(r'@everyone|@here', message, re.IGNORECASE) is not None

    @app_commands.command(name='say', description='Send a message as the bot')
    @app_commands.describe(message='The message to send')
    async def say(self, interaction: discord.Interaction, message: str):
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        # Prevent @everyone and @here
        if self.contains_ping(message):
            await interaction.response.send_message('<:Denied:1370806202094583918>  You cannot use `@everyone` or `@here` in your message.', ephemeral=True)
            return

        try:
            if not interaction.channel.permissions_for(interaction.guild.me).send_messages:
                await interaction.response.send_message('I do not have permission to send messages in this channel.', ephemeral=True)
                return

            await interaction.channel.send(message)
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
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        # Prevent @everyone and @here
        if self.contains_ping(message):
            await interaction.response.send_message('<:Denied:1370806202094583918>  You cannot use `@everyone` or `@here` in your message.', ephemeral=True)
            return

        try:
            await user.send(message)
            confirm_embed = discord.Embed(
                title='<:checkmark:1384993844671545506> DM Sent Successfully',
                description=f'Your message has been sent to {user.mention}',
                color=discord.Color.green()
            )
            confirm_embed.add_field(name='Message', value=message, inline=False)
            confirm_embed.add_field(name='Recipient', value=f'{user.name}#{user.discriminator}', inline=False)
            await interaction.response.send_message(embed=confirm_embed, ephemeral=True)
            logger.info(f'DM sent by {interaction.user.name} to {user.name}: {message[:50]}...')
            await log_command_usage(self.bot, interaction, 'dm', f'To: {user.name} | Message: {message[:50]}...')
        except discord.Forbidden:
            error_embed = discord.Embed(
                title='<:Denied:1370806202094583918>  DM Failed',
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
        if not has_moderator_role(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return

        # Prevent @everyone and @here
        if self.contains_ping(message):
            await interaction.response.send_message('<:Denied:1370806202094583918>  You cannot use `@everyone` or `@here` in your message.', ephemeral=True)
            return

        try:
            color_map = {
                'red': discord.Color.red(),
                'green': discord.Color.green(),
                'blue': discord.Color.blue(),
                'yellow': discord.Color.yellow(),
                'purple': discord.Color.purple(),
                'orange': discord.Color.orange()
            }
            embed_color = color_map.get(color.lower(), discord.Color.blue())

            embed = discord.Embed(title=title, description=message, color=embed_color)
            embed.set_footer(text=f'Announced by {interaction.user.name}', icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

            await interaction.channel.send(embed=embed)
            await interaction.response.send_message(f'Announcement sent successfully!', ephemeral=True)
            logger.info(f'Announcement sent by {interaction.user.name} in {interaction.channel.name}: {title}')
            await log_command_usage(self.bot, interaction, 'announce', f'Title: {title} | Color: {color}')
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to send messages in this channel.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error sending announcement: {e}')
            await interaction.response.send_message('An error occurred while sending the announcement.', ephemeral=True)

    @app_commands.command(name='mentionspam', description='Mention a user multiple times in separate messages (authorized user only)')
    @app_commands.describe(user='The user to mention', times='Number of times to mention in separate messages')
    async def mentionspam(self, interaction: discord.Interaction, user: discord.Member, times: int):
        allowed_user_id = 1121609529868681337

        if interaction.user.id != allowed_user_id:
            await interaction.response.send_message('<:Denied:1370806202094583918>  You are not authorized to use this command.', ephemeral=True)
            return

        if times <= 0 or times > 25:
            await interaction.response.send_message('<:Denied:1370806202094583918>  Message count must be between 1 and 25.', ephemeral=True)
            return

        try:
            await interaction.response.send_message(f'✅ Spamming {user.mention} with {times} messages.', ephemeral=True)
            for _ in range(times):
                await interaction.channel.send(f'{user.mention}')
            logger.info(f'{interaction.user} spam mentioned {user} with {times} separate messages')
            await log_command_usage(self.bot, interaction, 'mentionspam', f'Sent {times} messages tagging {user}')
        except Exception as e:
            logger.error(f'Error in mentionspam: {e}')
            await interaction.followup.send('<:Denied:1370806202094583918>  An error occurred while trying to mention spam.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(MessagingCog(bot))
