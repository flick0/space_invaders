<<<<<<< HEAD
import os

from bot import bot

bot.run(os.environ["TOKEN"])
=======
from os import environ
from discord.ext import commands

class SpaceInvaders(commands.Bot):
    def run(self):
        super().run(environ['TOKEN'])
>>>>>>> 6125b0a137b11fa58415e007a3c77b934ee47fc1
