from discord.ext import commands
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
import sys
import io
import discord


sys.path.insert(1, f"{os.getcwd()}/db")
from db.models import Hello


class Testdb(commands.Cog):
    """Insert a test value into the test db and emit the result"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def testdb(self, ctx, *query: str):
        with Session(self.bot.engine) as session:
            # if no query is given, insert a test value and emit the entire table
            if len(query) == 0:
                session.add(Hello(msg="Hello World!"))
                session.commit()
                res = session.query(Hello).all()
                await ctx.send(res)
                return
            sql = text(" ".join(query))
            res = session.execute(sql).all().__repr__()
            f = discord.File(io.StringIO(res), "query.txt")
            await ctx.send(file=f)


async def setup(bot):
    await bot.add_cog(Testdb(bot))
