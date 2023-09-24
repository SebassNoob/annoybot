import discord
from discord.ext import commands
from discord import app_commands

import aiohttp
from src.utils import fetch_json
from sqlalchemy.orm import Session
from db.models import UserSettings


class Urbandict(commands.Cog):
    """Lookup the information of an ip address"""

    def __init__(self, bot):
        self.bot = bot

        # returns a combined string of emojis

    @app_commands.command(
        name="urbandict", description="Looks up a term in urban dictionary"
    )
    @app_commands.describe(term="The term you want to search")
    async def urbandict(self, interaction: discord.Interaction, term: str):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session, f"http://api.urbandictionary.com/v0/define?term={term}"
            )

        # status will always be 200, so we don't need to check it, just the length of the list

        if len(res["list"]) == 0:
            await interaction.followup.send(
                content="❌ there were no results returned, actually search for a real word next time, you moron."
            )
            return

        best = sorted(res["list"], key=lambda x: int(x["thumbs_up"]), reverse=True)[0]

        definition = best["definition"].replace("[", "").replace("]", "")
        example = best["example"].replace("[", "").replace("]", "")

        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]

        description = f"**Definition:** {definition} \n\n **Examples:** {example}"
        em = discord.Embed(
            color=int(color, 16),
            title=f"Urban Dictionary result for {term}",
            description=description,
        )
        await interaction.followup.send(embed=em)


async def setup(bot):
    await bot.add_cog(Urbandict(bot))
