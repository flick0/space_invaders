from typing import List
from discord import SelectOption
from discord.ui import Select


class Rocket:
    def __init__(self, name: str, rate: float, price: float):
        self.name = name
        self.rate = rate
        self.price = price

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["name"], data["rate"], data["price"])

    def to_dict(self):
        return {"name": self.name, "rate": self.rate, "price": self.price}


class Business:
    def __init__(
        self,
        owner_id: int,
        name: str,
        rockets: List[Rocket],
        income_per_second: int,
        last_claim_time: int,
        money: int,
    ):
        self.owner_id = owner_id
        self.name = name
        self.rockets = rockets
        self.income_per_second = income_per_second
        self.last_claim_time = last_claim_time
        self.money = money

    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "name": self.name,
            "rockets": [rocket.to_dict() for rocket in self.rockets],
            "income_per_second": self.income_per_second,
            "last_claim_time": self.last_claim_time,
            "money": self.money,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["owner_id"],
            data["name"],
            [Rocket.from_dict(rocket) for rocket in data["rockets"]],
            data["income_per_second"],
            data["last_claim_time"],
            data["money"],
        )


class RocketMenu(Select):
    def __init__(self, rockets: list[Rocket]):

        options = []
        for rocket in rockets:
            options.append(
                SelectOption(
                    label=rocket.name,
                    value=rocket.name,
                    description=f"A rocket which costs {rocket.price} and earns {rocket.rate} per second.",
                    emoji="\U000025b6",
                )
            )

        super().__init__(
            placeholder="View available rockets!",
            min_values=1,
            max_values=len(rockets),
            options=options,
        )

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.response.edit(view=self)

    async def callback(self, interaction):
        business_data = await interaction.client.db.business.find_one(
            {"owner_id": interaction.author.id}
        )

        if not business_data:
            return await interaction.send("You don't own a business!")

        rockets = []
        total = 0

        for value in interaction.values:
            rocket = Rocket.from_dict(
                interaction.client.get_cog("Business").rockets[value]
            )
            total += rocket.price
            rockets.append(rocket)

        if total > business_data["money"]:
            return await interaction.send("You don't have enough money!")

        await interaction.client.db.business.update_one(
            {business_data, {"$inc": {"money": -total}}}
        )
        await interaction.response.send_message(
            f"You bought {', '.join([rocket.name for rocket in rockets])} for {total}!"
        )


class SellRocketMenu(RocketMenu):
    async def callback(self, interaction):
        business_data = await interaction.client.db.business.find_one(
            {"owner_id": interaction.author.id}
        )

        if not business_data:
            return await interaction.send("You don't own a business!")

        rockets = []
        total = 0

        for value in interaction.values:
            rocket = Rocket.from_dict(
                interaction.client.get_cog("Business").rockets[value]
            )
            total += rocket.price
            rockets.append(rocket)

        total *= 0.75

        await interaction.client.db.business.update_one(
            {business_data, {"$inc": {"money": total}}}
        )
        await interaction.response.send_message(
            f"You sold {', '.join([rocket.name for rocket in rockets])} for {total}!"
        )
