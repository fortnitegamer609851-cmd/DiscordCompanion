import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import logging
from keep_alive import keep_alive

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot configuration
TOKEN = os.getenv('DISCORD_TOKEN')
WELCOME_CHANNEL_ID = 1393737919121854584
MODERATOR_ROLE_ID = 1393754910088101958

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')
    
    # Sync slash commands immediately after bot ready
    await asyncio.sleep(2)  # Wait for Discord to be fully ready
    
    try:
        guild_id = 1369403919293485188  # Pennsylvania State Roleplay server ID
        guild = discord.Object(id=guild_id)
        
        # Log all available commands
        all_commands = bot.tree.get_commands()
        logger.info(f'Available commands: {[cmd.name for cmd in all_commands]}')
        
        # Sync to guild first (faster updates)
        synced_guild = await bot.tree.sync(guild=guild)
        logger.info(f'Synced {len(synced_guild)} command(s) to guild {guild_id}')
        
        # Also sync globally for backup
        synced_global = await bot.tree.sync()
        logger.info(f'Synced {len(synced_global)} command(s) globally')
        
        logger.info('All commands synced successfully!')
        
    except Exception as e:
        logger.error(f'Failed to sync commands: {e}')

@bot.event
async def on_guild_join(guild):
    logger.info(f'Joined guild: {guild.name} (ID: {guild.id})')

@bot.event
async def on_guild_remove(guild):
    logger.info(f'Left guild: {guild.name} (ID: {guild.id})')

# Load cogs
async def load_cogs():
    cogs = [
        'bot.cogs.welcome',
        'bot.cogs.moderation',
        'bot.cogs.member_count',
        'bot.cogs.messaging'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f'Loaded cog: {cog}')
        except Exception as e:
            logger.error(f'Failed to load cog {cog}: {e}')

# Basic commands
@bot.tree.command(name='ping', description='Check bot latency')
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f'Pong! Latency: {latency}ms')

@bot.tree.command(name='help', description='Get help with bot commands')
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title='Pennsylvania State Roleplay Bot Help',
        description='Here are the available commands:',
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name='General Commands',
        value='`/ping` - Check bot latency\n`/help` - Show this help message\n`/member_count` - Show current member count',
        inline=False
    )
    
    embed.add_field(
        name='Moderation Commands (Staff Only)',
        value='`/kick` - Kick a member\n`/mute` - Mute a member\n`/ban` - Ban a member\n`/softban` - Softban a member\n`/purge` - Delete multiple messages',
        inline=False
    )
    
    embed.add_field(
        name='Messaging Commands (Staff Only)',
        value='`/say` - Send a message as the bot\n`/dm` - Send a direct message to a user',
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name='sync', description='Force sync commands (Owner only)')
async def sync_command(interaction: discord.Interaction):
    """Manually sync slash commands"""
    if interaction.user.id != interaction.guild.owner_id:
        await interaction.response.send_message("❌ Only the server owner can use this command.", ephemeral=True)
        return
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        # Sync to current guild
        synced = await bot.tree.sync(guild=interaction.guild)
        # Also sync globally  
        synced_global = await bot.tree.sync()
        
        await interaction.followup.send(
            f"✅ Successfully synced {len(synced)} commands to this server and {len(synced_global)} commands globally.",
            ephemeral=True
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Failed to sync commands: {str(e)}", ephemeral=True)

async def main():
    # Keep the bot alive
    keep_alive()
    
    # Load cogs before starting
    await load_cogs()
    
    # Start the bot
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.error(f'Failed to start bot: {e}')

if __name__ == '__main__':
    asyncio.run(main())
