import discord
from discord.ext import commands
from discord import app_commands
from typing import List
from src.utils import check_usersettings_cache
import random
import asyncio
import datetime
import math


class MemButton(discord.ui.Button["MemButton"]):
    def __init__(self, x: int, y: int):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: MemGame = self.view

        if interaction.user.id != view.interaction.user.id:
            await interaction.response.send_message(
                content=f"This is not your game, {interaction.user.mention}, stupid fool."
            )
            return
        for child in view.children:
            child.label = "\u200b"
            child.style = discord.ButtonStyle.secondary
        if view.check(self.x, self.y):  # if check is true (passed)
            # edit the button properties
            self.style = discord.ButtonStyle.success
            self.label = "✓"

        else:
            self.style = discord.ButtonStyle.danger
            self.label = "✗"
            for child in view.children:
                child.disabled = True
            view.stop()
            expectedTime = ((view.level * (view.level + 1)) / 2) * (3.5 + view.level)

            bonus = expectedTime / (
                (datetime.datetime.now() - view.time).total_seconds()
            )
            if bonus < 1:
                bonus = 1
            score = view.level * bonus

            color = check_usersettings_cache(
                user=view.interaction.user,
                columns=["color"],
                engine=interaction.client.engine,
                redis_client=interaction.client.redis_client,
            )[0]
            em = discord.Embed(color=int(color, 16))
            em.add_field(
                name="stats",
                value=f"Level: {view.level}\nTime bonus: \u00D7{round(bonus,2)}\n**Score: {math.ceil(score)}**",
                inline=False,
            )
            await interaction.channel.send(embed=em)

        # hacky way to edit a deferred message
        await interaction.response.edit_message(
            content=f"Memory Game: Level {view.level}\nReplicate the sequence of highlighted squares to the best of your memory.",
            view=view,
        )
        if view.pattern == []:
            await view.levelup()


class MemGame(discord.ui.View):
    children: List[MemButton]

    def __init__(self, interaction: discord.Interaction):
        super().__init__()

        self.level = 1
        self.pattern = []  # list[tuple[x,y]]
        self.interaction = interaction
        self.time = datetime.datetime.now()

        for x in range(3):
            for y in range(3):
                self.add_item(MemButton(x, y))

    async def async_init(self):
        self.original_res = await self.interaction.original_response()

    def generate_pattern(self):
        coords = [
            (a.x, a.y) for a in self.children
        ]  # a list of coords eg. (0,1) corresponding to each button pressed
        self.pattern.append(random.choice(coords))
        return

    async def instructions(self):
        # edit the view (level) times displaying the color as green
        for child in self.children:
            child.label = "\u200b"
            child.disabled = True

        await self.original_res.edit(
            content=f"Memory Game: Level {self.level}\nReplicate the sequence of highlighted squares to the best of your memory.",
            view=self,
        )

        for i, coord in enumerate(self.pattern, start=1):
            x, y = coord
            # set properties of the child
            for child in self.children:
                child.style = discord.ButtonStyle.secondary
                child.label = "\u200b"

            def get_child(child):
                if child.x == x and child.y == y:
                    return True
                return False
                # unsure

            child = list(filter(get_child, self.children))[0]

            child.style = discord.ButtonStyle.success
            child.label = i
            await self.original_res.edit(view=self)
            await asyncio.sleep(1)

        for child in self.children:
            child.disabled = False
            child.style = discord.ButtonStyle.secondary
            child.label = "\u200b"

        await self.original_res.edit(view=self)

        return

    def check(self, x: int, y: int) -> bool:
        # check if x,y is first in pattern
        if (x, y) == self.pattern[0]:
            self.pattern.remove((x, y))

            return True
        return False

    async def levelup(self):
        self.level += 1
        for _ in range(self.level):
            self.generate_pattern()
        await self.instructions()

    async def start(self):
        self.generate_pattern()
        await self.instructions()


class Memorygame(commands.Cog):
    """Init a memory game"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="memorygame", description="Sets up a game to test your visual memory"
    )
    async def memorygame(self, interaction: discord.Interaction):
        view = MemGame(interaction)

        await interaction.response.send_message(
            content=f"Memory Game: Level {view.level}\nReplicate the sequence of highlighted squares to the best of your memory.",
            view=view,
        )
        await view.async_init()
        await view.start()


async def setup(bot):
    await bot.add_cog(Memorygame(bot))
