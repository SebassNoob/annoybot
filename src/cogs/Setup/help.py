import discord
from discord.ext import commands
from discord import app_commands
from src.utils import read_csv, read_json
import os


class HelpOptions(discord.ui.Select):
    def __init__(
        self, options: list[discord.SelectOption], pages: dict[str, discord.Embed]
    ):
        super().__init__(
            placeholder="Choose a category",
            options=options,
            min_values=1,
            max_values=1,
        )
        self.pages = pages

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(
            embed=self.pages[self.values[0]],
            view=discord.ui.View().add_item(self),
        )


class Help(commands.Cog):
    """Shows a help menu with all the commands"""

    def __init__(self, bot):
        self.bot = bot

        # read the select options and return the discord.SelectOption objects
        select_options_raw = read_json(
            f"{os.getcwd()}/src/public/help/select_options.json"
        )
        self.select_options = [
            discord.SelectOption(
                label=label, description=desc, emoji=emoji, value=label
            )
            for label, (desc, emoji) in select_options_raw.items()
        ]

        # read the csv files and return the embeds, mapped to select option labels
        workdir = f"{os.getcwd()}/src/public/help/"
        unloaded: list[tuple[str, str]] = [
            ("Core features", "main.csv"),
            ("Miscellaneous", "misc.csv"),
            ("Setup", "setup.csv"),
            ("Trolling", "trolling.csv"),
            ("Voice", "voice.csv"),
            ("Games", "games.csv"),
            ("Message", "message.csv"),
            ("Member", "member.csv"),
        ]
        additional_info = read_json(f"{workdir}additional_info.json")
        content = {label: read_csv(f"{workdir}{path}") for label, path in unloaded}
        self.embeds = {
            category: discord.Embed(
                color=0x000000, description=additional_info[category]
            )
            for category in content
        }
        # populate the embeds
        for category, fields in content.items():
            for field in fields:
                if len(field) != 4:
                    raise ValueError(f"Invalid field length for {category}: {field}")
                # description
                val = f"*{field[1]}*"

                # bot permissions
                if field[2] != "None":
                    val += f"\nRequires: ``{field[2]}``"
                # user permissions
                if field[3] != "None":
                    val += f"\nUser must have: ``{field[3]}``"
                self.embeds[category].add_field(
                    name=f"``{field[0]}``",
                    value=val,
                    inline=False,
                )

    @app_commands.command(
        name="help", description="Shows a list of commands that you can use"
    )
    async def help(self, interaction: discord.Interaction):
        view = discord.ui.View()
        view.add_item(HelpOptions(self.select_options, self.embeds))
        await interaction.response.send_message(
            "The values in brackets are additional arguments to give.\n* denotes an optional argument.\nAll commands require the ``send_messages`` permission.",
            embed=self.embeds["Core features"],
            view=view,
        )


async def setup(bot):
    await bot.add_cog(Help(bot))
