from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from db.models import Snipe
from sqlalchemy.orm import Session
import os
import aiohttp
import datetime
import json

load_dotenv(f"{os.getcwd()}/.env.local")


class Scheduler(commands.Cog):
    """Handle jobs that require to be run at a specific time"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.send_logs.start()
        self.clear_snipe.start()
        self.disconnect_voice.start()

    @tasks.loop(hours=3, reconnect=False)
    async def send_logs(self):
        """Send logs to the support server"""
        url = os.getenv("WEBHOOK_LOGS")
        if url is None:
            self.bot.logger.warning("No webhook url found for logs")
            return

        wh = discord.Webhook.from_url(url, client=self.bot)
        await wh.send(
            content=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            file=discord.File(f"{os.getcwd()}/logs/discord.log"),
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

    @send_logs.before_loop
    async def before_send_logs(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
