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

    async def on_ready(self):
        servers = len(self.guilds)
        self.logger.info(f"* {self.user} connected to {servers} servers")

        count = collections.Counter([guild.shard_id for guild in self.guilds])

        for t in count.items():
            self.logger.info(f"   - Shard {t[0]}: {t[1]} servers")

        await self.change_presence(
            activity=discord.Game(name=f"/help | annoying {servers} servers")
        )

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
