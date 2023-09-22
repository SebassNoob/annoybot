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


class Meme(commands.Cog):
    """Generate a reddit meme"""

    def __init__(self, bot):
        self.bot = bot
        self.subreddits = cycle(
            [
                "https://www.reddit.com/r/dankmemes/new.json?sort=hot",
                "https://www.reddit.com/r/okbuddyretard/new.json?sort=hot",
                "https://www.reddit.com/r/memes/new.json?sort=hot",
                "https://www.reddit.com/r/wholesomememes/new.json?sort=hot",
                "https://www.reddit.com/r/meme/new.json?sort=hot",
                "https://www.reddit.com/r/shitposting/new.json?sort=hot",
                "https://www.reddit.com/r/nukedmemes/new.json?sort=hot",
            ]
        )
        # this is a dict of subreddits mapped to a list of memes. each meme is a tuple of (title, url)
        self.meme_data = defaultdict(list)
        self.get_memes.start()

    @app_commands.command(name="meme", description="Sends a top meme from reddit")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()

        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]

        if len(self.meme_data.items()) == 0:
            await interaction.followup.send(
                content="❌ There was an error with the meme API. Try again later.",
                ephemeral=True,
            )
            return

        sub, data = random.choice(list(self.meme_data.items()))
        specific_meme = random.choice(data)

        embed = discord.Embed(color=int(color, 16), title=specific_meme[0])

        embed.set_image(url=specific_meme[1])

        await interaction.followup.send(content=f"source: {sub}", embed=embed)

    def cog_unload(self):
        self.get_memes.cancel()

    @tasks.loop(seconds=60.0)
    async def get_memes(self):
        sub = next(self.subreddits)
        res = requests.get(sub, headers={"Accept": "application/json"})
        if res.status_code != 200:
            self.bot.logger.warning(f"failed to get response from {sub}: {res.text}")

            # holdback for 30 seconds before trying again
            self.get_memes.change_interval(seconds=self.get_memes.seconds + 30)
            return
        try:
            # success! reset the interval to 60 seconds
            self.get_memes.change_interval(seconds=60.0)

            # parse the response
            memes = res.json()["data"]["children"]
            self.meme_data[sub] = [
                (i["data"]["title"], i["data"]["url"]) for i in memes
            ]
        except KeyError:
            self.bot.logger.warning(
                f"failed to parse response from {sub}: {res.status_code} {res.text}"
            )
        except Exception as e:
            self.bot.logger.error(e)
        return


async def setup(bot):
    await bot.add_cog(Meme(bot))
