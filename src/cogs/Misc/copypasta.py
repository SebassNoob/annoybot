import discord
from discord.ext import commands, tasks
from discord import app_commands

from src.utils import fetch_json, check_usersettings_cache

import random

import aiohttp


class Copypasta(commands.Cog):
    """Generate a reddit meme"""

    def __init__(self, bot):
        self.bot = bot

        self.get_copypastas.clear_exception_types()
        self.get_copypastas.start()

    @app_commands.command(
        name="copypasta", description="Gets a copypasta from r/copypasta"
    )
    async def copypasta(self, interaction: discord.Interaction):
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        if self.bot.redis_client.hlen("copypastas") == 0:
            await interaction.response.send_message(
                content="❌ There was an error with the copypasta API. Try again later.",
                ephemeral=True,
            )
            return

        title, desc = self.bot.redis_client.hrandfield(
            "copypastas", count=1, withvalues=True
        )
        embed = discord.Embed(color=int(color, 16), title=title, description=desc)

        await interaction.response.send_message(
            content=f"source: https://www.reddit.com/r/copypasta/new.json?sort=hot",
            embed=embed,
        )

    def cog_unload(self):
        self.get_copypastas.cancel()

    @tasks.loop(minutes=30.0, reconnect=False)
    async def get_copypastas(self):
        sub = "https://www.reddit.com/r/copypasta/new.json?sort=hot"
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                sub,
                headers={"Accept": "application/json", "User-Agent": "Heil Spez"},
            )

        if status != 200:
            self.bot.logger.warning(f"failed to get response from {sub}: {status}")

            # holdback for 10 min before trying again
            self.get_copypastas.change_interval(minutes=10)
            return
        try:
            # success! reset the interval to 30 mins
            self.get_copypastas.change_interval(minutes=30.0)

            # parse the response
            # this is a dict with title: selftext
            # we only want copypastas that are less than 4000 characters

            copypastas = {
                i["data"]["title"]: i["data"]["selftext"]
                for i in res["data"]["children"]
                if 0 < len(i["data"]["selftext"]) <= 4000
            }
            self.bot.redis_client.hmset("copypastas", copypastas)

        except KeyError:
            self.bot.logger.warning(f"failed to parse response from {sub}: {status}")
        except Exception as e:
            self.bot.logger.error(e)
        return


async def setup(bot):
    await bot.add_cog(Copypasta(bot))
