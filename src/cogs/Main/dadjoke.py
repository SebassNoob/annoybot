import discord
from discord.ext import commands, tasks
from discord import app_commands
from better_profanity import profanity

from src.utils import fetch_json, check_usersettings_cache

import aiohttp


class Dadjoke(commands.Cog):
    """Generate a dad joke"""

    def __init__(self, bot):
        self.bot = bot
        self.fetch_dadjokes.start()

    @app_commands.command(name="dadjoke", description="Sends a typical dad joke.")
    async def dadjoke(self, interaction: discord.Interaction):
        await interaction.response.defer()
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                "https://icanhazdadjoke.com/",
                headers={
                    "Accept": "application/json",
                    "User-Agent": "annoybot -- contact: sebassnoob on discord",
                },
            )

        if status != 200:
            # get from cache instead
            dadJoke = self.bot.redis_client.srandmember("dadjokes")
        else:
            # successful, get from api
            dadJoke = res["joke"]
        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )
        if ff:
            dadJoke = profanity.censor(dadJoke)

        em = discord.Embed(color=int(color, 16), description=dadJoke)
        em.set_author(
            name=f"{interaction.user.display_name}'s dad joke",
            icon_url=interaction.user.avatar,
        )

        await interaction.followup.send(embed=em)

    @tasks.loop(hours=1)
    async def fetch_dadjokes(self):
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                "https://icanhazdadjoke.com/search",
                headers={
                    "Accept": "application/json",
                    "User-Agent": "annoybot -- contact: sebassnoob on discord",
                },
            )
        if status != 200:
            self.bot.logger.warning(
                f"failed to fetch dad jokes from https://icanhazdadjoke.com/search: {status}"
            )
            return
        results = res["results"]
        jokes = [i["joke"] for i in results]
        self.bot.redis_client.sadd("dadjokes", *jokes)


async def setup(bot):
    await bot.add_cog(Dadjoke(bot))
