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


class Insult(commands.Cog):
    """Insult a person"""

    def __init__(self, bot):
        self.bot = bot

        self.insults = parse_txt(f"{os.getcwd()}/src/public/insults/insults.txt")

        self.sentence_starters = parse_txt(
            f"{os.getcwd()}/src/public/insults/starter.txt"
        )

        self.adjectives = parse_txt(f"{os.getcwd()}/src/public/insults/adjectives.txt")

    @app_commands.command(
        name="insult", description="Generates an insult and targets someone."
    )
    @app_commands.describe(user="Someone to insult")
    async def insult(
        self,
        interaction: discord.Interaction,
        user: Optional[Union[discord.Member, discord.User]] = None,
    ):
        insult = f"{random.choice(self.sentence_starters)} {random.choice(self.adjectives)} {random.choice(self.insults)}!"

        with Session(self.bot.engine) as session:
            ff, color = (
                session.query(UserSettings.family_friendly, UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )
            if ff:
                insult = profanity.censor(insult)
        embed = discord.Embed(color=int(color, 16), description=insult)

        embed.set_footer(text=f"Requested by {interaction.user.display_name}")

        await interaction.response.send_message(
            content=user.mention if user else "", embed=embed
        )


async def setup(bot):
    await bot.add_cog(Insult(bot))
