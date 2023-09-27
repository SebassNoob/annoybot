import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands.errors import CheckFailure, CommandOnCooldown

from sqlalchemy.exc import IntegrityError


class Error(commands.Cog):
    """Handle listeners for error events"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.bot.tree.on_error = self.err_handler_wrapped()

    def err_handler_wrapped(self):
        async def err_handler(
            interaction: discord.Interaction, error: app_commands.AppCommandError
        ):
            if isinstance(error, IntegrityError):
                # shit db is fucked in the head

                self.bot.logger.error(error)
                return
            if isinstance(error, CommandOnCooldown):
                self.bot.logger.error("Here")
                em = discord.Embed(
                    color=0x000000,
                    description="You have exceeded this command's ratelimits. Try again in **%.1fs** cooldown."
                    % error.retry_after,
                )

                await interaction.response.send_message(embed=em)
                return
            if isinstance(error, CheckFailure):
                # ignore error if blacklist check fails
                # this check is after commandoncooldown because it inherits from checkfailure
                return
            em = discord.Embed(
                color=0x000000,
                title="Unknown error.",
                description=f"This has been reported to the [support server](https://discord.gg/UCGAuRXmBD). Please join and provide the context on what happened and how to reproduce it.\n\nIf not, try giving the bot permissions as laid out in /help, or kick and re-add the bot.\n\nCommand: {error.command.name if hasattr(error, 'command') else 'unknown'}\nFull traceback:\n```{error}```\n",
            )
            await interaction.channel.send(embed=em)
            channel = self.bot.get_channel(953214132058992670)
            self.bot.logger.error(
                40,
                f"Command: {error.command.name if hasattr(error, 'command') else 'unknown'}\nFull traceback:\n{error}",
            )
            await channel.send(embed=em)
            return

        return err_handler

    # only occurs for message commands
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send(error)


async def setup(bot):
    await bot.add_cog(Error(bot))
