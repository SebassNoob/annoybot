from dotenv import load_dotenv
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

    @tasks.loop(hours=12, reconnect=False)
    async def send_logs(self):
        """Send logs to the support server"""
        url = os.getenv("WEBHOOK_LOGS")
        if url is None:
            self.bot.logger.warning("No webhook url found for logs")
            return

        files = {
            "payload_json": json.dumps(
                {
                    "content": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                }
            ),
            "files[0]": open(f"{os.getcwd()}/logs/discord.log", "rb"),
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=files) as response:
                if response.status not in [200, 204]:
                    self.bot.logger.warning(
                        f"Failed to send logs to the support server. Status code: {response.status}"
                    )
                    return
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
