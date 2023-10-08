import discord
import os
from discord import app_commands
from discord import Guild
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List


import dotenv

dotenv.load_dotenv(f"{os.getcwd()}/.env")

from db.models import UserServer, UserSettings, ServerSettings
from src.utils import page_query


# wraps add_users_to_db to pass in the engine
def add_users_to_db_wrapped_engine(engine: Engine):
    async def add_users_to_db(interaction: discord.Interaction):
        with Session(engine) as session:
            try:
                usersettings_present = (
                    session.query(UserSettings)
                    .filter(UserSettings.id == interaction.user.id)
                    .one_or_none()
                )

                if interaction.guild:
                    userserver_present = (
                        session.query(UserServer)
                        .filter(
                            (UserServer.user_id == interaction.user.id)
                            & (UserServer.server_id == interaction.guild.id)
                        )
                        .first()
                    )

                # if the user is not in the db, add them
                if not usersettings_present:
                    session.add(
                        UserSettings(
                            id=interaction.user.id,
                            color="000000",
                            family_friendly=False,
                            sniped=True,
                            block_dms=False,
                        )
                    )
                    session.commit()
                if interaction.guild and not userserver_present:
                    session.add(
                        UserServer(
                            user_id=interaction.user.id,
                            server_id=interaction.guild.id,
                            blacklist=False,
                        )
                    )
                    session.commit()
            except IntegrityError as e:
                session.rollback()
                raise Exception(e)

        # should always return True
        # This always executes before blacklist_check
        return True

    return add_users_to_db


def blacklist_check_wrapped_engine(engine: Engine):
    async def blacklist_check(interaction: discord.Interaction):
        if not interaction.guild:
            return True

        with Session(engine) as session:
            try:
                userserver = (
                    session.query(UserServer)
                    .filter(
                        (UserServer.user_id == interaction.user.id)
                        & (UserServer.server_id == interaction.guild.id)
                    )
                    .one()
                )
                if userserver.blacklist:
                    em = discord.Embed(
                        color=0x000000,
                        description=f"You have been banned from using this bot in this server: {interaction.guild.name}\nAsk the mods to unban you (/serversettings) or use this bot in another server.",
                    )
                    await interaction.response.send_message(embed=em, ephemeral=True)
                    return False
            except IntegrityError as e:
                session.rollback()
                raise Exception(e)
        return True

    return blacklist_check


async def custom_cooldown(interaction: discord.Interaction):
    if interaction.user.id == int(os.getenv("OWNER_ID")):
        return None

    if interaction.command.name in ("fakeban", "fakemute"):
        return app_commands.Cooldown(2, 30)

    # get the support server guild object
    guild = interaction.client.get_guild(858200514914287646)
    if guild and guild.get_member(interaction.user.id) is not None:
        return app_commands.Cooldown(12, 30)

    return app_commands.Cooldown(7, 30)


def check_guilds_not_in_db(engine: Engine, guilds: List[Guild]):
    """Returns which guilds are not in DB"""
    with Session(engine) as session:
        db_guild_ids = page_query(session.query(ServerSettings.id))
        flat_db_guild_ids = [g[0] for g in db_guild_ids]
        return [g for g in guilds if g.id not in flat_db_guild_ids]
