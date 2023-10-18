import discord
from discord.ext import commands
from discord import app_commands
from src.utils import parse_txt, check_usersettings_cache
import os
import random
import string
from collections import Counter
import threading
import asyncio
import math


class Vocabularygame(commands.Cog):
    """Init a game for vocabulary"""

    def __init__(self, bot):
        self.bot = bot
        self.words = parse_txt(f"{os.getcwd()}/src/public/vocabulary_game.txt")

    @app_commands.command(
        name="vocabularygame", description="Test your vocabulary with this game"
    )
    @app_commands.checks.bot_has_permissions(add_reactions=True)
    async def vocabularygame(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        vowels = ["a", "e", "i", "o", "u"]
        randomLetters = "".join(random.choices(string.ascii_lowercase, k=9)) + "".join(
            random.choices(vowels, k=3)
        )

        await interaction.followup.send(
            f"With the letters ``{randomLetters}`` type as many words as you can within 30s!"
        )

        reqLetters = Counter(randomLetters)

        def check(in_val: str, req: Counter) -> bool:
            # returns true if in_val is a subset of req
            # checks if the intersection is equal to the original in_val counter
            return Counter(in_val) & req == Counter(in_val)

        thr = threading.Timer(30.0, lambda: None)

        score = 0
        combo = 0
        maxcombo = 0
        correct = 0
        used_words = []
        bonus = 0
        thr.start()
        while thr.is_alive():
            try:
                msg: discord.Message = await self.bot.wait_for(
                    "message",
                    check=lambda i: i.author.id == interaction.user.id
                    and i.channel.id == interaction.channel.id,
                    timeout=1,
                )

                if (
                    msg.content in self.words
                    and msg.content not in used_words
                    and check(msg.content, reqLetters)
                ):
                    await msg.add_reaction("✅")
                    used_words.append(msg.content)
                    correct += 1

                    combo += 1
                    if maxcombo < combo:
                        maxcombo += 1

                    score += 100 + combo * 25
                else:
                    used_words.append(
                        msg.content
                    )  # this avoids an unnessesary function call to check()
                    combo = 0

            except asyncio.TimeoutError:
                continue
        try:
            accuracy = correct / len(used_words)
        except ZeroDivisionError:
            accuracy = 0

        bonus = score * (accuracy / 8)
        score += bonus

        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        em = discord.Embed(color=int(color, 16))
        em.add_field(
            name="``Stats``",
            value=f"Accuracy: {math.ceil(accuracy*100)}%\nNumber of correct words: {correct}\nMax combo: {maxcombo}\nAccuracy bonus: +{math.ceil(bonus)}\n**Total score: {math.ceil(score)}**",
            inline=False,
        )
        await interaction.channel.send(embed=em)


async def setup(bot):
    await bot.add_cog(Vocabularygame(bot))
