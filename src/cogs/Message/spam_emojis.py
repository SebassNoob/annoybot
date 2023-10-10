import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt
import os


class Emojispam(commands.Cog):
    """Append emojis to a message"""

    def __init__(self, bot):
        self.bot = bot
        emojis = parse_txt(f"{os.getcwd()}/src/public/emojis.txt")[0]
        self.emojis = [
            i.decode(encoding="utf-8") for i in bytes(emojis, "utf-8").split(b" ")
        ]
        self.emojispam = app_commands.ContextMenu(
            name="emojispam", callback=self.emojispam
        )
        self.bot.tree.add_command(self.emojispam)

    def random_emoji(self):
        yield random.choice(self.emojis)

    @app_commands.checks.bot_has_permissions(
        read_message_history=True, add_reactions=True
    )
    async def emojispam(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.send_message("attempting to spam emojis...")
        for _ in range(7):
            await message.add_reaction(next(self.random_emoji()))
        await interaction.edit_original_response(content="done. loser")


async def setup(bot):
    await bot.add_cog(Emojispam(bot))
