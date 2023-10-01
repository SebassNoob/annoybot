import discord
from discord.ext import commands, tasks
from discord import app_commands

from sqlalchemy.orm import Session
from db.models import UserSettings
from src.utils import fetch_json, check_usersettings_cache

import random
from itertools import cycle
from collections import defaultdict
import asyncio

import aiohttp


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
        # tries to get all memes from all subreddits 1 time
        self.get_all_memes.clear_exception_types()
        self.get_all_memes.start()

        # start the loop to refresh memes every 2 minutes
        self.get_memes.clear_exception_types()
        self.get_memes.start()

    @app_commands.command(name="meme", description="Sends a top meme from reddit")
    async def meme(self, interaction: discord.Interaction):
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        scanned_keys = self.bot.redis_client.scan(cursor=0, match="memes:*")
        if len(scanned_keys) == 0:
            await interaction.response.send_message(
                content="❌ There was an error with the meme API. Try again later.",
                ephemeral=True,
            )
            return
        rand_key = random.choice(scanned_keys[1])
        title, url = self.bot.redis_client.hrandfield(
            rand_key, count=1, withvalues=True
        )

        embed = discord.Embed(color=int(color, 16), title=title)

        embed.set_image(url=url)

        # remove the "memes:" part of the key with string slicing [6:]
        await interaction.response.send_message(
            content=f"source: {rand_key[6:]}", embed=embed
        )

    def cog_unload(self):
        self.get_memes.cancel()

    @tasks.loop(count=1, reconnect=False)
    async def get_all_memes(self):
        async with aiohttp.ClientSession() as session:
            for sub in self.subreddits:
                res, status = await fetch_json(
                    session, sub, headers={"Accept": "application/json"}
                )

                if status != 200:
                    self.bot.logger.warning(
                        f"failed to get response from {sub}: {status}"
                    )
                    # if we fail to get a response from a subreddit, stop trying since we probably are rate limited
                    self.get_all_memes.cancel()

                try:
                    # parse the response
                    meme_data = defaultdict(dict)
                    meme_data[sub] = {
                        i["data"]["title"]: i["data"]["url"]
                        for i in res["data"]["children"]
                    }
                    for sub, data in meme_data.items():
                        self.bot.redis_client.hmset(f"memes:{sub}", data)

                except KeyError:
                    self.bot.logger.warning(
                        f"failed to parse response from {sub}: {status}"
                    )
                except Exception as e:
                    self.bot.logger.error(e)

    @tasks.loop(minutes=2.0, reconnect=False)
    async def get_memes(self):
        sub = next(self.subreddits)
        async with aiohttp.ClientSession() as session:
            res, status = await fetch_json(
                session,
                sub,
                headers={"Accept": "application/json", "User-Agent": "Heil Spez"},
            )

        if status != 200:
            self.bot.logger.warning(f"failed to get response from {sub}: {status}")
            # holdback for 1 min before trying again
            self.get_memes.change_interval(minutes=self.get_memes.minutes + 1)
            return
        try:
            # success! reset the interval to 2 mins
            self.get_memes.change_interval(minutes=2.0)

            # parse the response
            # this is a dict with title: url
            # set meme:subreddit to this dict
            meme_data = {
                i["data"]["title"]: i["data"]["url"] for i in res["data"]["children"]
            }

            self.bot.redis_client.hmset(f"memes:{sub}", meme_data)

        except KeyError:
            self.bot.logger.warning(f"failed to parse response from {sub}: {res}")
        except Exception as e:
            self.bot.logger.error(e)
        return


async def setup(bot):
    await bot.add_cog(Meme(bot))
