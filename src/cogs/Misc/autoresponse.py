import discord
from discord.ext import commands
from discord import app_commands
from src.utils import check_usersettings_cache
from typing import Optional
import io

from sqlalchemy.orm import Session
from db.models import UserSettings, Autoresponse, ServerSettings


class Confirm(discord.ui.View):
    """A view that adds confirm and cancel buttons to a message. Used in /autoresponse resetdb"""

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.value = None
        self.interaction = interaction

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                "Not your button, dumbass", ephemeral=True
            )
            return
        await interaction.response.send_message("Confirming", ephemeral=True)

        self.value = True

        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                "Not your button, dumbass", ephemeral=True
            )
            return
        await interaction.response.send_message("Cancelling", ephemeral=True)
        self.value = False
        self.stop()


class Autoresponses(commands.Cog):
    """Autoresponses to certain messages"""

    def __init__(self, bot):
        self.bot = bot

    autoresponse = app_commands.Group(
        name="autoresponse",
        description="Responds to certain keywords guild-wide and sends a message in return.",
        guild_only=True,
    )

    def autoresponse_ui_handler(
        self, interaction: discord.Interaction, key_values: list[tuple[str, str]]
    ) -> tuple[discord.Embed, Optional[discord.File]]:
        if len(key_values) == 0:
            desc = "Nothing to see here! Try adding something."
        else:
            desc = "ID/Keyword: Response\n"
            desc += "\n".join(
                [f"{i} {row[0]}: {row[1]}" for i, row in enumerate(key_values)]
            )

        f = discord.File(io.StringIO(desc), "table.txt") if len(desc) > 4000 else None

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        em = discord.Embed(
            color=int(color, 16),
            description=f"``{desc if len(desc) <= 4000 else 'The autoresponse table is too large. The table will be sent as an attachment'}``",
        )
        em.set_author(name="Autoresponse keywords")
        em.set_footer(
            text="Mods can turn this off in /serversettings and edit with /autoresponse add or /autoresponse remove"
        )
        return em, f

    @autoresponse.command(
        name="menu",
        description="A list of words the bot will respond to in your server.",
    )
    @app_commands.checks.bot_has_permissions(read_messages=True)
    async def auto_menu(self, interaction: discord.Interaction):
        await interaction.response.defer()
        content = "Here is the list of autoresponse keywords. Mods can turn this off in ``/serversettings`` and edit with ``/autoresponse add`` or ``/autoresponse remove``"
        with Session(self.bot.engine) as session:
            on = (
                session.query(ServerSettings.autoresponse_on)
                .filter(ServerSettings.id == interaction.guild_id)
                .one()
            )[0]

            if not on:
                await interaction.followup.send(
                    content="⚠️ Autoresponse is turned off in this server. If you're a mod, turn it on in /serversettings",
                    ephemeral=True,
                )
                return
            # guaranteed to be not on -- not stored in cache
            key_values = (
                session.query(Autoresponse.msg, Autoresponse.response)
                .filter(Autoresponse.server_id == interaction.guild_id)
                .all()
            )

        em, f = self.autoresponse_ui_handler(interaction, key_values)
        if not f:
            await interaction.followup.send(content=content, embed=em)
            return
        await interaction.followup.send(content=content, embed=em, file=f)

    @autoresponse.command(name="add", description="Add autoresponse keywords")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(read_messages=True)
    @app_commands.describe(
        word="The word you want the bot to respond to",
        response="The resulting response to the aforementioned word",
    )
    async def add(
        self,
        interaction: discord.Interaction,
        word: app_commands.Range[str, 1, 1500],
        response: app_commands.Range[str, 1, 1500],
    ):
        await interaction.response.defer()

        content = f"✅ Added ``{word} : {response}``. Here is the new list."
        with Session(self.bot.engine) as session:
            if (
                session.query(Autoresponse)
                .filter(
                    Autoresponse.server_id == interaction.guild_id,
                    Autoresponse.msg == word,
                )
                .first()
            ):
                content += (
                    "\n⚠️ This word already exists. The response has been updated."
                )
                session.query(Autoresponse).filter(
                    Autoresponse.server_id == interaction.guild_id,
                    Autoresponse.msg == word,
                ).update({"response": response})
            else:
                session.add(
                    Autoresponse(
                        server_id=interaction.guild_id, msg=word, response=response
                    )
                )
            session.commit()

            # if cache has the word, add it
            # only if cache has the server else autoresponse is off
            if interaction.guild_id in self.bot.autoresponses:
                self.bot.autoresponses[interaction.guild_id][word] = response
                key_values = self.bot.autoresponses[interaction.guild_id].items()
            else:
                # if off, don't update cache and get from db
                key_values = (
                    session.query(Autoresponse.msg, Autoresponse.response)
                    .filter(Autoresponse.server_id == interaction.guild_id)
                    .all()
                )

        em, f = self.autoresponse_ui_handler(interaction, key_values)
        if not f:
            await interaction.followup.send(content=content, embed=em)
            return
        await interaction.followup.send(content=content, embed=em, file=f)

    @autoresponse.command(name="remove", description="Remove autoresponse keywords")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(read_messages=True)
    @app_commands.describe(
        word="The word you want the bot to stop responding to",
    )
    async def remove(self, interaction: discord.Interaction, word: str):
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            response = (
                session.query(Autoresponse.response)
                .filter(
                    Autoresponse.server_id == interaction.guild_id,
                    Autoresponse.msg == word,
                )
                .one_or_none()
            )
            if not response:
                await interaction.followup.send(
                    content="❌ This word does not exist. Use /autoresponse menu to check what words exist.",
                    ephemeral=True,
                )
                return

            session.query(Autoresponse).filter(
                Autoresponse.server_id == interaction.guild_id,
                Autoresponse.msg == word,
            ).delete()

            session.commit()

            # if cache has the word, delete it
            # only if cache has the server else autoresponse is off
            if interaction.guild_id in self.bot.autoresponses:
                del self.bot.autoresponses[interaction.guild_id][word]
                key_values = self.bot.autoresponses[interaction.guild_id].items()
            else:
                key_values = (
                    session.query(Autoresponse.msg, Autoresponse.response)
                    .filter(Autoresponse.server_id == interaction.guild_id)
                    .all()
                )

        em, f = self.autoresponse_ui_handler(interaction, key_values)
        if not f:
            await interaction.followup.send(
                content=f"✅ Removed ``{word} : {response[0]}``. Here is the new list.",
                embed=em,
            )
            return
        await interaction.followup.send(
            content=f"✅ Removed ``{word} : {response[0]}``. Here is the new list.",
            embed=em,
            file=f,
        )

    @autoresponse.command(
        name="resetdb", description="Reset the autoresponse menu to it's default state."
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.checks.bot_has_permissions(read_messages=True)
    async def resetdb(self, interaction: discord.Interaction):
        # confirmation
        await interaction.response.defer()
        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )[0]
        em = discord.Embed(
            color=int(color, 16),
            description="Are you certain you want to reset this server's autoresponse settings?",
        )

        view = Confirm(interaction)
        await interaction.followup.send(embed=em, view=view)

        await view.wait()
        original = await interaction.original_response()
        if not view.value:
            await original.edit(
                view=discord.ui.View()
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.success,
                        label="Confirm",
                        disabled=True,
                    )
                )
                .add_item(
                    item=discord.ui.Button(
                        style=discord.ButtonStyle.grey, label="Cancel", disabled=True
                    )
                )
            )
            return

        # reset
        with Session(self.bot.engine) as session:
            session.query(Autoresponse).filter(
                Autoresponse.server_id == interaction.guild_id
            ).delete()
            session.commit()
        # update cache
        if interaction.guild_id in self.bot.autoresponses:
            self.bot.autoresponses[interaction.guild_id].clear()

        # UI
        em, _ = self.autoresponse_ui_handler(interaction, [])

        await original.edit(
            content="✅ Resetted database to default. Here is the new list.",
            embed=em,
            view=None,
        )


async def setup(bot):
    await bot.add_cog(Autoresponses(bot))
