import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import check_usersettings_cache


class Uwuify(commands.Cog):
    """Uwuify a message"""

    def __init__(self, bot):
        self.bot = bot

        self.uwuify_cmd = app_commands.ContextMenu(name="uwuify", callback=self.uwuify)
        self.bot.tree.add_command(self.uwuify_cmd)

    async def uwuify(self, interaction: discord.Interaction, message: discord.Message):
        if len(message.content) == 0:
            await interaction.response.send_message(
                "This message is empty?", ephemeral=True
            )
            return
        to_mod = message.content.lower()
        out = "".join(
            [char.upper() if pos % 2 == 0 else char for pos, char in enumerate(to_mod)]
        )

        await interaction.response.send_message(out)


async def setup(bot):
    await bot.add_cog(Uwuify(bot))
