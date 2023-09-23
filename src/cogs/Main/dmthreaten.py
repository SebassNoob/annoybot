import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt
from better_profanity import profanity

from sqlalchemy.orm import Session
from db.models import UserSettings
from typing import Union, Optional


class Dmthreaten(commands.Cog):
    """Generate a your mom joke"""

    def __init__(self, bot):
        self.bot = bot
        self.threats = parse_txt(f"{os.getcwd()}/src/public/dm_threaten.txt")

    @app_commands.command(
        name="dmthreaten",
        description="Sends a threat to a direct message channel of a user. ",
    )
    @app_commands.describe(user="User to threaten", custom_threat="A custom message")
    async def dmthreaten(
        self,
        interaction: discord.Interaction,
        user: Union[discord.Member, discord.User],
        custom_threat: Optional[app_commands.Range[str, 1, None]] = None,
    ):
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            # get user settings if they exist
            # returns tuple of (family_friendly, color, block_dms)
            res = (
                session.query(
                    UserSettings.family_friendly,
                    UserSettings.color,
                    UserSettings.block_dms,
                )
                .filter(UserSettings.id == user.id)
                .one_or_none()
            )
            if res is None:
                res = (False, "0x000000", False)
            family_friendly, color, block_dms = res

        if block_dms or user.bot:
            await interaction.response.send_message(
                content="❌ The user you mentioned is either a bot, or does not want to be DM'ed. Bet you look stupid now.",
                ephemeral=True,
            )
            return

        threat = custom_threat or random.choice(self.threats)

        if family_friendly:
            threat = profanity.censor(threat)

        channel = await user.create_dm()

        em = discord.Embed(color=int(color, 16), description=threat)
        em.set_author(
            name=f"{interaction.user.display_name} from {interaction.guild.name}"
            if interaction.guild
            else interaction.user.display_name,
            icon_url=interaction.user.avatar,
        )
        em.set_footer(
            text=f"this was generated by /dmthreaten. if you want, use /settings to toggle this feature."
        )

        try:
            await channel.send(embed=em)
        except:
            await interaction.followup.send(
                content=f"❌ {user.display_name} blocked my message, what a pussy"
            )
            return
        await interaction.followup.send(
            content=f"✅ {user.display_name} has been sent this in DMs:", embed=em
        )


async def setup(bot):
    await bot.add_cog(Dmthreaten(bot))
