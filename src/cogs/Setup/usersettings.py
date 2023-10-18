import discord
from discord.ext import commands
from discord import app_commands
from src.utils import check_usersettings_cache
import re
from typing import Literal, Any

from sqlalchemy.orm import Session
from db.models import UserSettings, Snipe, UserServer


class Rmdata(discord.ui.View):
    def __init__(self, *, interaction: discord.Interaction, bot: commands.Bot):
        super().__init__()
        self.value = None
        self.interaction = interaction
        self.bot = bot

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def cfm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message(
                content="Not your menu, idiot", ephemeral=True
            )
            return
        self.value = True
        for child in self.children:
            child.disabled = True

        await interaction.response.defer()

        try:
            with Session(self.bot.engine) as session:
                session.query(UserServer).filter_by(
                    user_id=interaction.user.id
                ).delete()
                session.query(Snipe).filter_by(id=interaction.user.id).delete()
                session.query(UserSettings).filter_by(id=interaction.user.id).delete()
                session.commit()

            self.bot.redis_client.delete(f"usersettings:{interaction.user.id}")
        except Exception as e:
            self.bot.logger.error(e)
            await interaction.followup.send(
                content=f"❌ Failed to delete your settings. Please try again later.",
                ephemeral=True,
            )
            return
        await self.interaction.edit_original_response(view=self)
        await interaction.followup.send(
            "✅ Successfully deleted your settings, good riddance!", ephemeral=True
        )

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.primary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        for child in self.children:
            child.disabled = True
        await self.interaction.edit_original_response(
            content="cancelled, sad.", view=self
        )

        # defer to not get a 403
        await interaction.response.defer()


class Usersettings(commands.Cog):
    """User Settings"""

    def __init__(self, bot):
        self.bot = bot

    def update(
        self,
        user: discord.User,
        property: Literal["color", "family_friendly", "sniped", "block_dms"],
        value: Any,
    ) -> None:
        """Updates a user's settings in the database and cache."""

        with Session(self.bot.engine) as session:
            session.query(UserSettings).filter_by(id=user.id).update({property: value})
            session.commit()

        # update cache
        if not isinstance(value, str):
            value = str(value)
        self.bot.redis_client.hset(f"usersettings:{user.id}", property, value)

    settings_group = app_commands.Group(
        name="settings", description="Shows and updates your settings for the bot"
    )

    @settings_group.command(
        name="menu", description="Shows all the settings for the bot"
    )
    async def menu(self, interaction: discord.Interaction):
        color, family_friendly, sniped, block_dms = check_usersettings_cache(
            user=interaction.user,
            columns=["color", "family_friendly", "sniped", "block_dms"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        em = discord.Embed(color=int(color, 16), title="Settings")
        em.add_field(
            name="Preferred embed colour (color)",
            value=f"Current: **#{color}**\nChanges the colour of embed sent through the bot to a specific colour.",
            inline=False,
        ).add_field(
            name="Family Friendly (familyfriendly)",
            value=f"Current: **{family_friendly}**\nCensors swear words. ",
            inline=False,
        ).add_field(
            name="Can be sniped (sniped)",
            value=f"Current: **{sniped}**\nDetermines if you can be sniped by others.",
            inline=False,
        ).add_field(
            name="Can be DM'ed (blockdms)",
            value=f"Current: **{block_dms}**\nIf true, this blocks incoming DMs from the bot, and sends an error message to anyone trying to DM you with the bot.",
            inline=False,
        ).set_footer(
            text="Use /settings <setting> <value> to change a setting.\nDon't like the bot? Use /settings removedata to delete your settings."
        )

        await interaction.response.send_message(embed=em, ephemeral=True)

    @settings_group.command(
        name="color",
        description="Changes the colour of embed sent through the bot to a specific colour.",
    )
    @app_commands.describe(color="The hex code of the color you want in your embeds.")
    async def color(
        self, interaction: discord.Interaction, color: app_commands.Range[str, 6, 6]
    ):
        if not re.search("^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$", color):
            await interaction.response.send_message(
                "❌ Enter a valid [hex code](https://en.wikipedia.org/wiki/Web_colors), idiot.",
                ephemeral=True,
            )
            return
        await interaction.response.defer()

        try:
            self.update(user=interaction.user, property="color", value=color)
        except Exception as e:
            self.bot.logger.error(e)
            await interaction.followup.send(
                content=f"❌ Failed to change your embed colour. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            content=f"✅ Successfully changed your embed colour to {color}",
            ephemeral=True,
        )

    @settings_group.command(
        name="familyfriendly",
        description="Censors swear words.",
    )
    @app_commands.describe(onoff="True or False")
    async def fam_friendly(self, interaction: discord.Interaction, onoff: bool):
        await interaction.response.defer()

        try:
            self.update(user=interaction.user, property="family_friendly", value=onoff)
        except Exception as e:
            self.bot.logger.error(e)
            await interaction.followup.send(
                content=f"❌ Failed to change your family friendly setting. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            content=f"✅ Successfully changed your family friendly setting to {onoff}",
            ephemeral=True,
        )

    @settings_group.command(
        name="sniped",
        description="Determines if you can be sniped by others.",
    )
    @app_commands.describe(onoff="True or False")
    async def sniped(self, interaction: discord.Interaction, onoff: bool):
        await interaction.response.defer()

        try:
            self.update(user=interaction.user, property="sniped", value=onoff)
        except Exception as e:
            self.bot.logger.error(e)
            await interaction.followup.send(
                content=f"❌ Failed to change your sniped setting. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            content=f"✅ Successfully changed your sniped setting to {onoff}",
            ephemeral=True,
        )

    @settings_group.command(
        name="blockdms",
        description="If true, this blocks incoming DMs from the bot, and sends an error message.",
    )
    @app_commands.describe(onoff="True or False")
    async def block_dms(self, interaction: discord.Interaction, onoff: bool):
        await interaction.response.defer()
        try:
            self.update(user=interaction.user, property="block_dms", value=onoff)
        except Exception as e:
            self.bot.logger.error(e)
            await interaction.followup.send(
                content=f"❌ Failed to change your block DMs setting. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            content=f"✅ Successfully changed your block DMs setting to {onoff}",
            ephemeral=True,
        )

    @settings_group.command(
        name="removedata",
        description="Deletes your settings from the database and cache.",
    )
    async def remove_data(self, interaction: discord.Interaction):
        view = Rmdata(interaction=interaction, bot=self.bot)
        await interaction.response.send_message(
            content="Are you sure you wanna remove your data from the bot?\nYou will lose your personal settings.",
            view=view,
        )
        await view.wait()

        # if the menu times out
        if view.value is None:
            for child in view.children:
                child.disabled = True
            await interaction.edit_original_response(
                content="Timed out, loser", view=view
            )


async def setup(bot):
    await bot.add_cog(Usersettings(bot))
