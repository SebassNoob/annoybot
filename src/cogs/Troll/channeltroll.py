import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import asyncio
import os
from src.utils import parse_txt


class Channeltroll(commands.Cog):
    """Create a new thread to ping a user randomly"""

    def __init__(self, bot):
        self.bot = bot
        self.messages = parse_txt(f"{os.getcwd()}/src/public/channeltroll.txt")

    @app_commands.command(
        name="channeltroll",
        description="Creates a temporary thread then pings a user once to mess with them",
    )
    @app_commands.describe(user="The user to ping")
    @app_commands.checks.bot_has_permissions(
        send_messages_in_threads=True, create_public_threads=True, manage_threads=True
    )
    @app_commands.guild_only()
    async def channeltroll(
        self, interaction: discord.Interaction, user: discord.Member
    ):
        randomstr = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=10)
        )
        if isinstance(interaction.channel, (discord.TextChannel, discord.ForumChannel)):
            channel = await interaction.channel.create_thread(
                name=randomstr, auto_archive_duration=1440
            )
        elif isinstance(interaction.channel, discord.Thread):
            channel = await interaction.channel.parent.create_thread(
                name=randomstr, auto_archive_duration=1440
            )
        else:
            await interaction.response.send_message(
                "❌ This channel does not support threads. Try again in a text/forum channel."
            )
            return

        await interaction.response.send_message(
            f"A new thread {channel.mention} was created. The bot will ping {user.display_name} to annoy them."
        )

        try:
            await channel.send(f"Hello, {user.mention}. {random.choice(self.messages)}")

            # this blocks the thread until the user responds or timeout is raised
            await self.bot.wait_for(
                "message",
                check=lambda m: m.author == user and m.channel == channel,
                timeout=20,
            )

            await channel.send(
                f"courtesy of {interaction.user.mention}. this thread has been automatically archived, but you can keep it around if you'd like"
            )

        except asyncio.TimeoutError:
            # check if channel does not exist
            # ie. it was deleted manually
            if self.bot.get_channel(channel.id) is None:
                return

        await channel.edit(archived=True)


async def setup(bot):
    await bot.add_cog(Channeltroll(bot))
