import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy.orm import Session
from db.models import UserSettings
from src.utils import fetch_json

import aiohttp


class Iplookup(commands.Cog):
    """Lookup the information of an ip address"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="iplookup", description="Finds the location of a given ip"
    )
    @app_commands.describe(ip="The ip you want to find the location of")
    async def iplookup(self, interaction: discord.Interaction, ip: str):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                f"http://ip-api.com/json/{ip}",
            )
        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]

        if status != 200:
            await interaction.response.send_message(
                "❌ There was an error with the ip lookup API. Try again later.",
                ephemeral=True,
            )
            return

        if res["status"] != "success":
            await interaction.response.send_message(
                "❌ Thats not a valid ip, idiot.", ephemeral=True
            )
            return

        try:
            info = {
                "Country": res["country"] or "Unknown",
                "Region": res["regionName"] or "Unknown",
                "City": res["city"] or "Unknown",
                "Zip code": res["zip"] or "Unknown",
                "Coordinates": (res["lat"] or "Unknown", res["lon"] or "Unknown"),
                "ISP": res["isp"] or "Unknown",
            }

        except KeyError:
            await interaction.response.send_message(
                "❌ An unspecified error occured, the ip address probably is private. What a loser lmao."
            )
            return
        text = "".join([f"**{key}**: {str(value)}\n" for key, value in info.items()])
        await interaction.followup.send(
            embed=discord.Embed(color=int(color, 16), title=ip, description=text)
        )


async def setup(bot):
    await bot.add_cog(Iplookup(bot))
