import sys
from discord.ext import commands


class Sysexit(commands.Cog):
    """Command for killing bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sysexit(self, ctx, code: int = 1):
        await ctx.send("Bot has been taken offline.")
        sys.exit(code)


async def setup(bot):
    await bot.add_cog(Sysexit(bot))
