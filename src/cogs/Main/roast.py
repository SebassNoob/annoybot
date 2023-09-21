import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union
import random
from src.utils import parse_txt
from better_profanity import profanity

from sqlalchemy.orm import Session
from db.models import UserSettings


class Roast(commands.Cog):
    """Roast a person"""

    def __init__(self, bot):
        self.bot = bot
        self.roasts = parse_txt(f"{os.getcwd()}/src/public/roasts.txt")

    @app_commands.command(name="roast", description="Roasts someone.")
    @app_commands.describe(user="The person you wanna roast")
    async def roast(
        self,
        interaction: discord.Interaction,
        user: Optional[Union[discord.Member, discord.User]] = None,
    ):
        roast = random.choice(self.roasts)

        with Session(self.bot.engine) as session:
            ff, color = (
                session.query(UserSettings.family_friendly, UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )
            if ff:
                roast = profanity.censor(roast)

        embedVar = discord.Embed(color=int(color, 16), description=roast)
        embedVar.set_author(
            name=f"Roast from {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar,
        )

        embedVar.set_footer(text="u suck")

        await interaction.response.send_message(
            content=user.mention if user else "", embed=embedVar
        )


async def setup(bot):
    await bot.add_cog(Roast(bot))
