from typing import Dict

import discord
from discord import SelectOption
from discord.ui import Select

from .objects import *


async def win(interaction):
    await interaction.client.db.business.add_money(
            interaction.user.id, 50_000
    )
    embed = discord.Embed(title="You Win 50,000!")
    await interaction.message.edit(embed=embed, view=None)


async def lose(game):
    embed = discord.Embed(title="You Lose")
    await game.edit(embed=embed, view=None)


async def render_board(board):
    print(board)
    desc = ""
    for y in range(len(board[0])):
        for x in board:
            if x[y].get("bullet") and x[y].get("alien"):
                desc += "<:bl:979329177272610886>"
            elif x[y].get("alien"):
                desc += "<:al:979326671624740884>"
            elif x[y].get("ship"):
                desc += "<:sh:979326671285002250>"
            elif x[y].get("bullet"):
                desc += "<:bu:981184041598455858>"
            else:
                desc += "<:sp:979317788776726558>"
        desc += "\n"
    embed = discord.Embed(title=" ", description=desc)
    return embed

class Control(discord.ui.View):
    """buttons for controlling the game"""
    def __init__(self, level,author):
        self.level = level
        self.author = author
        super().__init__()

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("no you cant!",ephemeral=True)
            return False
        else:
            return True


    @discord.ui.button(
        label="<", custom_id="prev", style=discord.ButtonStyle.blurple
        )
    async def left(self, interaction, button):
        board = await self.level.control_ship("left")
        if board.get("win"):
            await win(interaction)
        elif board.get("lose"):
            await lose(interaction)
        elif board.get("board"):
            return await interaction.response.edit_message(
                embed=await render_board(board["board"]), view=self
            )

    @discord.ui.button(
        label="-", custom_id="stand", style=discord.ButtonStyle.green
    )
    async def stay(self, interaction, button):
        board = await self.level.update()
        if board.get("win"):
            await win(interaction)
        elif board.get("lose"):
            await lose(interaction)
        elif board.get("board"):
            return await interaction.response.edit_message(
                embed=await render_board(board["board"]), view=self
            )
        
    @discord.ui.button(
        label=">", custom_id="next", style=discord.ButtonStyle.blurple
    )
    async def right(self, interaction, button):
        board = await self.level.control_ship("right")
        if board.get("win"):
            await win(interaction)
        elif board.get("lose"):
            await lose(interaction)
        elif board.get("board"):
            return await interaction.response.edit_message(
                embed=await render_board(board["board"]), view=self
            )
    
class ShopMenu(Select):
    """select menu for shop"""
    def __init__(self, items:dict,author):
        self.items = items
        self.author = author
        options = []
        for item in items.values():
            options.append(
                SelectOption(
                    label=f"{item.name} +{item.step}",
                    value=item.name,
                    description=f"{int(item.price)}",
                    emoji=item.emoji,
                )
            )
        super().__init__(
            placeholder="View available upgrades",
            min_values=1,
            max_values=len(items),
            options=options,
        )

    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("no not you!",ephemeral=True)
            return False
        else:
            return True

    async def on_timeout(self):
        for child in self.children:
            child.disabled = True
        await self.response.edit(view=self)
    
    async def callback(self, interaction):
        business = await interaction.client.db.business.fetch_business(
            interaction.user.id
        )

        if not business:
            return await interaction.response.send_message(
                "You don't own a business!"
            )

        items = []
        total = 0

        for value in self.values:
            upgrade = self.items[value]
            total += upgrade.price
            items.append(upgrade)

        if total > business.money:
            return await interaction.response.send_message(
                "You don't have enough money!"
            )

        for item in items:
            await interaction.client.db.launcher.add_stats(
                interaction.user.id,
                item.name,
                item.step
                )

        await interaction.client.db.business.add_money(
            interaction.user.id, -total
        )
        await interaction.response.send_message(
            f"You bought {', '.join([item.name for item in items])} for {total}!"
        )


class RocketMenu(Select):
    """select menu for buying rockets"""
    def __init__(self, rockets: Dict[str, Rocket]):

        options = []
        for rocket in rockets.values():
            options.append(
                SelectOption(
                    label=rocket.name,
                    value=rocket.name,
                    description=f"A rocket which costs {rocket.price} and earns {rocket.rate} per second.",
                    emoji="🚀",
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
        business = await interaction.client.db.business.fetch_business(
            interaction.user.id
        )

        if not business:
            return await interaction.response.send_message(
                "You don't own a business!"
            )

        rockets = []
        total = 0

        for value in self.values:
            rocket = interaction.client.get_cog("Business").rockets[value]
            total += rocket.price
            rockets.append(rocket)

        if total > business.money:
            return await interaction.response.send_message(
                "You don't have enough money!"
            )

        await interaction.client.db.business.add_money(
            interaction.user.id, -total
        )
        await interaction.response.send_message(
            f"You bought {', '.join([rocket.name for rocket in rockets])} for {total}!"
        )


class SellRocketMenu(RocketMenu):
    """menu for selling rockets"""
    async def callback(self, interaction):
        business = await interaction.client.db.business.fetch_business(
            interaction.user.id
        )

        if not business:
            return await interaction.response.send_message(
                "You don't own a business!"
            )

        rockets = []
        total = 0

        for value in self.values:
            rocket = interaction.client.get_cog("Business").rockets[value]
            total += rocket.price
            rockets.append(rocket)

        total *= 0.75

        await interaction.client.db.business.add_money(
            interaction.user.id, total
        )
        await interaction.response.send_message(
            f"You sold {', '.join([rocket.name for rocket in rockets])} for {total}!"
        )
