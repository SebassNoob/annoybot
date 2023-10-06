import discord
from discord.ext import commands
from discord import app_commands

import os
import random

from src.utils import parse_txt


class Emojis(commands.Cog):
    """Lookup the information of an ip address"""

    def __init__(self, bot):
        self.bot = bot

        # returns a combined string of emojis
        self.emojis = parse_txt(f"{os.getcwd()}/src/public/emojis.txt")[0]

    @app_commands.command(
        name="emojitts", description="Reads out loud a long string of emojis"
    )
    @app_commands.describe(length="The length of the string of emojis to read")
    @app_commands.checks.bot_has_permissions(send_tts_messages=True)
    async def emojitts(
        self, interaction: discord.Interaction, length: app_commands.Range[int, 1, 75]
    ):
        # returns a list of emojis (length 200)
        a = [
            i.decode(encoding="utf-8") for i in bytes(self.emojis, "utf-8").split(b" ")
        ]

        i = random.randint(0, 75 - length)

        # generates random sub array of emojis
        # turning it into a string to be sent
        res = "".join(a[i : i + length])

        await interaction.response.send_message(res, tts=True)


async def setup(bot):
    await bot.add_cog(Emojis(bot))
