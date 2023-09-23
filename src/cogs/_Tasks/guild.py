import os
import discord
from discord.ext import commands, tasks


from sqlalchemy.orm import Session
from db.models import Autoresponse, ServerSettings, UserServer

from src.utils import read_csv
from src.checks import check_guilds_not_in_db


class Guild(commands.Cog):
    """Handle listeners for guild events"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.check_guilds.start()

    async def send_welcome(self, guild):
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                with open(f"{os.getcwd()}/src/static/welcome_message.txt", "r") as w:
                    em = discord.Embed(
                        color=0x000555,
                        title="A very suitable welcome message",
                        description=w.read(),
                    )
                em.set_footer(text="The embodiment of discord anarchy")
                await channel.send(embed=em)
                return
        # if there is no channel where the bot is allowed to send the welcome message in, ignore and log the server
        self.logger.warning(f"failed to send welcome to {guild.name}: {guild.id}")

    @commands.Cog.listener()
    async def on_guild_join(self, guild, send_welcome=True):
        self.bot.logger.info(f"joined {guild.name}: {guild.id}")
        self.bot.curr_guilds += 1

        # create server settings
        with Session(self.bot.engine) as session:
            session.add(ServerSettings(id=guild.id, autoresponse_on=False))

            # add default autoresponses
            default = read_csv(f"{os.getcwd()}/src/public/default_autoresponse.csv")
            res = [
                Autoresponse(server_id=guild.id, msg=msg, response=response)
                for msg, response in default
            ]

            session.add_all(res)
            session.commit()
        if send_welcome:
            await self.send_welcome(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.bot.logger.info(f"left {guild.name}: {guild.id}")
        self.bot.curr_guilds -= 1

        # delete server settings
        with Session(self.bot.engine) as session:
            session.query(Autoresponse).filter(
                Autoresponse.server_id == guild.id
            ).delete()
            session.query(UserServer).filter(UserServer.server_id == guild.id).delete()
            session.query(ServerSettings).filter(ServerSettings.id == guild.id).delete()
            session.commit()

    @tasks.loop(count=1)
    async def check_guilds(self):
        # sync guilds on load
        guilds_not_in_db = check_guilds_not_in_db(self.bot.engine, self.bot.guilds)
        for guild in guilds_not_in_db:
            await self.on_guild_join(guild, send_welcome=False)

    # wait until startup is done to ensure self.bot.guilds is populated
    @check_guilds.before_loop
    async def before_check_guilds(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(Guild(bot))
