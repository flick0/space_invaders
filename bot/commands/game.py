import discord
from discord.ext import commands

from game import space_invaders


async def win(game):
    embed = discord.Embed(title="You Win")
    await game.edit(embed=embed, view=None)


async def lose(game):
    embed = discord.Embed(title="You Lose")
    await game.edit(embed=embed, view=None)


async def render_board(board):
    print(board)
    desc = ""
    for y in range(len(board[0])):
        for x in board:
            if x[y].get("bullet") and x[y].get("alien"):
                desc += "<:bl:979329177272610886>"
            elif x[y].get("alien"):
                desc += "<:al:979326671624740884>"
            elif x[y].get("ship"):
                desc += "<:sh:979326671285002250>"
            elif x[y].get("bullet"):
                desc += "<:bu:979326671578603551>"
            else:
                desc += "<:sp:979317788776726558>"
        desc += "\n"
    embed = discord.Embed(title=" ", description=desc)
    return embed


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, x=10, y=5, level=3):
        level = space_invaders.new(level, x, y)
        game = await ctx.send("```starting...```")
        await game.edit(
            embed=await render_board(level.get_board().get("board")),
            view=Control(level),
        )


class Control(discord.ui.View):
    def __init__(self, level):
        self.level = level
        super().__init__()

    @discord.ui.button(label="<", custom_id="prev")
    async def left(self, interaction, button):
        board = self.level.control_ship("left")
        if board.get("win"):
            await win(interaction.message)
        elif board.get("lose"):
            await lose(interaction.message)
        elif board.get("board"):
            return await interaction.response.edit_message(
                embed=await render_board(board["board"]), view=self
            )

    @discord.ui.button(
        label=">", custom_id="next", style=discord.ButtonStyle.green
    )
    async def right(self, interaction, button):
        board = self.level.control_ship("right")
        if board.get("win"):
            await win(interaction.message)
        elif board.get("lose"):
            await lose(interaction.message)
        elif board.get("board"):
            return await interaction.response.edit_message(
                embed=await render_board(board["board"]), view=self
            )


async def setup(bot):
    await bot.add_cog(Game(bot))
