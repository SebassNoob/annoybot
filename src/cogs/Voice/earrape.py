import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer
import asyncio

import random
import os
from itertools import repeat, starmap
from operator import add


class Earrape(commands.Cog):
    """Play a specific Noise into a voice channel"""

    def __init__(self, bot):
        self.bot = bot

        directory = f"{os.getcwd()}/src/public/voice/"
        self.file_names = (
            "rickroll.mp3",
            "fallguys.mp3",
            "kahoot.mp3",
            "thomas.mp3",
            "wii.mp3",
            "android_earrape.mp3",
        )
        self.paths = list(starmap(add, zip(repeat(directory), self.file_names)))

    @app_commands.command(
        name="earrape", description="Plays earrape into a voice channel"
    )
    @app_commands.guild_only()
    @app_commands.describe(
        seconds="Number of seconds to play the earrape for. Max 10s."
    )
    async def earrape(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 1, 10] = 5,
    ):
        await interaction.response.defer()
        try:
            channel = interaction.user.voice.channel
            if channel is None:
                await interaction.followup.send("❌ You are not in a VC, stupid.")
                return
            if channel.user_limit is not None and channel.user_limit != 0:
                if len(channel.members) >= channel.user_limit:
                    await interaction.followup.send("❌ The VC is full.")
                    return

            voice = await channel.connect(reconnect=False)
        except discord.ClientException:
            await interaction.followup.send("❌ The bot is already playing something.")
            return
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Client timed out, try again later.")
            return

        file_name, path = random.choice(list(zip(self.file_names, self.paths)))

        voice.play(PCMVolumeTransformer(FFmpegPCMAudio(path), volume=2.0))
        await interaction.followup.send(
            f"✅ Playing file ``{file_name}`` for {seconds} seconds."
        )
        await asyncio.sleep(seconds)

        try:
            await interaction.guild.voice_client.disconnect(force=True)
            return

            # if already disconnected manually
        except AttributeError:
            return


async def setup(bot):
    await bot.add_cog(Earrape(bot))
