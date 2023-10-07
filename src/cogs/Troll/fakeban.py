import discord
from discord.ext import commands
from discord import app_commands
from src.utils import check_usersettings_cache
import datetime
import asyncio


class Fakeban(commands.Cog):
    """Fake bans a user"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="fakeban", description="Fakes a ban for a user")
    @app_commands.describe(user="The user to 'ban'")
    @app_commands.guild_only()
    @app_commands.checks.bot_has_permissions(
        moderate_members=True, manage_nicknames=True
    )
    async def fakeban(self, interaction: discord.Interaction, user: discord.Member):
        if (
            interaction.guild.me.top_role <= user.top_role
            or interaction.guild.owner_id == user.id
        ):
            await interaction.response.send_message(
                "❌ Can't do that, that member's top role is either equal to or higher than my top role."
            )
            return

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]
        em = discord.Embed(color=int(color, 16))

        em.add_field(
            name="**Ban**",
            value=f"**Offender:** {user.mention}\n**Responsible mod:** {interaction.user.display_name}",
            inline=False,
        )

        em.set_footer(text="imagine")

        original_nick = user.display_name
        await user.edit(nick=f"!<{user.id}>")

        try:
            await user.timeout(datetime.timedelta(seconds=1))
        except:
            await interaction.response.send_message(
                "user timeout failed, probably due to missing permissions", embed=em
            )
            return

        await interaction.response.send_message(embed=em)
        try:
            await self.bot.wait_for(
                "message", check=lambda m: m.author == user, timeout=180
            )
        except asyncio.TimeoutError:
            pass
        finally:
            await user.edit(nick=original_nick)


async def setup(bot):
    await bot.add_cog(Fakeban(bot))
