from discord import SelectOption
from discord.ui import Select
from .objects import *

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
        business = await interaction.client.db.business.fetch_business(interaction.user.id)

        if not business:
            return await interaction.response.send_message("You don't own a business!")

        rockets = []
        total = 0

        for value in interaction.values:
            rocket = Rocket.from_dict(
                interaction.client.get_cog("Business").rockets[value]
            )
            total += rocket.price
            rockets.append(rocket)

        if total > business.money:
            return await interaction.response.send_message("You don't have enough money!")

        await interaction.client.db.business.add_money(-total)
        await interaction.response.send_message(
            f"You bought {', '.join([rocket.name for rocket in rockets])[:-1]} for {total}!"
        )

class SellRocketMenu(RocketMenu):
    async def callback(self, interaction):
        business = await interaction.client.db.business.fetch_business(interaction.user.id)

        if not business:
            return await interaction.response.send_message("You don't own a business!")

        rockets = []
        total = 0

        for value in interaction.values:
            rocket = Rocket.from_dict(
                interaction.client.get_cog("Business").rockets[value]
            )
            total += rocket.price
            rockets.append(rocket)

        total *= 0.75

        await interaction.client.db.business.add_money(total)
        await interaction.response.send_message(
            f"You sold {', '.join([rocket.name for rocket in rockets])[:-1]} for {total}!"
        )
