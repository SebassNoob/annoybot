import discord
from discord.ext import commands
from discord import app_commands
from src.utils import read_csv, check_usersettings_cache, parse_txt
import os
import random
import asyncio


class options(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.insults = parse_txt(f"{os.getcwd()}/src/public/insults/insults.txt")
        self.who = {"op1": [], "op2": []}
        self.voted = []

    @discord.ui.button(label="Option 1", style=discord.ButtonStyle.green)
    async def op1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted:
            await interaction.response.send_message(
                f"You've already voted, you {random.choice(self.insults)}. ",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            "You voted for option 1!", ephemeral=True
        )

        self.who["op1"].append(interaction.user.display_name)
        self.voted.append(interaction.user.id)

    @discord.ui.button(label="Option 2", style=discord.ButtonStyle.green)
    async def op2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.voted:
            await interaction.response.send_message(
                f"You've already voted, you {random.choice(self.insults)}. ",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            "You voted for option 2!", ephemeral=True
        )
        self.who["op2"].append(interaction.user.display_name)
        self.voted.append(interaction.user.id)

    def disable_buttons(self):
        for b in self.children:
            b.disabled = True

        return self

    def results(self):
        return (self.who, self.voted)


class review_results(discord.ui.View):
    def __init__(self, results, em_color):
        super().__init__()
        self.results = results
        self.color = em_color

    @discord.ui.button(
        label="See who voted for what", style=discord.ButtonStyle.blurple
    )
    async def clback(self, interaction: discord.Interaction, button: discord.ui.Button):
        em = discord.Embed(
            color=int(self.color, 16),
            description=f"Option 1: {', '.join(self.results['op1'])}\nOption 2: {', '.join(self.results['op2'])}",
        )
        await interaction.response.send_message(embed=em, ephemeral=True)


class Wouldyourather(commands.Cog):
    """would you rather 2 options game"""

    def __init__(self, bot):
        self.bot = bot
        self.options = read_csv(f"{os.getcwd()}/src/public/would_you_rather.csv")

    @app_commands.command(
        name="wouldyourather", description="Generates a would you rather question"
    )
    async def wouldyourather(self, interaction: discord.Interaction):
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=interaction.client.engine,
            redis_client=interaction.client.redis_client,
        )[0]
        options_tuple = random.choice(self.options)
        em = discord.Embed(color=int(color, 16))
        em.add_field(
            name="Would you rather...",
            value=f"1. {options_tuple[0]}\n2. {options_tuple[1]} ",
            inline=False,
        )
        em.set_footer(text="Best played in a voice call!")
        view = options()
        await interaction.response.send_message(
            "You have 30s to select one of the below!", embed=em, view=view
        )

        await asyncio.sleep(10)

        results, voted = view.results()
        view.disable_buttons()
        interaction_msg = await interaction.original_response()
        await interaction.followup.edit_message(interaction_msg.id, view=view)

        em2 = discord.Embed(color=int(color, 16))
        try:
            em2.add_field(
                name="Results!",
                value=f"``{(len(results['op1'])/len(voted))*100}%`` {options_tuple[0]}\n``{(len(results['op2'])/len(voted))*100}%`` {options_tuple[1]}",
                inline=False,
            )
        except ZeroDivisionError:
            em2.add_field(
                name="Results!",
                value=f"``0%`` {options_tuple[0]}\n``0%`` {options_tuple[1]}",
                inline=False,
            )
        em2.set_footer(text="Best played in a voice call!")
        await interaction.channel.send(embed=em2, view=review_results(results, color))


async def setup(bot):
    await bot.add_cog(Wouldyourather(bot))
