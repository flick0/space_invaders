from asyncio import TimeoutError
from time import time
from typing import List, Optional

from discord import Embed, Forbidden, Member
from discord.ext import commands
from .helpers.components import *
from discord.ui import View


class Business(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rockets: List[Rocket] = [Rocket("Basic", 0.1, 100)]

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

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="create",
            value="Create a new business if you don't already have one.",
            inline=False,
        )
        embed.add_field(name="delete", value="Delete your business.", inline=False)
        embed.add_field(name="edit", value="Edit your business's name.", inline=False)
        embed.add_field(
            name="transfer",
            value="Transfer ownership of your business.",
            inline=False,
        )
        embed.add_field(
            name="information",
            value="View information about your business.",
            inline=False,
        )
        embed.add_field(
            name="take_off",
            value="Take off your business rockets.",
            inline=False,
        )

        await ctx.reply(embed=embed)

    @business.command(name="information", aliases=["i", "info"])
    async def business_information(self, ctx: commands.Context):
        business = await self.bot.db.business.fetch_business(ctx.author.id)

        if not business:
            return await ctx.reply("You don't have a business!")

        embed = Embed(
            title="Business Information",
            description="Information about your business.",
            color=ctx.author.color,
        )

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(name="Name", value=business.name, inline=False)
        embed.add_field(
            name="Income",
            value=f"{business.income_per_second} per second",
            inline=False,
        )
        embed.add_field(
            name="Money",
            value=f"{business.money}",
            inline=False,
        )
        embed.add_field(
            name="Money you can claim.",
            value=f"{business.income_per_second * (int(time.time()) - business.last_claim_time)}",
        )

        value = ""

        for rocket in business.to_dict()["rockets"]:

            if len(value > 1024):
                value += f"{rocket['name']} - {rocket['amount']}\n"
            else:
                embed.add_field(name="Rockets", value=value, inline=False)
            value = ""
        if value:
            embed.add_field(name="Rockets", value=value, inline=False)
        await ctx.reply(embed=embed)

    @business.command(
        name="create",
        aliases=["c"],
        description="Create a new business if you don't already have one.",
    )
    async def business_create(self, ctx: commands.Context):

        business = await self.bot.db.business.fetch_business(ctx.author.id)

        if business:
            return await ctx.reply("You already have a business!")

        await ctx.send("What is the name of your business?\nEnter `cancel` to cancel.")

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

        await self.bot.db.business.create_business(
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
            await ctx.send("Please enter a name. Enter `cancel` to cancel.")

            try:
                message = await self.bot.wait_for("message", check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout=15)
            except TimeoutError:
                return await ctx.reply("Timed out, try again when you're ready to make a commitment.")
            name = message.content

        business = await self.bot.db.business.fetch_business({"owner_id": ctx.author.id})

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        await self.bot.db.business.edit(business.owner_id, name)

        await ctx.reply("Business name updated.")

    @business.command(
        name="delete",
        aliases=["d"],
        description="Delete your business. This cannot be reversed.",
    )
    async def business_delete(self, ctx):
        business = await self.bot.db.business.fetch_business({"owner_id": ctx.author.id})

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

        if message.content.lower() != business.name:
            return await ctx.reply(
                "You didn't enter the name of your business correctly, so we won't delete it. Try again."
            )

        await self.bot.db.business.delete_business(business)
        await ctx.reply(
            "**Business deleted.** Don't cry to the developers if you want it back. You *can* restart later though."
        )

    @business.command(
        name="take_off",
        aliases=["tf"],
        description="Take off your rockets, gaining you money.",
    )
    async def business_take_off(self, ctx):
        business = await self.bot.db.business.fetch_business({"owner_id": ctx.author.id})
        if not business:
            return await ctx.reply("You don't have a business!")

        rockets = [Rocket.from_dict(data) for data in business.rockets]
        income = 0
        for rocket in rockets:
            seconds = (
                int(time()) - business.last_claim_time
            )  # CurrentTime - LastClaimTime = Difference
            multiplier = (
                seconds * rocket.income_per_second
            )  # Difference * IncomePerSecond
            income += rocket.rate * multiplier  # HowMuchMoneyRocketMakes * Difference
        await self.bot.db.business.add_money(business.owner_id, income)
        await self.bot.db.business.update_one(
            business, {"$set": {"last_claim_time": int(time())}}
        )
        await ctx.reply(f"You earned {income}!")

    @business.command(
        name="transfer",
        aliases=["t"],
        description="Transfer ownership of your business to another user.",
    )
    async def business_transfer(self, ctx, user: Member):
        business = await self.bot.db.business.fetch_business({"owner_id": ctx.author.id})

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

        await self.bot.db.business.transfer_business_ownership(business.to_dict(), {"$set": {"owner_id": user.id}})
        await ctx.reply(f"Business ownership transferred to **{user.display_name}**.")

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

        embed.set_author(name="Rocket Command", icon_url=ctx.author.avatar.url)
        embed.set_footer(
            text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url
        )

        embed.add_field(name="buy", value="Buy a rocket.", inline=False)
        embed.add_field(name="sell", value="Sell a rocket.", inline=False)
        embed.add_field(name="list", value="List all of your rockets.", inline=False)
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

async def setup(bot):
    await bot.add_cog(Business(bot))
