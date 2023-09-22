import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt
from better_profanity import profanity

from sqlalchemy.orm import Session
from db.models import UserSettings


class Darkjoke(commands.Cog):
    """Generates a dark joke"""

    def __init__(self, bot):
        self.bot = bot
        self.jokes = parse_txt(f"{os.getcwd()}/src/public/darkjokes.txt")

    @app_commands.command(
        name="darkjoke", description="Sends a dark joke. May be insensitive."
    )
    async def darkjoke(self, interaction: discord.Interaction):
        joke = random.choice(self.jokes)

        with Session(self.bot.engine) as session:
            ff, color = (
                session.query(UserSettings.family_friendly, UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )
            if ff:
                joke = profanity.censor(joke)

        await interaction.response.send_message(
            embed=discord.Embed(color=int(color, 16), description=joke)
        )


async def setup(bot):
    await bot.add_cog(Darkjoke(bot))
