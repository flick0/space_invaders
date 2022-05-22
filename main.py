from os import environ
from discord.ext import commands

class SpaceInvaders(commands.Bot):
    def run(self):
        super().run(environ['TOKEN'])
