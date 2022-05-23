from asyncio import TimeoutError
from typing import Optional

from discord import Embed, Forbidden, Member
from discord.ext import commands

class Business(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True, aliases=['b'], case_insensitive=True, description = "The top level Business command. Use a subcommand.")
    async def business(self, ctx: commands.Context):

        embed = Embed(title="Business", description="The top level Business command. Use a subcommand.", color=ctx.author.color)

        embed.set_footer(text=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)

        embed.add_field("create", "Create a new business if you don't already have one.", inline=False)

        await ctx.reply(embed = embed)
    
    @business.command(name="create", aliases=['c'], description="Create a new business if you don't already have one.")
    async def business_create(self, ctx: commands.Context):
        business = await self.bot.db.business.find_one({"owner_id": ctx.author.id})
        if business:
            return await ctx.reply("You already have a business!")

       
        await ctx.send("What is the name of your business?\nEnter `cancel` to cancel.")
        
        # Creation logic

        try:
            message = await self.bot.wait_for("message", check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout = 15) # Get name of business?

        except TimeoutError:
            return await ctx.reply("Timed out, try again when you're ready to make such a commitment.")

        if message.content.lower() == "cancel":
            return await ctx.reply("Cancelled. Come back when you're ready to make a commitment.") # If they cancelled then cancel

        await self.bot.db.business.insert_one({
            "owner_id": ctx.author.id,
            "name": message.content,
            "rockets": [],
            "income_per_second": 0
        })

        await ctx.reply("Business created!")

    @business.command(name = "edit", aliases = ['e'], description = "Edit your business's name.")
    async def business_edit(self, ctx, *, name: Optional[str]):
        if not name:
            return await ctx.reply("You need to specify a name.")

        business = await self.bot.db.business.find_one({"owner_id": ctx.author.id})
        
        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        await self.bot.db.business.update_one(business, {"$set": {"name": name}})

        await ctx.reply("Business name updated.")

    @business.command(name = "delete", aliases = ['d'], description = "Delete your business. This cannot be reversed.")
    async def business_delete(self, ctx):
        business = await self.bot.db.business.find_one({"owner_id": ctx.author.id})
        
        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        await ctx.send("To confirm you want to delete your business, enter your business's name in chat.\nEnter `cancel` to cancel.")
        try:
            message = await self.bot.wait_for("message", check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout = 15) # Get name of business for confirmation
        except TimeoutError:
            return await ctx.reply("Timed out, try again when you're ready to make such a bad choice.")
        
        if message.content.lower() != business["name"]:
            return await ctx.reply("You didn't enter the name of your business correctly, so we won't delete it. Try again.")
        
        await self.bot.db.business.delete_one(business)
        await ctx.reply("**Business deleted.** Don't cry to the developers if you want it back. You *can* restart later though.")
    
    @business.command(name = "transfer", aliases = ['t'], description = "Transfer ownership of your business to another user.")
    async def business_transfer(self, ctx, user: Member):
        business = await self.bot.db.business.find_one({"owner_id": ctx.author.id})

        if not business:
            return await ctx.reply("You don't have ownership of a business!")

        if user.id == ctx.author.id:
            return await ctx.reply("You can't transfer ownership to yourself.")
        await ctx.send(f"To confirm you want to transfer ownership of your business to **{user.display_name}**, enter your business's name in chat.\nEnter `cancel` to cancel.")

        try:
            message = await self.bot.wait_for("message", check = lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id, timeout = 15) # Get name of business for confirmation
        except TimeoutError:
            return await ctx.reply("Timed out, try again when you're ready to make such a bad choice.")
        
        if message.content.lower() != business["name"]:
            return await ctx.reply("You didn't enter the name of your business correctly, so we won't transfer ownership. Try again.")
        
        await self.bot.db.business.update_one(business, {"$set": {"owner_id": user.id}})
        await ctx.reply(f"Business ownership transferred to **{user.display_name}**.")

        try:
            await user.send(f"You have been given ownership of **{business['name']}** by **{ctx.author.display_name}**.")
        except Forbidden:
            await ctx.send(f"**{user.mention}**, you have been given ownership of **{business['name']}** by **{ctx.author.display_name}**.")
        
    """
    Ok so far we have created the business commands:
    business create
        For creation
    business edit
        For editing
    business delete
        For deletion
    business transfer
        For transformation
    
    Now that we have those, we need to implement how to:
        Get rockets
            Use rockets
        Get income from said rockets

    After that, we need to implement a rebirth system I'd guess.
    """