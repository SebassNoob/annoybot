import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional, Union
import random
from src.utils import parse_txt, check_usersettings_cache
from better_profanity import profanity


class Roast(commands.Cog):
    """Roast a person"""

    def __init__(self, bot):
        self.bot = bot
        self.roasts = parse_txt(f"{os.getcwd()}/src/public/roasts.txt")

    @app_commands.command(name="roast", description="Roasts someone.")
    @app_commands.describe(user="The person you wanna roast")
    async def roast(
        self,
        interaction: discord.Interaction,
        user: Optional[Union[discord.Member, discord.User]] = None,
    ):
        roast = random.choice(self.roasts)
        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff:
            roast = profanity.censor(roast)

        em = discord.Embed(color=int(color, 16), description=roast)
        em.set_author(
            name=f"Roast from {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar,
        )

        em.set_footer(text="u suck")

        await interaction.response.send_message(
            content=user.mention if user else "", embed=em
        )


async def setup(bot):
    await bot.add_cog(Roast(bot))
