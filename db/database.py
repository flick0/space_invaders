from time import time

from bot.commands.helpers import *


class ShipDatabase:
    """database holding all stats of player ships"""

    def __init__(self, db):
        self.db = db

    async def update_one(self, *args, **kwargs):
        return await self.db.update_one(*args, **kwargs)

    async def fetch_launcher(self, owner_id: int):
        data = await self.db.find_one({"owner_id": owner_id})
        if data:
            return data
        else:
            await self.create_launcher(owner_id)
            return await self.db.find_one({"owner_id": owner_id})

    async def add_stats(self, owner_id: int, stat: str, amount: int):
        if stat in ["dmg", "collision_dmg", "firerate", "speed", "pen", "hp"]:
            await self.db.update_one({"owner_id": owner_id}, {"$inc": {stat: amount}})
            return await self.fetch_launcher(owner_id)
        else:
            return False

    async def set_stats(self, owner_id: int, stat: str, amount: int):
        if stat in ["dmg", "collision_dmg", "firerate", "speed", "pen", "hp"]:
            await self.db.update_one({"owner_id": owner_id}, {"$set": {stat: amount}})
            return await self.fetch_launcher(owner_id)
        else:
            return False

    async def create_launcher(self, owner_id: int):
        await self.db.insert_one(
            {
                "owner_id": owner_id,
                "dmg": 1,
                "collision_dmg": 5,
                "firerate": 0.5,
                "speed": 1,
                "pen": 0,
                "hp": 1,
                "pattern": "single",
            }
        )


class BusinessDatabase:
    """database holding all businesses of players"""

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
        await self.db.update_one({"owner_id": owner_id}, {"$inc": {"money": amount}})
        return await self.fetch_business(owner_id)
    
    async def add_rocket(self,owner_id: int, rocket:Rocket):
        await self.db.update_one(
            {"owner_id": owner_id},
            {"$push": {"rockets": rocket.to_dict()}},
        )
        return await self.fetch_business(owner_id)

    async def fetch_rockets(self, owner_id: int):
        data = await self.db.find_one({"owner_id": owner_id})
        return [Rocket.from_dict(rocket) for rocket in data["rockets"]]

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
