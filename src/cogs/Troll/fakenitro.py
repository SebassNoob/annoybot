import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from src.utils import check_usersettings_cache
import datetime


class Claim(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.green)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.style = discord.ButtonStyle.grey
        button.disabled = True
        em = discord.Embed(
            color=0x000000,
            title="You received a gift, but...",
            description="The gift link has either expired or has been revoked.\nThe sender can still create a new link to send again.",
        ).set_thumbnail(url="https://i.imgur.com/w9aiD6F.png")
        await interaction.response.edit_message(embed=em, view=self)
        await interaction.followup.send(
            content="You idiot lol\nhttps://c.tenor.com/x8v1oNUOmg4AAAAd/rickroll-roll.gif",
            ephemeral=True,
        )


class Fakenitro(commands.Cog):
    """Fake mutes a user"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nitrotroll", description="Sends a fake nitro embed")
    async def nitrotroll(self, interaction: discord.Interaction):
        em = discord.Embed(
            color=0x7289DA,
            title="A wild gift appears!",
            description="Nitro classic (3 months)\nThis link will expire in 12 hours, claim it now!",
        ).set_thumbnail(url="https://i.imgur.com/w9aiD6F.png")

        await interaction.response.send_message(content=".")
        msg = await interaction.original_response()
        await msg.delete()
        await interaction.channel.send(
            content="https://dicsord.com/gifts/84329801239480219834",
            embed=em,
            view=Claim(),
        )


async def setup(bot):
    await bot.add_cog(Fakenitro(bot))
