from discord.ext import commands
from db.client import make_engine


class Connection(commands.Cog):
    """Handle listeners for connection events"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_shard_resumed(self, shard_id):
        # reset db connection to prevent ws timeout
        self.bot.engine.dispose()
        self.bot.engine = make_engine(loc=self.bot.db_loc)
        self.bot.logger.info(f"Shard {shard_id} resumed. Reset DB connection.")


async def setup(bot):
    await bot.add_cog(Connection(bot))
