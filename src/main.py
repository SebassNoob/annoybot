import dotenv
import os
import sys

# load environment variables from .env file
dotenv.load_dotenv(f"{os.getcwd()}/.env")
dotenv.load_dotenv(f"{os.getcwd()}/.env.local")

# check if the bot is running in production mode
if len(sys.argv) > 1 and "--prod" in sys.argv:
    PROD = True
else:
    PROD = False

import discord
from discord.ext import commands
from discord import app_commands

import collections
import logging
from logging.handlers import TimedRotatingFileHandler

# add parent directory to path
sys.path.insert(1, os.getcwd())
from db.client import make_engine

from src.checks import (
    add_users_to_db_wrapped_engine,
    custom_cooldown,
    blacklist_check_wrapped_engine,
    check_guilds_not_in_db,
)
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from db.models import Autoresponse, ServerSettings, UserServer

from utils import read_csv


# initialize bot
class Bot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(
            command_prefix="a$", intents=intents, shard_count=1, help_command=None
        )
        # make a logger and a database engine for the bot
        self.logger = logging.getLogger("bot")

        # if env is PROD, use the production database, else use the development database
        loc = os.getenv("PROD_DB_LOC") if PROD else os.getenv("DEV_DB_LOC")
        self.engine = make_engine(loc=loc)
        self.curr_guilds = 0

    async def on_ready(self):
        self.curr_guilds = len(self.guilds)

        self.logger.info(f"* {self.user} connected to {self.curr_guilds} servers")

        count = collections.Counter([guild.shard_id for guild in self.guilds])

        for t in count.items():
            self.logger.info(f"   - Shard {t[0]}: {t[1]} servers")

        # sync guilds
        guilds_not_in_db = check_guilds_not_in_db(self.engine, self.guilds)
        for guild in guilds_not_in_db:
            await self.on_guild_join(guild, send_welcome=False)

        # add checks to commands
        for cmd in self.tree.walk_commands():
            if not isinstance(cmd, app_commands.Group):
                cmd.add_check(add_users_to_db_wrapped_engine(self.engine))
                cmd.add_check(blacklist_check_wrapped_engine(self.engine))

            cmd = app_commands.checks.dynamic_cooldown(custom_cooldown)(cmd)

        self.tree.on_error = self.err_handler_wrapped()

        await self.change_presence(
            activity=discord.Game(name=f"/help | annoying {self.curr_guilds} servers")
        )

    async def send_welcome(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                with open(f"{os.getcwd()}/src/static/welcome_message.txt", "r") as w:
                    em = discord.Embed(
                        color=0x000555,
                        title="A very suitable welcome message",
                        description=w.read(),
                    )
                em.set_footer(text="The embodiment of discord anarchy")
                await channel.send(embed=em)
                return
        # if there is no channel where the bot is allowed to send the welcome message in, ignore and log the server
        self.logger.warning(f"failed to send welcome to {guild.name}: {guild.id}")

    async def on_guild_join(self, guild, send_welcome=True):
        self.logger.info(f"joined {guild.name}: {guild.id}")
        self.curr_guilds += 1

        # create server settings
        with Session(self.engine) as session:
            session.add(ServerSettings(id=guild.id, autoresponse_on=False))

            # add default autoresponses
            default = read_csv(f"{os.getcwd()}/src/public/default_autoresponse.csv")
            res = []
            for msg, response in default:
                res.append(Autoresponse(server_id=guild.id, msg=msg, response=response))
            session.add_all(res)
            session.commit()
        if send_welcome:
            await self.send_welcome(guild)

    async def on_guild_remove(self, guild):
        self.logger.info(f"left {guild.name}: {guild.id}")
        self.curr_guilds -= 1

        # delete server settings
        with Session(self.engine) as session:
            session.query(Autoresponse).filter(
                Autoresponse.server_id == guild.id
            ).delete()
            session.query(ServerSettings).filter(ServerSettings.id == guild.id).delete()
            session.query(UserServer).filter(UserServer.server_id == guild.id).delete()
            session.commit()

    def err_handler_wrapped(self):
        async def err_handler(
            interaction: discord.Interaction, error: app_commands.AppCommandError
        ):
            if isinstance(error, IntegrityError):
                # shit db is fucked in the head

                self.logger.error(error)
                return
            else:
                em = discord.Embed(
                    color=0x000000,
                    title="Unknown error.",
                    description=f"This has been reported to the [support server](https://discord.gg/UCGAuRXmBD). Please join and provide the context on what happened and how to reproduce it.\n\nIf not, try giving the bot permissions as laid out in /help, or kick and re-add the bot.\n\nCommand: {error.command.name if hasattr(error, 'command') else 'unknown'}\nFull traceback:\n```{error}```\n",
                )
                await interaction.channel.send(embed=em)
                channel = self.get_channel(953214132058992670)
                self.logger.error(
                    40,
                    f"Command: {error.command.name if hasattr(error, 'command') else 'unknown'}\nFull traceback:\n{error}",
                )
                await channel.send(embed=em)
                return

        return err_handler

    # load cogs
    async def setup_hook(self):
        # iterate through all the folders in the cogs directory
        for category in os.listdir("./src/cogs"):
            # filter out non-python files in the folder
            files = list(
                filter(
                    lambda file: file.endswith(".py"),
                    os.listdir(f"./src/cogs/{category}"),
                )
            )
            # load each cog in the folder
            for filename in files:
                try:
                    await bot.load_extension(f"cogs.{category}.{filename[:-3]}")
                except Exception as e:
                    self.logger.exception(f"{filename} failed to load: {e}")
                self.logger.info(f"{category}.{filename} loaded")


# 2 different log handlers for logging to file (manual error) and stdout (client error)
if not os.path.exists("./logs"):
    os.makedirs("./logs")
event_handler = TimedRotatingFileHandler(
    filename="logs/discord.log", when="D", encoding="utf-8"
)
stdout = logging.StreamHandler(sys.stdout)

# initiate bot and run
bot = Bot()
bot.logger.setLevel(logging.INFO)
bot.logger.addHandler(event_handler)
bot.logger.addHandler(stdout)
bot.run(os.getenv("TOKEN"), reconnect=True, log_handler=stdout, log_level=logging.INFO)
