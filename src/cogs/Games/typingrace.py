import discord
from discord.ext import commands
from discord import app_commands
from src.utils import parse_txt, check_usersettings_cache

from typing import List, Tuple, Dict
import os
import random
import datetime
from difflib import SequenceMatcher
import threading
import asyncio
import math


class join_race(discord.ui.View):
    def __init__(self, *, random_text: str):
        super().__init__()
        self.joined: List[discord.Member] = []
        self.text = random_text

        self.anticheat_text = "\u200b".join([char for char in self.text])
        self.insults = parse_txt(f"{os.getcwd()}/src/public/insults/insults.txt")

    def disable_buttons(self):
        for b in self.children:
            b.disabled = True

        return self

    @discord.ui.button(label="Join race!", style=discord.ButtonStyle.blurple)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.joined:
            await interaction.response.send_message(
                f"You've already joined, {random.choice(self.insults)}", ephemeral=True
            )
            return
        self.joined.append(interaction.user)
        await interaction.response.send_message(
            "You've joined the race successfully.", ephemeral=True
        )

    @discord.ui.button(label="Start race!", style=discord.ButtonStyle.blurple)
    async def start(self, interaction: discord.Interaction, button: discord.ui.Button):
        if len(self.joined) == 0:
            await interaction.response.send_message(
                "No one has joined this race yet!", ephemeral=True
            )
            return
        await interaction.response.edit_message(view=self.disable_buttons())
        color = check_usersettings_cache(
            user=interaction.user,
            columns=["color"],
            engine=interaction.client.engine,
            redis_client=interaction.client.redis_client,
        )[0]
        await interaction.channel.send(
            embed=discord.Embed(color=int(color, 16))
            .add_field(
                name="Typing race starts now! Type the following within 180s:",
                value=f"``{self.anticheat_text}``",
                inline=False,
            )
            .set_footer(
                text=f"Participating users: {', '.join([str(u.display_name) for u in self.joined])}"
            )
        )


class Typingrace(commands.Cog):
    """Init a race for typing"""

    def __init__(self, bot):
        self.bot = bot
        self.words = parse_txt(f"{os.getcwd()}/src/public/typing_race.txt")

        self.channels_running = []

    @app_commands.command(
        name="typingrace",
        description="Race against others to see who can type the quickest",
    )
    @app_commands.checks.bot_has_permissions(add_reactions=True)
    async def typingrace(self, interaction: discord.Interaction):
        # check if command is already running
        if interaction.channel.id in self.channels_running:
            await interaction.response.send_message(
                "Another typing race is happening in the same channel, please wait for it to finish.",
                ephemeral=True,
            )
            return
        else:
            self.channels_running.append(interaction.channel.id)

        race_buttons = join_race(random_text=random.choice(self.words))
        await interaction.response.send_message(
            content="Join the typing race here!", view=race_buttons
        )
        st_time = datetime.datetime.now()
        # race_buttons.text for text

        thr = threading.Timer(120, lambda: None)

        accuracy = 0
        wpm = 0
        penalty = 0

        leaderboards = {}

        def check_accuracy(input, text):
            return SequenceMatcher(None, input, text).ratio()

        thr.start()
        while thr.is_alive():
            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda i: i.author in race_buttons.joined
                    and i.channel.id == interaction.channel.id,
                    timeout=0.5,
                )
                time_taken = (datetime.datetime.now() - st_time).total_seconds()
                await msg.add_reaction("✅")

                # calc score
                accuracy = round(
                    check_accuracy(msg.content, race_buttons.text), 3
                )  # round to 3sf
                if accuracy < 0:
                    accuracy = 0
                race_buttons.joined.remove(msg.author)
                wpm = math.ceil(len(msg.content.split(" ")) / (time_taken / 60))

                penalty = math.floor(wpm * (1 - accuracy))
                wpm -= penalty

                leaderboards[msg.author.id] = {
                    "accuracy": accuracy,
                    "penalty": penalty,
                    "wpm": wpm,
                }

            except asyncio.TimeoutError:
                continue

        def arr_in_order(lb: List[Tuple[int, Dict[str, int]]]):
            arranged_lb = []

            for item in lb:
                if len(arranged_lb) == 0:
                    arranged_lb.append(item)

                    continue

                for i, wpm in enumerate(arranged_lb):
                    if item[1]["wpm"] <= wpm[1]["wpm"]:
                        arranged_lb.insert(i, item)
                        break
                    elif item[1]["wpm"] > wpm[1]["wpm"]:
                        arranged_lb.append(item)
                        break

            return arranged_lb[::-1]

        disp = arr_in_order(leaderboards.items())

        em = discord.Embed(color=0xFFFFFF, description="**Leaderboard**")
        for place, player in enumerate(disp, start=1):
            user = await self.bot.fetch_user(player[0])

            em.add_field(
                name=f"{place}/ {user.display_name}",
                value=f"Accuracy: {player[1]['accuracy']*100}%\nPenalty:{player[1]['penalty']} wpm\nTotal:{player[1]['wpm']} wpm",
                inline=False,
            )

        await interaction.channel.send(embed=em)
        self.channels_running.remove(
            interaction.channel.id
        )  # remove channel from running channels


async def setup(bot):
    await bot.add_cog(Typingrace(bot))
