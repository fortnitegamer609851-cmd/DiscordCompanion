import discord
import logging

logger = logging.getLogger(__name__)

COMMAND_LOG_CHANNEL_ID = 1393756933957226506

async def log_command_usage(bot, interaction: discord.Interaction, command_name: str, additional_info: str = ""):
    """Log command usage to the designated channel"""
    try:
        log_channel = bot.get_channel(COMMAND_LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(
                title="🔧 Command Used",
                color=discord.Color.blue(),
                timestamp=discord.utils.utcnow()
            )
            
            embed.add_field(
                name="Command", 
                value=f"`/{command_name}`", 
                inline=True
            )
            
            embed.add_field(
                name="User", 
                value=f"{interaction.user.mention} ({interaction.user.name})", 
                inline=True
            )
            
            embed.add_field(
                name="Channel", 
                value=f"{interaction.channel.mention}", 
                inline=True
            )
            
            if additional_info:
                embed.add_field(
                    name="Details", 
                    value=additional_info, 
                    inline=False
                )
            
            embed.set_footer(text=f"User ID: {interaction.user.id}")
            
            await log_channel.send(embed=embed)
            
    except Exception as e:
        logger.error(f"Failed to log command usage: {e}")