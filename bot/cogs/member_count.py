import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class MemberCountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.custom_person_emoji = "<:flst_person:1384991790838448209>"
        self.fallback_person_emoji = "👤"

    @discord.app_commands.command(name='member_count', description='Display the current member count')
    async def member_count(self, interaction: discord.Interaction):
        """Display member count with custom emoji button"""
        try:
            guild = interaction.guild
            if not guild:
                await interaction.response.send_message('This command can only be used in a server!', ephemeral=True)
                return
            
            member_count = guild.member_count
            
            # Try to use custom emoji, fallback to standard emoji
            try:
                person_emoji = self.custom_person_emoji
                button_label = f"{person_emoji} {member_count}"
            except:
                person_emoji = self.fallback_person_emoji
                button_label = f"{person_emoji} {member_count}"
            
            # Create embed
            embed = discord.Embed(
                title='Member Count',
                description=f'**{guild.name}** currently has **{member_count}** members!',
                color=discord.Color.green()
            )
            
            # Create button view
            view = MemberCountView(member_count, person_emoji)
            
            await interaction.response.send_message(embed=embed, view=view)
            logger.info(f'Member count displayed: {member_count}')
            
        except Exception as e:
            logger.error(f'Error displaying member count: {e}')
            await interaction.response.send_message('An error occurred while fetching member count.', ephemeral=True)

class MemberCountView(discord.ui.View):
    def __init__(self, member_count, emoji):
        super().__init__(timeout=300)  # 5 minute timeout
        self.member_count = member_count
        self.emoji = emoji
        
        # Add button with member count
        self.add_item(MemberCountButton(member_count, emoji))

class MemberCountButton(discord.ui.Button):
    def __init__(self, member_count, emoji):
        super().__init__(
            label=f"{member_count}",
            emoji=emoji,
            style=discord.ButtonStyle.primary,
            disabled=False
        )
        self.member_count = member_count

    async def callback(self, interaction: discord.Interaction):
        """Update member count when button is clicked"""
        try:
            # Get updated member count
            guild = interaction.guild
            if guild:
                updated_count = guild.member_count
                
                # Update button label
                self.label = f"{updated_count}"
                
                # Update embed
                embed = discord.Embed(
                    title='Member Count',
                    description=f'**{guild.name}** currently has **{updated_count}** members!',
                    color=discord.Color.green()
                )
                
                await interaction.response.edit_message(embed=embed, view=self.view)
                logger.info(f'Member count updated: {updated_count}')
            else:
                await interaction.response.send_message('Unable to update member count.', ephemeral=True)
                
        except Exception as e:
            logger.error(f'Error updating member count: {e}')
            await interaction.response.send_message('An error occurred while updating member count.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(MemberCountCog(bot))
