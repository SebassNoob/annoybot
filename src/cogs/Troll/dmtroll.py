import discord
from discord.ext import commands
from discord import app_commands
from src.utils import check_usersettings_cache


class Dmtroll(commands.Cog):
    """Ping a user in a DM to annoy them"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dmtroll", description="pings a user in DMs once")
    @app_commands.describe(user="The user to ping")
    @app_commands.guild_only()
    async def dmtroll(self, interaction: discord.Interaction, user: discord.Member):
        block_dms = check_usersettings_cache(
            user=user,
            columns=["block_dms"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]
        if block_dms or user.bot:
            await interaction.response.send_message(
                content=f"❌ {user.display_name} that you mentioned is either a bot, or does not want to be DM'ed. Bet you look stupid now.",
                ephemeral=True,
            )
            return
        await interaction.response.defer()
        channel = await user.create_dm()

        try:
            await channel.send(
                f"{user.mention} hey 😏, did u like the ping sound?\n/dmtroll from {interaction.user.display_name} in {interaction.guild.name}"
            )
        except:
            await interaction.followup.send(
                content=f"❌ {user.display_name} blocked this bot from sending messages to them, lol pussy"
            )

        await interaction.followup.send(
            content="The trolled user has been pinged through dms lol."
        )


async def setup(bot):
    await bot.add_cog(Dmtroll(bot))
