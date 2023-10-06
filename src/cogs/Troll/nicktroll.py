import discord
from discord.ext import commands
from discord import app_commands
import random
import string
import asyncio
from typing import Optional


class Nicktroll(commands.Cog):
    """Rename a user to a random string of characters"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="nicktroll", description="Generates a temporary nickname for a user"
    )
    @app_commands.checks.bot_has_permissions(manage_nicknames=True)
    @app_commands.describe(member="The member to troll", name="A nick to give")
    async def nicktroll(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        name: Optional[app_commands.Range[str, 1, 32]] = None,
    ):
        bot_member = interaction.guild.me
        if (
            bot_member.top_role <= member.top_role
            or member.id == interaction.guild.owner_id
        ):
            await interaction.response.send_message(
                "❌ Can't do that, that member's top role is either equal to or higher than my top role."
            )
            return
        else:
            if name is None:
                name = "".join(
                    random.choices(string.ascii_letters + string.digits, k=10)
                )

            original_nick = member.display_name
            await member.edit(nick=name)

            await interaction.response.send_message(
                f"Nickname was changed for {member} to **{name}** for 3 minutes. "
            )
            await asyncio.sleep(180.0)

            await member.edit(nick=original_nick)


async def setup(bot):
    await bot.add_cog(Nicktroll(bot))
