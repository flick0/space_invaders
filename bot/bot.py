import os
from time import time

import discord
import motor.motor_asyncio
from discord.ext import commands

from db import *

from .commands.helpers import Business


class Bot(commands.Bot):
    """discord"""

    def __init__(self):
        self.COGS = []
        super().__init__(
            command_prefix="=",
            intents=discord.Intents.all(),
            activity=discord.Game(name="=help"),
        )
        self.owner_ids = [482139697796349953, 507969622876618754]

    def calculate_income(self, business: Business) -> float | int:
        """Calculates the income for a business."""
        base = 1
        base *= int(
            int(int(time()) - int(business.last_claim_time) / 60)
        )  # How many seconds its been since last claim.

        multiplier = [rocket.rate for rocket in business.rockets]
        multiplier.append(1)

        base *= sum(multiplier)

        return base

    async def on_ready(self):
        """Run when bot is Ready."""
        print(f"{self.user} is ready!")
        async for cog in self.load_all():
            if cog[1] is not None:
                print(f"Failed to load {cog[0]}: {cog[1]}")
                raise (cog[1])
            else:
                print(f"Loaded {cog[0]}")
        """
        load databases
        """
        self.db = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
        self.db.business = BusinessDatabase(
            self.db["business"]["businesses"]
        )  # Database -> Collection or other way round I forgot
        self.db.launcher = ShipDatabase(self.db["business"]["launchers"])

    def run(self):
        super().run(os.environ["TOKEN"])

    #
    # Cog controls
    #

    async def load_all(self) -> tuple[str, Exception]:
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

    async def unload_all(self) -> tuple[str, Exception]:
        for cog in list(self.COGS):
            err = None
            try:
                await super().unload_extension(cog)
            except Exception as e:
                err = e
            self.COGS.remove(cog)
            yield (cog, err)

    async def load_cog(self, cog: str, *, package=None) -> tuple[str, Exception]:
        err = None
        try:
            await super().load_extension(cog, package=package)
        except Exception as e:
            err = e
        self.COGS.append(cog)
        return (cog, err)

    async def unload_cog(self, cog: str, *, package=None) -> tuple[str, Exception]:
        err = None
        try:
            await super().unload_extension(cog, package=package)
        except Exception as e:
            err = e
        self.COGS.remove(cog)
        return (cog, err)


def run():
    return Bot().run()
