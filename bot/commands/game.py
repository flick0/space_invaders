from discord.ext import commands,tasks

from game import space_invaders

from .helpers.components import Control, render_board


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def stats(self, ctx,mode, stat, amount:int):
        if mode == "add":
            await ctx.send(
                await self.bot.db.launcher.add_stats(ctx.author.id, stat, amount)
            )
        elif mode == "remove":
            await ctx.send(
                await self.bot.db.launcher.add_stats(ctx.author.id, stat, -amount)
            )
        elif mode == "set":
            await ctx.send(
                await self.bot.db.launcher.set_stats(ctx.author.id,stat,amount)
            )

            

    @commands.command()
    async def play(self, ctx, x=10, y=10, level=5):
        launcher = await self.bot.db.launcher.fetch_launcher(ctx.author.id)
        level = space_invaders.new(launcher, level, x, y)
        game = await ctx.send("```starting...```")
        await game.edit(
            content="",
            embed=await render_board(level.get_board().get("board")),
            view=Control(level),
        )
        @tasks.loop(seconds=1)
        async def game_loop():
            await game.edit(
                content="",
                embed=await render_board(level.get_board().get("board")),
                view=Control(level),
            )
        game_loop.start()


async def setup(bot):
    await bot.add_cog(Game(bot))
