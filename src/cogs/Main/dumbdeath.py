import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Union
import random
from src.utils import read_csv, check_usersettings_cache
from better_profanity import profanity


class Dumbdeath(commands.Cog):
    """Makes up a dumb death as a fictional scenario"""

    def __init__(self, bot):
        self.bot = bot

        self.deaths: list[dict[str, str]] = read_csv(
            f"{os.getcwd()}/src/public/dumb_deaths.csv", as_dict=True
        )

    @app_commands.command(
        name="dumbdeath",
        description="Makes up a fictional scenario where the person you mentioned died a dumb death",
    )
    @app_commands.describe(user="The user involved.")
    async def dumbdeath(
        self,
        interaction: discord.Interaction,
        user: Union[discord.Member, discord.User],
    ):
        if isinstance(interaction.channel, discord.abc.GuildChannel):
            nsfw = interaction.channel.nsfw
        elif isinstance(interaction.channel, discord.Thread):
            nsfw = interaction.channel.parent.nsfw
        else:
            nsfw = True

            # if nsfw anything is ok
            # else filter

        deaths = self.deaths

        if nsfw:
            deaths = list(filter(lambda item: item["nsfw"] == "0", deaths))

        choice = random.choice(deaths)["content"]

        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff:
            choice = profanity.censor(choice)

        em = discord.Embed(
            color=int(color, 16), description=choice.replace("#", user.name)
        )
        await interaction.response.send_message(content=user.mention, embed=em)


async def setup(bot):
    await bot.add_cog(Dumbdeath(bot))
