import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
import asyncio

from sqlalchemy.orm import Session
from db.models import ServerSettings, UserServer, UserSettings, Autoresponse

from src.utils import add_user


class Serversettings(commands.Cog):
    """Shows server settings"""

    def __init__(self, bot):
        self.bot = bot

    server_group = app_commands.Group(
        name="serversettings",
        description="Shows the settings for this server",
        guild_only=True,
    )

    @server_group.command(name="menu", description="Shows the menu for server settings")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def s_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            autoresponse = (
                session.query(ServerSettings.autoresponse_on)
                .filter(ServerSettings.id == interaction.guild.id)
                .one()
            )[0]
            blacklist = (
                session.query(UserServer.user_id)
                .filter(
                    (UserServer.server_id == interaction.guild.id)
                    & (UserServer.blacklist == True)
                )
                .all()
            )
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]

        blacklist_ids = [x[0] for x in blacklist]
        blacklist = await asyncio.gather(
            *[interaction.client.fetch_user(uid) for uid in blacklist_ids]
        )
        blacklist_fmt = ", ".join([usr.mention for usr in blacklist]) or None

        em = discord.Embed(color=int(color, 16))
        em.set_author(name="Annoybot Server Settings")
        em.add_field(
            name="Autoresponse (autoresponse)",
            value=f"Current: **{autoresponse}**\nIf true, autoresponse will be enabled",
            inline=False,
        )
        em.add_field(
            name="Blacklisted users (blacklist)",
            value=f"Current list: **{blacklist_fmt}**\nBlacklists certain users from using annoybot commands.",
            inline=False,
        )

        await interaction.followup.send(embed=em, ephemeral=True)

    @server_group.command(
        name="autoresponse", description="Turns /autoresponse on or off"
    )
    @app_commands.describe(
        onoff="If true, turns autoresponse on, if false, turns it off"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def s_auto(self, interaction: discord.Interaction, onoff: bool):
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            # update the autoresponse_on column
            session.query(ServerSettings).filter(
                ServerSettings.id == interaction.guild.id
            ).update({"autoresponse_on": onoff})
            session.commit()

            # dump in cache if is turned on
        if onoff:
            contents = (
                session.query(Autoresponse.msg, Autoresponse.response)
                .filter(Autoresponse.server_id == interaction.guild.id)
                .all()
            )
            self.bot.autoresponses[interaction.guild.id] = {
                msg: response for msg, response in contents
            }
        else:
            del self.bot.autoresponses[interaction.guild.id]

        await interaction.followup.send(
            content=f"✅ autoresponse setting updated to **{onoff}**", ephemeral=True
        )

    @server_group.command(
        name="blacklist", description="Blacklists certain users from using the bot"
    )
    @app_commands.describe(
        modify="add/remove people from the blacklist",
        user="User to blacklist/unblacklist",
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    async def s_black(
        self,
        interaction: discord.Interaction,
        modify: Literal["add", "remove"],
        user: discord.Member,
    ):
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            bl = (
                session.query(UserServer.blacklist)
                .filter(
                    (UserServer.user_id == user.id)
                    & (UserServer.server_id == interaction.guild.id)
                )
                .one_or_none()
            )
            if bl is None:
                add_user(user, self.bot.engine)

                bl = False
            else:
                # get the blacklist value which is a tuple so we need to index it to 0
                bl = bl[0]

        if modify == "add":
            # cant ban yourself
            if user.id == interaction.user.id:
                await interaction.response.send_message(
                    "❌ You can't blacklist yourself, dumb.", ephemeral=True
                )
                return

            # cant blacklist twice
            if bl:
                await interaction.response.send_message(
                    "❌ This person is already blacklisted? Get good next time.",
                    ephemeral=True,
                )
                return

            # add to blacklist
            with Session(self.bot.engine) as session:
                session.query(UserServer).filter(
                    (UserServer.user_id == user.id)
                    & (UserServer.server_id == interaction.guild.id)
                ).update({"blacklist": True})
                session.commit()
            await interaction.followup.send(
                f"✅ Added {user.display_name} to blacklist", ephemeral=True
            )

        elif modify == "remove":
            # cant unban yourself
            if user.id == interaction.user.id:
                await interaction.response.send_message(
                    "❌ You can't unblacklist yourself, dumb.", ephemeral=True
                )
                return

            # cant unban someone who isnt banned
            if not bl:
                await interaction.response.send_message(
                    f"❌ {user.display_name} is not blacklisted???????", ephemeral=True
                )
                return

            with Session(self.bot.engine) as session:
                session.query(UserServer).filter(
                    (UserServer.user_id == user.id)
                    & (UserServer.server_id == interaction.guild.id)
                ).update({"blacklist": False})
                session.commit()

            await interaction.followup.send(
                f"✅ Removed {user.display_name} from blacklist", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(Serversettings(bot))
