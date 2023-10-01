import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt, check_usersettings_cache
from better_profanity import profanity


class Uninspire(commands.Cog):
    """Generate an uninspiring quote"""

    def __init__(self, bot):
        self.bot = bot
        self.quotes = parse_txt(f"{os.getcwd()}/src/public/uninspiring_quotes.txt")

    @app_commands.command(name="uninspire", description="Generate an uninspiring quote")
    async def uninspire(self, interaction: discord.Interaction):
        quote = random.choice(self.quotes)

        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff:
            quote = profanity.censor(quote)

        embed = discord.Embed(color=int(color, 16), description=quote)
        embed.set_footer(
            text=f"requested by {interaction.user.display_name}\nimagine having a mom."
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Uninspire(bot))
