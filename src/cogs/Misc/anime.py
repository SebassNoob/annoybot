import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from src.utils import parse_txt
from better_profanity import profanity
from waifu import WaifuClient

from sqlalchemy.orm import Session
from db.models import UserSettings


class anime_embed(discord.Embed):
    def __init__(
        self,
        *,
        color: str,
        pic_type: str,
        interaction_user: discord.Interaction.user,
        image_url: str,
    ):
        self.pic_type = pic_type
        super().__init__(color=int(color, 16), title=f"a {pic_type}")
        self.set_author(
            name=f"{pic_type} requested by {interaction_user.display_name}",
            icon_url=interaction_user.display_avatar,
        ).set_image(url=image_url)

    def define(self):
        desc = {
            "waifu": "A fictional female character from  an anime, manga, or video game to whom one is romantically attracted",
            "neko": "A woman with cat ears, whiskers, and sometimes paws or a tail.",
            "shinobu": "A fictional character with this surname",
            "megumin": "A fictional character with this surname",
            "bully": "A woman who bullies others into submission",
            "cuddle": "A person who is cuddling something",
            "cry": "An anime character crying",
            "hug": "An anime character hugging something",
            "kiss": "An anime character kissing something",
            "lick": "An anime character licking something",
            "blush": "An anime character blushing",
            "smile": "An anime character smiling",
            "wave": "An anime character waving",
            "happy": "An anime character being happy",
            "dance": "An anime character dancing",
        }
        return desc[self.pic_type]


class nerd(discord.ui.View):
    def __init__(self, em: anime_embed):
        super().__init__()
        self.em = em

    @discord.ui.button(
        label="🤓 Hopefully apt description", style=discord.ButtonStyle.grey
    )
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(self.em.define(), ephemeral=True)


class Anime(commands.Cog):
    """Generate a random anime image"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="anime", description="Sends a pic of an anime woman")
    @app_commands.describe(pic_type="Type of picture you want to see")
    async def anime(
        self,
        interaction: discord.Interaction,
        pic_type: Literal[
            "waifu",
            "neko",
            "shinobu",
            "megumin",
            "bully",
            "cuddle",
            "cry",
            "hug",
            "kiss",
            "lick",
            "blush",
            "smile",
            "wave",
            "happy",
            "dance",
        ],
    ):
        pic = WaifuClient().sfw(category=pic_type)

        with Session(self.bot.engine) as session:
            color = (
                session.query(UserSettings.color)
                .filter(UserSettings.id == interaction.user.id)
                .one()
            )

        em = anime_embed(
            color=color[0],
            pic_type=pic_type,
            interaction_user=interaction.user,
            image_url=pic,
        )

        await interaction.response.send_message(embed=em, view=nerd(em))


async def setup(bot):
    await bot.add_cog(Anime(bot))
