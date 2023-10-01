import os
import discord
from discord.ext import commands
from discord import app_commands
from better_profanity import profanity
from src.utils import check_usersettings_cache
from sqlalchemy.orm import Session
from db.models import UserSettings, Snipe


class Snipes(commands.Cog):
    """Snipe a deleted message"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="snipe", description="Sends the most recently deleted messaage of a user."
    )
    @app_commands.guild_only()
    @app_commands.describe(user="The user you want to snipe")
    async def snipe(self, interaction: discord.Interaction, user: discord.Member):
        with Session(self.bot.engine) as session:
            # check if user can be sniped
            res = (
                session.query(
                    UserSettings.sniped,
                )
                .filter(UserSettings.id == user.id)
                .one_or_none()
            )
            sniped = res[0] if res is not None else True

            # check if user can be sniped
            if not sniped:
                await interaction.response.send_message(
                    "❌ This guy can't be sniped, what a loser. (/settings sniped False)"
                )
                return

            # check if user deleted a message recently
            res = (
                session.query(
                    Snipe.msg,
                    Snipe.date,
                    Snipe.nsfw,
                )
                .filter(Snipe.id == user.id)
                .one_or_none()
            )

            if res is None:
                await interaction.response.send_message("❌ There's nothing to snipe!")
                return

            message, time, nsfw = res

            # check if 1. user deleted a message in a nsfw channel and 2. the channel is not nsfw
            if (
                nsfw
                and isinstance(
                    interaction.channel, (discord.abc.GuildChannel, discord.Thread)
                )
                and not interaction.channel.nsfw
            ):
                await interaction.response.send_message(
                    f"{user.display_name} last deleted their message in a nsfw channel. 🔞"
                )
                return

            ff, color = check_usersettings_cache(
                user=interaction.user,
                columns=["family_friendly", "color"],
                engine=self.bot.engine,
                redis_client=self.bot.redis_client,
            )

        if ff:
            message = profanity.censor(message)

        embed = discord.Embed(color=int(color, 16), description=message, timestamp=time)

        embed.set_author(name=f"Quote from {user.name}", icon_url=user.display_avatar)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Snipes(bot))
