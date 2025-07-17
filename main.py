import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv
import logging
# from keep_alive import keep_alive  # Commented out for Render, uncomment if needed
from bot.cogs.blacklist import blacklisted_users  # shared global blacklist set

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    logger.error("DISCORD_TOKEN environment variable not set!")
    exit(1)  # Stop running if token is missing

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Global check for all slash commands
async def global_blacklist_check(interaction: discord.Interaction) -> bool:
    if interaction.user.id in blacklisted_users:
        await interaction.response.send_message(
            "<:parp_caution:1393980985950998769> You have been blacklisted from using this bot.",
            ephemeral=True
        )
        return False
    return True

# ✅ Attach global check
bot.tree.interaction_check = global_blacklist_check

async def load_cogs():
    for cog in [
        'bot.cogs.welcome',
        'bot.cogs.moderation',
        'bot.cogs.member_count',
        'bot.cogs.messaging',
        'bot.cogs.infraction',
        'bot.cogs.suggestions',
        'bot.cogs.promote',
        'bot.cogs.topicc',
        'bot.cogs.session',
        'bot.cogs.blacklist',
        'bot.cogs.review'
    ]:
        try:
            await bot.load_extension(cog)
            logger.info(f"Loaded {cog}")
        except Exception as e:
            logger.error(f"Cog load failed {cog}: {e}")

@bot.event
async def on_ready():
    logger.info(f"{bot.user} connected; in {len(bot.guilds)} guilds")
    await asyncio.sleep(2)
    try:
        guild = discord.Object(id=1369403919293485188)
        synced = await bot.tree.sync(guild=guild)
        logger.info(f"Synced {len(synced)} guild cmds")
        synced_glob = await bot.tree.sync()
        logger.info(f"Synced {len(synced_glob)} global cmds")
    except Exception as e:
        logger.error(f"Sync failed: {e}")

async def main():
    # keep_alive()  # Commented out for Render compatibility; uncomment if you want to keep it
    await load_cogs()
    try:
        await bot.start(TOKEN)
    except Exception as e:
        logger.error(f"Bot start failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
