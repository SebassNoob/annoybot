from dotenv import load_dotenv
from discord.ext import commands, tasks
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

    @send_logs.before_loop
    async def before_send_logs(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Scheduler(bot))
