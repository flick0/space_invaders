import discord
from discord.ext import commands

from game import space_invaders


def render_board(board):
    print(board)
    desc = ""
    for y in board:
        for x in y:
            if x.get("alien"):
                desc += "o"
            elif x.get("ship"):
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
    async def play(self, ctx, rows=5, cols=5):
        level = space_invaders.new(1, rows, cols)
        await ctx.send(embed=render_board(level.get_board()))


async def setup(bot):
    await bot.add_cog(Game(bot))
