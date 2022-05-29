from time import time
import motor.motor_asyncio
from .commands.helpers import Business
import os

import discord
from discord.ext import commands


class BusinessDatabase:
    def __init__(self, db):
        self.db = db

    async def update_one(self, *args, **kwargs):
        return await self.db.update_one(*args, **kwargs)

    async def fetch_business(self, owner_id: int):
        data = await self.db.find_one({"owner_id": owner_id})
        return Business.from_dict(data) if data else None

    async def delete_business(self, owner_id: int):
        data = await self.db.delete_one({"owner_id": owner_id})
        return Business.from_dict(data)

    async def transfer_business_ownership(self, old_owner_id: int, new_owner_id: int):
        await self.db.update_one(
            {"owner_id": old_owner_id}, {"$set": {"owner_id": new_owner_id}}
        )
        return await self.fetch_business(new_owner_id)

    async def edit(self, owner_id: int, name: str):
        await self.db.update_one({"owner_id": owner_id}, {"$set": {"name": name}})
        return await self.fetch_business(owner_id)

    async def add_money(self, owner_id: int, amount: int):
        await self.db.update_one(
            {"owner_id": owner_id}, {"$inc": {"money": amount}}
        )
        return await self.fetch_business(owner_id)

    async def create_business(self, owner_id: int, name: str):
        await self.db.insert_one(
            {
                "owner_id": owner_id,  # The owner of the business
                "name": name,  # The name of the business
                "rockets": [],  # The rockets they own
                "money": 100,  # How much money they have
                "last_claim_time": int(
                    time()
                ),  # The last time they claimed their money
            }
        )


class Bot(commands.Bot):
    def __init__(self):
        self.COGS = []
        super().__init__(
            command_prefix="=",
            intents=discord.Intents.all(),
            activity=discord.Game(name="=help"),
        )
        self.owner_ids = [482139697796349953, 507969622876618754]

    def calculate_income(self, business: Business):
        """Calculates the income for a business."""
        base = 1
        base *= int(time() - business.last_claim_time) 
        multiplier = 1
        for rocket in business.rockets:
            multiplier += rocket.rate
        base *= multiplier
        return base

    async def on_ready(self):
        """Ran when bot is Ready."""

        print(f"{self.user} is ready!")

        async for cog in self.load_all():
            if cog[1] is not None:
                print(f"Failed to load {cog[0]}: {cog[1]}")
                raise (cog[1])
            else:
                print(f"Loaded {cog[0]}")

        self.db = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGO_URI"])
        self.db.business = BusinessDatabase(
            self.db["business"]["businesses"]
        )  # Database -> Collection or other way round I forgot

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
