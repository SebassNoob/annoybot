import discord
from discord.ext import commands
from discord import app_commands
from src.utils import read_csv, check_usersettings_cache
import os
import random
from typing import List


class Reroll(discord.ui.View):
    def __init__(self, func):
        super().__init__()
        self.func = func

    @discord.ui.button(label="reroll", style=discord.ButtonStyle.grey)
    async def re(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.func.callback(interaction)


class Tord(discord.ui.View):
    def __init__(self, *, truths: List[str], dares: List[str]):
        super().__init__()
        self.truths = truths
        self.dares = dares

    @discord.ui.button(label="Truth", style=discord.ButtonStyle.green)
    async def op1(self, interaction: discord.Interaction, button: discord.ui.Button):
        truth = random.choice(self.truths)

        await interaction.response.edit_message(content=truth, view=Reroll(self.op1))

    @discord.ui.button(label="Dare", style=discord.ButtonStyle.green)
    async def op2(self, interaction: discord.Interaction, button: discord.ui.Button):
        dare = random.choice(self.dares)

        await interaction.response.edit_message(content=dare, view=Reroll(self.op2))


class Truthordare(commands.Cog):
    """truth or dare game"""

    def __init__(self, bot):
        self.bot = bot
        raw = read_csv(f"{os.getcwd()}/src/public/truth_or_dare.csv", as_dict=True)
        self.truths = [d["content"] for d in raw if d["type"] == "0"]
        self.dares = [d["content"] for d in raw if d["type"] == "1"]

    @app_commands.command(
        name="truthordare", description="Generates a truth or dare question"
    )
    async def truthordare(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Truth or dare?", view=Tord(truths=self.truths, dares=self.dares)
        )


async def setup(bot):
    await bot.add_cog(Truthordare(bot))
