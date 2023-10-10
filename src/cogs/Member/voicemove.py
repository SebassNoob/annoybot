import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio


class Voicemove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voicemove_cmd = app_commands.ContextMenu(
            name="gtfo from VC", callback=self.voicemove
        )
        self.bot.tree.add_command(self.voicemove_cmd)

    @app_commands.checks.bot_has_permissions(move_members=True)
    async def voicemove(self, interaction: discord.Interaction, user: discord.Member):
        if user.voice is None:
            await interaction.response.send_message(
                "❌ This member is not currently connected to a voice channel."
            )
            return
        allowed_vcs = list(
            filter(
                lambda v: v.permissions_for(user).connect and v != user.voice.channel,
                [vc for vc in user.guild.voice_channels],
            )
        )
        await interaction.response.send_message(
            f"✅ {user.display_name} will be moved between VCs thrice, LOL"
        )
        attempts = 3

        while attempts >= 0:
            try:
                await user.move_to(random.choice(allowed_vcs))
                await asyncio.sleep(0.7)
                attempts -= 1
            except (discord.Forbidden, discord.HTTPException):
                await interaction.followup.send(
                    f"❌ Failed to move {user.display_name} to a voice channel."
                )
                break


async def setup(bot):
    await bot.add_cog(Voicemove(bot))
