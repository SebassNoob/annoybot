import discord
import os

from discord import app_commands

import dotenv

dotenv.load_dotenv(f"{os.getcwd()}/.env")


async def add_users_to_db(interaction: discord.Interaction):
    # TODO: add users to server db if not already there
    # access through interaction.guild.id and interaction.user.id
    # should always return True
    # This always executes before blacklist_check
    return True


async def blacklist_check(interaction: discord.Interaction):
    if not interaction.guild:
        return True

        # TODO: add blacklist check => query db for user blacklisted
    # if interaction.user.id in eval(getData(interaction.guild.id)['blacklist']):
    if False:
        em = discord.Embed(
            color=0x000000,
            description=f"You have been banned from using this bot in this server: {interaction.guild.name}\nAsk the mods to unban you (/serversettings) or use this bot in another server.",
        )
        await interaction.response.send_message(embed=em, ephemeral=True)
        return False
    # REMOVE THIS LINE
    return True


async def custom_cooldown(interaction: discord.Interaction):
    if interaction.user.id == int(os.getenv("OWNER_ID")):
        return None

    # get the support server guild object
    guild = interaction.client.get_guild(858200514914287646)

    if guild and guild.get_member(interaction.user.id):
        return app_commands.Cooldown(12, 30)

    return app_commands.Cooldown(7, 30)
