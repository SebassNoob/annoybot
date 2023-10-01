import discord
from discord.ext import commands
from discord import app_commands
from src.utils import parse_txt, check_usersettings_cache
import os
import asyncio

from sqlalchemy.orm import Session
from db.models import UserSettings

import dotenv

dotenv.load_dotenv(f"{os.getcwd()}/.env")


class InfoView(discord.ui.View):
    def __init__(
        self,
        *,
        patchnotes: str,
        legal_docs: dict[str, str],
        color: int,
    ):
        super().__init__()
        self.invite = os.getenv("INVITE_LINK")
        self.support = os.getenv("SUPPORT_SERVER")
        self.patchnotes = patchnotes
        self.legal_docs = legal_docs
        self.color = color

        # add link button to support server
        self.add_item(
            discord.ui.Button(
                label="Support server",
                style=discord.ButtonStyle.link,
                url=self.support,
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Invite link",
                style=discord.ButtonStyle.link,
                url=self.invite,
            )
        )

    @discord.ui.button(label="Patch notes", style=discord.ButtonStyle.green)
    async def cl(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(color=self.color, description=self.patchnotes)
        await interaction.response.send_message(embed=em)

    @discord.ui.button(label="Legal documents", style=discord.ButtonStyle.primary)
    async def legal_docs(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            embed=discord.Embed(
                color=self.color,
                description="Choose a document to view!",
            ),
            view=LegalDocsView(
                licence=self.legal_docs["licence"],
                privacy_policy=self.legal_docs["privacy_policy"],
                terms_of_use=self.legal_docs["terms_of_use"],
                color=self.color,
            ),
        )


class LegalDocsView(discord.ui.View):
    def __init__(
        self, *, licence: str, privacy_policy: str, terms_of_use: str, color: int
    ):
        super().__init__()
        self.licence = licence
        self.privacy_policy = privacy_policy
        self.terms_of_use = terms_of_use
        self.color = color

    @discord.ui.button(label="Terms of use", style=discord.ButtonStyle.primary)
    async def tos(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(color=self.color, description=self.terms_of_use)
        await interaction.response.send_message(embed=em)

    @discord.ui.button(label="Privacy policy", style=discord.ButtonStyle.primary)
    async def privacy_pol(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        em = discord.Embed(color=self.color, description=self.privacy_policy)
        await interaction.response.send_message(embed=em)

    @discord.ui.button(label="License", style=discord.ButtonStyle.primary)
    async def lic(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(color=self.color, description=self.licence)
        await interaction.response.send_message(embed=em)


class Info(commands.Cog):
    """Shows general information and support links."""

    def __init__(self, bot):
        self.bot = bot

        # return a future that can be awaited to get user
        self.creator = asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(
                self.bot.fetch_user(int(os.getenv("OWNER_ID"))), self.bot.loop
            )
        )
        self.version = os.getenv("VERSION")

        self.patchnotes = "\n".join(
            parse_txt(f"{os.getcwd()}/src/static/PATCHNOTES.txt")
        )
        self.licence = "\n".join(parse_txt(f"{os.getcwd()}/src/static/LICENCE.txt"))
        self.privacy_policy = "\n".join(
            parse_txt(f"{os.getcwd()}/src/static/PRIVACY_POLICY.txt")
        )
        self.terms_of_use = "\n".join(
            parse_txt(f"{os.getcwd()}/src/static/TERMS_OF_USE.txt")
        )

    @app_commands.command(
        name="info", description="Shows general information and support links."
    )
    async def credit(self, interaction: discord.Interaction):
        guilds = str(len(self.bot.guilds))

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        em = discord.Embed(color=int(color, 16))
        em.add_field(
            name=f"Annoybot {self.version}",
            value=f"""Developed by {str(await self.creator)}
      Library: discord.py 2.3.2\n
      Support us!!
      [top.gg](https://top.gg/bot/844757192313536522)
      [dbl link](https://discordbotlist.com/bots/annoybot-4074)
      [AYB link](https://ayblisting.com/bots/844757192313536522)
      Server count: {guilds}""",
            inline=False,
        )

        await interaction.response.send_message(
            embed=em,
            view=InfoView(
                patchnotes=self.patchnotes,
                legal_docs={
                    "licence": self.licence,
                    "privacy_policy": self.privacy_policy,
                    "terms_of_use": self.terms_of_use,
                },
                color=int(color, 16),
            ),
        )


async def setup(bot):
    await bot.add_cog(Info(bot))
