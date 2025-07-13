import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot.utils.command_logger import log_command_usage
from bot.utils.case_tracker import CaseTracker

logger = logging.getLogger(__name__)

class InfractionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.case_tracker = CaseTracker()
        self.infraction_role_id = 1393737607653097614

    def has_infraction_permission(self, user: discord.Member) -> bool:
        """Check if user has the infraction role"""
        return any(role.id == self.infraction_role_id for role in user.roles)

    @app_commands.command(name='infract', description='Issue an infraction to a staff member')
    @app_commands.describe(
        staff_member='The staff member to infract',
        punishment='The punishment being issued',
        reason='Reason for the infraction'
    )
    async def infract(self, interaction: discord.Interaction, staff_member: discord.Member, punishment: str, reason: str):
        """Issue an infraction with embed and appeal thread"""
        if not self.has_infraction_permission(interaction.user):
            await interaction.response.send_message('You do not have permission to use this command.', ephemeral=True)
            return
        
        try:
            # Get case number
            case_number = self.case_tracker.get_next_case_number()
            
            # Create infraction embed
            embed = discord.Embed(
                title="Staff Infraction",
                description="The high-ranking team has decided to take disciplinary action against you.",
                color=0x8AA0AE  # Updated hex color
            )
            
            # Add fields
            embed.add_field(name="Staff Member:", value=staff_member.mention, inline=False)
            embed.add_field(name="Punishment:", value=punishment, inline=False)
            embed.add_field(name="Reason:", value=reason, inline=False)
            embed.add_field(name="Notes:", value="None", inline=False)
            
            # Add footer with issuer info and infraction ID
            embed.set_footer(
                text=f"Issued by: {interaction.user.display_name} | Infraction ID: {case_number}",
                icon_url=interaction.user.avatar.url if interaction.user.avatar else None
            )
            
            # Set the provided image as the main embed image
            embed.set_image(url="https://media.discordapp.net/attachments/1393280610855813250/1393284667641430016/Screenshot_2025-07-11_at_10.35.46_AM.png?ex=68753ff6&is=6873ee76&hm=76b5cac4637a95d7a9a8bb09cd92f54593f0821de658d2ae930b5b23c047d552&=&width=1851&height=142")
            
            # Set server logo as thumbnail (top right)
            if interaction.guild and interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)
            else:
                # Fallback to PA logo if no server icon
                embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1369403919293485191/1322362936154423357/image.png")
            
            # Get the specific infraction channel
            infraction_channel = self.bot.get_channel(1393737982120558674)
            if not infraction_channel:
                await interaction.response.send_message('❌ Could not find the infraction channel.', ephemeral=True)
                return
            
            # Send the infraction embed to the specific channel
            infraction_message = await infraction_channel.send(embed=embed)
            
            # Create appeal thread with the name "Appeal Here"
            thread = await infraction_message.create_thread(
                name="Appeal Here",
                auto_archive_duration=10080  # 7 days
            )
            
            # Send appeal message in thread
            await thread.send(f"{staff_member.mention} Appeal Here")
            
            # Save case
            self.case_tracker.save_case(case_number, 'infraction', staff_member.id, interaction.user.id, f'{punishment} - {reason}')
            
            # Confirm to the user
            await interaction.response.send_message(f'✅ Infraction issued to {staff_member.mention}. Appeal thread created.', ephemeral=True)
            logger.info(f'Infraction issued: {staff_member.name} ({staff_member.id}) by {interaction.user.name} - Case #{case_number}')
            await log_command_usage(self.bot, interaction, 'infract', f'Target: {staff_member.name} | Punishment: {punishment} | Reason: {reason} | Case: #{case_number}')
            
        except discord.Forbidden:
            await interaction.response.send_message('I do not have permission to create threads or send messages.', ephemeral=True)
        except Exception as e:
            logger.error(f'Error issuing infraction: {e}')
            await interaction.response.send_message('An error occurred while issuing the infraction.', ephemeral=True)

async def setup(bot):
    await bot.add_cog(InfractionCog(bot))