import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt
from better_profanity import profanity

from sqlalchemy.orm import Session
from db.models import UserSettings


class Uninspire(commands.Cog):
    """Generate an uninspiring quote"""

    def __init__(self, bot):
        self.bot = bot
        self.quotes = parse_txt(f"{os.getcwd()}/src/public/uninspiring_quotes.txt")

    @app_commands.command(name="uninspire", description="Generate an uninspiring quote")
    async def uninspire(self, interaction: discord.Interaction):
        quote = random.choice(self.quotes)

        with Session(self.bot.engine) as session:
            ff, color = (
                session.query(UserSettings.family_friendly, UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
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
