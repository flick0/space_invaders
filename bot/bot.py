import os

import discord
from discord.ext import commands


class Bot(commands.AutoShardedBot):
    def __init__(self):
        self.COGS = []
        self.message_cache = {}
        super().__init__(
            command_prefix="!",
            strip_after_prefix=True,
            intents=discord.Intents.all(),
        )

    async def on_ready(self):
        """run when bot is ready"""
        print(f"{self.user} is ready!")
        await self.change_presence(activity=discord.Game(name="!help"))

        async for cog in self.load_all():
            if cog[1] is not None:
                print(f"Failed to load {cog[0]}: {cog[1]}")
                raise (cog[1])
            else:
                print(f"Loaded {cog[0]}")

    async def load_all(self):
        await super().load_extension("jishaku")
        for file in os.listdir("./bot/commands"):
            if file.endswith(".py"):
                err = None
                try:
                    await super().load_extension(f"bot.commands.{file[:-3]}")
                except Exception as e:
                    err = e
                self.COGS.append(f"bot.commands.{file[:-3]}")
                yield (f"bot.commands.{file[:-3]}", err)

    async def unload_all(self):
        for cog in list(self.COGS):
            err = None
            try:
                await super().unload_extension(cog)
            except Exception as e:
                err = e
            self.COGS.remove(cog)
            yield (cog, err)

    async def load_cog(self, cog: str, *, package=None):
        err = None
        try:
            await super().load_extension(cog, package=package)
        except Exception as e:
            err = e
        self.COGS.append(cog)
        return (cog, err)

    async def unload_cog(self, cog: str, *, package=None):
        err = None
        try:
            await super().unload_extension(cog, package=package)
        except Exception as e:
            err = e
        self.COGS.remove(cog)
        return (cog, err)


def run(token):
    return Bot().run(token)
