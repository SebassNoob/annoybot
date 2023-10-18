import discord
from discord.ext import commands
from discord import app_commands
from typing import List


# Defines a custom button that contains the logic of the game.
# The ['TicTacToe'] bit is for type hinting purposes to tell your IDE or linter
# what the type of `self.view` is. It is not required.
class TicTacToeButton(discord.ui.Button["TicTacToeView"]):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToeView = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.user1:
            if interaction.user.id != view.user1.id:
                await interaction.response.send_message(
                    content="It's not your turn, stupid", ephemeral=True
                )
                return
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.user2
            content = f"It is now {view.user2.mention}'s' turn"
        else:
            if interaction.user.id != view.user2.id:
                await interaction.response.send_message(
                    content="It's not your turn, stupid", ephemeral=True
                )
                return
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.user1
            content = f"It is now {view.user1.mention}'s turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{view.user1.mention} won!"
            elif winner == view.O:
                content = f"{view.user2.mention} won!"
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


class TicTacToeView(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self, user1: discord.User, user2: discord.User):
        super().__init__()
        self.current_player = user1
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.user1 = user1
        self.user2 = user2

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class Tictactoe(commands.Cog):
    """Init a tictactoe game"""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="tictactoe", description="Starts a game of tictactoe with another user"
    )
    @app_commands.describe(user="The user you want to challenge")
    async def tictactoe(self, interaction: discord.Interaction, user: discord.User):
        if user.id == interaction.user.id:
            await interaction.response.send_message(
                content="You can't challange yourself, silly", ephemeral=True
            )
            return
        if user.bot:
            await interaction.response.send_message(
                content="You can't challenge a bot, duh?", ephemeral=True
            )
            return
        await interaction.response.send_message(
            content=f"TicTacToe: {interaction.user.mention} goes first",
            view=TicTacToeView(interaction.user, user),
        )


async def setup(bot):
    await bot.add_cog(Tictactoe(bot))
