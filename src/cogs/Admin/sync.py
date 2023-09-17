from discord.ext import commands


class Sync(commands.Cog):
    """Command syncing local command tree with discord"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.send("attempting to sync...")
        await self.bot.tree.sync()
        await ctx.send("synced!")


async def setup(bot):
    await bot.add_cog(Sync(bot))
