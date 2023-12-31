import os
import discord
from discord.ext import commands
from discord import app_commands
import random
from src.utils import parse_txt, check_usersettings_cache
from better_profanity import profanity


class Utils(commands.Cog):
    """set of utilities that fit the rude theme"""

    def __init__(self, bot):
        self.bot = bot
        self.predict_res = parse_txt(f"{os.getcwd()}/src/public/predictions.txt")
        self.insults = parse_txt(f"{os.getcwd()}/src/public/insults/insults.txt")

    utils = app_commands.Group(
        name="utils", description="Random utilities that fit the rude theme."
    )

    @utils.command(
        name="pick", description="Picks a random option from a list of given words."
    )
    @app_commands.describe(arguments="a comma separated list of options to choose from")
    async def pick(
        self,
        interaction: discord.Interaction,
        arguments: app_commands.Range[str, 1, 1800],
    ):
        choice = random.choice([arg.strip() for arg in arguments.split(",")]) or " "
        random_insult = random.choice(self.insults)

        ff = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff[0]:
            random_insult = profanity.censor(random_insult)

        await interaction.response.send_message(
            f"{interaction.user.mention}\nI pick ``{choice}``, you indecisive {random_insult}."
        )

    @utils.command(
        name="8ball", description="Gives you a yes/no answer based on a given question"
    )
    @app_commands.describe(question="The yes/no question you want to ask")
    async def predict(
        self,
        interaction: discord.Interaction,
        question: app_commands.Range[str, 1, 256],
    ):
        prediction = random.choice(self.predict_res)

        ff, color = check_usersettings_cache(
            user=interaction.user,
            columns=["family_friendly", "color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )

        if ff:
            prediction = profanity.censor(prediction)

        em = discord.Embed(color=int(color, 16), title=question, description=prediction)

        em.set_footer(text=f"requested by {interaction.user.display_name}")

        await interaction.response.send_message(embed=em)


async def setup(bot):
    await bot.add_cog(Utils(bot))
