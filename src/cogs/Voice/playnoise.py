import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio
import asyncio
from src.utils import check_usersettings_cache

from mutagen.mp3 import MP3
import os


class NoiseView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="⬜", style=discord.ButtonStyle.red)
    async def callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        try:
            button.disabled = True
            button.style = discord.ButtonStyle.grey

            await interaction.response.edit_message(view=self)

            await interaction.guild.voice_client.disconnect()
            await interaction.followup.send(
                "✅ disconnected successfully, imagine being that annoyed"
            )

            self.stop()

        except AttributeError:
            await interaction.followup.send(
                "❌ The bot isn't in a voice channel, idiot.", ephemeral=True
            )
            self.stop()
            return
        except Exception as e:
            await interaction.followup.send(
                "❌ Yikes! something went wrong. " + str(e), ephemeral=True
            )
            self.stop()
            return

    @staticmethod
    def disabled_button():
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(style=discord.ButtonStyle.grey, disabled=True, label="⬜")
        )
        return view


class Noise:
    def __init__(
        self, bot: discord.Client, interaction: discord.Interaction, path: str
    ):
        self.path = path
        self.interaction = interaction
        self.bot = bot

    # represents a success/failure, message = message if fails
    async def response(self, status: bool, message: str = None):
        view = NoiseView()
        color = check_usersettings_cache(
            user=self.interaction.user,
            columns=["color"],
            engine=self.bot.engine,
            redis_client=self.bot.redis_client,
        )[0]

        # if successful...
        if status:
            em = discord.Embed(
                color=int(color, 16),
                description=f"enjoy your {self.interaction.command.name}, loser",
            ).set_footer(
                text="You can force the bot to disconnect with the button below, if youre a pussy that is"
            )
            await self.interaction.response.send_message(embed=em, view=view)

        # an error was encountered!!!! wow!!!
        else:
            em = discord.Embed(color=int(color, 16), description=message)
            await self.interaction.response.send_message(embed=em)

    async def play(self):
        try:
            voicestate = self.interaction.user.voice
            if voicestate is None or voicestate.channel is None:
                await self.response(False, "❌ You are not in a VC, stupid.")
                return

            channel = voicestate.channel

            # if user_limit is 0, then there is no limit
            if channel.user_limit is not None and channel.user_limit != 0:
                if len(channel.members) >= channel.user_limit:
                    await self.response(False, "❌ The VC is full.")
                    return

            voice = await channel.connect(reconnect=False)
        except discord.ClientException:
            await self.response(False, "❌ The bot is already playing something.")
            return
        except asyncio.TimeoutError:
            await self.response(False, "❌ Client timed out, try again later.")
            return

        # create a MP3 object to check its length
        audio = MP3(self.path)

        await self.response(True)
        voice.play(FFmpegPCMAudio(self.path))

        # wait for the audio to finish playing
        await asyncio.sleep(audio.info.length)
        await self.interaction.edit_original_response(view=NoiseView.disabled_button())

        try:
            await self.interaction.guild.voice_client.disconnect(force=True)
            return

            # if already disconnected manually
        except AttributeError:
            return


class PlayNoise(commands.Cog):
    """Play a specific Noise into a voice channel"""

    def __init__(self, bot):
        self.bot = bot

    playnoise_group = app_commands.Group(
        name="playnoise",
        description="Plays a specific noise into your VC",
        guild_only=True,
    )

    @playnoise_group.command(name="fart", description="Plays a fart Noise into your VC")
    @app_commands.checks.bot_has_permissions(speak=True)
    async def fart(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/fart.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="micblow", description="Plays a breathing/blowing Noise into your VC"
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def micblow(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/mic.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="asmr", description="Plays a chewing Noise into your VC"
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def asmr(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/asmr.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="cartoon", description="Plays a goofy cartoon Noise into your VC"
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def cartoon(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/cartoon.mp3"
        )
        await to_play.play()

    @playnoise_group.command(name="cbat", description="Plays cbat into your VC")
    @app_commands.checks.bot_has_permissions(speak=True)
    async def cbat(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/cbat.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="scream", description="Plays a female screaming Noise into your VC"
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def scream(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/scream.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="rickroll",
        description="Plays Never Gonna Give You Up (Rick Astley, 1987) into your VC",
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def rickroll(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/rick_astley.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="indianinsult",
        description="Plays the voice of an indian dude insulting your cock into your VC",
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def indian(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/indian_shitpost.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="fnafscream", description="plays the scream of freddy fazbear from fnaf"
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def fnaf(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/fnaf_scream.mp3"
        )
        await to_play.play()

    @playnoise_group.command(
        name="androidearrape",
        description="plays a bass boosted android notification sound",
    )
    @app_commands.checks.bot_has_permissions(speak=True)
    async def android(self, interaction: discord.Interaction):
        to_play = Noise(
            self.bot, interaction, f"{os.getcwd()}/src/public/voice/android_earrape.mp3"
        )
        await to_play.play()


async def setup(bot):
    await bot.add_cog(PlayNoise(bot))
