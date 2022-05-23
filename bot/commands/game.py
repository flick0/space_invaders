import discord
from discord.ext import commands

from game import space_invaders


def render_board(board):
    print(board)
    desc = ""
    for y in range(len(board[0])):
        for x in board:
            if x[y].get("alien"):
                desc += "o"
            elif x[y].get("ship"):
                desc += "="
            else:
                desc += "-"
        desc += "\n"
    embed = discord.Embed(title="space invaders", description=desc)
    return embed


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, x=10, y=5, level=3):
        level = space_invaders.new(3, x, y)
        game = await ctx.send(
            embed=render_board(level.get_board()), view=Control(level)
        )


class Control(discord.ui.View):
    def __init__(self, level):
        self.level = level
        super().__init__()

    @discord.ui.button(label="<", custom_id="prev")
    async def left(self, interaction, button):
        board = self.level.control_ship("left")
        if board:
            return await interaction.response.edit_message(
                embed=render_board(self.level.get_board()), view=self
            )

    @discord.ui.button(
        label=">", custom_id="next", style=discord.ButtonStyle.green
    )
    async def right(self, interaction, button):
        board = self.level.control_ship("right")
        if board:
            return await interaction.response.edit_message(
                embed=render_board(self.level.get_board()), view=self
            )


async def setup(bot):
    await bot.add_cog(Game(bot))
