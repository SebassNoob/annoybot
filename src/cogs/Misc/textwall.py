import discord
from discord.ext import commands
from discord import app_commands

from sqlalchemy.orm import Session
from db.models import UserSettings
from better_profanity import profanity
from typing import Optional


class Textwall(commands.Cog):
    """Lookup the information of an ip address"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="textwall", description="Sends a wall of repeated text in a single message"
    )
    @app_commands.describe(num="The number of times to spam", content="What to spam")
    async def textwall(
        self,
        interaction: discord.Interaction,
        num: app_commands.Range[int, 1, None],
        content: app_commands.Range[str, 1, None],
        tts: Optional[bool] = False,
    ):
        toSend = " ".join([content.strip() for _ in range(num)])

        if len(toSend) > 2000:
            await interaction.response.send_message(
                f"❌ Your text wall ({len(toSend)} characters) is too long (>2000 characters), you moron."
            )
            return

        with Session(self.bot.engine) as session:
            ff = (
                session.query(UserSettings.family_friendly)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]
        if ff:
            toSend = profanity.censor(toSend)
        await interaction.response.send_message(toSend, tts=tts)


async def setup(bot):
    await bot.add_cog(Textwall(bot))
