import discord
from discord.ext import commands
from discord import app_commands

from src.utils import fetch_json, check_usersettings_cache

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
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        if status != 200:
            await interaction.followup.send(
                "❌ There was an error with the ip lookup API. Try again later.",
                ephemeral=True,
            )
            return

        if res["status"] != "success":
            await interaction.followup.send(
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
            await interaction.followup.send(
                "❌ An unspecified error occured, the ip address probably is private. What a loser lmao."
            )
            return
        text = "".join([f"**{key}**: {str(value)}\n" for key, value in info.items()])
        await interaction.followup.send(
            embed=discord.Embed(color=int(color, 16), title=ip, description=text)
        )


async def setup(bot):
    await bot.add_cog(Iplookup(bot))
