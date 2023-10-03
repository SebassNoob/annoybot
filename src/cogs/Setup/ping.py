import discord
from discord.ext import commands
from discord import app_commands
from src.utils import check_usersettings_cache


class Ping(commands.Cog):
    """Ping the bot"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ping", description="Shows connectivity information of the bot"
    )
    async def ping(self, interaction: discord.Interaction):
        shard = self.bot.get_shard(interaction.guild.shard_id)
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]
        em = discord.Embed(
            color=int(color, 16),
            description=f"Pong!🏓\nPing: {round(shard.latency * 1000)}ms\nShard {shard.id} of {shard.shard_count}",
        )

        await interaction.response.send_message(embed=em)


async def setup(bot):
    await bot.add_cog(Ping(bot))
