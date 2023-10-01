import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt, check_usersettings_cache
from better_profanity import profanity


class Urmom(commands.Cog):
    """Generate a your mom joke"""

    def __init__(self, bot):
        self.bot = bot
        self.joke = parse_txt(f"{os.getcwd()}/src/public/ur_mom_jokes.txt")

    @app_commands.command(name="urmom", description="Generates a 'yo mom' joke")
    async def urmom(self, interaction: discord.Interaction):
        joke = random.choice(self.joke)

        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff:
            joke = profanity.censor(joke)

        embed = discord.Embed(color=int(color, 16), description=joke)
        embed.set_footer(
            text=f"requested by {interaction.user.display_name}\nimagine having a mom."
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Urmom(bot))
