from discord.ext import commands

from game import space_invaders

from .helpers.components import Control, render_board


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx, stat, amount):
        await ctx.send(
            await self.bot.db.launcher.add_stats(ctx.author.id, stat, amount)
        )

    @commands.command()
    async def play(self, ctx, x=10, y=5, level=3):
        launcher = await self.bot.db.launcher.fetch_launcher(ctx.author.id)
        level = space_invaders.new(launcher, level, x, y)
        game = await ctx.send("```starting...```")
        await game.edit(
            content="",
            embed=await render_board(level.get_board().get("board")),
            view=Control(level),
        )


async def setup(bot):
    await bot.add_cog(Game(bot))
