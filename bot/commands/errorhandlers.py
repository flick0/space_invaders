import sys
import traceback

import discord
from discord.ext import commands


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx, *, _=None):
        await ctx.reply(f"Pong! {round(self.bot.latency * 1000, 2)}")

    global embed_grey
    embed_grey = discord.Color.light_gray()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, "on_error"):
            return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None:
                return
        ignored = (commands.CommandNotFound,)
        error = getattr(error, "original", error)
        if isinstance(error, ignored):
            return
        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f"{ctx.command} has been disabled.")
        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(
                    f"{ctx.command} can not be used in Private Messages."
                )
            except discord.HTTPException:
                pass
        else:
            # all errors not returned

            print(
                "Ignoring exception in command {}:".format(ctx.command),
                file=sys.stderr,
            )
            traceback.print_exception(
                type(error), error, error.__traceback__, file=sys.stderr
            )
            await ctx.reply(
                embed=discord.Embed(
                    title=f"🛑   **{ctx.command.qualified_name}** ",
                    description=f"```py\n{error}```",
                    color=embed_grey,
                )
            )


async def setup(client):
    await client.add_cog(CommandErrorHandler(client))
