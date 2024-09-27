from sqlalchemy.orm import Session
from db.models import UserSettings
from discord.ext import commands


class Countusers(commands.Cog):
    """Command for getting user count"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def countusers(self, ctx):
        with Session(self.bot.engine) as session:
          cnt = session.query(UserSettings).count()
          await ctx.send(f"User count: {cnt}")


async def setup(bot):
    await bot.add_cog(Countusers(bot))
