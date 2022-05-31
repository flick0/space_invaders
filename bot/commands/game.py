from discord.ext import commands,tasks

from game import space_invaders

from .helpers.components import Control, render_board


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
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

        def calculate_level(launcher):
            """calculate level bsaed on stats"""
            defaults = self.bot.get_cog("Shop").items
            level = 1
            for key, value in launcher.items():
                if key in ["_id","owner_id"]:
                    continue
                elif value > defaults[key]:
                    if defaults[key] < 0 and value.price < 0:
                        level += value.price*10 - defaults[key]*10 
                    elif defaults[key] < 0 and value.price > 0:
                        level += value.price - defaults[key]*10 
                    else:
                        level += value.price - defaults[key]
            print("level: ",int(level))
            return int(level)

        level = space_invaders.new(launcher, calculate_level(launcher), x, y)
        game = await ctx.send("```starting...```")
        await game.edit(
            content="",
            embed=await render_board(level.get_board().get("board")),
            view=Control(level),
        )
        @tasks.loop(seconds=3)
        async def game_loop():
            """
            an alternate update method
            """
            await game.edit(
                content="",
                embed=await render_board(level.update().get("board")),
                view=Control(level),
            )
        # game_loop.start()


async def setup(bot):
    await bot.add_cog(Game(bot))
