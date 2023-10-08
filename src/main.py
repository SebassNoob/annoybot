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
import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler


# add parent directory to path
sys.path.insert(1, os.getcwd())
from db.client import make_engine
from db.models import ServerSettings, Autoresponse
from src.utils import page_query

from src.checks import (
    add_users_to_db_wrapped_engine,
    custom_cooldown,
    blacklist_check_wrapped_engine,
)

from sqlalchemy.orm import Session

from db.cache import get_redis


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

        # connect to redis with the appropriate uri and port
        redis_uri = os.getenv("PROD_CACHE_URI") if PROD else os.getenv("DEV_CACHE_URI")
        redis_port = (
            int(os.getenv("PROD_CACHE_PORT"))
            if PROD
            else int(os.getenv("DEV_CACHE_PORT"))
        )
        retry = True if PROD else False
        self.redis_client = get_redis(redis_uri, redis_port, retry_on_error=retry)

        # block until redis is ready
        self.redis_client.block_until_ready(check_interval=0.2, logger=self.logger)

        self.curr_guilds = 0

        with Session(self.engine) as session:
            self.autoresponse_servers = set(
                [
                    i[0]
                    for i in page_query(
                        session.query(ServerSettings.id).filter(
                            ServerSettings.autoresponse_on
                        )
                    )
                ]
            )
            raw = page_query(
                (session.query(Autoresponse)).filter(
                    Autoresponse.server_id.in_(self.autoresponse_servers)
                )
            )

            # map raw[0] which is a server id to a dict of all the autoresponses
            # acts as a cache
            self.autoresponses = collections.defaultdict(dict)
            for autoresponse in raw:
                self.autoresponses[autoresponse.server_id][
                    autoresponse.msg
                ] = autoresponse.response

    async def on_ready(self):
        self.curr_guilds = len(self.guilds)

        self.logger.info(f"* {self.user} connected to {self.curr_guilds} servers")

        count = collections.Counter([guild.shard_id for guild in self.guilds])

        for t in count.items():
            self.logger.info(f"   - Shard {t[0]}: {t[1]} servers")

        # add checks to commands
        for cmd in self.tree.walk_commands():
            if not isinstance(cmd, app_commands.Group):
                cmd.add_check(add_users_to_db_wrapped_engine(self.engine))
                cmd.add_check(blacklist_check_wrapped_engine(self.engine))

            cmd = app_commands.checks.dynamic_cooldown(custom_cooldown)(cmd)

        await self.change_presence(
            activity=discord.Game(name=f"/help | annoying {self.curr_guilds} servers")
        )

    # load cogs
    async def setup_hook(self):
        # iterate through all the folders in the cogs directory
        cogs = []
        for category in os.listdir("./src/cogs"):
            # filter out non-python files in the folder
            files = list(
                filter(
                    lambda file: file.endswith(".py"),
                    os.listdir(f"./src/cogs/{category}"),
                )
            )
            cogs += [f"cogs.{category}.{file[:-3]}" for file in files]

        # load all the cogs asynchronously
        res = await asyncio.gather(
            *[bot.load_extension(cog) for cog in cogs], return_exceptions=True
        )

        # output any errors
        for exe in filter(lambda x: isinstance(x, Exception), res):
            self.logger.error(exe)

        # log how many cogs were loaded (if loading was successful, the load_extension function returns None)
        self.logger.info(f"Loaded {len(tuple(filter(lambda x: x is None, res)))} cogs")


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
