import motor.motor_asyncio
import os

import discord
from discord.ext import commands


class Bot(commands.Bot):
    def __init__(self):
        self.COGS = []
        super().__init__(
            command_prefix = "=",
            intents = discord.Intents.all(),
            activity = discord.Game(name="=help")
        )

    async def on_ready(self):
        """Ran when bot is Ready."""

        print(f"{self.user} is ready!")

        async for cog in self.load_all():
            if cog[1] is not None:
                print(f"Failed to load {cog[0]}: {cog[1]}")
                raise (cog[1])
            else:
                print(f"Loaded {cog[0]}")
    
        self.db = motor.motor_asyncio.AsyncIOMotorClient(f"mongodb+srv://Untraceable:PasswordThatIsSecure!@localhost:27017/")
        self.db.business = self.db["business"]["businesses"] # Collection -> Database or other way round I forgot

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

    def run(self):
        super().run(os.environ["TOKEN"])

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


def run():
    return Bot().run()