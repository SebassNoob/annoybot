import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio


class Ghosttroll(commands.Cog):
    """Ghostping a user in 3 different channels"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ghosttroll", description="Ghostpings a user in 3 different channels"
    )
    @app_commands.describe(user="The user to ping")
    @app_commands.guild_only()
    async def ghosttroll(self, interaction: discord.Interaction, user: discord.Member):
        allowedChannels: list[discord.TextChannel] = []

        for channel in interaction.guild.channels:
            if (
                channel.type == discord.ChannelType.text
                and channel.permissions_for(user).read_messages
                and channel.permissions_for(interaction.guild.me).send_messages
            ):
                allowedChannels.append(channel)

        if len(allowedChannels) != 0:
            await interaction.response.send_message(
                f"{user.display_name} will be ghost pinged in 3 channels to annoy them."
            )
        else:
            await interaction.response.send_message(
                "That user can't access any channels, bruh wtf"
            )
            return

        i = 3
        while i != 0:
            try:
                targetChannel = random.choice(allowedChannels)

                message = await targetChannel.send("{}".format(user.mention))
                await asyncio.sleep(0.1)
                await message.delete()
                i -= 1
                await asyncio.sleep(1)

            except Exception as e:
                # this really should not be happening
                self.bot.logger.warning(e)
                break


async def setup(bot):
    await bot.add_cog(Ghosttroll(bot))
