from typing import Any, Coroutine
import discord
from discord.ext import commands, tasks
from discord import app_commands

from sqlalchemy.orm import Session
from db.models import UserSettings

import random
from itertools import cycle
from collections import defaultdict

import requests


class Copypasta(commands.Cog):
    """Generate a reddit meme"""

    def __init__(self, bot):
        self.bot = bot

        # a list of copypastas (title, selftext)
        self.copypastas = []
        self.get_copypastas.start()

    @app_commands.command(
        name="copypasta", description="Gets a copypasta from r/copypasta"
    )
    async def copypasta(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]

        if len(self.copypastas) == 0:
            await interaction.followup.send(
                content="❌ There was an error with the copypasta API. Try again later.",
                ephemeral=True,
            )
            return

        title, desc = random.choice(self.copypastas)

        embed = discord.Embed(color=int(color, 16), title=title, description=desc)

        await interaction.followup.send(
            content=f"source: https://www.reddit.com/r/copypasta/new.json?sort=hot",
            embed=embed,
        )

    def cog_unload(self):
        self.get_copypastas.cancel()

    @tasks.loop(minutes=30.0)
    async def get_copypastas(self):
        sub = "https://www.reddit.com/r/copypasta/new.json?sort=hot"
        res = requests.get(sub, headers={"Accept": "application/json"})
        if res.status_code != 200:
            self.bot.logger.warning(f"failed to get response from {sub}: {res.text}")

            # holdback for 30 seconds before trying again
            self.get_copypastas.change_interval(seconds=30)
            return
        try:
            # success! reset the interval to 30 mins
            self.get_copypastas.change_interval(minutes=30.0)

            # parse the response
            # this is a list of (title, selftext)
            # we only want copypastas that are less than 4000 characters
            self.copypastas = [
                (i["data"]["title"], i["data"]["selftext"])
                for i in res.json()["data"]["children"]
                if 0 < len(i["data"]["selftext"]) <= 4000
            ]

        except KeyError:
            self.bot.logger.warning(
                f"failed to parse response from {sub}: {res.status_code} {res.text}"
            )
        except Exception as e:
            self.bot.logger.error(e)
        return


async def setup(bot):
    await bot.add_cog(Copypasta(bot))
