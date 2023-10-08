from functools import lru_cache
import random
import datetime
import os

import discord
from discord.ext import commands


from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from db.models import UserServer, Snipe, UserSettings
from utils import HDict, parse_txt


class Message(commands.Cog):
    """Handle listeners for message events"""

    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot
        self.angry_responses = parse_txt(
            f"{os.getcwd()}/src/public/angry_responses.txt"
        )

    @staticmethod
    @lru_cache(maxsize=64)
    def handle_autoresponse(
        autoresponses_in_server: dict[str, str], message_content: str
    ) -> str | None:
        # server is guaranteed to be in the autoresponse_servers set due to earlier check
        # if message_content is in the autoresponses dict, return the value else None
        return autoresponses_in_server.get(message_content)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        # ignore bots
        if message.author.bot:
            return
        if (
            message
            and message.guild
            and message.guild.id in self.bot.autoresponse_servers
        ):
            response = self.handle_autoresponse(
                HDict(self.bot.autoresponses[message.guild.id]), message.content
            )
            if not message.channel.permissions_for(message.guild.me).send_messages:
                return
            if response:
                await message.channel.send(response)

        if self.bot.user.mention in message.content:
            if "help" in message.content:
                em = discord.Embed(
                    color=0x000555,
                    title="You need help? Get it yourself.",
                    description="Visit the [support server](https://discord.gg/UCGAuRXmBD), or use /help.",
                )
                em.set_footer(text="The embodiment of discord anarchy")
                await message.channel.send(embed=em)

            else:
                await message.channel.send(random.choice(self.angry_responses))

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        current_time = datetime.datetime.now()
        if isinstance(message.channel, discord.abc.GuildChannel):
            nsfw = message.channel.nsfw
        elif isinstance(message.channel, discord.Thread):
            nsfw = message.channel.parent.nsfw
        else:
            nsfw = True

        with Session(self.bot.engine) as session:
            try:
                usersettings_present = (
                    session.query(UserSettings)
                    .filter(UserSettings.id == message.author.id)
                    .one_or_none()
                )

                if message.guild:
                    userserver_present = (
                        session.query(UserServer)
                        .filter(
                            UserServer.user_id == message.author.id
                            or UserServer.server_id == message.guild.id
                        )
                        .first()
                    )
                snipe_present = (
                    session.query(Snipe)
                    .filter(Snipe.id == message.author.id)
                    .one_or_none()
                )
                # if the user is not in the db, add them
                if not usersettings_present:
                    session.add(
                        UserSettings(
                            id=message.author.id,
                            color="000000",
                            family_friendly=False,
                            sniped=True,
                            block_dms=False,
                        )
                    )
                    session.commit()

                if message.guild and not userserver_present:
                    session.add(
                        UserServer(
                            user_id=message.author.id,
                            server_id=message.guild.id,
                            blacklist=False,
                        )
                    )
                    session.commit()
                if not snipe_present:
                    session.add(
                        Snipe(
                            id=message.author.id,
                            msg=message.content,
                            date=current_time,
                            nsfw=nsfw,
                        )
                    )
                else:
                    session.query(Snipe).filter(Snipe.id == message.author.id).update(
                        {
                            Snipe.msg: message.content,
                            Snipe.date: current_time,
                            Snipe.nsfw: nsfw,
                        }
                    )
                session.commit()
            except IntegrityError as e:
                session.rollback()
                self.bot.logger.error(e)


async def setup(bot):
    await bot.add_cog(Message(bot))
