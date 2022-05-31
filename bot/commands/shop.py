from asyncio import TimeoutError
from time import time
from typing import Dict, Optional

from discord import Embed, Forbidden, Member
from discord.ext import commands
from discord.ui import View

from .helpers.components import ShopMenu

class Item:
    def __init__(self,name:str,price:int,emoji:str,step:int):
        self.name = name
        self.price = price
        self.emoji = emoji
        self.step = step
    
    def multiplier(self,multiply:int):
        self.price *= multiply
    
    def from_dict(self,data:Dict):
        self.name = data["name"]
        self.price = data["price"]
        self.emoji = data["emoji"]
    
    def to_dict(self):
        return {
            "name":self.name,
            "price":self.price,
            "emoji":self.emoji
        }
        

class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.items = {
            "dmg":Item("dmg",5_000,"💥",1),
            "collision_dmg":Item("collision_dmg",10_000,"💥",1),
            "firerate":Item("firerate",20_000,"🔥",0.1),
            "speed":Item("speed",20_000,"🚀",0.1),
            "pen":Item("pen",70_000,"💣",1),
            "hp":Item("hp",10_000,"❤️",1)
        }

    @commands.group(
        invoke_without_command=True,
        aliases=["s"],
        case_insensitive=True,
        description="The top level shop command. Use a subcommand.",
    )
    async def shop(self, ctx: commands.Context):

        embed = Embed(
            title="Shop",
            description="The top level Shop command. Use a subcommand.",
            color=ctx.author.color,
        )

        embed.set_footer(
            text=ctx.author.display_name, icon_url=ctx.author.avatar.url
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)

        embed.add_field(
            name="buy", value="buy an item from the list", inline=False
        )
        await ctx.reply(embed=embed)


    @shop.command(name="buy", description="Buy a rocket.", aliases=["b"])
    async def rocket_buy(self, ctx):
        launcher = await self.bot.db.launcher.fetch_launcher(ctx.author.id)
        items = self.items.copy()
        for item in items.values():
            if launcher[item.name] < 0:
                item.multiplier(int(launcher[item.name]*10))
            elif launcher[item.name] != 0:
                item.multiplier(launcher[item.name])
        await ctx.reply(
            "Select a upgrade to buy from the menu below.",
            view=View().add_item(ShopMenu(items,ctx.author)),
        )


async def setup(bot):
    await bot.add_cog(Shop(bot))
