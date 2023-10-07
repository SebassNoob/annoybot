import discord
from discord.ext import commands
from discord import app_commands
import random
from typing import Optional
from src.utils import check_usersettings_cache
import datetime


class Fakemute(commands.Cog):
    """Fake mutes a user"""

    def __init__(self, bot):
        self.bot = bot
        self.reasons = (
            "Too annoying in chat.",
            "Being a absolute idiot",
            "Having an opinion.",
            "Needing help.",
            "Farting in vc",
            "Breaking rule class 'c' section 'f' rule '12-02'. ",
            "Being the alpha male",
            "wearing a condom and livestreaming it.",
        )

    @app_commands.command(name="fakemute", description="Fakes a mute for a user")
    @app_commands.describe(user="The user to 'mute'")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    async def fakemute(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        reason: Optional[str] = None,
    ):
        # check subset of permissions or role
        if (
            interaction.guild.me.top_role <= user.top_role
            or user.guild_permissions.administrator
        ):
            await interaction.response.send_message(
                "❌ Can't do that, that member's top role is either equal to or higher than my top role."
            )
            return

        if not reason:
            reason = random.choice(self.reasons)

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]
        em = (
            discord.Embed(color=int(color, 16))
            .add_field(
                name="**Mute**",
                value=f"**Offender:** {user.mention}\n**Reason:** {reason}\n**Responsible mod:** {interaction.user.display_name}",
                inline=False,
            )
            .set_footer(text="imagine")
        )
        try:
            await user.timeout(datetime.timedelta(seconds=1))
        except:
            await interaction.response.send_message(
                "user timeout failed, probably due to missing permissions", embed=em
            )
            return

        await interaction.response.send_message(embed=em)


async def setup(bot):
    await bot.add_cog(Fakemute(bot))
