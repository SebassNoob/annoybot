import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import check_usersettings_cache


class Ratio(commands.Cog):
    """Ratio a message"""

    def __init__(self, bot):
        self.bot = bot
        self.accompany = (
            "No one cares",
            "Shut the fuck up",
            "L",
            "Who asked?",
            "Your opinion is invalid",
            "No one gives 2 shits about your opinion",
            "Get good",
            "Uninstall discord mate",
            "Really? nobody asked",
        )
        self.ratio_cmd = app_commands.ContextMenu(name="ratio", callback=self.ratio)
        self.bot.tree.add_command(self.ratio_cmd)

    @app_commands.checks.bot_has_permissions(
        read_message_history=True, add_reactions=True
    )
    async def ratio(self, interaction: discord.Interaction, message: discord.Message):
        if len(message.content) == 0:
            await interaction.response.send_message(
                "This message is empty?", ephemeral=True
            )
            return

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]
        em = discord.Embed(
            color=int(color, 16),
            description=f"'{message.content}'\n**{random.choice(self.accompany)} + ratio**",
        )

        em.set_author(
            name=f"Replying to {message.author.name}",
            icon_url=message.author.display_avatar,
        )
        await interaction.response.send_message(embed=em)

        await (await interaction.original_response()).add_reaction("👍")


async def setup(bot):
    await bot.add_cog(Ratio(bot))
