import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.command_logger import log_command_usage

logger = logging.getLogger(__name__)

class SuggestionView(discord.ui.View):
    def __init__(self, suggestion_text: str, author: discord.Member):
        super().__init__(timeout=None)
        self.suggestion_text = suggestion_text
        self.author = author
        self.upvotes = 0
        self.downvotes = 0
        self.voted_users = set()
        
    @discord.ui.button(emoji='<:checkmark:1384993844671545506>', style=discord.ButtonStyle.success)
    async def upvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("You have already voted on this suggestion!", ephemeral=True)
            return
            
        self.upvotes += 1
        self.voted_users.add(interaction.user.id)
        
        # Update the embed
        await self.update_embed(interaction)
        
    @discord.ui.button(emoji='<:Denied:1370806202094583918>', style=discord.ButtonStyle.danger)
    async def downvote(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted_users:
            await interaction.response.send_message("You have already voted on this suggestion!", ephemeral=True)
            return
            
        self.downvotes += 1
        self.voted_users.add(interaction.user.id)
        
        # Update the embed
        await self.update_embed(interaction)
        
    async def update_embed(self, interaction: discord.Interaction):
        # Calculate percentages
        total_votes = self.upvotes + self.downvotes
        upvote_percentage = (self.upvotes / total_votes * 100) if total_votes > 0 else 0
        downvote_percentage = (self.downvotes / total_votes * 100) if total_votes > 0 else 0
        
        # Create updated embed
        embed = discord.Embed(
            title="New Suggestion!",
            color=0x2F3136,
            description=""
        )
        
        # Add author info
        embed.set_author(name=self.author.display_name, icon_url=self.author.avatar.url if self.author.avatar else None)
        
        # Add suggestion text
        embed.add_field(
            name="Suggestion:",
            value=self.suggestion_text,
            inline=False
        )
        
        # Add results
        embed.add_field(
            name="Suggestion Results",
            value=f"<:checkmark:1384993844671545506> {self.upvotes} upvotes ({upvote_percentage:.0f}%)\n<:Denied:1370806202094583918> {self.downvotes} downvotes ({downvote_percentage:.0f}%)",
            inline=False
        )
        
        # Add Pennsylvania banner
        embed.add_field(
            name="",
            value="# pennsylvania",
            inline=False
        )
        
        # Edit the original message
        await interaction.response.edit_message(embed=embed, view=self)

class SuggestionsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @app_commands.command(name='suggest', description='Submit a suggestion to the server')
    @app_commands.describe(suggestion='Your suggestion for the server')
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        """Submit a suggestion to the server"""
        
        # Create the suggestion embed
        embed = discord.Embed(
            title="New Suggestion!",
            color=0x2F3136,
            description=""
        )
        
        # Add author info
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        
        # Add suggestion text
        embed.add_field(
            name="Suggestion:",
            value=suggestion,
            inline=False
        )
        
        # Add initial results
        embed.add_field(
            name="Suggestion Results",
            value="<:checkmark:1384993844671545506> 0 upvotes (0%)\n<:Denied:1370806202094583918> 0 downvotes (0%)",
            inline=False
        )
        
        # Add Pennsylvania banner
        embed.add_field(
            name="",
            value="# pennsylvania",
            inline=False
        )
        
        # Create the view with voting buttons
        view = SuggestionView(suggestion, interaction.user)
        
        # Send the suggestion embed
        await interaction.response.send_message(embed=embed, view=view)
        
        # Create a thread for discussion
        message = await interaction.original_response()
        thread = await message.create_thread(
            name="Suggestions Discussion",
            auto_archive_duration=10080  # 7 days
        )
        
        # Send a message in the thread
        await thread.send(f"Discussion for {interaction.user.mention}'s suggestion.")
        
        # Log the command usage
        try:
            await log_command_usage(interaction, 'suggest', f'Suggestion: {suggestion[:100]}...' if len(suggestion) > 100 else f'Suggestion: {suggestion}')
        except Exception as e:
            logger.error(f"Failed to log command usage: {e}")

async def setup(bot):
    await bot.add_cog(SuggestionsCog(bot))