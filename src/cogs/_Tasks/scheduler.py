from dotenv import load_dotenv
from db.client import make_engine
import discord
from discord.ext import commands, tasks
from db.models import Snipe, Hello
from sqlalchemy.orm import Session
import os
import datetime
import asyncio
import io

load_dotenv(f"{os.getcwd()}/.env.local")


class Scheduler(commands.Cog):
    """Handle jobs that require to be run at a specific time"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.send_logs.start()
        self.clear_snipe.start()
        self.disconnect_voice.start()
        self.update_stats.start()
        self.reset_db_connection.start()
        self.test_db_connection.start()

    @tasks.loop(hours=3)
    async def send_logs(self):
        """Send logs to the support server"""
        url = os.getenv("WEBHOOK_LOGS")
        if url is None:
            self.bot.logger.warning("No webhook url found for logs")
            return

        wh = discord.Webhook.from_url(url, client=self.bot)

        # read the logs
        # for some godforsaken reason, discord.File can't read the contents of the file unless explicitly opened and passed
        # this occurs only when update_stats is running
        with open(f"{os.getcwd()}/logs/discord.log", "r") as f:
            logs = f.read()
        await wh.send(
            content=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            file=discord.File(io.StringIO(logs), "logs.txt"),
        )

        self.bot.logger.info("Logs sent to the support server")

    @tasks.loop(hours=24, reconnect=False)
    async def clear_snipe(self):
        """Clear snipe cache"""
        with Session(self.bot.engine) as session:
            session.query(Snipe).delete()
            session.commit()

    @tasks.loop(minutes=5, reconnect=False)
    async def disconnect_voice(self):
        """Disconnect from voice channels"""
        for guild in self.bot.guilds:
            if guild.voice_client is not None and not guild.voice_client.is_playing():
                await guild.voice_client.disconnect()

    @tasks.loop(hours=1, reconnect=False)
    async def update_stats(self):
        """Update server count on status"""
        await self.bot.change_presence(
            activity=discord.Game(
                name=f"/help | annoying {self.bot.curr_guilds} servers"
            )
        )
        self.bot.logger.info("Updated stats")

    @tasks.loop(minutes=10)
    async def reset_db_connection(self):
        """Reset the database connection"""
        self.bot.engine.dispose()
        self.bot.engine = make_engine(loc=self.bot.db_loc)
        self.bot.logger.info("Reset DB connection")

    @tasks.loop(minutes=60)
    async def test_db_connection(self):
        """Test the database connection"""
        msg = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        try:
            with Session(self.bot.engine) as session:
                session.add(Hello(msg=msg))
                session.commit()
                res = session.query(Hello).where(Hello.msg == msg).first()

                self.bot.logger.info("Tested DB connection, result: %s", res)

        except Exception as e:
            self.bot.logger.error("Tested DB connection, error: %s", e)
            raise SystemExit(1)

    @test_db_connection.before_loop
    async def before_test_db_connection(self):
        await self.bot.wait_until_ready()

    @reset_db_connection.before_loop
    async def before_reset_db_connection(self):
        await self.bot.wait_until_ready()

    @send_logs.before_loop
    async def before_send_logs(self):
        await self.bot.wait_until_ready()

        # wait until the log file is created
        while not os.path.exists(f"{os.getcwd()}/logs/discord.log"):
            await asyncio.sleep(1)

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
