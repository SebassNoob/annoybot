import discord
from discord.ext import commands
from discord import app_commands
from better_profanity import profanity

from sqlalchemy.orm import Session
from db.models import UserSettings
from src.utils import fetch_json

import aiohttp


class Dadjoke(commands.Cog):
    """Generate a dad joke"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dadjoke", description="Sends a typical dad joke.")
    async def dadjoke(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                "https://icanhazdadjoke.com/",
                headers={"Accept": "application/json"},
            )

        if status != 200:
            await interaction.response.send_message(
                content="❌ There was an error with the dad joke API. Try again later.",
                ephemeral=True,
            )
            return

        dadJoke = res["joke"]
        with Session(self.bot.engine) as session:
            ff, color = (
                session.query(UserSettings.family_friendly, UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )
            if ff:
                dadJoke = profanity.censor(dadJoke)

        em = discord.Embed(color=int(color, 16), description=dadJoke)
        em.set_author(
            name=f"{interaction.user.display_name}'s dad joke",
            icon_url=interaction.user.avatar,
        )

        await interaction.followup.send(embed=em)


async def setup(bot):
    await bot.add_cog(Dadjoke(bot))
