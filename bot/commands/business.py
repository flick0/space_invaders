from asyncio import TimeoutError
from time import time
from typing import List, Optional

from discord import Embed, Forbidden, Member, SelectOption
from discord.ext import commands
from discord.ui import Select, View


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
    def __init__(self, owner_id: int, name: str, rockets: List[Rocket], income_per_second: int, last_claim_time: int, money: int):
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
            "money": self.money
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(data["owner_id"], data["name"], [Rocket.from_dict(rocket) for rocket in data["rockets"]], data["income_per_second"], data["last_claim_time"], data["money"])


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


class Business(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rockets: List[Rocket] = [
            Rocket(
                "Basic",
                0.1,
                100
            )
        ]

    @commands.group(
        invoke_without_command=True,
        aliases=["b"],
        case_insensitive=True,
        description="The top level Business command. Use a subcommand.",
    )
    async def business(self, ctx: commands.Context):

        embed = Embed(
            title="Business",
            description="The top level Business command. Use a subcommand.",
            color=ctx.author.color,
        )

        embed.set_footer(
            text=ctx.author.display_name, icon_url=ctx.author.avatar.url
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="create",
            value="Create a new business if you don't already have one.",
            inline=False,
        )
        embed.add_field(
            name="delete", value="Delete your business.", inline=False
        )
        embed.add_field(
            name="edit", value="Edit your business's name.", inline=False
        )
        embed.add_field(
            name="transfer",
            value="Transfer ownership of your business.",
            inline=False,
        )
        embed.add_field(
            name = "information",
            value = "View information about your business.",
            inline = False,
        )
        embed.add_field(
            name = "take_off",
            value = "Take off your business rockets.",
            inline = False,
        )

        await ctx.reply(embed=embed)

    @business.command(name = "information", aliases = ["i", "info"])
    async def business_information(self, ctx: commands.Context):
        business_data = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )

        if not business_data:
            return await ctx.send("You don't own a business!")

        embed = Embed(
            title="Business Information",
            description="Information about your business.",
            color=ctx.author.color,
        )

        embed.set_footer(
            text=ctx.author.display_name, icon_url=ctx.author.avatar.url
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="Name", value=business_data["name"], inline=False
        )
        embed.add_field(
            name="Income",
            value=f"{business_data['income_per_second']} per second",
            inline=False,
        )
        embed.add_field(
            name="Money",
            value=f"{business_data['money']}",
            inline=False,
        )

        await ctx.reply(embed=embed)

    @business.command(
        name="create",
        aliases=["c"],
        description="Create a new business if you don't already have one.",
    )
    async def business_create(self, ctx: commands.Context):
        business = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )
        if business:
            return await ctx.reply("You already have a business!")

        await ctx.send(
            "What is the name of your business?\nEnter `cancel` to cancel."
        )

        # Creation logic

        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=15,
            )  # Get name of business?

        except TimeoutError:
            return await ctx.reply(
                "Timed out, try again when you're ready to make such a commitment."
            )

        if message.content.lower() == "cancel":
            return await ctx.reply(
                "Cancelled. Come back when you're ready to make a commitment."
            )  # If they cancelled then cancel

        await self.bot.db.business.insert_one(
            {
                "owner_id": ctx.author.id,
                "name": message.content,
                "rockets": [],
                "income_per_second": 0,
                "last_claim_time": int(time()),
                "money": 100,
            }
        )

        await ctx.reply("Business created!")

    @business.command(
        name="edit", aliases=["e"], description="Edit your business's name."
    )
    async def business_edit(self, ctx, *, name: Optional[str]):
        if not name:
            return await ctx.reply("You need to specify a name.")

        business = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        await self.bot.db.business.update_one(
            business, {"$set": {"name": name}}
        )

        await ctx.reply("Business name updated.")

    @business.command(
        name="delete",
        aliases=["d"],
        description="Delete your business. This cannot be reversed.",
    )
    async def business_delete(self, ctx):
        business = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        await ctx.send(
            "To confirm you want to delete your business, enter your business's name in chat.\nEnter `cancel` to cancel."
        )
        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=15,
            )  # Get name of business for confirmation
        except TimeoutError:
            return await ctx.reply(
                "Timed out, try again when you're ready to make such a bad choice."
            )

        if message.content.lower() != business["name"]:
            return await ctx.reply(
                "You didn't enter the name of your business correctly, so we won't delete it. Try again."
            )

        await self.bot.db.business.delete_one(business)
        await ctx.reply(
            "**Business deleted.** Don't cry to the developers if you want it back. You *can* restart later though."
        )

    @business.command(
        name="take_off",
        aliases=["tf"],
        description="Take off your rockets, gaining you money.",
    )
    async def business_take_off(self, ctx):
        business_data = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )
        if not business_data:
            return await ctx.reply("You don't have a business!")

        rockets = business_data["rockets"]
        income = 0
        for rocket in rockets:
            seconds = (
                int(time()) - business_data["last_claim_time"]
            )  # CurrentTime - LastClaimTime = Difference
            multiplier = (
                seconds * rocket["income_per_second"]
            )  # Difference * IncomePerSecond
            income += (
                rocket.rate * multiplier
            )  # HowMuchMoneyRocketMakes * Difference
        await self.bot.db.business.update_one(
            business_data, {"$inc": {"money": income}}
        )
        await self.bot.db.business.update_one(
            business_data, {"$set": {"last_claim_time": int(time())}}
        )
        await ctx.reply(f"You earned {income}!")

    @business.command(
        name="transfer",
        aliases=["t"],
        description="Transfer ownership of your business to another user.",
    )
    async def business_transfer(self, ctx, user: Member):
        business = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        if user.id == ctx.author.id:
            return await ctx.reply("You can't transfer ownership to yourself.")
        await ctx.send(
            f"To confirm you want to transfer ownership of your business to **{user.display_name}**, enter your business's name in chat.\nEnter `cancel` to cancel."
        )

        try:
            message = await self.bot.wait_for(
                "message",
                check=lambda m: m.author.id == ctx.author.id
                and m.channel.id == ctx.channel.id,
                timeout=15,
            )  # Get name of business for confirmation
        except TimeoutError:
            return await ctx.reply(
                "Timed out, try again when you're ready to make such a bad choice."
            )

        if message.content.lower() != business["name"]:
            return await ctx.reply(
                "You didn't enter the name of your business correctly, so we won't transfer ownership. Try again."
            )

        await self.bot.db.business.update_one(
            business, {"$set": {"owner_id": user.id}}
        )
        await ctx.reply(
            f"Business ownership transferred to **{user.display_name}**."
        )

        try:
            await user.send(
                f"You have been given ownership of **{business['name']}** by **{ctx.author.display_name}**."
            )
        except Forbidden:
            await ctx.send(
                f"**{user.mention}**, you have been given ownership of **{business['name']}** by **{ctx.author.display_name}**."
            )

    @commands.group(
        name="rocket",
        invoke_without_command=True,
        description="The top level rocket command. Use a subcommand.",
        case_insensitive=True,
    )
    async def rocket(self, ctx):
        embed = Embed(
            title="Rocket Command",
            description="Use a subcommand to get information about rockets.",
            color=0x00FF00,
        )

        embed.set_author(
            name="Rocket Command", icon_url=ctx.author.avatar.url
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )

        embed.add_field(name="buy", value="Buy a rocket.", inline=False)
        embed.add_field(name="sell", value="Sell a rocket.", inline=False)
        embed.add_field(
            name="list", value="List all of your rockets.", inline=False
        )
        embed.add_field(
            name="info", value="Get information about a rocket.", inline=False
        )

        await ctx.reply(embed=embed)

    @rocket.command(name="buy", description="Buy a rocket.", aliases=["b"])
    async def rocket_buy(self, ctx):
        await ctx.reply(
            "Select a rocket to buy from the menu below.",
            view=View().add_item(RocketMenu()),
        )

    @rocket.command(name="sell", description="Sell a rocket.", aliases=["s"])
    async def rocket_sell(self, ctx):
        await ctx.reply(
            "Select a rocket to sell from the menu below.",
            view=View().add_item(SellRocketMenu()),
        )

    @rocket.command(
        name="list", description="List all of your rockets.", aliases=["l"]
    )
    async def rocket_list(self, ctx):
        business = await self.bot.db.business.find_one(
            {"owner_id": ctx.author.id}
        )

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        if not business["rockets"]:
            return await ctx.reply("You don't have any rockets!")

        embed = Embed(
            title="Rocket List",
            description="All of your rockets.",
            color=0x00FF00,
        )
        embed.set_author(name="Rocket List", icon_url=self.ctx.author.avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )

        for rocket in business["rockets"]:
            embed.add_field(
                name=rocket["name"],
                value=f"Cost: {rocket['cost']}",
                inline=False,
            )

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(Business(bot))