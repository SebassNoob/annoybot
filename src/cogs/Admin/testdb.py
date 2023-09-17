from discord.ext import commands
from sqlalchemy.orm import Session
import os
import sys

sys.path.insert(1, f"{os.getcwd()}/db")
from db.models.hello import Hello


class Testdb(commands.Cog):
    """Insert a test value into the test db and emit the result"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def testdb(self, ctx):
        with Session(self.bot.engine) as session:
            session.add(Hello(msg="Hello World!"))
            session.commit()
            res = session.query(Hello).all()
            await ctx.send(res)


async def setup(bot):
    await bot.add_cog(Testdb(bot))
