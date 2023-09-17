import io
import discord
from discord.ext import commands


class Servers(commands.Cog):
    """Command for getting name and id about servers the bot is in"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def servers(self, ctx):
        servers = "".join([f"{s.name}: {s.id}\n" for s in self.bot.guilds])

        f = discord.File(io.StringIO(servers), "servers.txt")

        await ctx.send("file created", file=f)


async def setup(bot):
    await bot.add_cog(Servers(bot))
